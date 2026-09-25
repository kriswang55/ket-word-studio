"""Account-free desktop demo: vocabulary, quizzes, review, statistics and export.

Role switching is an interface convention for reviewers, not authentication.
Each quiz stores word snapshots so later vocabulary edits cannot change its grade.
"""

from datetime import datetime, timezone, timedelta
import csv
import io
import json
import random
import secrets
import sqlite3
from .paths import data_directory
from .storage import Store
from .vocabulary import Vocabulary, normalize


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class StudioService:
    def __init__(self, db_path=None):
        self.store = Store(db_path or data_directory() / "demo.sqlite3")
        self.role = "student"
        with self.store.connection(write=True) as db:
            if not db.execute(
                "SELECT 1 FROM metadata WHERE key='initialized'"
            ).fetchone():
                self._seed(db)

    @staticmethod
    def _word(row):
        return {
            **{k: row[k] for k in ("id", "english", "chinese", "category")},
            "aliases": json.loads(row["aliases"]),
            "enabled": bool(row["enabled"]),
        }

    @property
    def vocabulary(self):
        with self.store.connection() as db:
            return Vocabulary(
                words=[
                    self._word(r)
                    for r in db.execute(
                        "SELECT * FROM words WHERE enabled=1 ORDER BY rowid"
                    )
                ]
            )

    def _seed(self, db):
        words = Vocabulary().words
        db.executemany(
            "INSERT INTO words VALUES(?,?,?,?,?,?,1,?)",
            [
                (
                    w["id"],
                    w["english"],
                    normalize(w["english"]),
                    w["chinese"],
                    w["category"],
                    json.dumps(w.get("aliases", [])),
                    now(),
                )
                for w in words
            ],
        )
        for day in range(3):
            completed = (
                datetime.now(timezone.utc) - timedelta(days=3 - day)
            ).isoformat(timespec="seconds")
            quiz_id = f"sample-{day}"
            db.execute(
                "INSERT INTO quizzes VALUES(?,'random','全部主题',?,?,'completed',1)",
                (quiz_id, completed, completed),
            )
            for i, w in enumerate(words[day * 5 : day * 5 + 5]):
                correct = i < day + 2
                db.execute(
                    "INSERT INTO answers VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        quiz_id,
                        i,
                        w["id"],
                        w["english"],
                        w["chinese"],
                        w["category"],
                        json.dumps(w.get("aliases", [])),
                        w["english"] if correct else "",
                        int(correct),
                        completed,
                    ),
                )
        db.execute("INSERT OR REPLACE INTO metadata VALUES('initialized','1')")

    def reset(self):
        with self.store.connection(write=True) as db:
            db.execute("DELETE FROM answers")
            db.execute("DELETE FROM quizzes")
            db.execute("DELETE FROM words")
            self._seed(db)

    def switch_role(self, role):
        if role not in ("student", "admin"):
            raise AppError("请选择学生或教师页面。")
        self.role = role

    def _require_role(self, role):
        if self.role != role:
            raise AppError(
                "请切换到教师页面。" if role == "admin" else "请切换到学生页面。", 403
            )

    def status(self):
        v = self.vocabulary
        return {
            "word_count": len(v.words),
            "categories": v.categories,
            "version": "3.0.0",
        }

    def words(self, query="", category="全部主题"):
        return self.vocabulary.search(query, category)

    def admin_words(self, query="", category="全部主题"):
        self._require_role("admin")
        with self.store.connection() as db:
            words = [
                self._word(r)
                for r in db.execute("SELECT * FROM words ORDER BY rowid DESC")
            ]
        return Vocabulary(words=words).search(query, category)

    @staticmethod
    def _text(value, label, limit):
        if (
            not isinstance(value, str)
            or not 1 <= len(value.strip()) <= limit
            or any(ord(c) < 32 for c in value)
        ):
            raise AppError(f"{label}需要 1–{limit} 个字符，不能包含控制字符。")
        return value.strip()

    def save_word(
        self, english, chinese, category, aliases=None, word_id=None, enabled=True
    ):
        english = self._text(english, "英文", 100)
        chinese = self._text(chinese, "中文释义", 200)
        category = self._text(category, "主题", 40)
        if not any("a" <= c <= "z" for c in normalize(english)):
            raise AppError("英文词条需要包含英文字母。")
        if type(enabled) is not bool or not isinstance(
            aliases if aliases is not None else [], list
        ):
            raise AppError("词条格式无效。")
        aliases = aliases or []
        if len(aliases) > 20:
            raise AppError("可接受答案最多填写 20 个。")
        aliases = list(dict.fromkeys(self._text(a, "可接受答案", 100) for a in aliases))
        with self.store.connection(write=True) as db:
            self._require_role("admin")
            if (
                word_id is not None
                and not db.execute(
                    "SELECT 1 FROM words WHERE id=?", (word_id,)
                ).fetchone()
            ):
                raise AppError("词条不存在。", 404)
            word_id = word_id or "w_" + secrets.token_hex(12)
            try:
                db.execute(
                    """INSERT INTO words VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                    english=excluded.english,english_key=excluded.english_key,chinese=excluded.chinese,
                    category=excluded.category,aliases=excluded.aliases,enabled=excluded.enabled,updated_at=excluded.updated_at""",
                    (
                        word_id,
                        english,
                        normalize(english),
                        chinese,
                        category,
                        json.dumps(aliases),
                        int(enabled),
                        now(),
                    ),
                )
            except sqlite3.IntegrityError:
                raise AppError("该英文词条已存在，请编辑已有词条。", 409) from None
            return self._word(
                db.execute("SELECT * FROM words WHERE id=?", (word_id,)).fetchone()
            )

    def _quiz(self, db, quiz_id):
        row = db.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,)).fetchone()
        if row is None:
            raise AppError("找不到这次练习。", 404)
        return row

    def _quiz_view(self, db, quiz):
        rows = db.execute(
            "SELECT * FROM answers WHERE quiz_id=? ORDER BY position", (quiz["id"],)
        ).fetchall()
        pending = [r for r in rows if r["user_answer"] is None]
        result = dict(quiz)
        result.update(
            total=len(rows),
            answered=len(rows) - len(pending),
            correct=sum(r["correct"] or 0 for r in rows),
        )
        result["current"] = (
            {
                "index": pending[0]["position"],
                "chinese": pending[0]["chinese"],
                "category": pending[0]["category"],
            }
            if pending
            else None
        )
        return result

    def active_quiz(self):
        with self.store.connection() as db:
            self._require_role("student")
            quiz = db.execute("SELECT * FROM quizzes WHERE status='active'").fetchone()
            return self._quiz_view(db, quiz) if quiz else None

    def start_quiz(self, count=10, category="全部主题", mode="random"):
        if type(count) is not int or not 1 <= count <= 500:
            raise AppError("题数必须是 1–500 之间的整数。")
        if mode not in ("random", "review"):
            raise AppError("不支持的练习模式。")
        if category not in ["全部主题", *self.vocabulary.categories]:
            raise AppError("不存在的词汇主题。")
        with self.store.connection(write=True) as db:
            self._require_role("student")
            if db.execute("SELECT 1 FROM quizzes WHERE status='active'").fetchone():
                raise AppError("还有未完成的练习，请先继续或结束它。", 409)
            pool = self.vocabulary.search(category=category)
            if mode == "review":
                wrong_ids = {w["word_id"] for w in self._mistakes(db)}
                pool = [w for w in pool if w["id"] in wrong_ids]
            if not pool:
                raise AppError("这个主题暂时没有待复习的错词，试试随机练习。")
            selected = random.SystemRandom().sample(pool, min(count, len(pool)))
            quiz_id = secrets.token_hex(16)
            db.execute(
                "INSERT INTO quizzes VALUES(?,?,?,?,?,?,?)",
                (quiz_id, mode, category, now(), None, "active", 0),
            )
            db.executemany(
                "INSERT INTO answers(quiz_id,position,word_id,english,chinese,category,aliases) VALUES(?,?,?,?,?,?,?)",
                [
                    (
                        quiz_id,
                        i,
                        w["id"],
                        w["english"],
                        w["chinese"],
                        w["category"],
                        json.dumps(w.get("aliases", [])),
                    )
                    for i, w in enumerate(selected)
                ],
            )
            return self._quiz_view(
                db,
                db.execute("SELECT * FROM quizzes WHERE id=?", (quiz_id,)).fetchone(),
            )

    def answer(self, quiz_id, index, answer):
        if type(index) is not int or not isinstance(answer, str) or len(answer) > 200:
            raise AppError("答案格式无效或超过 200 个字符。")
        with self.store.connection(write=True) as db:
            self._require_role("student")
            quiz = self._quiz(db, quiz_id)
            row = db.execute(
                "SELECT * FROM answers WHERE quiz_id=? AND position=?", (quiz_id, index)
            ).fetchone()
            if row is None:
                raise AppError("题目不存在。", 404)
            if row["user_answer"] is not None:
                if row["user_answer"] != answer.strip():
                    raise AppError("这道题已提交，不能修改。", 409)
                # Retrying a lost network response must not append a second answer.
                return {"feedback": dict(row), "quiz": self._quiz_view(db, quiz)}
            first = db.execute(
                "SELECT MIN(position) FROM answers WHERE quiz_id=? AND user_answer IS NULL",
                (quiz_id,),
            ).fetchone()[0]
            if quiz["status"] != "active" or first != index:
                raise AppError("练习状态已改变，请继续当前题目。", 409)
            word = {"english": row["english"], "aliases": json.loads(row["aliases"])}
            correct = int(Vocabulary.matches(word, answer))
            db.execute(
                "UPDATE answers SET user_answer=?,correct=?,answered_at=? WHERE quiz_id=? AND position=?",
                (answer.strip(), correct, now(), quiz_id, index),
            )
            if not db.execute(
                "SELECT 1 FROM answers WHERE quiz_id=? AND user_answer IS NULL",
                (quiz_id,),
            ).fetchone():
                db.execute(
                    "UPDATE quizzes SET status='completed',completed_at=? WHERE id=?",
                    (now(), quiz_id),
                )
            feedback = dict(
                db.execute(
                    "SELECT * FROM answers WHERE quiz_id=? AND position=?",
                    (quiz_id, index),
                ).fetchone()
            )
            return {
                "feedback": feedback,
                "quiz": self._quiz_view(
                    db,
                    db.execute(
                        "SELECT * FROM quizzes WHERE id=?", (quiz_id,)
                    ).fetchone(),
                ),
            }

    def abandon(self, quiz_id):
        with self.store.connection(write=True) as db:
            self._require_role("student")
            quiz = self._quiz(db, quiz_id)
            if quiz["status"] == "active":
                db.execute(
                    "UPDATE quizzes SET status='abandoned' WHERE id=?", (quiz_id,)
                )

    def record_detail(self, quiz_id):
        with self.store.connection() as db:
            quiz = self._quiz(db, quiz_id)
            if quiz["status"] != "completed":
                raise AppError("这次练习尚未完成。", 409)
            record = self._quiz_view(db, quiz)
            record["details"] = [
                dict(r)
                for r in db.execute(
                    "SELECT * FROM answers WHERE quiz_id=? ORDER BY position",
                    (quiz_id,),
                )
            ]
            return record

    def mistakes(self):
        with self.store.connection() as db:
            self._require_role("student")
            return self._mistakes(db)

    def dashboard(self):
        with self.store.connection() as db:
            records = self._records(db)
            total = sum(r["total"] for r in records)
            correct = sum(r["correct"] for r in records)
            scores = [r["accuracy"] for r in records]
            return {
                "attempts": len(records),
                "questions": total,
                "accuracy": round(correct / total * 100, 1) if total else 0,
                "best": max(scores, default=0),
                "worst": min(scores, default=0),
                "average": round(sum(scores) / len(scores), 1) if scores else 0,
                "mistake_count": len(self._mistakes(db)),
                "recent": records[:7],
                "word_count": len(self.vocabulary.words),
            }

    def _records(self, db):
        records = [
            dict(r)
            for r in db.execute("""SELECT q.*,COUNT(a.position) AS total,SUM(a.correct) AS correct
            FROM quizzes q JOIN answers a ON a.quiz_id=q.id WHERE q.status='completed'
            GROUP BY q.id ORDER BY q.completed_at DESC,q.rowid DESC""")
        ]
        for r in records:
            r["accuracy"] = round(100 * r["correct"] / r["total"], 1)
        return records

    def records(self):
        with self.store.connection() as db:
            return self._records(db)

    def admin_summary(self):
        self._require_role("admin")
        return {"records": self.records(), **self.dashboard()}

    def _mistakes(self, db):
        rows = db.execute("""SELECT a.*,q.rowid AS quiz_order FROM answers a JOIN quizzes q ON q.id=a.quiz_id
              WHERE q.status='completed' ORDER BY q.completed_at DESC,q.rowid DESC,a.position""").fetchall()
        words = {}
        for r in rows:
            item = words.setdefault(
                r["word_id"],
                {
                    "word_id": r["word_id"],
                    "english": r["english"],
                    "chinese": r["chinese"],
                    "category": r["category"],
                    "last_answer": r["user_answer"],
                    "last_correct": bool(r["correct"]),
                    "wrong_count": 0,
                },
            )
            item["wrong_count"] += int(not r["correct"])
        return sorted(
            [r for r in words.values() if not r["last_correct"]],
            key=lambda x: (-x["wrong_count"], x["english"]),
        )

    def export(self, format="json"):
        if format not in ("json", "csv"):
            raise AppError("仅支持 JSON 或 CSV 导出。")
        with self.store.connection() as db:
            records = self._records(db)
            for r in records:
                r["details"] = [
                    dict(a)
                    for a in db.execute(
                        "SELECT * FROM answers WHERE quiz_id=? ORDER BY position",
                        (r["id"],),
                    )
                ]
        if format == "json":
            return json.dumps(
                {"schema_version": 1, "exported_at": now(), "records": records},
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8")
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            ["完成时间", "主题", "方式", "题数", "正确数", "正确率(%)", "来源"]
        )

        def safe(value):
            value = str(value)
            return (
                "'" + value
                if value.lstrip().startswith(("=", "+", "-", "@"))
                else value
            )

        for r in records:
            writer.writerow(
                [
                    safe(x)
                    for x in [
                        r["completed_at"],
                        r["category"],
                        "错题复习" if r["mode"] == "review" else "随机练习",
                        r["total"],
                        r["correct"],
                        r["accuracy"],
                        "示例记录" if r["sample"] else "本次演示",
                    ]
                ]
            )
        return output.getvalue().encode("utf-8-sig")
