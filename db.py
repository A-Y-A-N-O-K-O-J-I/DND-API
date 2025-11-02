import sqlite3
from flask import g

DATABASE = 'videos.db'

def get_db():
    """Get a database connection for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # optional: makes results behave like dicts
    return g.db

def close_db(e=None):
    """Close the database connection if it exists."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
def init_db():
    """Create the videos table if it doesn't exist."""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filepath TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)
    db.commit()
