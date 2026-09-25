import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest

pytest.importorskip("PySide6")
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QComboBox
from ket_studio.desktop import StudioWindow
from ket_studio.service import StudioService


def test_desktop_role_navigation_word_editor_and_quiz(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = StudioWindow(StudioService(tmp_path / "demo.sqlite3"))
    window.switch_language("zh-CN")
    window.show()
    app.processEvents()
    assert set(window.nav) == {"home", "quiz", "words", "mistakes", "records"}
    window.switch_role()
    app.processEvents()
    assert set(window.nav) == {"admin", "manage_words", "class_records"}
    for page in ("admin", "class_records", "manage_words"):
        window.show_page(page)
        app.processEvents()
    errors = []

    def edit():
        try:
            dlg = window.findChild(QDialog)
            fields = {w.accessibleName(): w for w in dlg.findChildren(QLineEdit)}
            fields["英文"].setText("robot")
            fields["中文释义"].setText("机器人")
            dlg.findChild(QComboBox).setCurrentText("科技")
            next(b for b in dlg.findChildren(QPushButton) if b.text() == "保存").click()
        except Exception as e:
            errors.append(e)
            for dlg in window.findChildren(QDialog):
                dlg.reject()

    QTimer.singleShot(0, edit)
    window.word_editor()
    app.processEvents()
    assert not errors
    assert len(window.service.words("robot")) == 1
    window.switch_role()
    window.show_page("words")
    window.word_search.setText("robot")
    app.processEvents()
    assert window.word_table.rowCount() == 1
    window.show_page("quiz")
    window.quiz_count.setValue(1)
    window.quiz_category.setCurrentText("科技")
    window.start_quiz()
    app.processEvents()
    window.answer_input.setText("ROBOT")
    window.submit_answer()
    app.processEvents()
    assert window.quiz["status"] == "completed" and window.quiz["correct"] == 1
    for page in ("home", "mistakes", "records"):
        window.show_page(page)
        app.processEvents()
    assert len(window.service.records()) == 4
    window.close()
    app.processEvents()
