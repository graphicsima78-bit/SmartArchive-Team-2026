"""
database.py
مدیریت پایگاه‌داده SQLite برای ArchivePro
Handles file records, hashes (duplicate detection) and reporting.
"""

import sqlite3
import json
import threading
from datetime import datetime


class DatabaseManager:
    """Thread-safe-ish SQLite wrapper (uses a lock around writes)."""

    def __init__(self, db_path="archivepro.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        self._init_db()

    def _get_conn(self):
        # each thread gets its own connection
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tab TEXT,
                source_path TEXT,
                dest_path TEXT,
                category TEXT,
                sub_category TEXT,
                filename TEXT,
                file_hash TEXT,
                size INTEGER,
                status TEXT,
                reason TEXT,
                scan_date TEXT
            )
        ''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_hash ON files(file_hash)')
        conn.commit()

    def hash_exists(self, file_hash):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('SELECT dest_path FROM files WHERE file_hash=? LIMIT 1', (file_hash,))
        row = cur.fetchone()
        return row[0] if row else None

    def insert_file(self, data: dict):
        with self._lock:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO files (
                    tab, source_path, dest_path, category, sub_category,
                    filename, file_hash, size, status, reason, scan_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('tab', ''),
                data.get('source', ''),
                data.get('dest', ''),
                data.get('category', ''),
                data.get('sub_category', ''),
                data.get('filename', ''),
                data.get('file_hash', ''),
                data.get('size', 0),
                data.get('status', 'ok'),
                data.get('reason', ''),
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_all_files(self, tab=None):
        conn = self._get_conn()
        cur = conn.cursor()
        if tab:
            cur.execute('SELECT * FROM files WHERE tab=? ORDER BY id', (tab,))
        else:
            cur.execute('SELECT * FROM files ORDER BY id')
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def clear_tab(self, tab):
        with self._lock:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute('DELETE FROM files WHERE tab=?', (tab,))
            conn.commit()

    def close(self):
        if hasattr(self._local, "conn"):
            self._local.conn.close()
