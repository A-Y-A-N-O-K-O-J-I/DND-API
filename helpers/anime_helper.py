import asyncio
from playwright.async_api import async_playwright,TimeoutError
import requests
from bs4 import BeautifulSoup
from db import get_db
import json
import os
import time


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
    db = get_db()
    cursor = db.execute(
        "SELECT episode FROM anime_episode WHERE external_id = ?", (external_id,))
    row = cursor.fetchone()
    if not row or not row["episode"]:
        cookies = asyncio.run(get_animepahe_cookies())
        res = requests.get(
            f"https://animepahe.si/api?m=release&id={external_id}", cookies=cookies, timeout=10)
        data = res.json()
        db.execute("INSERT INTO anime_episode(episode,external_id,page_count) VALUES(?,?,?)",
                   (data.get("total"), external_id, data.get("last_page")))
        db.commit()
        print("Get actual episodes ran")
        return data.get("total")
    else:
        print("Get actual episodes ran with caching")
        return row["episode"]


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


async def fetch_page_html(url, wait_time=5.5):
    """
    Fetch the HTML of a page after waiting for `wait_time` seconds.
    Useful for pages like pahe.win where content loads after a short delay.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        print("Headless mode running")
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        print(f"Gone to {url} successfully")
        await asyncio.sleep(wait_time)  # wait for dynamic content to appear
        html = await page.content()
        await browser.close()
        print(f"Fetched html page for {url}")
        return html


async def get_kiwi_url(pahe_url):
    if not pahe_url:
        print("No pahe.win link")
        return None

    html = await fetch_page_html(pahe_url)
    if not html:
        print("no html")
        return None

    soup = BeautifulSoup(html, "html.parser")
    info = soup.find_all("div", class_="row")

    # Safety checks
    if len(info) < 2:
        return None

    container = info[1]
    info_for_cont = container.find("div", class_="row")
    if not info_for_cont:
        return None

    info_for_internal_cont = info_for_cont.find("a", class_="btn-block")
    if not info_for_internal_cont or not info_for_internal_cont.get("href"):
        return None
    print(f"Kiwi url gotten successfully({info_for_internal_cont['href']})")
    return info_for_internal_cont["href"]



async def get_kiwi_info(kiwi_url):
    if not kiwi_url:
        print("⚠️ No Kiwi URL provided")
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
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
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.5",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://kwik.cx",
                "priority": "u=0, i",
                "referer": kiwi_url,
                "sec-ch-ua": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            }
            cookie_dict = {c['name']: c['value'] for c in cookies}
            print("Successfully gotten kiwi info")
            return {
                "cookies": cookie_dict,
                "html": html,
                "headers": headers
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
    token = form_info.find("input")["value"]
    payload = {
        "_token": token
    }

    # Convert /f/ to /d/ for POST request
    post_url = url.replace("/f/", "/d/")

    res = requests.post(post_url, cookies=info.get(
        "cookies"), headers=info.get("headers"), data=payload, timeout=10,allow_redirects=False)
    html_content = res.text
    another_soup = BeautifulSoup(html_content,"html.parser")
    direct_link = another_soup.find_all("a")[1]["href"]
    db.execute("INSERT OR REPLACE INTO cached_video_url(internal_id,episode,video_url,size) VALUES(?,?,?,?)",(id,episode,direct_link,size))
    db.commit()
    print(f"Direct url {direct_link} detected sending response now")
    return {
    "direct_link":direct_link,
    "episode":episode,
    "status":200,
    "size":size
    }
