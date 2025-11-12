from flask import Flask
from flask import send_file, abort
from dotenv import load_dotenv
import os
from db import init_db, close_db, get_db
from blueprints.tiktok import dl_bp
from blueprints.anime import anime_bp
load_dotenv()
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.register_blueprint(dl_bp)
app.register_blueprint(anime_bp)
app.teardown_appcontext(close_db)
with app.app_context():
    init_db()


@app.route("/<code>")
def serve_video(code):
    db = get_db()
    cursor = db.execute(
        "SELECT filepath FROM videos WHERE short_code = ?", (code,))
    row = cursor.fetchone()
    if row:
        file_path = row["filepath"]
        print(file_path)
    else:
        return "Video not found", 404
    if not file_path or not os.path.exists(file_path):
        abort(404)
    filename = os.path.basename(file_path)
    return send_file(file_path, as_attachment=True, download_name=filename)


if "__main__" == __name__:
    app.run(host="0.0.0.0", port=7860)
