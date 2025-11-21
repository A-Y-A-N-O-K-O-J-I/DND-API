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
    "upgrade-insecure-requests": "1",
    "cookie": "srv=s0; dom3ic8zudi28v8lr6fgphwffqoz0j6c=dfe095dc-ae34-4fe7-a9af-ed60c63b1abd%3A3%3A1; pp_main_4e5...YOUR_COOKIES... "
}

payload = {
    "_token":"LlFG4W3AWM0udAzSjM0DbIFF1aZ51T4RjOJfn7FF"
}

response = session.post(url, headers=headers, data=payload, allow_redirects=True)

print("Status:", response.status_code)
print("URL:", response.url)
print("Length:", len(response.text))
print("Preview:", response.text[:300])
