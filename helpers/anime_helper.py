import asyncio
import re
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
            browser = await p.chromium.launch(headless=True, args=[  # Changed to headless=False for testing
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ])
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                color_scheme='light',
                device_scale_factor=1,
            )
            
            page = await context.new_page()

            # Variable to store the direct download URL
            direct_url = None

            # Listen for responses after form submission
            async def handle_response(response):
                nonlocal direct_url
                url = response.url
                
                # Only care about responses AFTER we submit the form
                if 'vault' in url or '.mp4' in url:
                    direct_url = url
                    print(f"✅ Found direct URL: {direct_url}")
                elif response.status in [301, 302, 303, 307, 308]:
                    redirect_location = response.headers.get('location')
                    if redirect_location and ('vault' in redirect_location or '.mp4' in redirect_location):
                        direct_url = redirect_location
                        print(f"✅ Found redirect URL: {direct_url}")

            page.on('response', handle_response)

            # Go to the Kiwi URL
            print(f"📂 Navigating to: {kiwi_url}")
            await page.goto(kiwi_url, wait_until='load')

            # Wait for Cloudflare and page to fully load
            print("⏳ Waiting for page to load (including Cloudflare checks)...")
            await asyncio.sleep(5)  # Give Cloudflare time to finish

            # Wait for the download button/form to be visible
            try:
                print("🔍 Looking for download button...")
                await page.wait_for_selector('button[type="submit"].button.is-success', state='visible', timeout=15000)
                print("✅ Download button found!")
            except:
                print("⚠️ Timeout waiting for button, but continuing...")

            # NOW click the button
            try:
                print("🖱️ Clicking download button...")
                
                # Click the button and wait for navigation
                async with page.expect_navigation(timeout=30000):
                    await page.click('button[type="submit"].button.is-success')
                
                print("✅ Button clicked, waiting for redirect...")
                
                # Wait for the redirect to complete
                await asyncio.sleep(3)
                
                # Check if we got the direct URL
                if not direct_url:
                    current_url = page.url
                    print(f"🌐 Current URL: {current_url}")
                    
                    if 'vault' in current_url or '.mp4' in current_url:
                        direct_url = current_url
                    else:
                        # Check for meta refresh
                        html_content = await page.content()
                        
                        soup = BeautifulSoup(html_content, 'html.parser')
                        meta_tag = soup.find('meta', {'http-equiv': 'refresh'})
                        
                        if meta_tag:
                            content = meta_tag.get('content', '')
                            match = re.search(r"url=['\"]?([^'\">\s]+)", content)
                            if match:
                                direct_url = match.group(1)
                                print(f"✅ Extracted URL from meta refresh: {direct_url}")
                
            except Exception as e:
                print(f"❌ Error clicking button: {e}")
                import traceback
                traceback.print_exc()

            # Get cookies and HTML
            cookies = await context.cookies()
            html = await page.content()
            
            await browser.close()

            # Convert list of cookies to dict
            cookie_dict = {c['name']: c['value'] for c in cookies}
            
            if direct_url:
                print(f"🎉 SUCCESS! Direct URL: {direct_url}")
            else:
                print("❌ Could not extract direct download URL")
            
            return {
                "direct_url": direct_url,
                "cookies": cookie_dict,
                "html": html,
            }

    except Exception as e:
        print(f"❌ Error in get_kiwi_info: {e}")
        import traceback
        traceback.print_exc()
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
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://kwik.cx',
    'priority': 'u=0, i',
    'referer': url,
    'sec-ch-ua': '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36'
}
    if info.get("direct_url"):
        return {
    "direct_link":info.get("direct_url"),
    "episode":episode,
    "status":200,
    "size":size
    }

    res = requests.post(post_url, cookies=info.get(
        "cookies"), headers=headers, data=payload, timeout=10,allow_redirects=False)
    html_content = res.text
    print(html_content)
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
