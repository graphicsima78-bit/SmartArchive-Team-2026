import json
import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """مدیریت پایگاه‌داده و سازگاری امن با نسخه‌های قدیمی ArchivePro."""

    REQUIRED_FILE_COLUMNS = {
        "id",
        "source_path",
        "dest_path",
        "md5",
        "sha256",
        "size",
        "mtime",
        "mime",
        "metadata_json",
    }

    def __init__(self, db_path="archivepro.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.legacy_files_table = None
        self._init_schema()

    def _table_exists(self, table_name):
        row = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        return row is not None

    def _table_columns(self, table_name):
        return {
            row[1]
            for row in self.conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
        }

    def _preserve_incompatible_files_table(self):
        """جدول files قدیمی را حذف نمی‌کند؛ آن را با نام legacy نگه می‌دارد."""
        if not self._table_exists("files"):
            return

        existing_columns = self._table_columns("files")
        if self.REQUIRED_FILE_COLUMNS.issubset(existing_columns):
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        legacy_name = f"files_legacy_{timestamp}"
        self.conn.execute(f'ALTER TABLE "files" RENAME TO "{legacy_name}"')
        self.conn.commit()
        self.legacy_files_table = legacy_name

    def _init_schema(self):
        self._preserve_incompatible_files_table()

        self.conn.execute(
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
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self.conn.commit()

    def has_sha256(self, sha256):
        row = self.conn.execute(
            "SELECT 1 FROM files WHERE sha256=? LIMIT 1",
            (sha256,),
        ).fetchone()
        return row is not None

    def insert_file(self, source_path, dest_path, md5, sha256, size, mtime, mime, metadata):
        self.conn.execute(
            """INSERT OR IGNORE INTO files
               (source_path, dest_path, md5, sha256, size, mtime, mime, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                source_path,
                dest_path,
                md5,
                sha256,
                size,
                mtime,
                mime,
                json.dumps(metadata, ensure_ascii=False),
            ),
        )
        self.conn.commit()

    def insert_duplicate(self, source_path, sha256):
        self.conn.execute(
            "INSERT INTO duplicates(source_path, sha256) VALUES (?, ?)",
            (source_path, sha256),
        )
        self.conn.commit()

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
