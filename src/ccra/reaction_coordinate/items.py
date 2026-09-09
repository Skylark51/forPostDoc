from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Signal, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject, QGraphicsPathItem, QInputDialog, QStyleOptionGraphicsItem, QWidget

from .models import DiagramEdge, DiagramNode


class NodeItem(QGraphicsObject):
    moved = Signal(str)
    drag_started = Signal()
    edited = Signal(str)

    WIDTH = 122.0
    HEIGHT = 92.0

    def __init__(self, node: DiagramNode):
        super().__init__()
        self.node = node
        self.setPos(node.x, node.y)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.WIDTH / 2, -42, self.WIDTH, self.HEIGHT)

    def _canvas(self) -> dict:
        scene = self.scene()
        return getattr(getattr(scene, "diagram", None), "canvas", {}) if scene else {}

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        canvas = self._canvas()
        selected = self.isSelected()
        color = QColor(self.node.color or "#202124")
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if selected:
            painter.setBrush(QBrush(QColor("#eef4ff")))
            painter.setPen(QPen(QColor("#7b9ed6"), 1.0, Qt.PenStyle.DashLine))
            painter.drawRoundedRect(self.boundingRect().adjusted(2, 2, -2, -2), 5, 5)
        if self.node.node_type == "annotation":
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#7b8088"), 1.0))
            painter.drawRoundedRect(QRectF(-52, -24, 104, 48), 4, 4)
        else:
            pen = QPen(color, 2.4 if self.node.node_type == "transition_state" else 2.0)
            if self.node.node_type == "transition_state":
                pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(QPointF(-45, 0), QPointF(45, 0))
        painter.setPen(QPen(QColor("#202124")))
        font = QFont("Segoe UI", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(-58, -36, 116, 25), Qt.AlignmentFlag.AlignCenter, self.node.label)
        lines: list[str] = []
        if canvas.get("show_energy", True) and self.node.energy is not None:
            lines.append(f"{self.node.energy:g} {self.node.energy_unit}")
        if canvas.get("show_spin_multiplicity", True):
            spin_text = self.node.spin.strip()
            mult_text = f"M={self.node.multiplicity}" if self.node.multiplicity else ""
            extra = " · ".join(value for value in [spin_text, mult_text] if value)
            if extra:
                lines.append(extra)
        if canvas.get("show_subtitle", True) and self.node.subtitle:
            lines.append(self.node.subtitle)
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor("#545b66")))
        painter.drawText(QRectF(-60, 8, 120, 42), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "\n".join(lines))

    def mousePressEvent(self, event) -> None:
        self.drag_started.emit()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        text, ok = QInputDialog.getText(None, "노드 이름", "Label", text=self.node.label)
        if ok and text.strip():
            self.node.label = text.strip()
            self.update()
            self.edited.emit(self.node.id)
        event.accept()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene() is not None:
            scene = self.scene()
            if getattr(scene, "snap_to_grid", False):
                grid = max(1.0, float(getattr(scene, "grid_size", 20.0)))
                point = value
                return QPointF(round(point.x() / grid) * grid, round(point.y() / grid) * grid)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            point = self.pos()
            self.node.x, self.node.y = point.x(), point.y()
            self.moved.emit(self.node.id)
        return super().itemChange(change, value)


class EdgeItem(QGraphicsPathItem):
    def __init__(self, edge: DiagramEdge, source: NodeItem, target: NodeItem):
        super().__init__()
        self.edge = edge
        self.source = source
        self.target = target
        self.setZValue(-10)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.update_path()

    def _canvas(self) -> dict:
        scene = self.scene()
        return getattr(getattr(scene, "diagram", None), "canvas", {}) if scene else {}

    def update_path(self) -> None:
        start = self.source.pos()
        end = self.target.pos()
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = max(1.0, math.hypot(dx, dy))
        ux, uy = dx / length, dy / length
        start = QPointF(start.x() + ux * 48, start.y() + uy * 8)
        end = QPointF(end.x() - ux * 48, end.y() - uy * 8)
        path = QPainterPath(start)
        canvas = self._canvas()
        curved = self.edge.edge_type == "curved" or canvas.get("force_curved", False)
        if curved:
            nx, ny = -uy, ux
            bend = min(120.0, length * 0.22)
            c1 = QPointF(start.x() + dx * 0.33 + nx * bend, start.y() + dy * 0.33 + ny * bend)
            c2 = QPointF(start.x() + dx * 0.66 + nx * bend, start.y() + dy * 0.66 + ny * bend)
            path.cubicTo(c1, c2, end)
        else:
            path.lineTo(end)
        self.setPath(path)

    @staticmethod
    def _arrow_polygon(tip: QPointF, tail: QPointF, size: float = 9.0) -> QPolygonF:
        angle = math.atan2(tip.y() - tail.y(), tip.x() - tail.x())
        left = QPointF(tip.x() - size * math.cos(angle - math.pi / 6), tip.y() - size * math.sin(angle - math.pi / 6))
        right = QPointF(tip.x() - size * math.cos(angle + math.pi / 6), tip.y() - size * math.sin(angle + math.pi / 6))
        return QPolygonF([tip, left, right])

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        canvas = self._canvas()
        color = QColor("#202124" if not self.isSelected() else "#2457a6")
        pen = QPen(color, 1.7)
        if self.edge.edge_type == "dashed":
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
        if canvas.get("show_arrows", True) and self.edge.edge_type != "no-arrow":
            tip = self.path().pointAtPercent(1.0)
            tail = self.path().pointAtPercent(0.965)
            painter.setBrush(QBrush(color))
            painter.drawPolygon(self._arrow_polygon(tip, tail))
            if self.edge.edge_type == "reversible":
                start = self.path().pointAtPercent(0.0)
                ahead = self.path().pointAtPercent(0.035)
                painter.drawPolygon(self._arrow_polygon(start, ahead))
        label_parts: list[str] = []
        if canvas.get("show_edge_label", True) and self.edge.label:
            label_parts.append(self.edge.label)
        if canvas.get("show_barrier", True) and self.edge.barrier is not None:
            label_parts.append(f"Δ‡ {self.edge.barrier:g}")
        if label_parts:
            midpoint = self.path().pointAtPercent(0.5)
            painter.setPen(QPen(QColor("#555b66")))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(QRectF(midpoint.x() - 55, midpoint.y() - 30, 110, 24), Qt.AlignmentFlag.AlignCenter, " · ".join(label_parts))
