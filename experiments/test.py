import requests
import json

url = "https://access-kwik.apex-cloud.workers.dev/"

payload = {
    "service": "kwik",
    "action": "fetch",
    "content": {
        "kwik": "https://kwik.cx/f/u1gohmECOejS"  # make sure kwikLink is defined above
    },
    "auth": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.O0FKaqhJjEZgCAVfZoLz6Pjd7Gs9Kv6qi0P8RyATjaE"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

print(response.status_code)
print(response.json().get("content").get("url"))
