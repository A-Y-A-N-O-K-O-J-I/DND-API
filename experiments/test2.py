import asyncio
import time
from bs4 import BeautifulSoup
import requests
from helpers.anime_helper import get_kiwi_info

url = "https://kwik.cx/f/gyqPa8VjFYnJ"
info = asyncio.run(get_kiwi_info(url))
html = info.get("html")
soup = BeautifulSoup(html,"html.parser")
form_info = soup.find("form")
size = soup.find("form").find("span").get_text().split("(")[1].split(")")[0]
token = form_info.find("input")["value"]
payload = {
    "_token":token
}

# Convert /f/ to /d/ for POST request
post_url = url.replace("/f/", "/d/")

res = requests.post(post_url, cookies=info.get("cookies"), headers=info.get("headers"), allow_redirects=False, data=payload,timeout=10)
html_content = res.text
another_soup = BeautifulSoup(html_content,"html.parser")
direct_link = another_soup.find_all("a")[1]["href"]

print(direct_link)