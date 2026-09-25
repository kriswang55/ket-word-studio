import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from ket_studio.service import StudioService, AppError
from ket_studio.vocabulary import normalize


@pytest.fixture
def service(tmp_path):
    return StudioService(tmp_path / "demo.sqlite3")


def expected(service, q):
    with service.store.connection() as db:
        return [
            dict(r)
            for r in db.execute(
                "SELECT * FROM answers WHERE quiz_id=? ORDER BY position", (q["id"],)
            )
        ]


def finish(service, q, correct=True):
    for row in expected(service, q):
        service.answer(
            q["id"], row["position"], row["english"] if correct else "incorrect-answer"
        )


def clean(service):
    with service.store.connection(write=True) as db:
        db.execute("DELETE FROM answers")
        db.execute("DELETE FROM quizzes")


def test_default_demo_without_accounts(service):
    assert service.role == "student"
    assert len(service.words()) == 178 and len(service.vocabulary.categories) == 19
    assert len(service.records()) == 3 and all(r["sample"] for r in service.records())
    assert service.dashboard()["accuracy"] == 60
    with service.store.connection() as db:
        names = {
            r[0]
            for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert "users" not in names and "sessions" not in names


def test_normalization(service):
    assert normalize("  PENCIL　 Case ") == "pencil case"
    assert service.vocabulary.matches(
        {"english": "pencil case"}, "ＰＥＮＣＩＬ　ＣＡＳＥ"
    )
    assert service.vocabulary.matches(
        {"english": "colour", "aliases": ["color"]}, " COLOR "
    )


def test_vocabulary_edit_persistence_and_roles(service):
    with pytest.raises(AppError):
        service.save_word("robot", "机器人", "科技")
    service.switch_role("admin")
    w = service.save_word("robot", "机器人", "科技", ["a robot"])
    assert StudioService(service.store.path).words("机器人")[0]["id"] == w["id"]
    with pytest.raises(AppError):
        service.save_word("ＲＯＢＯＴ", "重复", "科技")
    with pytest.raises(AppError):
        service.start_quiz()
    service.save_word("robot", "机器人", "科技", word_id=w["id"], enabled=False)
    assert service.words("robot") == [] and len(service.admin_words("robot")) == 1
    service.switch_role("student")
    with pytest.raises(AppError):
        service.admin_words()


@pytest.mark.parametrize("count", [0, -1, 501, True, 1.5, "10"])
def test_invalid_count(service, count):
    with pytest.raises(AppError):
        service.start_quiz(count)


def test_sampling_and_question_view(service):
    q = service.start_quiz(500, "四季时光")
    assert q["total"] == 4 and "english" not in q["current"]
    assert len({r["word_id"] for r in expected(service, q)}) == 4
    with pytest.raises(AppError):
        service.start_quiz()


def test_resume_retry_order_and_snapshot(service):
    clean(service)
    q = service.start_quiz(3)
    rows = expected(service, q)
    with pytest.raises(AppError):
        service.answer(q["id"], 1, "wrong")
    service.answer(q["id"], 0, rows[0]["english"].upper())
    service.answer(q["id"], 0, rows[0]["english"].upper())
    with pytest.raises(AppError):
        service.answer(q["id"], 0, "changed")
    reopened = StudioService(service.store.path)
    assert reopened.active_quiz()["current"]["index"] == 1
    reopened.switch_role("admin")
    w = reopened.admin_words()[0]
    target = next(w for w in reopened.admin_words() if w["id"] == rows[1]["word_id"])
    reopened.save_word(
        "renamed word",
        "改过的释义",
        target["category"],
        word_id=target["id"],
        enabled=False,
    )
    reopened.switch_role("student")
    reopened.answer(q["id"], 1, rows[1]["english"])
    reopened.answer(q["id"], 2, "")
    assert (
        reopened.active_quiz() is None
        and reopened.record_detail(q["id"])["correct"] == 2
    )
    assert reopened.dashboard()["accuracy"] == 66.7


def test_review_and_abandoned_quizzes(service):
    clean(service)
    q = service.start_quiz(4, "四季时光")
    finish(service, q, False)
    assert len(service.mistakes()) == 4
    review = service.start_quiz(10, mode="review")
    assert review["total"] == 4
    finish(service, review)
    assert service.mistakes() == []
    q = service.start_quiz(2)
    service.answer(q["id"], 0, "")
    service.abandon(q["id"])
    assert len(service.records()) == 2 and service.mistakes() == []


def test_statistics_exports_and_reset(service):
    clean(service)
    finish(service, service.start_quiz(1))
    finish(service, service.start_quiz(3), False)
    d = service.dashboard()
    assert d["accuracy"] == 25 and d["average"] == 50
    assert len(json.loads(service.export())["records"]) == 2
    assert service.export("csv").startswith(b"\xef\xbb\xbf")
    service.reset()
    assert len(service.records()) == 3 and len(service.words()) == 178


def test_csv_formula_escape(service):
    clean(service)
    service.switch_role("admin")
    service.save_word("robot", "机器人", "=1+1")
    service.switch_role("student")
    finish(service, service.start_quiz(1, "=1+1"))
    assert "'=1+1" in service.export("csv").decode("utf-8-sig")


def test_simultaneous_submission(service):
    clean(service)
    q = service.start_quiz(1)
    answer = expected(service, q)[0]["english"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: service.answer(q["id"], 0, answer), range(2)))
    assert (
        all(r["quiz"]["correct"] == 1 for r in results) and len(service.records()) == 1
    )


def test_corrupt_database_not_overwritten(tmp_path):
    path = tmp_path / "broken.sqlite3"
    path.write_bytes(b"broken")
    with pytest.raises(Exception):
        StudioService(path)
    assert path.read_bytes() == b"broken"
