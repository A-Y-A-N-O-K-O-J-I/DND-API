import tls_client

session = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=True
)

url = "https://kwik.cx/d/VFjuoZpRvYtH"  # change if needed

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.6",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Chromium\";v=\"142\", \"Brave\";v=\"142\", \"Not_A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "referer":"https://kwik.cx/f/VFjuoZpRvYtH",
    "upgrade-insecure-requests": "1",
    "cookie":"kwik_session=eyJpdiI6Im9EZGZJcmIwZVAwK2VKTUNRWU1pT1E9PSIsInZhbHVlIjoibTRsTW0rK3k4c1pDeWx4dTMwUGhiWC9ZcVJ3MFIyNGFrK2wvUTRVcUE5dGFFNlEzenQ0UURWWVFrVkM3TUFoUkJqVVd6ckZNR2wvY1lpZGJYZkZiQ2U0aHUvc3dhTkdtU0F5cWhDRTlCVE5Va3FaVm9Sc054eTZtN0FwVlRKd0EiLCJtYWMiOiI0YjhiN2Y4Mzg0ZjAxMWRjNzRjODFlMmU3NzQxMTVlNzhiNzY2OGE2OGZmOTY3YTA0MjE1MDllNDAwMjc5ZTYyIiwidGFnIjoiIn0%3D"
}

payload = {
    "_token":"LlFG4W3AWM0udAzSjM0DbIFF1aZ51T4RjOJfn7FF"
}

response = session.post(url, headers=headers, data=payload, allow_redirects=False)

print("Status:", response.status_code)
print("URL:", response.url)
print("Length:", len(response.text))
print("Preview:", response.text[:300])
