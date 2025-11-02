import re
def check_platform(url):
    patterns = {
        "tiktok": r"(https?://)?(www\.)?(vm\.)?tiktok\.com/",
        "instagram": r"(https?://)?(www\.)?instagram\.com/",
        "youtube": r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
        "facebook": r"(https?://)?(www\.)?(facebook\.com|fb\.watch)/"
    }

    for platform, pattern in patterns.items():
        if re.search(pattern, url):
            return platform
    return None