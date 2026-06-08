import os
import sqlite3
import threading
import time
import logging

logger = logging.getLogger('neighborhood_helpboard')


class Database:
    def __init__(self, path='helpboard.db', max_posts=50):
        self.path = path
        self.max_posts = max_posts
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self._configure_pragmas()
        self._initialize_db()

    def _configure_pragmas(self):
        with self.lock:
            try:
                self.conn.execute('PRAGMA journal_mode = WAL')
                self.conn.execute('PRAGMA synchronous = NORMAL')
                self.conn.execute('PRAGMA foreign_keys = ON')
            except Exception as e:
                logger.warning('Failed to configure SQLite pragmas for %s: %s', self.path, e)

    def _initialize_db(self):
        with self.lock:
            try:
                self.conn.execute(
                    '''
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        type TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp REAL NOT NULL
                    )
                    '''
                )
                self.conn.commit()
            except Exception as e:
                logger.error('Failed to initialize SQLite database %s: %s', self.path, e)
                raise

    def load(self):
        # Kept for compatibility but SQLite initializes on startup.
        return self.list_posts(limit=self.max_posts)

    def save(self):
        with self.lock:
            try:
                self.conn.commit()
            except Exception as e:
                logger.error('Failed to commit SQLite database %s: %s', self.path, e)

    def add_post(self, username, type_, message):
        timestamp = time.time()
        with self.lock:
            try:
                cursor = self.conn.execute(
                    'INSERT INTO posts (username, type, message, timestamp) VALUES (?, ?, ?, ?)',
                    (username, type_, message, timestamp)
                )
                self.conn.commit()
                post_id = cursor.lastrowid
            except Exception as e:
                logger.error('Failed to insert post into SQLite: %s', e)
                raise

        return {
            'id': post_id,
            'username': username,
            'type': type_,
            'message': message,
            'timestamp': timestamp
        }

    def list_posts(self, type_filter=None, limit=10):
        with self.lock:
            try:
                if type_filter:
                    rows = self.conn.execute(
                        'SELECT id, username, type, message, timestamp FROM posts WHERE type = ? ORDER BY id DESC LIMIT ?',
                        (type_filter, limit)
                    ).fetchall()
                else:
                    rows = self.conn.execute(
                        'SELECT id, username, type, message, timestamp FROM posts ORDER BY id DESC LIMIT ?',
                        (limit,)
                    ).fetchall()
                posts = [dict(row) for row in reversed(rows)]
                return posts
            except Exception as e:
                logger.error('Failed to list posts from SQLite: %s', e)
                return []

    def get_post(self, id_):
        with self.lock:
            try:
                row = self.conn.execute(
                    'SELECT id, username, type, message, timestamp FROM posts WHERE id = ?',
                    (id_,)
                ).fetchone()
                return dict(row) if row else None
            except Exception as e:
                logger.error('Failed to get post %s from SQLite: %s', id_, e)
                return None
