import json
import os
import time
import asyncio
import re
from playwright.async_api import async_playwright,TimeoutError
import requests
from bs4 import BeautifulSoup
import cloudscraper
from db import get_db


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


async def get_kiwi_info(kiwi_url):
    if not kiwi_url:
        print("⚠️ No Kiwi URL provided")
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True,args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ])
            context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',  # Use common timezone
            permissions=['geolocation'],
            color_scheme='light',
            device_scale_factor=1,
        )
            await context.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            })
            page = await context.new_page()

            # Go to the Kiwi URL
            await page.goto(kiwi_url)

            # Wait for page to load, but don’t crash if it times out
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except TimeoutError:
                print("⚠️ Timeout waiting for page to load, continuing anyway...")

            # Small sleep to ensure cookies are set
            await asyncio.sleep(1)

            cookies = await context.cookies()
            html = await page.content()
            await browser.close()

            # Convert list of cookies to dict
            cookie_dict = {c['name']: c['value'] for c in cookies}
            print("Successfully gotten kiwi info")
            return {
                "cookies": cookie_dict,
                "html": html,
            }

    except Exception as e:
        print(f"⚠️ Failed to get Kiwi info: {e}")
        return None


def get_redirect_link(url,id,episode):
    if not url or not id or not episode:
        print("No url,episode or id detected ending now")
        return None
    db = get_db()
    info = asyncio.run(get_kiwi_info(url))
    if not info:
        return {
            "status":500,
            "message":"Server timed out, retry request"
        }
    html = info.get("html")
    soup = BeautifulSoup(html, "html.parser")
    form_info = soup.find("form")
    size = soup.find("form").find(
        "span").get_text().split("(")[1].split(")")[0]
    base_url = "https://access-kwik.apex-cloud.workers.dev"
    payload = {
        "service": "kwik",
        "action": "fetch",
        "content": {
            "kwik": url
        },
        "auth": ""#"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.O0FKaqhJjEZgCAVfZoLz6Pjd7Gs9Kv6qi0P8RyATjaE"
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    res = requests.post(base_url,data=json.dumps(payload),headers=headers)
    if res.status_code != 200:
        return {
            "status":500,
            "message":"Server timed out, retry request"
        }
    data = res.json()
    direct_link = data.get("content").get("url")
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
