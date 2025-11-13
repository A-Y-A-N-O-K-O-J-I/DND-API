import re
import requests
from bs4 import BeautifulSoup
res = requests.get("https://pahe.win/FCeVI")
soup = BeautifulSoup(res.text,"html.parser")
info = soup.find("script")
m = re.search(r"https?://(?:www\.)?kwik\.cx[^\s\"');]+", info.text)
print(m.group(0))