"""Native PySide6 widgets, sharing all data and rules with the browser edition."""

from datetime import datetime
from pathlib import Path
import argparse
import logging
import sys
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QTranslator
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPainterPath
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QComboBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QDialog,
    QFileDialog,
    QProgressBar,
    QSizePolicy,
    QCheckBox,
)
from .paths import PACKAGE_DIR, data_directory
from .i18n import Translator, LOCALES, LANGUAGE_NAMES
from .vocabulary import normalize

_translator = Translator()


def tr(message, *args):
    return _translator.text(message, *args)


def category_text(value):
    return _translator.category(value)


def meaning_text(value):
    return _translator.meaning(value)


class QtControlsTranslator(QTranslator):
    """Translate standard Qt dialog controls with the active application locale."""

    def isEmpty(self):
        return False

    def translate(self, context, source, disambiguation=None, n=-1):
        keys = {
            "Yes": "是",
            "No": "否",
            "OK": "完成",
            "Cancel": "取消",
            "Save": "保存",
            "Open": "打开",
            "Close": "关闭对话框",
            "File name:": "文件名：",
            "Files of type:": "文件类型：",
            "Look in:": "查找位置：",
            "Save in:": "保存位置：",
            "All Files (*)": "所有文件 (*)",
            "Name": "名称",
            "Size": "大小",
            "Type": "类型",
            "Date Modified": "修改日期",
            "New Folder": "新建文件夹",
            "Back": "后退",
            "Parent Directory": "上级目录",
            "List View": "列表视图",
            "Detail View": "详细视图",
        }
        key = keys.get(source.replace("&", ""))
        return tr(key) if key else ""


def add_categories(combo, values):
    for value in values:
        combo.addItem(category_text(value), value)


def category_value(combo):
    return (
        combo.currentData()
        if combo.currentIndex() >= 0
        and combo.currentText() == combo.itemText(combo.currentIndex())
        else combo.currentText()
    )


from .service import StudioService, AppError

STYLE = """
QWidget {font-family:'Segoe UI','Microsoft YaHei';font-size:14px;color:#243f36;}
QMainWindow,QWidget#root,QWidget#page,QScrollArea {background:#f6f4ed;}
QFrame#sidebar {background:#eeeee5;border-right:1px solid #d9ddd2;}
QFrame#card {background:#fffef9;border:1px solid #dedfd5;border-radius:13px;}
QFrame#hero {background:#e7ecdc;border:1px solid #d7ddcc;border-radius:16px;}
QLabel {background:transparent;border:none;}
QLabel#muted {color:#748079;font-size:12px;}
QLabel#eyebrow {color:#81907d;font-size:10px;letter-spacing:2px;}
QLabel#title {font-size:29px;font-weight:650;}
QLabel#serif {font-family:Georgia,'SimSun';font-size:37px;}
QLabel#stat {font-family:Georgia;font-size:34px;color:#214d3f;}
QLabel#error {color:#a34435;font-size:12px;}
QPushButton {border:none;border-radius:9px;padding:12px 20px;background:#214d3f;color:#fffef9;font-weight:600;}
QPushButton:hover {background:#35634e;}
QPushButton:pressed {background:#193d31;}
QPushButton:disabled {background:#bdc9b7;color:#f8faf5;}
QPushButton#secondary {background:#e5eddf;color:#214d3f;}
QPushButton#secondary:hover {background:#d7e4cf;}
QPushButton#ghost {background:transparent;border:1px solid #d7dbcf;color:#687865;padding:9px 15px;}
QPushButton#nav {text-align:left;background:transparent;color:#6d7a69;padding:13px 16px;font-weight:500;}
QPushButton#nav:hover {background:#e1e6d8;}
QPushButton#nav:checked {background:#214d3f;color:white;}
QPushButton#language {background:transparent;color:#687865;border:1px solid #d7dbcf;padding:8px 3px;font-size:12px;font-weight:500;}
QPushButton#language:checked {background:#214d3f;color:white;border-color:#214d3f;}
QPushButton#language:hover:!checked {background:#e5eddf;}
QPushButton#topic {text-align:left;background:#f0f3e8;color:#3f6147;font-weight:500;padding:17px;}
QPushButton#topic:hover {background:#e3ebd8;}
QLineEdit,QComboBox,QSpinBox {background:#fffef9;border:1px solid #cdd5c5;border-radius:8px;padding:11px;color:#243f36;selection-background-color:#557b59;}
QLineEdit:focus,QComboBox:focus,QSpinBox:focus {border:2px solid #779575;padding:10px;}
QLineEdit:disabled {background:#eeeee5;color:#6d7a69;}
QComboBox::drop-down {border:0;width:25px;}
QComboBox QAbstractItemView {background:#fffef9;selection-background-color:#dfe9d6;color:#243f36;}
QTableWidget {background:#fffef9;alternate-background-color:#f5f6ef;border:1px solid #dce0d3;border-radius:8px;gridline-color:#e6e9df;selection-background-color:#dce8cf;selection-color:#243f36;}
QTableWidget::item {padding:9px;border-bottom:1px solid #e7eadf;}
QHeaderView::section {background:#edf0e5;border:none;padding:11px;text-align:left;color:#75846e;font-size:12px;}
QScrollArea {border:0;}
QScrollBar:vertical {background:transparent;width:9px;margin:0;}
QScrollBar::handle:vertical {background:#c5cebd;border-radius:4px;min-height:24px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0;}
QProgressBar {border:0;border-radius:3px;background:#e2e8d8;height:6px;max-height:6px;}
QProgressBar::chunk {background:#69875f;border-radius:3px;}
QDialog,QMessageBox {background:#f6f4ed;}
"""


def label(text, name=None, wrap=False):
    widget = QLabel(str(text))
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setWordWrap(wrap)
    if name:
        widget.setObjectName(name)
    return widget


def button(text, callback, name=None):
    widget = QPushButton(text)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    if name:
        widget.setObjectName(name)
    widget.clicked.connect(callback)
    return widget


def panel(name="card", margins=24):
    frame = QFrame()
    frame.setObjectName(name)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(margins, margins, margins, margins)
    layout.setSpacing(16)
    return (frame, layout)


def row_layout(*items):
    row = QHBoxLayout()
    row.setSpacing(12)
    for item in items:
        row.addWidget(item)
    return row


def local_date(value):
    return datetime.fromisoformat(value).astimezone().strftime("%m-%d %H:%M")


class TrendChart(QWidget):
    def __init__(self, records):
        super().__init__()
        self.records = list(reversed(records))
        self.setMinimumHeight(154)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = (self.width(), self.height())
        for score in (0, 50, 100):
            y = 20 + (h - 45) * (1 - score / 100)
            p.setPen(QColor("#87937d"))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, int(y + 4), f"{score}%")
            p.setPen(QPen(QColor("#e1e6d8"), 1, Qt.PenStyle.DashLine))
            p.drawLine(35, int(y), w - 10, int(y))
        if not self.records:
            p.setPen(QColor("#819078"))
            p.drawText(
                QRectF(40, 0, w - 60, h),
                Qt.AlignmentFlag.AlignCenter,
                tr("暂无已完成的练习。"),
            )
        else:
            pts = [
                QPointF(
                    40 + i * (w - 60) / max(len(self.records) - 1, 1),
                    20 + (h - 45) * (1 - r["accuracy"] / 100),
                )
                for i, r in enumerate(self.records)
            ]
            p.setPen(QPen(QColor("#587c55"), 2.5))
            for a, b in zip(pts, pts[1:]):
                p.drawLine(a, b)
            for i, point in enumerate(pts):
                p.setBrush(QColor("#587c55"))
                p.setPen(QPen(QColor("#fffef9"), 2))
                p.drawEllipse(point, 4, 4)
                p.setPen(QColor("#87937d"))
                p.drawText(int(point.x() - 3), h - 3, str(i + 1))
        p.end()


class StudioWindow(QMainWindow):
    def __init__(self, service):
        super().__init__()
        global _translator
        self.translator = Translator(
            preferences=service.store.path.with_name("preferences.json")
        )
        _translator = self.translator
        self.language_snapshot = None
        self.question_view = None
        self.service = service
        self.qt_translator = QtControlsTranslator(self)
        QApplication.instance().installTranslator(self.qt_translator)
        self.page_name = "home"
        self.quiz = None
        self.feedback = None
        self.setWindowTitle(tr("KET Word Studio · 单词测试系统"))
        self.setWindowIcon(QIcon(str(PACKAGE_DIR.parent / "site/icon.svg")))
        self.resize(1220, 880)
        self.setMinimumSize(980, 720)
        self.setStyleSheet(STYLE)
        self.build_shell()
        self.show_page("home")

    def guard(self, callback):

        def run(*_):
            try:
                callback()
            except AppError as exc:
                QMessageBox.information(self, tr("提示"), tr(str(exc)))
            except Exception:
                logging.exception("Desktop operation failed")
                QMessageBox.warning(
                    self,
                    tr("操作未完成"),
                    tr("请重试。详细信息已记录在数据目录的 desktop.log 中。"),
                )

        return run

    def build_shell(self):
        root = QWidget()
        root.setObjectName("root")
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        sidebar, side = panel("sidebar", 22)
        sidebar.setFixedWidth(265)
        side.addWidget(label("KET Word Studio"))
        language_row = QHBoxLayout()
        language_row.setSpacing(4)
        self.language_buttons = {}
        for locale in LOCALES:
            language_button = button(
                LANGUAGE_NAMES[locale],
                self.guard(lambda code=locale: self.switch_language(code)),
                "language",
            )
            language_button.setCheckable(True)
            language_button.setChecked(locale == self.translator.locale)
            language_button.setAccessibleName(LANGUAGE_NAMES[locale])
            language_row.addWidget(language_button, 1)
            self.language_buttons[locale] = language_button
        side.addLayout(language_row)
        side.addSpacing(18)
        switch = button(
            tr("切换到学生页面")
            if self.service.role == "admin"
            else tr("切换到教师页面"),
            self.guard(self.switch_role),
            "secondary",
        )
        side.addWidget(switch)
        side.addSpacing(15)
        names = (
            [
                ("admin", tr("管理概览")),
                ("manage_words", tr("词库管理")),
                ("class_records", tr("练习记录")),
            ]
            if self.service.role == "admin"
            else [
                ("home", tr("学习概览")),
                ("quiz", tr("单词练习")),
                ("words", tr("词汇手册")),
                ("mistakes", tr("错题复习")),
                ("records", tr("学习记录")),
            ]
        )
        self.nav = {}
        for key, text in names:
            b = button(text, self.guard(lambda k=key: self.show_page(k)), "nav")
            b.setCheckable(True)
            side.addWidget(b)
            self.nav[key] = b
        side.addStretch()
        side.addWidget(
            label(
                tr("教师页面") if self.service.role == "admin" else tr("学生页面"),
                "muted",
            )
        )
        side.addWidget(label(tr("数据保存在当前电脑。"), "muted"))
        side.addWidget(button(tr("重置演示数据"), self.guard(self.reset_demo), "ghost"))
        outer.addWidget(sidebar)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        outer.addWidget(self.scroll, 1)
        self.setCentralWidget(root)

    def switch_language(self, locale):
        global _translator
        page = self.page_name
        draft = self.answer_input.text() if page == "quiz" and self.quiz else None
        config = (
            (
                self.quiz_count.value(),
                category_value(self.quiz_category),
                self.quiz_mode.currentIndex(),
            )
            if page == "quiz" and not self.quiz
            else None
        )
        search = (
            self.word_search.text()
            if page == "words"
            else self.manage_search.text()
            if page == "manage_words"
            else None
        )
        category = category_value(self.word_category) if page == "words" else None
        if page == "quiz" and self.feedback:
            self.language_snapshot = (self.quiz, self.feedback, self.question_view)
        saved = self.translator.select(locale)
        _translator = self.translator
        self.setWindowTitle(tr("KET Word Studio · 单词测试系统"))
        self.build_shell()
        self.show_page(page)
        if draft is not None and self.quiz:
            self.answer_input.setText(draft)
        if config:
            self.quiz_count.setValue(config[0])
            self.quiz_category.setCurrentIndex(self.quiz_category.findData(config[1]))
            self.quiz_mode.setCurrentIndex(config[2])
        if search is not None:
            (self.word_search if page == "words" else self.manage_search).setText(
                search
            )
        if category is not None:
            self.word_category.setCurrentIndex(self.word_category.findData(category))
        if not saved:
            QMessageBox.information(
                self, tr("提示"), tr("语言偏好无法保存，下次启动将使用英语。")
            )

    def switch_role(self):
        self.service.switch_role("student" if self.service.role == "admin" else "admin")
        self.quiz = None
        self.feedback = None
        self.build_shell()
        self.show_page("admin" if self.service.role == "admin" else "home")

    def reset_demo(self):
        if (
            QMessageBox.question(
                self,
                tr("重置演示数据"),
                tr("恢复初始词库和示例成绩？新增词汇和练习记录将被删除。"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            self.service.reset()
            self.quiz = None
            self.feedback = None
            self.show_page("admin" if self.service.role == "admin" else "home")

    def show_page(self, name):
        if name not in self.nav:
            name = "admin" if self.service.role == "admin" else "home"
        self.page_name = name
        for key, b in self.nav.items():
            b.setChecked(key == name)
        page = QWidget()
        page.setObjectName("page")
        self.body = QVBoxLayout(page)
        self.body.setContentsMargins(32, 32, 32, 26)
        self.body.setSpacing(22)
        self.scroll.setWidget(page)
        getattr(self, "page_" + name)()
        self.body.addStretch()
        self.scroll.verticalScrollBar().setValue(0)

    def heading(self, title, subtitle):
        box = QVBoxLayout()
        box.setSpacing(7)
        box.addWidget(label(title, "title"))
        self.body.addLayout(box)
        if subtitle:
            box.addWidget(label(subtitle, "muted", True))

    def stats(self, items):
        row = QHBoxLayout()
        row.setSpacing(13)
        for title, value in items:
            frame, layout = panel(margins=19)
            layout.setSpacing(8)
            layout.addWidget(label(title, "muted"))
            layout.addWidget(label(value, "stat"))
            row.addWidget(frame, 1)
        self.body.addLayout(row)

    def page_home(self):
        d = self.service.dashboard()
        self.heading(
            tr("学习概览"), tr("初始包含 3 条示例记录，新增练习会标注为本次演示。")
        )
        self.body.addLayout(
            row_layout(
                button(
                    tr("开始 / 继续练习"), self.guard(lambda: self.show_page("quiz"))
                ),
                button(tr("复习错题"), self.guard(self.begin_review), "secondary"),
            )
        )
        self.stats(
            [
                (tr("已完成练习"), tr("{0} 次", f"{d['attempts']}")),
                (tr("累计正确率"), f"{d['accuracy']}%"),
                (tr("待复习单词"), tr("{0} 个", f"{d['mistake_count']}")),
                (tr("累计作答"), tr("{0} 题", f"{d['questions']}")),
            ]
        )
        frame, layout = panel()
        layout.addWidget(label(tr("最近 7 次练习正确率")))
        layout.addWidget(TrendChart(d["recent"]))
        self.body.addWidget(frame)

    def open_topic(self, category):
        self.show_page("words")
        self.word_category.setCurrentText(category)

    def table(self, headers, rows, min_height=310):
        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(49)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setMinimumHeight(min_height)
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                table.setItem(i, j, item)
        return table

    def page_words(self):
        self.heading(tr("词汇手册"), tr("搜索已启用的词汇。"))
        self.word_search = QLineEdit()
        self.word_search.setPlaceholderText(tr("搜索英文或中文释义…"))
        self.word_search.setAccessibleName(tr("搜索词汇"))
        self.word_category = QComboBox()
        add_categories(
            self.word_category, ["全部主题", *self.service.vocabulary.categories]
        )
        self.word_category.setAccessibleName(tr("词汇主题"))
        self.body.addLayout(row_layout(self.word_search, self.word_category))
        self.word_table = self.table([tr("英文"), tr("中文释义"), tr("主题")], [], 380)
        self.body.addWidget(self.word_table)
        self.word_count = label("", "muted")
        self.body.addWidget(self.word_count)
        self.word_search.textChanged.connect(self.guard(self.refresh_words))
        self.word_category.currentTextChanged.connect(self.guard(self.refresh_words))
        self.refresh_words()

    def refresh_words(self):
        query = normalize(self.word_search.text())
        words = [
            w
            for w in self.service.words(category=category_value(self.word_category))
            if query
            in normalize(
                w["english"] + " " + w["chinese"] + " " + meaning_text(w["chinese"])
            )
        ]
        self.word_table.setRowCount(len(words))
        for i, w in enumerate(words):
            for j, key in enumerate(("english", "chinese", "category")):
                value = (
                    meaning_text(w[key])
                    if key == "chinese"
                    else category_text(w[key])
                    if key == "category"
                    else w[key]
                )
                item = QTableWidgetItem(value)
                item.setToolTip(w[key])
                self.word_table.setItem(i, j, item)
        self.word_count.setText(tr("找到 {0} 个词条", f"{len(words)}"))

    def page_quiz(self):
        if self.language_snapshot:
            quiz, feedback, view = self.language_snapshot
            self.language_snapshot = None
            self.quiz = view
            self.draw_question()
            self.quiz, self.feedback = quiz, feedback
            self.render_feedback()
            return
        self.quiz = self.service.active_quiz()
        self.feedback = None
        if self.quiz:
            self.draw_question()
            return
        self.heading(tr("单词练习"), tr("根据中文释义填写英文。"))
        frame, layout = panel(margins=30)
        layout.addWidget(
            label(
                tr("根据中文释义写出英文。随机抽题，同一次练习不重复。"), "muted", True
            )
        )
        layout.addWidget(label(tr("练习方式")))
        self.quiz_mode = QComboBox()
        self.quiz_mode.addItems([tr("随机练习"), tr("错题复习")])
        layout.addWidget(self.quiz_mode)
        layout.addWidget(label(tr("题目数量")))
        self.quiz_count = QSpinBox()
        self.quiz_count.setRange(1, max(1, len(self.service.vocabulary.words)))
        self.quiz_count.setValue(10)
        layout.addWidget(self.quiz_count)
        layout.addWidget(label(tr("词汇主题")))
        self.quiz_category = QComboBox()
        add_categories(
            self.quiz_category, ["全部主题", *self.service.vocabulary.categories]
        )
        layout.addWidget(self.quiz_category)
        self.start_button = button(tr("开始练习"), self.guard(self.start_quiz))
        self.start_button.setEnabled(bool(self.service.vocabulary.words))
        layout.addWidget(self.start_button)
        layout.addWidget(
            label(
                tr("不区分大小写，自动整理多余空格。词数不足时使用实际可用数量。"),
                "muted",
                True,
            )
        )
        self.body.addWidget(frame)

    def start_quiz(self):
        self.quiz = self.service.start_quiz(
            self.quiz_count.value(),
            category_value(self.quiz_category),
            "review" if self.quiz_mode.currentIndex() == 1 else "random",
        )
        self.show_page("quiz")

    def draw_question(self):
        self.question_view = self.quiz
        q = self.quiz
        current = q["current"]
        self.heading(tr("单词练习"), tr("已提交的答案即时保存，离开后可以继续。"))
        frame, layout = panel(margins=30)
        layout.addLayout(
            row_layout(
                label(category_text(current["category"]), "eyebrow"),
                label(
                    tr("第 {0} / {1} 题", f"{current['index'] + 1}", f"{q['total']}"),
                    "muted",
                ),
            )
        )
        self.progress = QProgressBar()
        self.progress.setRange(0, q["total"])
        self.progress.setValue(q["answered"])
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        layout.addSpacing(12)
        layout.addWidget(label(tr("请写出对应的英文单词或短语"), "muted"))
        layout.addWidget(label(meaning_text(current["chinese"]), "serif", True))
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText(tr("输入英文答案"))
        self.answer_input.setMaxLength(200)
        self.answer_input.setAccessibleName(tr("你的答案"))
        self.answer_input.setStyleSheet(
            "font-family:Georgia;font-size:25px;padding:17px;"
        )
        layout.addWidget(self.answer_input)
        self.feedback_label = label("", wrap=True)
        layout.addWidget(self.feedback_label)
        self.submit_button = button(tr("检查答案  ↵"), self.guard(self.submit_answer))
        self.skip_button = button(
            tr("跳过此题"), self.guard(lambda: self.submit_answer(skip=True)), "ghost"
        )
        self.next_button = button(tr("下一题  →"), self.guard(self.next_question))
        self.next_button.hide()
        layout.addLayout(
            row_layout(self.submit_button, self.skip_button, self.next_button)
        )
        self.body.addWidget(frame)
        self.quiz_note = label(tr("已答对 {0} 题", f"{q['correct']}"), "muted")
        self.body.addLayout(
            row_layout(
                self.quiz_note,
                button(tr("结束本次练习"), self.guard(self.abandon_quiz), "ghost"),
            )
        )
        self.answer_input.returnPressed.connect(self.guard(self.submit_answer))
        QTimer.singleShot(0, self.answer_input, self.answer_input.setFocus)

    def submit_answer(self, skip=False):
        if self.feedback or not self.submit_button.isEnabled():
            return
        text = "" if skip else self.answer_input.text()
        result = self.service.answer(
            self.quiz["id"], self.quiz["current"]["index"], text
        )
        self.quiz = result["quiz"]
        self.feedback = result["feedback"]
        self.answer_input.setText(text)
        self.answer_input.setEnabled(False)
        self.render_feedback()

    def render_feedback(self):
        self.answer_input.setText(self.feedback["user_answer"])
        self.answer_input.setEnabled(False)
        f = self.feedback
        color = "#4a7251" if f["correct"] else "#a4563e"
        self.feedback_label.setStyleSheet(
            f"background:{('#e9f0e2' if f['correct'] else '#faeae0')};color:{color};border-radius:9px;padding:18px;font-size:18px;"
        )
        self.feedback_label.setText(
            (tr("回答正确。") if f["correct"] else tr("回答错误，正确答案："))
            + "\n"
            + f["english"]
        )
        self.progress.setValue(self.quiz["answered"])
        self.quiz_note.setText(tr("已答对 {0} 题", f"{self.quiz['correct']}"))
        self.submit_button.hide()
        self.skip_button.hide()
        self.next_button.show()
        self.next_button.setText(
            tr("查看本次成绩")
            if self.quiz["status"] == "completed"
            else tr("下一题  →")
        )
        self.next_button.setFocus()

    def next_question(self):
        if self.quiz["status"] == "completed":
            self.show_result(self.quiz["id"])
        else:
            self.show_page("quiz")

    def abandon_quiz(self):
        if self.quiz["status"] == "completed":
            self.show_result(self.quiz["id"])
            return
        if (
            QMessageBox.question(
                self,
                tr("结束练习"),
                tr("结束后，本次未完成练习不会计入成绩。历史记录不会改变。"),
            )
            == QMessageBox.StandardButton.Yes
        ):
            self.service.abandon(self.quiz["id"])
            self.show_page("quiz")

    def detail_rows(self, r):
        return [
            [
                meaning_text(a["chinese"]),
                a["english"],
                a["user_answer"] or tr("（跳过）"),
                tr("正确") if a["correct"] else tr("待复习"),
            ]
            for a in r["details"]
        ]

    def show_result(self, quiz_id):
        r = self.service.record_detail(quiz_id)
        self.show_page("records")
        self.detail_dialog(
            r, title=tr("练习完成 · {0}%", f"{r['correct'] / r['total'] * 100:.1f}")
        )

    def detail_dialog(self, r, title=None):
        title = title or tr("练习详情")
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(860, 560)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.addWidget(label(title, "title"))
        layout.addWidget(
            label(
                tr(
                    "{0} · 共 {1} 题，答对 {2} 题",
                    f"{local_date(r['completed_at'])}",
                    f"{r['total']}",
                    f"{r['correct']}",
                ),
                "muted",
            )
        )
        layout.addWidget(
            self.table(
                [tr("中文释义"), tr("正确答案"), tr("你的答案"), tr("结果")],
                self.detail_rows(r),
            ),
            1,
        )
        layout.addWidget(button(tr("完成"), dlg.accept))
        dlg.exec()

    def export_buttons(self):
        return row_layout(
            button(
                tr("导出 JSON"),
                self.guard(lambda: self.export_records("json")),
                "ghost",
            ),
            button(
                tr("导出 CSV"), self.guard(lambda: self.export_records("csv")), "ghost"
            ),
        )

    def export_records(self, format):
        payload = self.service.export(format, locale=self.translator.locale)
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("导出学习记录"),
            f"ket-records.{format}",
            f"{format.upper()} (*.{format})",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if path:
            Path(path).write_bytes(payload)
            QMessageBox.information(
                self, tr("导出完成"), tr("已保存到：\n{0}", f"{path}")
            )

    def records_table(self, records, admin=False):
        headers = [
            tr("完成时间"),
            tr("主题"),
            tr("方式"),
            tr("正确 / 题数"),
            tr("正确率"),
            tr("来源"),
        ]
        rows = [
            [
                local_date(r["completed_at"]),
                category_text(r["category"]),
                tr("错题复习") if r["mode"] == "review" else tr("随机练习"),
                f"{r['correct']} / {r['total']}",
                f"{r['accuracy']}%",
                tr("示例记录") if r["sample"] else tr("本次演示"),
            ]
            for r in records
        ]
        table = self.table(headers, rows)

        def open_selected():
            i = table.currentRow()
            if i < 0:
                raise AppError(tr("请先选中一条练习记录。"))
            self.detail_dialog(self.service.record_detail(records[i]["id"]))

        table.cellDoubleClicked.connect(self.guard(open_selected))
        self.body.addWidget(table)
        self.body.addWidget(
            button(tr("查看选中练习的详情"), self.guard(open_selected), "secondary")
        )

    def page_records(self):
        records = self.service.records()
        d = self.service.dashboard()
        self.heading(tr("学习记录"), tr("已完成的练习与成绩。"))
        self.stats(
            [
                (tr("最高正确率"), f"{d['best']}%"),
                (tr("最低正确率"), f"{d['worst']}%"),
                (tr("平均正确率"), f"{d['average']}%"),
                (tr("已完成练习"), tr("{0} 次", f"{d['attempts']}")),
            ]
        )
        self.body.addLayout(self.export_buttons())
        if records:
            self.records_table(records)
        else:
            self.body.addWidget(label(tr("暂无已完成的练习。"), "muted"))
        self.body.addWidget(
            label(
                tr("平均正确率是各次练习正确率的算术平均；累计正确率按总题数加权。"),
                "muted",
                True,
            )
        )

    def begin_review(self):
        self.show_page("quiz")
        if not self.quiz:
            self.quiz_mode.setCurrentIndex(1)
        else:
            QMessageBox.information(
                self, tr("提示"), tr("请先完成或结束当前练习，再开始错题复习。")
            )

    def page_mistakes(self):
        rows = self.service.mistakes()
        self.heading(tr("错题复习"), "")
        self.body.addWidget(
            label(
                tr(
                    "显示最近一次完整练习仍答错的词。后续完整练习答对后，会移出待复习清单。"
                ),
                "muted",
                True,
            )
        )
        if rows:
            self.body.addWidget(
                button(tr("开始错题练习  →"), self.guard(self.begin_review))
            )
            self.body.addWidget(
                self.table(
                    [tr("正确拼写"), tr("中文释义"), tr("上次答案"), tr("累计答错")],
                    [
                        [
                            r["english"],
                            meaning_text(r["chinese"]),
                            r["last_answer"] or tr("（跳过）"),
                            tr("答错 {0} 次", r["wrong_count"]),
                        ]
                        for r in rows
                    ],
                )
            )
        else:
            self.body.addWidget(label(tr("暂无待复习错词。"), "muted", True))

    def page_admin(self):
        d = self.service.admin_summary()
        self.heading(tr("管理概览"), tr("展示当前电脑中学生页面的练习数据。"))
        self.stats(
            [
                (tr("启用词汇"), str(d["word_count"])),
                (tr("词汇主题"), str(len(self.service.vocabulary.categories))),
                (tr("完成练习"), str(d["attempts"])),
                (tr("累计正确率"), f"{d['accuracy']}%"),
            ]
        )
        frame, layout = panel()
        layout.addWidget(label(tr("最近 7 次练习正确率")))
        layout.addWidget(TrendChart(d["recent"]))
        self.body.addWidget(frame)
        self.body.addWidget(label(tr("最近练习")))
        self.records_table(d["records"][:3])

    def page_class_records(self):
        self.heading(tr("练习记录"), tr("示例记录与本次演示的记录均已标注来源。"))
        self.body.addLayout(self.export_buttons())
        records = self.service.records()
        if records:
            self.records_table(records, True)
        else:
            self.body.addWidget(label(tr("暂无已完成的练习。"), "muted"))

    def page_manage_words(self):
        self.heading(
            tr("词库管理"), tr("停用词汇不再用于新练习，已保存的练习内容保持不变。")
        )
        self.manage_search = QLineEdit()
        self.manage_search.setPlaceholderText(tr("搜索英文或中文释义"))
        self.manage_search.setAccessibleName(tr("搜索管理词汇"))
        self.body.addLayout(
            row_layout(
                self.manage_search,
                button(tr("添加词汇"), self.guard(lambda: self.word_editor())),
            )
        )
        self.manage_table = self.table(
            [tr("英文"), tr("中文释义"), tr("主题"), tr("状态")], [], 420
        )
        self.body.addWidget(self.manage_table)
        self.manage_count = label("", "muted")
        self.body.addWidget(self.manage_count)
        self.body.addWidget(
            button(tr("编辑选中词汇"), self.guard(self.edit_selected_word), "secondary")
        )
        self.manage_search.textChanged.connect(self.guard(self.refresh_manage_words))
        self.manage_table.cellDoubleClicked.connect(self.guard(self.edit_selected_word))
        self.refresh_manage_words()

    def refresh_manage_words(self):
        query = normalize(self.manage_search.text())
        self.managed_words = [
            w
            for w in self.service.admin_words()
            if query
            in normalize(
                w["english"] + " " + w["chinese"] + " " + meaning_text(w["chinese"])
            )
        ]
        self.manage_table.setRowCount(len(self.managed_words))
        for i, w in enumerate(self.managed_words):
            for j, value in enumerate(
                [
                    w["english"],
                    meaning_text(w["chinese"]),
                    category_text(w["category"]),
                    tr("启用") if w["enabled"] else tr("停用"),
                ]
            ):
                self.manage_table.setItem(i, j, QTableWidgetItem(value))
        self.manage_count.setText(tr("共 {0} 个词条", f"{len(self.managed_words)}"))

    def edit_selected_word(self):
        i = self.manage_table.currentRow()
        if i < 0:
            raise AppError(tr("请先选中一个词条。"))
        self.word_editor(self.managed_words[i])

    def editor(self, title):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setMinimumWidth(520)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)
        layout.addWidget(label(title, "title"))
        return (dlg, layout)

    @staticmethod
    def editor_field(layout, title, value="", limit=100):
        layout.addWidget(label(title))
        field = QLineEdit(value)
        field.setAccessibleName(title)
        field.setMaxLength(limit)
        layout.addWidget(field)
        return field

    def word_editor(self, word=None):
        w = word or {}
        dlg, layout = self.editor(tr("编辑词汇") if word else tr("添加词汇"))
        english = self.editor_field(layout, tr("英文"), w.get("english", ""))
        chinese = self.editor_field(layout, tr("中文释义"), w.get("chinese", ""), 200)
        layout.addWidget(label(tr("主题")))
        category = QComboBox()
        category.setEditable(True)
        add_categories(category, self.service.vocabulary.categories)
        category.setCurrentText(category_text(w.get("category", "")))
        category.setAccessibleName(tr("主题"))
        layout.addWidget(category)
        aliases = self.editor_field(
            layout,
            tr("其他可接受答案（用英文分号分隔）"),
            "; ".join(w.get("aliases", [])),
            2020,
        )
        enabled = QCheckBox(tr("启用词汇"))
        enabled.setChecked(w.get("enabled", True))
        layout.addWidget(enabled)
        error = label("", "error", True)
        layout.addWidget(error)

        def save():
            try:
                self.service.save_word(
                    english.text(),
                    chinese.text(),
                    category_value(category),
                    [a.strip() for a in aliases.text().split(";") if a.strip()],
                    w.get("id"),
                    enabled.isChecked(),
                )
                dlg.accept()
                self.show_page("manage_words")
            except AppError as exc:
                error.setText(tr(str(exc)))

        layout.addLayout(
            row_layout(
                button(tr("保存"), save), button(tr("取消"), dlg.reject, "ghost")
            )
        )
        dlg.exec()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="KET Word Studio native Qt application"
    )
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--smoke-test", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    directory = args.data_dir or data_directory()
    directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=directory / "desktop.log", level=logging.WARNING, encoding="utf-8"
    )
    app = QApplication(sys.argv[:1])
    app.setApplicationName("KET Word Studio")
    app.setOrganizationName("KETWordStudio")
    app.setStyle("Fusion")
    try:
        window = StudioWindow(StudioService(directory / "demo.sqlite3"))
    except Exception as exc:
        logging.exception("Startup failed")
        QMessageBox.critical(
            None, tr("无法启动"), tr("无法打开学习数据：{0}", f"{exc}")
        )
        return 1
    window.show()
    if args.smoke_test:

        def capture():
            args.smoke_test.parent.mkdir(parents=True, exist_ok=True)
            ok = window.grab().save(str(args.smoke_test))
            app.exit(0 if ok else 2)

        QTimer.singleShot(1300, capture)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
