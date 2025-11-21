import re
import requests

# Global variables
base_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"
encoded_string = "XXX"
zp = 17
alphabet_key = "XXX"
offset = 1
base = 5
placeholder = 24


def _0xe16c(IS: str, Iy: int, ms: int) -> int:
    """Convert string from base Iy to base ms"""
    h = base_alphabet[:Iy]
    i = base_alphabet[:ms]

    # Decode string IS from base Iy to int j
    j = 0
    for idx, ch in enumerate(reversed(IS)):
        pos = h.find(ch)
        if pos != -1:
            j += pos * (Iy ** idx)

    # Convert int j to base ms string
    if j == 0:
        return int(i[0])

    k = ""
    while j > 0:
        k = i[j % ms] + k
        j //= ms

    return int(k)


def decode_js_style(Hb: str, zp: int, Wg: str, Of: int, Jg: int, gj_placeholder: int) -> str:
    """Decode the obfuscated JavaScript string"""
    gj = ""
    i = 0

    while i < len(Hb):
        s = ""
        # Collect characters until we hit the delimiter
        while i < len(Hb) and Hb[i] != Wg[Jg]:
            s += Hb[i]
            i += 1

        # Replace alphabet characters with their positions
        for j, char in enumerate(Wg):
            s = s.replace(char, str(j))

        # Decode and subtract offset
        if s:
            code = _0xe16c(s, Jg, 10) - Of
            gj += chr(code)

        i += 1

    return gj


def fetch_kwik_direct(kwik_link: str, token: str, kwik_session: str) -> str:
    """Fetch the direct download link by following the redirect"""
    headers = {
        "referer": kwik_link,
        "cookie": f"kwik_session={kwik_session}",
    }
    data = {"_token": token}

    # Make POST request with redirects disabled
    response = requests.post(
        kwik_link,
        headers=headers,
        data=data,
        allow_redirects=False
    )

    # Check if status code is 302 (redirect)
    if response.status_code == 302:
        redirect_location = response.headers.get("Location")
        if redirect_location:
            return redirect_location
        raise RuntimeError(f"Redirect Location not found in response from {kwik_link}")
    else:
        raise RuntimeError(f"Expected 302 redirect, got {response.status_code} from {kwik_link}")


def fetch_kwik_dlink(kwik_link: str, retries: int = 3) -> str:
    """Fetch and decode the Kwik page to extract direct link"""
    global encoded_string, alphabet_key, offset, base
    
    if retries <= 0:
        raise RuntimeError(f"Kwik fetch failed: exceeded retry limit : {kwik_link}")

    try:
        response = requests.get(kwik_link)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to Get Kwik from {kwik_link}, StatusCode: {response.status_code}")

        # Clean the response text
        clean_text = response.text.replace('\r\n', '').replace('\r', '').replace('\n', '')

        # Extract session from cookies
        kwik_session = response.cookies.get('kwik_session', '')

        # Extract encoded parameters
        encode_pattern = r'\(\s*"([^",]*)"\s*,\s*\d+\s*,\s*"([^",]*)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*\d+[a-zA-Z]?\s*\)'
        encode_match = re.search(encode_pattern, clean_text)

        if not encode_match or not encode_match.group(1) or not encode_match.group(2):
            return fetch_kwik_dlink(kwik_link, retries - 1)

        # Update global variables
        encoded_string = encode_match.group(1)
        alphabet_key = encode_match.group(2)
        offset = int(encode_match.group(3))
        base = int(encode_match.group(4))

        # Decode the obfuscated string
        decoded_string = decode_js_style(
            encoded_string,
            zp,
            alphabet_key,
            offset,
            base,
            placeholder
        )

        # Extract link and token from decoded string
        link_match = re.search(r'"(https?://kwik\.[^/\s"]+/[^/\s"]+/[^"\s]*)"', decoded_string)
        token_match = re.search(r'name="_token"[^"]*"(\S*)">', decoded_string)

        if not link_match or not token_match or not link_match.group(1) or not token_match.group(1):
            return fetch_kwik_dlink(kwik_link, retries - 1)

        link = link_match.group(1)
        token = token_match.group(1)

        # Fetch the direct link
        direct_link = fetch_kwik_direct(link, token, kwik_session)
        return direct_link

    except Exception as e:
        if retries > 1:
            return fetch_kwik_dlink(kwik_link, retries - 1)
        raise


def extract_kwik_link(link: str) -> str:
    """Extract the direct download link from an Animepahe episode URL"""
    print("\n * Extracting Kwik Link...", end='', flush=True)
    
    response = requests.get(link)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to Get Kwik from {link}, StatusCode: {response.status_code}")

    clean_text = response.text.replace('\r\n', '').replace('\r', '').replace('\n', '')

    # First attempt: direct link extraction
    kwik_match = re.search(r'"(https?://kwik\.[^/\s"]+/[^/\s"]+/[^"\s]*)"', clean_text)

    if not kwik_match or not kwik_match.group(1):
        # Second attempt: decode and extract
        encode_pattern = r'\(\s*"([^",]*)"\s*,\s*\d+\s*,\s*"([^",]*)"\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*\d+[a-zA-Z]?\s*\)'
        encode_match = re.search(encode_pattern, clean_text)

        if not encode_match:
            raise RuntimeError(f"Failed to extract encoding parameters from {link}")

        try:
            temp_encoded = encode_match.group(1)
            temp_alphabet = encode_match.group(2)
            temp_offset = int(encode_match.group(3))
            temp_base = int(encode_match.group(4))

            decoded_string = decode_js_style(
                temp_encoded,
                zp,
                temp_alphabet,
                temp_offset,
                temp_base,
                placeholder
            )

            kwik_match = re.search(r'"(https?://kwik\.[^/\s"]+/[^/\s"]+/[^"\s]*)"', decoded_string)

            if not kwik_match or not kwik_match.group(1):
                raise RuntimeError("Failed to extract Kwik link from decoded content")

            kwik_link = kwik_match.group(1)
            kwik_link = re.sub(r'(https://kwik\.[^/]+/)d/', r'\1f/', kwik_link)

        except Exception as e:
            raise RuntimeError(f"Failed to decode and extract Kwik link: {e}")
    else:
        kwik_link = kwik_match.group(1)

    print("\r * Extracting Kwik Link : \033[92mOK!\033[0m")
    print(" * Fetching Kwik Direct Link...", end='', flush=True)

    direct_link = fetch_kwik_dlink(kwik_link)

    print("\r * Fetching Kwik Direct Link : \033[92mOK!\033[0m")
    return direct_link


# Example usage
if __name__ == "__main__":
    # Replace with actual Animepahe episode URL
    episode_url = "https://kwik.cx/f/u1gohmECOejS"
    
    try:
        direct_link = extract_kwik_link(episode_url)
        print(f"\nDirect Download Link: {direct_link}")
    except Exception as e:
        print(f"\nError: {e}")