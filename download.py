import os
import re
import yt_dlp
from datetime import datetime
import secrets
from db import get_db


def videoDL(url):
    try:
        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL({"quiet": True}) as yt:
            info = yt.extract_info(url, download=False)

        PROJECT_TYPE= os.getenv('PROJECT_TYPE')
        title = info.get("title", "video")

        # Clean title
        title = re.sub(r"[^\w\s-]", "", title)
        title = title.strip().replace(" ", "_")
        title = title[:40]  # shorten to 40 chars

        # Add timestamp (unique)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title}_{timestamp}.mp4"

        file_path = os.path.join("downloads", filename)

        # Download with clean filename
        options = {
            "format": "best",
            "outtmpl": file_path,
            "quiet": False,
            "nocheckcertificate": True,
            "retries": 10,
            "fragment_retries": 10,
            "noprogress": True

        }

        with yt_dlp.YoutubeDL(options) as yt:
            yt.download([url])

        short_code = secrets.token_urlsafe(6)  # e.g. 'JFGGPGHMHM'
        dlurl = f"http://localhost:7860/{short_code}" if PROJECT_TYPE == "dev" else f"https://a-y-a-n-o-k-o-j-i-dnd-api.hf.space/{short_code}"
        db = get_db()
        db.execute(
            "INSERT INTO videos (title, filepath, short_code) VALUES (?, ?, ?)",
            (title, file_path, short_code)
        )
        db.commit()
        return {
            "channel_info": {
            "channel_name": info.get('channel'),
            "channel_url":info.get('channel_url')

        },'video_info':{
            "title": info.get('title'),
            "comment_count": info.get('comment_count'),
            'description': info.get('description'),
            'like_count': info.get('like_count')
        },
        "download_url": dlurl
        }

    except Exception as e:
        print("Error downloading:", e)
        return None
