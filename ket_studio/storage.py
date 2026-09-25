"""SQLite persistence for the local, account-free demonstration."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS words (
 id TEXT PRIMARY KEY, english TEXT NOT NULL, english_key TEXT NOT NULL UNIQUE,
 chinese TEXT NOT NULL, category TEXT NOT NULL, aliases TEXT NOT NULL,
 enabled INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS quizzes (
 id TEXT PRIMARY KEY, mode TEXT NOT NULL, category TEXT NOT NULL, started_at TEXT NOT NULL,
 completed_at TEXT, status TEXT NOT NULL CHECK(status IN ('active','completed','abandoned')),
 sample INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_quiz ON quizzes(status) WHERE status='active';
CREATE TABLE IF NOT EXISTS answers (
 quiz_id TEXT NOT NULL REFERENCES quizzes(id), position INTEGER NOT NULL, word_id TEXT NOT NULL,
 english TEXT NOT NULL, chinese TEXT NOT NULL, category TEXT NOT NULL, aliases TEXT NOT NULL,
 user_answer TEXT, correct INTEGER CHECK(correct IN (0,1)), answered_at TEXT,
 PRIMARY KEY(quiz_id,position)
);
PRAGMA user_version=3;
"""


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 3):
                raise RuntimeError("数据库版本不兼容，请指定新的演示数据目录。")
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript(SCHEMA)

    @contextmanager
    def connection(self, write=False):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
