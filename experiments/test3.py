from playwright.async_api import async_playwright,TimeoutError
import asyncio
import requests
from bs4 import BeautifulSoup
import json
import os
import time
async def get_kiwi_info(kiwi_url):
    if not kiwi_url:
        print("⚠️ No Kiwi URL provided")
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
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
                timezone_id='America/New_York',
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

            # Variable to store the direct download URL
            direct_url = None
            all_urls = []  # Track all URLs we see

            # Listen for ALL requests and responses
            async def handle_request(request):
                url = request.url
                if 'vault' in url or '.mp4' in url or 'kwik.cx/d/' in url:
                    print(f"📤 Request: {url}")
                    all_urls.append(url)

            async def handle_response(response):
                nonlocal direct_url
                url = response.url
                
                # Log interesting URLs
                if 'vault' in url or '.mp4' in url or 'kwik.cx/d/' in url:
                    print(f"📥 Response ({response.status}): {url}")
                    all_urls.append(url)
                
                # Check if this is a redirect response
                if response.status in [301, 302, 303, 307, 308]:
                    redirect_location = response.headers.get('location')
                    if redirect_location:
                        print(f"🔀 Redirect to: {redirect_location}")
                        if 'vault' in redirect_location or '.mp4' in redirect_location:
                            direct_url = redirect_location
                            print(f"✅ Found redirect URL: {direct_url}")
                
                # Check if we landed on the final URL
                if 'vault' in url or '.mp4' in url:
                    direct_url = url
                    print(f"✅ Found direct URL: {direct_url}")

            page.on('request', handle_request)
            page.on('response', handle_response)

            # Go to the Kiwi URL
            print(f"📂 Navigating to: {kiwi_url}")
            await page.goto(kiwi_url, wait_until='domcontentloaded')


            # Wait for page to load
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except TimeoutError:
                print("⚠️ Timeout waiting for networkidle, continuing...")

            # Small sleep to ensure page is ready
            await asyncio.sleep(2)

            # Find and click the download button
            try:
                # Try multiple selectors for the button
                button_selectors = [
                    'form[action*="/d/"] button',
                ]
                
                download_button = None
                for selector in button_selectors:
                    try:
                        download_button = await page.wait_for_selector(selector, timeout=3000)
                        if download_button:
                            print(f"🎯 Found button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not download_button:
                    print("❌ Could not find download button")
                    # Get the form action URL as fallback
                    form = await page.query_selector('form[action*="/d/"]')
                    if form:
                        action = await form.get_attribute('action')
                        print(f"📝 Found form action: {action}")
                        # Navigate directly to the action URL
                        await page.goto(action, wait_until='domcontentloaded')
                        await asyncio.sleep(3)
                else:
                    print("🖱️ Clicking download button...")
                    
                    # Try clicking with navigation expectation
                    try:
                        async with page.expect_navigation(timeout=30000, wait_until='domcontentloaded'):
                            await download_button.click()
                    except:
                        # If navigation fails, just click anyway
                        await download_button.click()
                        await asyncio.sleep(3)
                
                # Wait for any redirects to complete
                await asyncio.sleep(3)
                
                # If we still don't have the direct URL, check current page
                if not direct_url:
                    current_url = page.url
                    print(f"🌐 Current URL: {current_url}")
                    
                    if 'vault' in current_url or '.mp4' in current_url:
                        direct_url = current_url
                        print(f"✅ Got final URL from page: {direct_url}")
                    else:
                        # Check for meta refresh redirect in HTML
                        html_content = await page.content()
                        
                        from bs4 import BeautifulSoup
                        import re
                        
                        soup = BeautifulSoup(html_content, 'html.parser')
                        meta_tag = soup.find('meta', {'http-equiv': 'refresh'})
                        
                        if meta_tag:
                            content = meta_tag.get('content', '')
                            match = re.search(r"url=['\"]?([^'\">\s]+)", content)
                            if match:
                                direct_url = match.group(1)
                                print(f"✅ Extracted URL from meta refresh: {direct_url}")
                
                # Final fallback: check all captured URLs
                if not direct_url and all_urls:
                    for url in reversed(all_urls):  # Check most recent first
                        if 'vault' in url and '.mp4' in url:
                            direct_url = url
                            print(f"✅ Found URL from captured requests: {direct_url}")
                            break
                
            except Exception as e:
                print(f"⚠️ Error during button click: {e}")
                import traceback
                traceback.print_exc()

            # Get cookies and HTML
            cookies = await context.cookies()
            html = await page.content()
            
            await browser.close()

            # Convert list of cookies to dict
            cookie_dict = {c['name']: c['value'] for c in cookies}
            
            if direct_url:
                print(f"🎉 Successfully extracted direct URL!")
                print(f"🔗 {direct_url}")
            else:
                print("❌ Could not extract direct download URL")
                if all_urls:
                    print(f"📋 Captured URLs: {all_urls}")
            
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

url = asyncio.run(get_kiwi_info("https://kwik.cx/f/3qJNj2U0NYp1"))
print(url)