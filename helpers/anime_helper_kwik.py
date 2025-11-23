import json
import os
import time
import asyncio
import re
from playwright.async_api import async_playwright,TimeoutError
import requests
from bs4 import BeautifulSoup
from db import get_db
from utils.helper import deobfuscate,extract_info

def cookies_expired(cookie_dict):
    now = time.time()
    for c in cookie_dict.values():
        exp = c.get("expires")
        if exp and exp < now:
            return True
    return False


CACHE_FILE = "animepahe_cookies.json"




CACHE_FILE = "animepahe_cookies.json"

async def get_animepahe_cookies():
    # 1️⃣ Check if cached cookies exist and are still valid
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        if not cookies_expired(data):  # Your existing expiry check
            print("Used cookies from Cached")
            return {k: v["value"] for k, v in data.items()}

    # 2️⃣ Else: try to regenerate cookies
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Go to Animepahe
            await page.goto("https://animepahe.si")

            # Wait for main content to load, not full network idle
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except TimeoutError:
                print("⚠️ Timeout waiting for DOMContentLoaded, continuing anyway...")

            # Optional small sleep to ensure cookies are set
            await asyncio.sleep(1)

            cookies = await context.cookies()
            await browser.close()

            # Prepare cookie dict
            cookie_dict = {
                c['name']: {
                    "value": c['value'],
                    "expires": c.get("expires")
                }
                for c in cookies
            }

            # Save to cache
            with open(CACHE_FILE, "w") as f:
                json.dump(cookie_dict, f)
            print("Used cookies from animepahe server")
            return {k: v["value"] for k, v in cookie_dict.items()}

    except Exception as e:
        print("⚠️ Failed to get new cookies:", e)
        # Fallback: return cached cookies if they exist, even if expired
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                print("Cookies gotten through the try except method")
            return {k: v["value"] for k, v in data.items()}
        return None  # No cookies available


def get_cached_anime_info(id):
    db = get_db()
    if not id:
        return None
    cursor = db.execute("SELECT * FROM anime_info WHERE internal_id =?", (id,))
    row = cursor.fetchone()
    episodes = get_actual_episode(row["external_id"])
    if not episodes:
        return None
    if int(episodes) != int(row["episodes"]):
        db.execute("UPDATE anime_info SET episodes = ? WHERE internal_id = ?",(episodes,id))
        db.commit()
        cursor = db.execute("SELECT * FROM anime_info WHERE internal_id =?", (id,))
        row = cursor.fetchone()
    print("Cached anime info function ran")
    return row

# Helper function used to get actual episode for the search because some episodes might 0 instead of actual value


def get_actual_episode(external_id):
    if not external_id:
        return None
    cookies = asyncio.run(get_animepahe_cookies())
    res = requests.get(
        f"https://animepahe.si/api?m=release&id={external_id}", cookies=cookies, timeout=10)
    data = res.json()
    return data.get("total")


def get_episode_session(id):
    if not id:
        return None

    db = get_db()
    cookies = asyncio.run(get_animepahe_cookies())  # Always available
    episode_result = []

    cursor = db.execute(
        "SELECT page_count FROM anime_episode WHERE external_id = ?", (id,))
    row = cursor.fetchone()

    if not row or not row["page_count"]:
        res = requests.get(
            f"https://animepahe.si/api?m=release&id={id}", cookies=cookies, timeout=10)
        data = res.json()

        if not data or not data.get("last_page"):
            return None

        db.execute(
            "INSERT INTO anime_episode(episode, external_id, page_count) VALUES (?, ?, ?)",
            (data.get("total"), id, data.get("last_page"))
        )
        db.commit()
        page_count = data.get("last_page")
    else:
        page_count = row["page_count"]

    for page in range(1, page_count + 1):  # clean range
        res = requests.get(
            f"https://animepahe.si/api?m=release&id={id}&sort=episode_asc&page={page}",
            cookies=cookies,
            timeout=10
        )
        data = res.json()
        time.sleep(1.5)
        episode_result.extend(data.get("data", []))
    print("Episode session function ran successfully")
    return episode_result


def get_pahewin_link(external_id, episode_id):
    if not episode_id or not external_id:
        return None
    url = f"https://animepahe.si/play/{external_id}/{episode_id}"
    cookies = asyncio.run(get_animepahe_cookies())
    print("Getting anime pahe cookies in get_pahewin_link function")
    res = requests.get(url, cookies=cookies, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    dropdown = soup.find("div", id="pickDownload")
    if not dropdown:
        return None
    links = dropdown.find_all("a", class_="dropdown-item")
    for a in links:
        text = a.get_text(" ", strip=True).lower()  # normalize and lowercase
        if "720p" in text and "eng" not in text:   # first 720p non-ENG
            print(f"Gotten pahe.win link successfully for {url}")
            print(f"Pahe.win link:{a['href']}")
            return a["href"]

    # If nothing found
    print("No link found")
    return None


def get_kiwi_url(pahe_url):
    if not pahe_url:
        print("No pahe.win link")
        return None
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*"
}

    res = requests.get(pahe_url,timeout=10,headers=headers)
    soup = BeautifulSoup(res.text,"html.parser")
    info = soup.find("script")
    if not info or "kwik" not in info.text:
        return None
    m = re.search(r"https?://(?:www\.)?kwik\.cx[^\s\"');]+", info.text)
    return m.group(0)


def get_kiwi_info(kiwi_url):
    try:
        if not kiwi_url:
            return None
        res = requests.get(kiwi_url,timeout=10)
        html_soup = BeautifulSoup(res.text,"html.parser")
        scripts = html_soup.find_all("script")
        obf_js = scripts[-2].text
        deobf_js = deobfuscate(obf_js)
        return {
            **extract_info(deobf_js),
            "kwik_session":res.cookies.get_dict().get("kwik_session")

        }
    except IndexError:
        print("Script is out of range -2")
        return None
    except Exception as e:
        print("Kiwi error Occured",e)
        traceback.print_exc()
        return None


def get_redirect_link(url,id,episode):
    if not url or not id or not episode:
        print("No url,episode or id detected ending now")
        return None
    db = get_db()
    info = get_kiwi_info(url)
    if not info:
        return {
            "status":500,
            "message":"Server timed out, retry request"
        }
    
    base_url = "https://wispy-resonance-ee4a.ayanokojix2306.workers.dev/"
    payload = {
        "kwik_url":url,
        "token":info.get("token"),
        "kwik_session":info.get("kwik_session")
    }
    res = requests.post(base_url,data=json.dumps(payload),timeout=10)
    if res.status_code != 200:
        print(res.text)
        return {
            "status":500,
            "message":"Server timed out"
        }
    data = res.json()
    size = info.get("size")
    direct_link = data.get("download_link")
    db.execute("INSERT OR REPLACE INTO cached_video_url(internal_id,episode,video_url,size) VALUES(?,?,?,?)",
               (id, episode, direct_link, size))
    db.commit()
    print(f"Direct url {direct_link} detected sending response now")
    return {
    "direct_link":direct_link,
    "episode":episode,
    "status":200,
    "size":size
    }
