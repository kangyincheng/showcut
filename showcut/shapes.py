from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSignal
from PyQt5.QtGui import QPainterPath, QPen, QColor, QPainter


class Shape:
    def __init__(self, pen=None):
        self.pen = pen or QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
        self.start_point = QPoint()
        self.end_point = QPoint()

    def set_pen(self, color, width, style):
        self.pen = QPen(color, width, style)

    def paint(self, painter):
        pass

    def contains(self, point):
        return False

    def move_by(self, delta):
        self.start_point += delta
        self.end_point += delta


class RectangleShape(Shape):
    def paint(self, painter):
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        rect = QRectF(self.start_point, self.end_point).normalized()
        painter.drawRect(rect)

    def contains(self, point):
        rect = QRectF(self.start_point, self.end_point).normalized()
        return (
            abs(point.x() - rect.left()) < self.pen.width() + 2
            or abs(point.x() - rect.right()) < self.pen.width() + 2
            or abs(point.y() - rect.top()) < self.pen.width() + 2
            or abs(point.y() - rect.bottom()) < self.pen.width() + 2
        ) and rect.contains(point)


class CircleShape(Shape):
    def paint(self, painter):
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        rect = QRectF(self.start_point, self.end_point).normalized()
        painter.drawEllipse(rect)

    def contains(self, point):
        rect = QRectF(self.start_point, self.end_point).normalized()
        center = rect.center()
        rx = rect.width() / 2
        ry = rect.height() / 2
        if rx <= 0 or ry <= 0:
            return False
        dist = ((point.x() - center.x()) ** 2) / (rx ** 2) + (
            (point.y() - center.y()) ** 2
        ) / (ry ** 2)
        return 0.9 < dist < 1.1


class LineShape(Shape):
    def paint(self, painter):
        painter.setPen(self.pen)
        painter.drawLine(self.start_point, self.end_point)

    def contains(self, point):
        line_len = (self.end_point - self.start_point).manhattanLength()
        if line_len == 0:
            return False
        dist = (
            abs(
                (self.end_point.y() - self.start_point.y()) * point.x()
                - (self.end_point.x() - self.start_point.x()) * point.y()
                + self.end_point.x() * self.start_point.y()
                - self.end_point.y() * self.start_point.x()
            )
            / line_len
        )
        return dist < self.pen.width() + 3 and QRectF(
            self.start_point, self.end_point
        ).normalized().contains(point)


class PolylineShape(Shape):
    def __init__(self, pen=None):
        super().__init__(pen)
        self.points = []
        self.is_finished = False

    def add_point(self, point):
        self.points.append(QPoint(point))

    def paint(self, painter):
        painter.setPen(self.pen)
        if len(self.points) < 2:
            return
        for i in range(len(self.points) - 1):
            painter.drawLine(self.points[i], self.points[i + 1])
        if not self.is_finished and self.end_point:
            painter.drawLine(self.points[-1], self.end_point)

    def contains(self, point):
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            line_len = (p2 - p1).manhattanLength()
            if line_len == 0:
                continue
            dist = (
                abs(
                    (p2.y() - p1.y()) * point.x()
                    - (p2.x() - p1.x()) * point.y()
                    + p2.x() * p1.y()
                    - p2.y() * p1.x()
                )
                / line_len
            )
            if dist < self.pen.width() + 3 and QRectF(p1, p2).normalized().contains(
                point
            ):
                return True
        return False

    def move_by(self, delta):
        for i in range(len(self.points)):
            self.points[i] += delta


class ArrowShape(Shape):
    def paint(self, painter):
        painter.setPen(self.pen)
        painter.drawLine(self.start_point, self.end_point)

        dx = self.end_point.x() - self.start_point.x()
        dy = self.end_point.y() - self.start_point.y()
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return

        size = 10 + self.pen.width() * 2
        ux = dx / length
        uy = dy / length
        nx = -uy
        ny = ux

        tip = self.end_point
        p1 = QPoint(
            int(tip.x() - size * ux + size * 0.5 * nx),
            int(tip.y() - size * uy + size * 0.5 * ny),
        )
        p2 = QPoint(
            int(tip.x() - size * ux - size * 0.5 * nx),
            int(tip.y() - size * uy - size * 0.5 * ny),
        )

        painter.setBrush(self.pen.color())
        pen = QPen(self.pen)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)

        path = QPainterPath()
        path.moveTo(tip)
        path.lineTo(p1)
        path.lineTo(p2)
        path.closeSubpath()
        painter.drawPath(path)
        painter.fillPath(path, self.pen.color())

    def contains(self, point):
        line_len = (self.end_point - self.start_point).manhattanLength()
        if line_len == 0:
            return False
        dist = (
            abs(
                (self.end_point.y() - self.start_point.y()) * point.x()
                - (self.end_point.x() - self.start_point.x()) * point.y()
                + self.end_point.x() * self.start_point.y()
                - self.end_point.y() * self.start_point.x()
            )
            / line_len
        )
        return dist < self.pen.width() + 3 and QRectF(
            self.start_point, self.end_point
        ).normalized().contains(point)
