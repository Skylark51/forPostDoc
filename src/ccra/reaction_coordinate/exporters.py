from __future__ import annotations

from html import escape
from pathlib import Path

from PySide6.QtCore import QRectF, QSize
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtSvg import QSvgGenerator
from PySide6.QtWidgets import QApplication, QGraphicsScene

from .models import Diagram


def _source_rect(scene: QGraphicsScene) -> QRectF:
    rect = scene.itemsBoundingRect().adjusted(-40, -40, 40, 40)
    return rect if not rect.isEmpty() else QRectF(0, 0, 800, 600)


def export_png(scene: QGraphicsScene, destination: Path, scale: float = 2.5) -> Path:
    destination = Path(destination)
    rect = _source_rect(scene)
    width = max(1, int(rect.width() * scale))
    height = max(1, int(rect.height() * scale))
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor("white"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    scene.render(painter, QRectF(0, 0, width, height), rect)
    painter.end()
    if not image.save(str(destination)):
        raise OSError(f"Could not save PNG: {destination}")
    return destination


def export_svg(scene: QGraphicsScene, destination: Path) -> Path:
    destination = Path(destination)
    rect = _source_rect(scene)
    generator = QSvgGenerator()
    generator.setFileName(str(destination))
    generator.setSize(QSize(max(1, int(rect.width())), max(1, int(rect.height()))))
    generator.setViewBox(QRectF(0, 0, rect.width(), rect.height()))
    generator.setTitle("CCRA Reaction Coordinate")
    painter = QPainter(generator)
    scene.render(painter, QRectF(0, 0, rect.width(), rect.height()), rect)
    painter.end()
    return destination


def copy_as_image(scene: QGraphicsScene, scale: float = 2.0) -> None:
    rect = _source_rect(scene)
    image = QImage(max(1, int(rect.width() * scale)), max(1, int(rect.height() * scale)), QImage.Format.Format_ARGB32)
    image.fill(QColor("white"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    scene.render(painter, QRectF(0, 0, image.width(), image.height()), rect)
    painter.end()
    QApplication.clipboard().setImage(image)


def export_model_svg(diagram: Diagram, destination: Path) -> Path:
    """Pure-model SVG writer used for deterministic snapshots and tests."""
    destination = Path(destination)
    width = int(diagram.canvas.get("width", 1600))
    height = int(diagram.canvas.get("height", 1000))
    nodes = {node.id: node for node in diagram.nodes}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>']
    for edge in diagram.edges:
        a, b = nodes.get(edge.source), nodes.get(edge.target)
        if not a or not b:
            continue
        dash = ' stroke-dasharray="7 5"' if edge.edge_type == "dashed" else ""
        parts.append(f'<line x1="{a.x:.2f}" y1="{a.y:.2f}" x2="{b.x:.2f}" y2="{b.y:.2f}" stroke="#202124" stroke-width="2"{dash}/>')
    for node in diagram.nodes:
        parts.append(f'<line x1="{node.x-45:.2f}" y1="{node.y:.2f}" x2="{node.x+45:.2f}" y2="{node.y:.2f}" stroke="#202124" stroke-width="2"/>')
        parts.append(f'<text x="{node.x:.2f}" y="{node.y-14:.2f}" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="600">{escape(node.label)}</text>')
        if node.energy is not None:
            parts.append(f'<text x="{node.x:.2f}" y="{node.y+22:.2f}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#555">{node.energy:g} {escape(node.energy_unit)}</text>')
    parts.append("</svg>")
    destination.write_text("\n".join(parts), encoding="utf-8")
    return destination
