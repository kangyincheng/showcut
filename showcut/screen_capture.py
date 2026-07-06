from PyQt5.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QCursor
from PyQt5.QtWidgets import QWidget
import sys

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes


class ScreenCaptureWidget(QWidget):
    captureCompleted = pyqtSignal(QPixmap)
    captureCancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        self.full_pixmap = None
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_rect = QRect()
        self.is_selecting = False
        self.is_moving = False
        self.move_start = QPoint()
        self.windows = []
        self.hovered_window = None

    def start_capture(self):
        screen = self.screen()
        if screen:
            self.full_pixmap = screen.grabWindow(0)
            self.setGeometry(screen.geometry())
            self._enum_windows()
            self.showFullScreen()
            self.raise_()
            self.activateWindow()

    def _enum_windows(self):
        self.windows = []
        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32

                def enum_callback(hwnd, lParam):
                    if user32.IsWindowVisible(hwnd):
                        rect = wintypes.RECT()
                        user32.GetWindowRect(hwnd, ctypes.byref(rect))
                        width = rect.right - rect.left
                        height = rect.bottom - rect.top
                        if width > 50 and height > 50:
                            self.windows.append(
                                QRect(rect.left, rect.top, width, height)
                            )
                    return True

                WNDENUMPROC = ctypes.WINFUNCTYPE(
                    ctypes.c_bool, wintypes.HWND, wintypes.LPARAM
                )
                user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
            except Exception:
                pass

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.full_pixmap:
            painter.drawPixmap(0, 0, self.full_pixmap)

        dim_color = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), dim_color)

        if self.hovered_window and not self.is_selecting:
            painter.setPen(QPen(QColor(0, 120, 215), 3, Qt.SolidLine))
            painter.setBrush(QColor(0, 120, 215, 30))
            painter.drawRect(self.hovered_window)
            painter.fillRect(self.hovered_window, QColor(0, 120, 215, 30))

        if not self.selection_rect.isNull():
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.drawPixmap(
                self.selection_rect.topLeft(),
                self.full_pixmap.copy(self.selection_rect),
            )
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            pen = QPen(QColor(0, 120, 215), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.selection_rect)

            self._draw_handles(painter)

            size_text = f"{self.selection_rect.width()} x {self.selection_rect.height()}"
            font = QFont("Arial", 10)
            painter.setFont(font)
            text_rect = painter.fontMetrics().boundingRect(size_text)
            text_x = self.selection_rect.right() - text_rect.width() - 8
            text_y = self.selection_rect.bottom() + 25
            if text_y + text_rect.height() > self.height():
                text_y = self.selection_rect.top() - 25
            painter.fillRect(
                text_x - 4,
                text_y - text_rect.height() - 4,
                text_rect.width() + 8,
                text_rect.height() + 8,
                QColor(0, 0, 0, 180),
            )
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(
                QRect(
                    text_x,
                    text_y - text_rect.height(),
                    text_rect.width(),
                    text_rect.height(),
                ),
                Qt.AlignCenter,
                size_text,
            )

        else:
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", 14)
            painter.setFont(font)
            text = "拖拽选择截图区域 | 按 ESC 取消 | 点击窗口自动对齐"
            text_rect = painter.fontMetrics().boundingRect(text)
            painter.drawText(
                (self.width() - text_rect.width()) // 2,
                50,
                text,
            )

    def _draw_handles(self, painter):
        rect = self.selection_rect
        handles = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
            QPoint(rect.center().x(), rect.top()),
            QPoint(rect.center().x(), rect.bottom()),
            QPoint(rect.left(), rect.center().y()),
            QPoint(rect.right(), rect.center().y()),
        ]
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(QColor(0, 120, 215), 1))
        for handle in handles:
            painter.drawRect(handle.x() - 4, handle.y() - 4, 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True
            self.hovered_window = None

            if self.selection_rect.contains(event.pos()):
                self.is_moving = True
                self.move_start = event.pos() - self.selection_rect.topLeft()
            else:
                self.selection_rect = QRect()
                self.is_moving = False
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting and not self.is_moving:
            self.end_point = event.pos()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
        elif self.is_moving:
            new_top_left = event.pos() - self.move_start
            self.selection_rect = QRect(
                new_top_left, self.selection_rect.size()
            )
        else:
            self.hovered_window = None
            for win_rect in self.windows:
                if win_rect.contains(event.pos()):
                    self.hovered_window = win_rect
                    break

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            self.is_moving = False

            if self.selection_rect.isNull() and self.hovered_window:
                self.selection_rect = QRect(self.hovered_window)
                self.update()

    def mouseDoubleClickEvent(self, event):
        if self.selection_rect.isNull() and self.hovered_window:
            self.selection_rect = QRect(self.hovered_window)
            self._finish_capture()
        elif not self.selection_rect.isNull():
            self._finish_capture()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._cancel_capture()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not self.selection_rect.isNull():
                self._finish_capture()

    def _finish_capture(self):
        if self.full_pixmap and not self.selection_rect.isNull():
            cropped = self.full_pixmap.copy(self.selection_rect)
            self.hide()
            self.captureCompleted.emit(cropped)

    def _cancel_capture(self):
        self.hide()
        self.captureCancelled.emit()
