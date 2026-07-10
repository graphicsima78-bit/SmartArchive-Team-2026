import json
import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path="archivepro.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                dest_path TEXT NOT NULL,
                md5 TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                size INTEGER,
                mtime REAL,
                mime TEXT,
                metadata_json TEXT,
                UNIQUE(sha256, dest_path)
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self.conn.commit()

    def has_sha256(self, sha256):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM files WHERE sha256=? LIMIT 1", (sha256,))
        return cur.fetchone() is not None

    def insert_file(self, source_path, dest_path, md5, sha256, size, mtime, mime, metadata):
        self.conn.execute(
            "INSERT OR IGNORE INTO files(source_path, dest_path, md5, sha256, size, mtime, mime, metadata_json) VALUES (?,?,?,?,?,?,?,?)",
            (source_path, dest_path, md5, sha256, size, mtime, mime, json.dumps(metadata, ensure_ascii=False)),
        )
        self.conn.commit()

    def insert_duplicate(self, source_path, sha256):
        self.conn.execute(
            "INSERT INTO duplicates(source_path, sha256) VALUES (?,?)",
            (source_path, sha256),
        )
        self.conn.commit()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
