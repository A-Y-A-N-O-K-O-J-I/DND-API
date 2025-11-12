import os
import re
import yt_dlp
import ffmpeg
from datetime import datetime
from db import get_db
import secrets

def videoDL(url):
    try:
        os.makedirs("downloads", exist_ok=True)

        # Get video info first
        with yt_dlp.YoutubeDL({"quiet": True}) as yt:
            info = yt.extract_info(url, download=False)

        PROJECT_TYPE = os.getenv('PROJECT_TYPE')
        title = info.get("title", "video")

        # Clean title
        title = re.sub(r"[^\w\s-]", "", title)
        title = title.strip().replace(" ", "_")
        title = title[:40]  # shorten to 40 chars

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        downloaded_path = os.path.join("downloads", f"{title}_{timestamp}_raw.mp4")
        final_path = os.path.join("downloads", f"{title}_{timestamp}.mp4")

        # Download original video first (no recode)
        options = {
            "format": "best",
            "outtmpl": downloaded_path,
            "quiet": False,
            "nocheckcertificate": True,
            "retries": 10,
            "fragment_retries": 10,
            "noprogress": True
        }
        with yt_dlp.YoutubeDL(options) as yt:
            yt.download([url])

        probe = ffmpeg.probe(downloaded_path)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), {})
        audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), {})

        vcodec = video_stream.get('codec_name')
        acodec = audio_stream.get('codec_name')

        if vcodec == 'h264' and acodec in ('aac', 'mp3'):
            # Just copy directly
            ffmpeg.input(downloaded_path).output(
                final_path,
                vcodec='copy',
                acodec='copy',
                movflags='+faststart'
            ).run(overwrite_output=True)
        else:
            # Re-encode to make it universal
            ffmpeg.input(downloaded_path).output(
                final_path,
                vcodec='libx264',
                acodec='aac',
                preset='superfast',
                crf=28,
                vf='scale=720:-2',
                r=30,
                threads=2,
                movflags='+faststart'
            ).run(overwrite_output=True)


        # Optional: remove the raw download to save space
        os.remove(downloaded_path)

        # Generate short code and DB insert
        short_code = secrets.token_urlsafe(6)
        dlurl = f"http://localhost:7860/{short_code}" if PROJECT_TYPE == "dev" else f"https://a-y-a-n-o-k-o-j-i-dnd-api.hf.space/{short_code}"

        db = get_db()
        db.execute(
            "INSERT INTO videos (title, filepath, short_code) VALUES (?, ?, ?)",
            (title, final_path, short_code)
        )
        db.commit()

        return {
            "channel_info": {
                "channel_name": info.get('channel'),
                "channel_url": info.get('channel_url')
            },
            "video_info": {
                "title": info.get('title'),
                "comment_count": info.get('comment_count'),
                "description": info.get('description'),
                "like_count": info.get('like_count')
            },
            "download_url": dlurl
        }

    except Exception as e:
        print("Error downloading:", e)
        return None
def videoDL_for_insta(url):
    try:
        os.makedirs("downloads", exist_ok=True)

        # Get video info first
        with yt_dlp.YoutubeDL({"quiet": True,'cookiefile': './insta_cookies.txt'}) as yt:
            info = yt.extract_info(url, download=False)

        PROJECT_TYPE = os.getenv('PROJECT_TYPE')
        title = info.get("title", "video")

        # Clean title
        title = re.sub(r"[^\w\s-]", "", title)
        title = title.strip().replace(" ", "_")
        title = title[:40]  # shorten to 40 chars

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        downloaded_path = os.path.join("downloads", f"{title}_{timestamp}_raw.mp4")
        final_path = os.path.join("downloads", f"{title}_{timestamp}.mp4")

        # Download original video first (no recode)
        options = {
            "format": "best",
            "outtmpl": downloaded_path,
            "quiet": False,
            "nocheckcertificate": True,
            "retries": 10,
            'cookiefile': './insta_cookies.txt',
            "fragment_retries": 10,
            "noprogress": True
        }
        with yt_dlp.YoutubeDL(options) as yt:
            yt.download([url])

        # Convert to H.264 + AAC using ffmpeg-python
        ffmpeg.input(downloaded_path).output(
            final_path,
            vcodec='libx264',
            acodec='aac',       # or 'copy' if already AAC
            preset='superfast',
            crf=28,
            vf='scale=720:-2',
            r=30,
            threads=2,
            movflags='+faststart'
        ).run(overwrite_output=True)


        # Optional: remove the raw download to save space
        os.remove(downloaded_path)

        # Generate short code and DB insert
        short_code = secrets.token_urlsafe(6)
        dlurl = f"http://localhost:7860/{short_code}" if PROJECT_TYPE == "dev" else f"https://dnd-api.up.railway.app/{short_code}"

        db = get_db()
        db.execute(
            "INSERT INTO videos (title, filepath, short_code) VALUES (?, ?, ?)",
            (title, final_path, short_code)
        )
        db.commit()

        return {
            "channel_info": {
                "channel_name": info.get('channel'),
                "channel_url": info.get('channel_url')
            },
            "video_info": {
                "title": info.get('title'),
                "comment_count": info.get('comment_count'),
                "description": info.get('description'),
                "like_count": info.get('like_count')
            },
            "download_url": dlurl
        }

    except Exception as e:
        print("Error downloading:", e)
        return None
