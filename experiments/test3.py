import requests

base_url = "https://access-kwik.apex-cloud.workers.dev"
kwik_url = "https://kwik.cx/f/VFjuoZpRvYtH"
payload = {
        "service": "kwik",
        "action": "fetch",
        "content": {
            "kwik": kwik_url
        },
        "auth": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.O0FKaqhJjEZgCAVfZoLz6Pjd7Gs9Kv6qi0P8RyATjaE"
    }
headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
response = requests.post(base_url,data=payload,headers=headers,timeout=6)
print(response.status_code)
print(response.json())
