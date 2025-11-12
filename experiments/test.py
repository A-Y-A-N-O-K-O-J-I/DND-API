import requests

url = "https://kwik.cx/d/Hd8rsjV7bew0"

# Cookies taken from the curl -b string
cookies = {
    "srv": "s0",
    "pp_main_4e5e04716f26fd21bf611637f4fb8a46": "1",
    "pp_exp_4e5e04716f26fd21bf611637f4fb8a46": "1762816748750",
    "cf_clearance": "Hr1JoV6o5RCjMf4MnIwjkmZ8aFq2JWrvXinzxpPnmDo-1762813149-1.2.1.1-q3JbDXaTMpdJ03rZ9rfVWZzRpgBOgbdZ7_e3MtzImMqMPdeUv19so5Uu7R1levTMm7IEtuMl7W.CcW7O1XHc2N9B.Cy.Mtdiq6Fd7PEnbJXGzHfCRTQUZKzFZ2reAP9RvSw1zVqcQz40CSQNy60drv8T59CetQ7vyGN.KJAnNeGhGSfwRpdTCKExlDvhg0.7tcNXIN67ttYlvF1vyguDRbS0EKeqXQpKFEyEPjph9Ms",
    "kwik_session": "eyJpdiI6ImR0S2FPUHFnL2JGd2JGREl6eHpHS0E9PSIsInZhbHVlIjoiMHBCUmZuWFhkaEovc2UzNDZab1ZNQmtEbjhuS3lkOG42L3RLTDRPOGsySkxEY0NmMjZoS0kySDIvWENkeHdjMHIydUNXR2RXb0xkNWZQVjRGb0VLT25Dck5yN0l5YkRzbzRVWmp1UWsxQ0lPb3FGczczamNwc0gyUjBQRmg1c0ciLCJtYWMiOiIzZWZkOGFkOTU3M2NmNzNhMzU2YWE3M2ZlZGM3YzgyMjEzNGU4NjFiNjM0YmI2YjJkNzdhOWQ1YjBhMDhhNDdmIiwidGFnIjoiIn0%3D",
    "pp_show_on_4e5e04716f26fd21bf611637f4fb8a46": "3",
    'dom3ic8zudi28v8lr6fgphwffqoz0j6c': 'eb3197ab-0d61-4699-82a3-f1383d4c1829%3A1%3A1',
    'uid_id2': 'eb3197ab-0d61-4699-82a3-f1383d4c1829:1:1'
}

# Headers mirrored from curl (minus Cookie which is passed via `cookies`)
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.5",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://kwik.cx",
    "priority": "u=0, i",
    "referer": "https://kwik.cx/f/Hd8rsjV7bew0",
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

# form payload (same as --data-raw '_token=...')
data = {"_token": "ErDN80t5f8Rr9UWYghwlQTtOl4QnNoP5v71zLaSV"}

# Use a session to keep things tidy
with requests.Session() as s:
    try:
        # you can pass cookies to session.post or rely on s.cookies.update(cookies) before posting
        resp = s.post(url, headers=headers, cookies=cookies, data=data, timeout=20,allow_redirects=False)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
    else:
        print("Status code:", resp.status_code)
        print("Final URL:", resp.url)
        print("Response snippet:\n", resp.text)
