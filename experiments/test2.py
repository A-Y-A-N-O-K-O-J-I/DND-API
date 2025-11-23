import requests

res = requests.get("https://kwik.cx/f/I9kUGgPpESEZ")
print(res.cookies.get_dict().get("kwik_session"))