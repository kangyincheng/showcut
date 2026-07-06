from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget
from shapes import RectangleShape, CircleShape, LineShape, PolylineShape, ArrowShape


class CanvasWidget(QWidget):
    shapesChanged = pyqtSignal(int)

    TOOL_NONE = "none"
    TOOL_RECTANGLE = "rectangle"
    TOOL_CIRCLE = "circle"
    TOOL_LINE = "line"
    TOOL_POLYLINE = "polyline"
    TOOL_ARROW = "arrow"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.shapes = []
        self.current_tool = self.TOOL_NONE
        self.current_shape = None
        self.is_drawing = False
        self.pen_color = QColor(255, 0, 0)
        self.pen_width = 2
        self.pen_style = Qt.SolidLine
        self.setMouseTracking(True)

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.shapes = []
        self.current_shape = None
        self.current_tool = self.TOOL_NONE
        self.setFixedSize(pixmap.size())
        self.update()

    def set_tool(self, tool):
        self.current_tool = tool
        self.current_shape = None
        if tool == self.TOOL_NONE:
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setCursor(Qt.CrossCursor)

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_width(self, width):
        self.pen_width = width

    def set_pen_style(self, style):
        self.pen_style = style

    def undo(self):
        if self.shapes:
            self.shapes.pop()
            self.shapesChanged.emit(len(self.shapes))
            self.update()

    def clear_shapes(self):
        self.shapes.clear()
        self.current_shape = None
        self.shapesChanged.emit(0)
        self.update()

    def get_result_pixmap(self):
        if not self.pixmap:
            return QPixmap()
        result = QPixmap(self.pixmap)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        for shape in self.shapes:
            shape.paint(painter)
        painter.end()
        return result

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.pixmap:
            painter.drawPixmap(0, 0, self.pixmap)

        for shape in self.shapes:
            shape.paint(painter)

        if self.current_shape and self.is_drawing:
            self.current_shape.paint(painter)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or self.current_tool == self.TOOL_NONE:
            return

        if self.current_tool == self.TOOL_RECTANGLE:
            self.current_shape = RectangleShape()
        elif self.current_tool == self.TOOL_CIRCLE:
            self.current_shape = CircleShape()
        elif self.current_tool == self.TOOL_LINE:
            self.current_shape = LineShape()
        elif self.current_tool == self.TOOL_ARROW:
            self.current_shape = ArrowShape()
        elif self.current_tool == self.TOOL_POLYLINE:
            if self.current_shape is None:
                self.current_shape = PolylineShape()
                self.current_shape.add_point(event.pos())
            self.current_shape.add_point(event.pos())
            self.current_shape.end_point = event.pos()
            self.update()
            return

        if self.current_shape:
            self.current_shape.set_pen(self.pen_color, self.pen_width, self.pen_style)
            self.current_shape.start_point = event.pos()
            self.current_shape.end_point = event.pos()
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing and self.current_shape:
            if isinstance(self.current_shape, PolylineShape):
                self.current_shape.end_point = event.pos()
            else:
                self.current_shape.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.is_drawing and self.current_shape:
            if isinstance(self.current_shape, PolylineShape):
                pass
            else:
                self.shapes.append(self.current_shape)
                self.current_shape = None
                self.is_drawing = False
                self.shapesChanged.emit(len(self.shapes))
            self.update()

    def mouseDoubleClickEvent(self, event):
        if self.current_tool == self.TOOL_POLYLINE and self.current_shape:
            if isinstance(self.current_shape, PolylineShape):
                if len(self.current_shape.points) >= 2:
                    self.current_shape.is_finished = True
                    self.shapes.append(self.current_shape)
                self.current_shape = None
                self.is_drawing = False
                self.shapesChanged.emit(len(self.shapes))
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.current_shape:
                self.current_shape = None
                self.is_drawing = False
                self.update()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.current_tool == self.TOOL_POLYLINE and self.current_shape:
                if isinstance(self.current_shape, PolylineShape):
                    if len(self.current_shape.points) >= 2:
                        self.current_shape.is_finished = True
                        self.shapes.append(self.current_shape)
                    self.current_shape = None
                    self.is_drawing = False
                    self.shapesChanged.emit(len(self.shapes))
                    self.update()
