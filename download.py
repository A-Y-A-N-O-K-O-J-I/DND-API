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
            "quiet": True
        }

        with yt_dlp.YoutubeDL(options) as yt:
            yt.download([url])

        short_code = secrets.token_urlsafe(6)  # e.g. 'JFGGPGHMHM'
        db = get_db()
        db.execute(
            "INSERT INTO videos (title, filepath, short_code) VALUES (?, ?, ?)",
            (title, file_path, short_code)
        )
        db.commit()
        return {"url": f"http://localhost:5000/{short_code}", "channel_info": {
           "channel_name": info['channel'],
        },
        "title":info['title'],
        'info':info
        }

    except Exception as e:
        print("Error downloading:", e)
        return None
