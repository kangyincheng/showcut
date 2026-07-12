from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QComboBox,
    QColorDialog,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QFrame,
    QSplitter,
    QTextEdit,
    QShortcut,
    QAction,
    QToolBar,
    QStatusBar,
    QDialog,
    QDialogButtonBox,
    QRadioButton,
    QButtonGroup,
)
from screen_capture import ScreenCaptureWidget
from canvas_widget import CanvasWidget
from translator import Translator


class ColorButton(QPushButton):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, color=QColor(255, 0, 0), parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedSize(32, 32)
        self.setStyleSheet(self._get_style())
        self.clicked.connect(self._choose_color)

    def _get_style(self):
        return f"""
            QPushButton {{
                background-color: {self.color.name()};
                border: 2px solid #888;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #555;
            }}
        """

    def _choose_color(self):
        color = QColorDialog.getColor(self.color, self, "选择颜色")
        if color.isValid():
            self.color = color
            self.setStyleSheet(self._get_style())
            self.colorChanged.emit(color)

    def get_color(self):
        return self.color


class ToolButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumHeight(36)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
                border: 1px solid #0078d4;
            }
        """
        )


class TranslateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("截图翻译")
        self.setMinimumSize(500, 400)
        self.translator = Translator()

        layout = QVBoxLayout(self)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("源语言:"))
        self.from_combo = QComboBox()
        self.from_combo.addItems(["自动检测", "中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"])
        lang_layout.addWidget(self.from_combo)

        lang_layout.addWidget(QLabel("目标语言:"))
        self.to_combo = QComboBox()
        self.to_combo.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"])
        self.to_combo.setCurrentIndex(0)
        lang_layout.addWidget(self.to_combo)
        lang_layout.addStretch()

        self.translate_btn = QPushButton("翻译")
        self.translate_btn.clicked.connect(self._do_translate)
        lang_layout.addWidget(self.translate_btn)

        layout.addLayout(lang_layout)

        layout.addWidget(QLabel("原文:"))
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("粘贴或输入要翻译的文本...")
        layout.addWidget(self.source_text, 1)

        layout.addWidget(QLabel("翻译结果:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text, 1)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self._lang_map = {
            "自动检测": "auto",
            "中文": "zh",
            "英文": "en",
            "日文": "ja",
            "韩文": "ko",
            "法文": "fr",
            "德文": "de",
            "西班牙文": "es",
        }

    def set_source_text(self, text):
        self.source_text.setPlainText(text)

    def _do_translate(self):
        text = self.source_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入要翻译的文本")
            return

        from_lang = self._lang_map.get(self.from_combo.currentText(), "auto")
        to_lang = self._lang_map.get(self.to_combo.currentText(), "zh")

        self.translate_btn.setEnabled(False)
        self.translate_btn.setText("翻译中...")
        QApplication.processEvents()

        result = self.translator.translate(text, from_lang, to_lang)

        self.result_text.setPlainText(result)
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText("翻译")


from PyQt5.QtWidgets import QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShowCut - 截图工具")
        self.setMinimumSize(900, 600)

        self.screen_capture = None
        self.translator = Translator()
        self.current_pixmap = None
        self._temp_file = None

        self._create_ui()
        self._create_shortcuts()

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_toolbar = QHBoxLayout()
        top_toolbar.setContentsMargins(8, 8, 8, 8)
        top_toolbar.setSpacing(8)

        self.capture_btn = QPushButton("📷  开始截图")
        self.capture_btn.setMinimumHeight(36)
        self.capture_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """
        )
        self.capture_btn.clicked.connect(self.start_capture)
        top_toolbar.addWidget(self.capture_btn)

        top_toolbar.addWidget(self._create_separator())

        shape_label = QLabel("绘图工具:")
        top_toolbar.addWidget(shape_label)

        self.rect_btn = ToolButton("□ 矩形")
        self.rect_btn.clicked.connect(lambda: self.set_tool(CanvasWidget.TOOL_RECTANGLE))
        top_toolbar.addWidget(self.rect_btn)

        self.circle_btn = ToolButton("○ 圆形")
        self.circle_btn.clicked.connect(lambda: self.set_tool(CanvasWidget.TOOL_CIRCLE))
        top_toolbar.addWidget(self.circle_btn)

        self.line_btn = ToolButton("／ 直线")
        self.line_btn.clicked.connect(lambda: self.set_tool(CanvasWidget.TOOL_LINE))
        top_toolbar.addWidget(self.line_btn)

        self.arrow_btn = ToolButton("→ 箭头")
        self.arrow_btn.clicked.connect(lambda: self.set_tool(CanvasWidget.TOOL_ARROW))
        top_toolbar.addWidget(self.arrow_btn)

        self.polyline_btn = ToolButton("〰 多边形")
        self.polyline_btn.setToolTip("点击添加顶点，双击或按Enter完成")
        self.polyline_btn.clicked.connect(lambda: self.set_tool(CanvasWidget.TOOL_POLYLINE))
        top_toolbar.addWidget(self.polyline_btn)

        top_toolbar.addWidget(self._create_separator())

        color_label = QLabel("颜色:")
        top_toolbar.addWidget(color_label)

        self.color_btn = ColorButton(QColor(255, 0, 0))
        self.color_btn.colorChanged.connect(self.on_color_changed)
        top_toolbar.addWidget(self.color_btn)

        for color_name, color_hex in [
            ("红", "#FF0000"),
            ("黄", "#FFFF00"),
            ("蓝", "#0000FF"),
            ("绿", "#00FF00"),
            ("黑", "#000000"),
            ("白", "#FFFFFF"),
        ]:
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color_hex};
                    border: 1px solid #888;
                    border-radius: 2px;
                }}
                QPushButton:hover {{
                    border: 2px solid #0078d4;
                }}
            """
            )
            btn.setToolTip(color_name)
            btn.clicked.connect(lambda checked, c=color_hex: self.set_preset_color(c))
            top_toolbar.addWidget(btn)

        top_toolbar.addWidget(self._create_separator())

        width_label = QLabel("粗细:")
        top_toolbar.addWidget(width_label)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20)
        self.width_spin.setValue(2)
        self.width_spin.valueChanged.connect(self.on_width_changed)
        top_toolbar.addWidget(self.width_spin)

        top_toolbar.addWidget(self._create_separator())

        style_label = QLabel("线型:")
        top_toolbar.addWidget(style_label)

        self.style_combo = QComboBox()
        self.style_combo.addItem("实线", Qt.SolidLine)
        self.style_combo.addItem("虚线", Qt.DashLine)
        self.style_combo.addItem("点线", Qt.DotLine)
        self.style_combo.addItem("点划线", Qt.DashDotLine)
        self.style_combo.currentIndexChanged.connect(self.on_style_changed)
        top_toolbar.addWidget(self.style_combo)

        top_toolbar.addWidget(self._create_separator())

        self.undo_btn = QPushButton("↶ 撤销")
        self.undo_btn.setMinimumHeight(32)
        self.undo_btn.clicked.connect(self.undo_shape)
        self.undo_btn.setEnabled(False)
        top_toolbar.addWidget(self.undo_btn)

        self.clear_btn = QPushButton("🗑  清除标注")
        self.clear_btn.setMinimumHeight(32)
        self.clear_btn.clicked.connect(self.clear_shapes)
        self.clear_btn.setEnabled(False)
        top_toolbar.addWidget(self.clear_btn)

        top_toolbar.addStretch()

        self.translate_btn = QPushButton("🌐 翻译")
        self.translate_btn.setMinimumHeight(32)
        self.translate_btn.clicked.connect(self.show_translate)
        self.translate_btn.setEnabled(False)
        top_toolbar.addWidget(self.translate_btn)

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setMinimumHeight(32)
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        top_toolbar.addWidget(self.save_btn)

        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.setMinimumHeight(32)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        top_toolbar.addWidget(self.copy_btn)

        main_layout.addLayout(top_toolbar)

        top_bar = QFrame()
        top_bar.setFrameShape(QFrame.HLine)
        top_bar.setStyleSheet("color: #ddd;")
        main_layout.addWidget(top_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.canvas = CanvasWidget()
        self.canvas.shapesChanged.connect(self.on_shapes_changed)

        scroll_area.setWidget(self.canvas)
        main_layout.addWidget(scroll_area, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("点击「开始截图」按钮开始截图")

        self._tool_buttons = [
            self.rect_btn,
            self.circle_btn,
            self.line_btn,
            self.arrow_btn,
            self.polyline_btn,
        ]

    def _create_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #ddd;")
        return sep

    def _create_shortcuts(self):
        capture_sc = QShortcut("Ctrl+Shift+A", self)
        capture_sc.activated.connect(self.start_capture)

        save_sc = QShortcut("Ctrl+S", self)
        save_sc.activated.connect(self.save_image)

        undo_sc = QShortcut("Ctrl+Z", self)
        undo_sc.activated.connect(self.undo_shape)

        copy_sc = QShortcut("Ctrl+C", self)
        copy_sc.activated.connect(self.copy_to_clipboard)

        esc_sc = QShortcut("Esc", self)
        esc_sc.activated.connect(self.set_none_tool)

    def start_capture(self):
        self.hide()
        QTimer.singleShot(300, self._do_capture)

    def _do_capture(self):
        self.screen_capture = ScreenCaptureWidget()
        self.screen_capture.captureCompleted.connect(self.on_capture_completed)
        self.screen_capture.captureCancelled.connect(self.on_capture_cancelled)
        self.screen_capture.start_capture()

    def on_capture_completed(self, pixmap):
        self.current_pixmap = pixmap
        self.canvas.set_pixmap(pixmap)
        self.show()
        self.raise_()
        self.activateWindow()
        self.save_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.translate_btn.setEnabled(True)
        self.clear_btn.setEnabled(False)
        self.undo_btn.setEnabled(False)
        self.status_bar.showMessage(
            f"截图完成 - {pixmap.width()} x {pixmap.height()} | Ctrl+S 保存 | Ctrl+C 复制"
        )
        self.screen_capture = None

    def on_capture_cancelled(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.status_bar.showMessage("截图已取消")
        self.screen_capture = None

    def set_tool(self, tool):
        self.canvas.set_tool(tool)
        for btn in self._tool_buttons:
            btn.setChecked(False)

        if tool == CanvasWidget.TOOL_RECTANGLE:
            self.rect_btn.setChecked(True)
            self.status_bar.showMessage("矩形工具 - 拖拽绘制矩形")
        elif tool == CanvasWidget.TOOL_CIRCLE:
            self.circle_btn.setChecked(True)
            self.status_bar.showMessage("圆形工具 - 拖拽绘制圆形/椭圆")
        elif tool == CanvasWidget.TOOL_LINE:
            self.line_btn.setChecked(True)
            self.status_bar.showMessage("直线工具 - 拖拽绘制直线")
        elif tool == CanvasWidget.TOOL_ARROW:
            self.arrow_btn.setChecked(True)
            self.status_bar.showMessage("箭头工具 - 拖拽绘制箭头")
        elif tool == CanvasWidget.TOOL_POLYLINE:
            self.polyline_btn.setChecked(True)
            self.status_bar.showMessage("多边形工具 - 点击添加顶点，双击或按Enter完成")

    def set_none_tool(self):
        self.set_tool(CanvasWidget.TOOL_NONE)

    def on_color_changed(self, color):
        self.canvas.set_pen_color(color)

    def set_preset_color(self, color_hex):
        color = QColor(color_hex)
        self.color_btn.color = color
        self.color_btn.setStyleSheet(self.color_btn._get_style())
        self.canvas.set_pen_color(color)

    def on_width_changed(self, value):
        self.canvas.set_pen_width(value)

    def on_style_changed(self, index):
        style = self.style_combo.itemData(index)
        self.canvas.set_pen_style(style)

    def on_shapes_changed(self, count):
        self.undo_btn.setEnabled(count > 0)
        self.clear_btn.setEnabled(count > 0)
        if count > 0:
            self.status_bar.showMessage(f"标注数量: {count}")
        else:
            self.status_bar.showMessage("")

    def undo_shape(self):
        self.canvas.undo()

    def clear_shapes(self):
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有标注吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.canvas.clear_shapes()

    def save_image(self):
        if not self.current_pixmap:
            return

        result = self.canvas.get_result_pixmap()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存截图",
            "screenshot.png",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;BMP图片 (*.bmp)",
        )
        if file_path:
            result.save(file_path)
            self.status_bar.showMessage(f"已保存到: {file_path}")

    def copy_to_clipboard(self):
        if not self.current_pixmap:
            return

        result = self.canvas.get_result_pixmap()
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(result)
        self.status_bar.showMessage("已复制到剪贴板")

    def show_translate(self):
        dialog = TranslateDialog(self)
        dialog.exec_()

    def closeEvent(self, event):
        if self.screen_capture:
            self.screen_capture._cancel_capture()
        event.accept()
