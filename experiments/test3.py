import httpx

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
    "cookie": "srv=s0; dom3ic8zudi28v8lr6fgphwffqoz0j6c=dfe095dc-ae34-4fe7-a9af-ed60c63b1abd%3A3%3A1; pp_main_4e5e04716f26fd21bf611637f4fb8a46=1; pp_exp_4e5e04716f26fd21bf611637f4fb8a46=1763706198823; sb_main_e1010ee4b61613b1b253d71d1c531c2e=1; kwik_session=eyJpdiI6IkdVOTU3SC9Ob1Y4Mm02VXBESXhNOGc9PSIsInZhbHVlIjoib01XaEdwSWo0dlAzT0lRQnVYRXJlMWVteHNpY0wyam42Yzc0TWJnNFd2Vis5VksrMEhUNCszZVZjUFB2ejEwcllTQjZSdHR6QkVNS0FiQTVUcE1GbG1tRFZEWUZsOGdzSkpyYkdGcGI0S3dtcUZwZUlray91Nm1yM21tWTdrVXYiLCJtYWMiOiJhMTE5ZmY5OTU1ZWYyZjNhMTA1NDk5MzJmMzA3MTljOTlkZjJkZWY5OGY2ZWM1NzAyMTQ4NGNiMzljNjZkNDMzIiwidGFnIjoiIn0%3D; pp_show_on_4e5e04716f26fd21bf611637f4fb8a46=2; sb_count_e1010ee4b61613b1b253d71d1c531c2e=2; cf_clearance=MjihTeVpHrXwyJa1aalAg8sDwlZXlHVXIFrtsC7hoxI-1763702603-1.2.1.1-NvP4QPNYeaHR3lHBd7QQMIxbjohSRZN0moevSCY7BmjvpGzwN7ON_FmXSRNmrJz6lmUgnf62LJkZNpqyEvn6SgzAMDYTgApMfQAwWsGBokE5eB08vRm_LWxQROw74JxVUdYxQNEE.e5P0j7.hBeukoweREyMedP0NeGed.AvaK4U7031Xpm6SsKU8uM1Qlq8WV4P6VOo_kfOGNKJaqDBJ9o9gJFPQwUgJ_BKzac6be4",
    "Referer": "https://kwik.cx/f/VFjuoZpRvYtH"
}

payload= {
    "_token":"LlFG4W3AWM0udAzSjM0DbIFF1aZ51T4RjOJfn7FF"
}

with httpx.Client(follow_redirects=False, headers=headers) as client:
    r = client.post("https://kwik.cx/d/VFjuoZpRvYtH",data=payload)
    print(r.text)        # This becomes the REAL MP4 URL
    print(r.status_code)