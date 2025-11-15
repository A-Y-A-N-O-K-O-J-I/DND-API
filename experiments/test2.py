import re
from playwright.async_api import async_playwright,TimeoutError
import asyncio
from bs4 import BeautifulSoup
import requests
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

info = asyncio.run(get_kiwi_info("https://kwik.cx/f/3qJNj2U0NYp1"))
print(info["direct_url"])