from __future__ import annotations

import json

from PySide6.QtCore import QRectF, Signal, Qt
from PySide6.QtGui import QColor, QTransform
from PySide6.QtWidgets import QApplication, QGraphicsScene

from .items import EdgeItem, NodeItem
from .layout import apply_layout
from .models import Diagram, DiagramEdge, DiagramNode, new_id


CLIP_PREFIX = "CCRA_REACTION_COORDINATE:"


class ReactionScene(QGraphicsScene):
    model_changed = Signal()

    def __init__(self, diagram: Diagram | None = None, parent=None):
        super().__init__(parent)
        self.diagram = diagram or Diagram()
        self.mode = "select"
        self.edge_source: str | None = None
        self.node_items: dict[str, NodeItem] = {}
        self.edge_items: dict[str, EdgeItem] = {}
        self.undo_stack: list[dict] = []
        self.redo_stack: list[dict] = []
        self._restoring = False
        self.setSceneRect(QRectF(0, 0, float(self.diagram.canvas.get("width", 1600)), float(self.diagram.canvas.get("height", 1000))))
        self.rebuild()

    @property
    def snap_to_grid(self) -> bool:
        return bool(self.diagram.canvas.get("snap_to_grid", False))

    @property
    def grid_size(self) -> float:
        return float(self.diagram.canvas.get("grid_size", 20))

    def checkpoint(self) -> None:
        if self._restoring:
            return
        snapshot = self.diagram.to_dict()
        if not self.undo_stack or self.undo_stack[-1] != snapshot:
            self.undo_stack.append(snapshot)
            if len(self.undo_stack) > 100:
                self.undo_stack.pop(0)
        self.redo_stack.clear()

    def load_diagram(self, diagram: Diagram, reset_history: bool = True) -> None:
        self.diagram = diagram
        self.setSceneRect(QRectF(0, 0, float(diagram.canvas.get("width", 1600)), float(diagram.canvas.get("height", 1000))))
        if reset_history:
            self.undo_stack.clear()
            self.redo_stack.clear()
        self.rebuild()

    def rebuild(self) -> None:
        self._restoring = True
        self.clear()
        self.node_items.clear()
        self.edge_items.clear()
        for node in self.diagram.nodes:
            item = NodeItem(node)
            item.moved.connect(self._node_moved)
            item.drag_started.connect(self.checkpoint)
            item.edited.connect(lambda _node_id: self._emit_changed())
            self.addItem(item)
            self.node_items[node.id] = item
        for edge in self.diagram.edges:
            source = self.node_items.get(edge.source)
            target = self.node_items.get(edge.target)
            if source and target:
                item = EdgeItem(edge, source, target)
                self.addItem(item)
                self.edge_items[edge.id] = item
        self._restoring = False
        self.update()

    def _emit_changed(self) -> None:
        self.diagram.touch()
        self.model_changed.emit()
        self.update()

    def _node_moved(self, node_id: str) -> None:
        for edge_item in self.edge_items.values():
            if edge_item.edge.source == node_id or edge_item.edge.target == node_id:
                edge_item.update_path()
        self._emit_changed()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.edge_source = None

    def add_node(self, x: float, y: float, node_type: str = "intermediate") -> NodeItem:
        self.checkpoint()
        prefix = "TS" if node_type == "transition_state" else "INT"
        count = 1 + sum(1 for node in self.diagram.nodes if node.node_type == node_type)
        node = DiagramNode(label=f"{prefix}{count}", node_type=node_type, x=x, y=y)
        self.diagram.nodes.append(node)
        item = NodeItem(node)
        item.moved.connect(self._node_moved)
        item.drag_started.connect(self.checkpoint)
        item.edited.connect(lambda _node_id: self._emit_changed())
        self.addItem(item)
        self.node_items[node.id] = item
        self.clearSelection()
        item.setSelected(True)
        self._emit_changed()
        return item

    def add_edge(self, source_id: str, target_id: str, edge_type: str = "normal") -> EdgeItem | None:
        if source_id == target_id or source_id not in self.node_items or target_id not in self.node_items:
            return None
        self.checkpoint()
        edge = DiagramEdge(source=source_id, target=target_id, edge_type=edge_type)
        self.diagram.edges.append(edge)
        item = EdgeItem(edge, self.node_items[source_id], self.node_items[target_id])
        self.addItem(item)
        self.edge_items[edge.id] = item
        self._emit_changed()
        return item

    def mousePressEvent(self, event) -> None:
        item = self.itemAt(event.scenePos(), QTransform())
        node_item = item if isinstance(item, NodeItem) else None
        if self.mode == "edge" and node_item is not None:
            if self.edge_source is None:
                self.edge_source = node_item.node.id
                self.clearSelection()
                node_item.setSelected(True)
            else:
                self.add_edge(self.edge_source, node_item.node.id)
                self.edge_source = None
            event.accept()
            return
        if self.mode in {"node", "ts"} and item is None:
            kind = "transition_state" if self.mode == "ts" else "intermediate"
            self.add_node(event.scenePos().x(), event.scenePos().y(), kind)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if self.itemAt(event.scenePos(), QTransform()) is None:
            self.add_node(event.scenePos().x(), event.scenePos().y(), "intermediate")
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def delete_selected(self) -> None:
        selected = self.selectedItems()
        if not selected:
            return
        self.checkpoint()
        node_ids = {item.node.id for item in selected if isinstance(item, NodeItem)}
        edge_ids = {item.edge.id for item in selected if isinstance(item, EdgeItem)}
        edge_ids.update(edge.id for edge in self.diagram.edges if edge.source in node_ids or edge.target in node_ids)
        self.diagram.nodes = [node for node in self.diagram.nodes if node.id not in node_ids]
        self.diagram.edges = [edge for edge in self.diagram.edges if edge.id not in edge_ids]
        self.rebuild()
        self._emit_changed()

    def copy_selected(self) -> None:
        selected = self.selectedItems()
        node_ids = {item.node.id for item in selected if isinstance(item, NodeItem)}
        if not node_ids:
            return
        data = {
            "nodes": [node.to_dict() for node in self.diagram.nodes if node.id in node_ids],
            "edges": [edge.to_dict() for edge in self.diagram.edges if edge.source in node_ids and edge.target in node_ids],
        }
        QApplication.clipboard().setText(CLIP_PREFIX + json.dumps(data, ensure_ascii=False))

    def paste(self, offset: float = 35.0) -> None:
        text = QApplication.clipboard().text()
        if not text.startswith(CLIP_PREFIX):
            return
        try:
            data = json.loads(text[len(CLIP_PREFIX):])
        except json.JSONDecodeError:
            return
        self.checkpoint()
        mapping: dict[str, str] = {}
        new_nodes: list[DiagramNode] = []
        for raw in data.get("nodes", []):
            old_id = raw.get("id", "")
            raw = dict(raw)
            raw["id"] = new_id("node")
            raw["x"] = float(raw.get("x", 0.0)) + offset
            raw["y"] = float(raw.get("y", 0.0)) + offset
            node = DiagramNode.from_dict(raw)
            mapping[old_id] = node.id
            new_nodes.append(node)
        self.diagram.nodes.extend(new_nodes)
        for raw in data.get("edges", []):
            if raw.get("source") not in mapping or raw.get("target") not in mapping:
                continue
            raw = dict(raw)
            raw["id"] = new_id("edge")
            raw["source"] = mapping[raw["source"]]
            raw["target"] = mapping[raw["target"]]
            self.diagram.edges.append(DiagramEdge.from_dict(raw))
        self.rebuild()
        for node in new_nodes:
            self.node_items[node.id].setSelected(True)
        self._emit_changed()

    def duplicate_selected(self) -> None:
        self.copy_selected()
        self.paste()

    def undo(self) -> None:
        if not self.undo_stack:
            return
        self.redo_stack.append(self.diagram.to_dict())
        snapshot = self.undo_stack.pop()
        self._restoring = True
        self.load_diagram(Diagram.from_dict(snapshot), reset_history=False)
        self._restoring = False
        self._emit_changed()

    def redo(self) -> None:
        if not self.redo_stack:
            return
        self.undo_stack.append(self.diagram.to_dict())
        snapshot = self.redo_stack.pop()
        self._restoring = True
        self.load_diagram(Diagram.from_dict(snapshot), reset_history=False)
        self._restoring = False
        self._emit_changed()

    def auto_layout(self, layout_type: str | None = None) -> None:
        self.checkpoint()
        apply_layout(self.diagram, layout_type)
        for node in self.diagram.nodes:
            self.node_items[node.id].setPos(node.x, node.y)
        for edge in self.edge_items.values():
            edge.update_path()
        self._emit_changed()

    def align_selected(self, axis: str, mode: str) -> None:
        items = [item for item in self.selectedItems() if isinstance(item, NodeItem)]
        if len(items) < 2:
            return
        self.checkpoint()
        if axis == "x":
            values = [item.x() for item in items]
            target = min(values) if mode == "min" else max(values) if mode == "max" else sum(values) / len(values)
            for item in items:
                item.setX(target)
        else:
            values = [item.y() for item in items]
            target = min(values) if mode == "min" else max(values) if mode == "max" else sum(values) / len(values)
            for item in items:
                item.setY(target)
        self._emit_changed()

    def distribute_selected(self, horizontal: bool = True) -> None:
        items = [item for item in self.selectedItems() if isinstance(item, NodeItem)]
        if len(items) < 3:
            return
        self.checkpoint()
        items.sort(key=lambda item: item.x() if horizontal else item.y())
        start = items[0].x() if horizontal else items[0].y()
        end = items[-1].x() if horizontal else items[-1].y()
        step = (end - start) / (len(items) - 1)
        for index, item in enumerate(items):
            if horizontal:
                item.setX(start + index * step)
            else:
                item.setY(start + index * step)
        self._emit_changed()

    def set_display_option(self, key: str, value: bool) -> None:
        self.diagram.canvas[key] = bool(value)
        for edge in self.edge_items.values():
            edge.update_path()
        self._emit_changed()
