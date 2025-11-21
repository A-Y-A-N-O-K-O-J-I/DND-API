import requests

base_url = "https://access-kwik.apex-cloud.workers.dev"
kwik_url = "https://kwik.cx/f/VFjuoZpRvYtH"
payload = {
        "service": "kwik",
        "action": "fetch",
        "content": {
            "kwik": kwik_url
        },
        "auth": "eyJpdiI6InhoQWlYZ3lVVmpxR3ZIbVNzTWpNbVE9PSIsInZhbHVlIjoiOHJzUS9RKzdWNDZkVlVTeDBlSitlejFrNk9xNnRjYnRNTnZyZWhFSFhXVTFna29oRUdqb0QvZjJITjcwaksrVE5NSTNYNnZ0aWVmcHcyUGpPZVNvdzVEcnk3S1c2czZNaHpTbmNJUWNUMFI2QVp0L1Q3VWk1ajBSaXl1YzRBaGIiLCJtYWMiOiI0NDBhM2I5ODY4ZDAzN2IxNWQwYTk4ZDAyNDdmMDBhNGU5NjFjNjE5NjM0MzUzYTkyODM0ODY0NmIxY2QyOGUzIiwidGFnIjoiIn0="
    }
headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
response = requests.post(base_url,data=payload,headers=headers,timeout=10)
print(response.status_code)
print(response.text)
