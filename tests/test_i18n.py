import json
import os
import pytest
from ket_studio.i18n import Translator, LOCALES, catalogue
from ket_studio.service import StudioService


def test_catalogue_defaults_and_preference_isolation(tmp_path):
    service = StudioService(tmp_path / "demo.sqlite3")
    translator = Translator(preferences=tmp_path / "preferences.json")
    assert translator.locale == "en"
    before = service.export()
    assert translator.select("zh-HK")
    assert Translator(preferences=tmp_path / "preferences.json").locale == "zh-HK"
    assert json.loads(before)["records"] == json.loads(service.export())["records"]
    assert (
        translator.text("英文需要 1–100 个字符，不能包含控制字符。")
        == "英文需要 1–100 個字符，不能包含控制字符。"
    )
    assert translator.meaning("儿子") == "兒子"
    assert Translator("unexpected").locale == "en"
    with pytest.raises(ValueError):
        translator.select("unexpected")


@pytest.mark.parametrize("locale", LOCALES)
def test_localized_csv_and_shared_catalogue(locale, tmp_path):
    service = StudioService(tmp_path / "demo.sqlite3")
    translator = Translator(locale)
    csv = service.export("csv", locale=locale).decode("utf-8-sig")
    assert translator.text("完成时间") in csv
    assert translator.category("全部主题") in csv
    assert set(catalogue(locale)["messages"]) == set(catalogue("en")["messages"])


def test_qt_switch_preserves_question_draft_feedback_and_completed_score(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication
    from ket_studio.desktop import StudioWindow

    app = QApplication.instance() or QApplication([])
    service = StudioService(tmp_path / "demo.sqlite3")
    window = StudioWindow(service)
    assert window.translator.locale == "en"
    assert window.nav["home"].text() == "Learning overview"
    window.show_page("quiz")
    window.quiz_count.setValue(2)
    window.start_quiz()
    quiz_id = window.quiz["id"]
    window.answer_input.setText("draft")
    window.language_buttons["zh-HK"].click()
    assert window.language_buttons["zh-HK"].isChecked()
    assert window.language_buttons["zh-HK"].text() == "繁体中文"
    assert window.answer_input.text() == "draft"
    assert window.quiz["id"] == quiz_id
    assert window.nav["home"].text() == "學習概覽"
    window.submit_answer(skip=True)
    window.language_buttons["zh-CN"].click()
    assert window.quiz["answered"] == 1
    assert window.feedback is not None
    assert not window.answer_input.isEnabled()
    window.next_question()
    window.submit_answer(skip=True)
    window.language_buttons["en"].click()
    assert window.quiz["status"] == "completed"
    assert window.next_button.text() == "View result"
    assert len(service.records()) == 4
    window.close()
    reopened = StudioWindow(service)
    assert reopened.translator.locale == "en"
    reopened.close()
    app.processEvents()
