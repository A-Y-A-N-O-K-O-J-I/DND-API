import sqlite3
from flask import g

DATABASE = 'dnd.db'

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
    db.execute("""
        CREATE TABLE IF NOT EXISTS anime_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            episodes TEXT NOT NULL,
            internal_id TEXT NOT NULL UNIQUE,
            external_id TEXT NOT NULL UNIQUE
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS anime_episode (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_count INTEGER,
            episode TEXT,
            external_id TEXT NOT NULL UNIQUE
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS cached_video_url (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            internal_id TEXT NOT NULL,
            episode TEXT,
            video_url TEXT,
            size TEXT,
            UNIQUE(internal_id, episode)
        )
    """)
    db.commit()
