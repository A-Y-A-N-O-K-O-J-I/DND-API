import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

def deobfuscate(packed_code):
    # 1. Extract the arguments from the eval(function(...)...) call
    pattern = r'eval\(function\(.*?\)\{(.*?)\}\("(.*?)",(\d+),"(.*?)",(\d+),(\d+),(\d+)\)\)'
    match = re.search(pattern, packed_code, re.S)

    if not match:
        print("No match found")
        return None

    func_body, payload, p1, delimiter, p2, p3, p4 = match.groups()

    p1 = int(p1)
    p2 = int(p2)
    p3 = int(p3)
    p4 = int(p4)

    # 2. Base conversion function (same logic as _0xe46c in JS)
    def base_convert(zq, Pt, lS):
        g = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/")
        h = g[:Pt]
        i = g[:lS]

        # Convert reversed encoded string → integer
        j = 0
        for power, char in enumerate(reversed(zq)):
            if char in h:
                j += h.index(char) * (Pt ** power)

        # Convert integer to base-lS
        if j == 0:
            return "0"

        result = ""
        while j > 0:
            result = i[j % lS] + result
            j //= lS

        return result

    XP = ""
    Qz = list(delimiter)
    
    i = 0
    length = len(payload)

    # 3. Loop through payload and decode chunks
    while i < length:
        s = ""

        # build chunk until hitting the separator character
        while i < length and payload[i] != Qz[p3]:
            s += payload[i]
            i += 1

        # skip delimiter
        i += 1

        if s:
            # Replace each delimiter symbol with its index
            for idx, symbol in enumerate(Qz):
                s = s.replace(symbol, str(idx))

            # Convert chunk and append the decoded character
            char_code = int(base_convert(s, p3, 10)) - p2
            XP += chr(char_code)

    # 4. Decode unicode
    return urllib.parse.unquote(XP)

import re

def extract_info(js_code):
    # 1. Extract embed URL
    embed_match = re.search(r"var\s+url\s*=\s*['\"]([^'\"]+)['\"]", js_code)
    embed_url = embed_match.group(1) if embed_match else None

    # 2. Extract kwik link from <form action="">
    kwik_match = re.search(r'<form[^>]+action=["\']([^"\']+)', js_code)
    kwik_url = kwik_match.group(1) if kwik_match else None

    # 3. Extract _token value
    token_match = re.search(r'name="_token"\s+value=["\']([^"\']+)', js_code)
    token = token_match.group(1) if token_match else None

    return {
        "embed_url": embed_url,
        "kwik_url": kwik_url,
        "token": token
    }

res = requests.get("https://kwik.cx/f/I9kUGgPpESEZ")


html_soup = BeautifulSoup(res.text,"html.parser")
scripts = html_soup.find_all("script")
obf_js = scripts[-2].text
deobf_js = deobfuscate(obf_js)
print(extract_info(deobf_js))
