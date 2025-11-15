import cloudscraper
import requests
scraper = cloudscraper.create_scraper()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "referer":"https://kwik.cx/f/cJFkUIfRwxTf",
    "Accept": "*/*"
}

cookies = {
    "kwik_session": "eyJpdiI6Illld3JRRkJBVUlwTFZyeDJ1M0JRYWc9PSIsInZhbHVlIjoiTkVJeG9Ody9UM1MyNDg0ZXNaVWg0dlRSVExrWkErbENPV1JwektVUVZyRkdOcytjcy9CYjJMS2o5MXl1QlZrVU8xN1A1VkRRK0c2NkxNZitXTXFoVnFHQVZYQkVPWUlQQ1pGbGhrT2g1NTBmVFA3WDJvRGxhZ3NhRzFHTlpVa1YiLCJtYWMiOiIwZWM5MjkwZjMxMDVkZGIyNmE5MjE5OGFlYzI5NWE0MzUxMjJhYmFhNzliOGI1MmJiYjRkZGNmYmJkYzViNThmIiwidGFnIjoiIn0%3D",
    "pp_exp_4e5e04716f26fd21bf611637f4fb8a46": "1763231229958",
    "pp_main_4e5e04716f26fd21bf611637f4fb8a46": "1",
    "pp_show_on_4e5e04716f26fd21bf611637f4fb8a46": "1",
    "sb_count_e1010ee4b61613b1b253d71d1c531c2e": "1",
    "sb_main_e1010ee4b61613b1b253d71d1c531c2e": "1",
    "srv": "s0"
}

payload ={
    "_token":"dR3Oex3uW3vJYgY6EojxnVVauGiUXBF36hIyHfWt"
}
res = scraper.get("https://animepahe.si")
print(res.text)

