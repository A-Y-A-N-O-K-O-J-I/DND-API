import requests

response = requests.get("https://animepahe.si")
print(response.cookies)
