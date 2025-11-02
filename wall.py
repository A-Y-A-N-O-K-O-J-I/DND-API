import requests
from bs4 import BeautifulSoup
import os
base_url = "https://4kwallpapers.com/search/?q=death-note"
response = requests.get(base_url)

soup = BeautifulSoup(response.text,"html.parser")

pics = soup.find_all("div",id = "pics-list")
for pic in pics:
    links = pic.find_all("a",class_="wallpapers__canvas_image")
    for link in links:
        html_wall_url = link.get("href")
        response = requests.get(html_wall_url)
        soup = BeautifulSoup(response.text,"html.parser")
        span = soup.find("span",class_="res-ttl")
        link = span.a.get("href")
        full_dl_link = base_url + link
        binary_data = requests.get(full_dl_link)
        file_name = full_dl_link.split("/")[-1]
        folder_path = os.path.expanduser(f"~/Pictures/{file_name}")
        if binary_data.status_code == 200:           
            with open(folder_path,"wb") as f:
                print(f"Writing to {folder_path}...")
                f.write(binary_data.content)
            
    print("Bulk Wallpaper Download Complete")