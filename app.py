from flask import Flask
from flask import send_file, abort
import os
from db import init_db,close_db,get_db
from tiktok import dl_bp
app = Flask(__name__)
app.register_blueprint(dl_bp)
app.teardown_appcontext(close_db)
with app.app_context():
    init_db()

@app.route("/<code>")
def serve_video(code):
    db = get_db()
    cursor = db.execute("SELECT filepath FROM videos WHERE short_code = ?",(code,))
    row = cursor.fetchone()
    if row:
        file_path = row["filepath"]
        print(file_path)
    else:
        return "Video not found", 404
    if not file_path or not os.path.exists(file_path):
        abort(404)
    return send_file(file_path)


if "__main__" == __name__:
    app.run(debug=True)
    