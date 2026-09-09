from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .controller import ReactionCoordinateController
from .exporters import copy_as_image, export_png, export_svg
from .items import EdgeItem, NodeItem
from .models import Diagram
from .scene import ReactionScene


class CanvasView(QGraphicsView):
    def __init__(self, scene: ReactionScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setBackgroundBrush(Qt.GlobalColor.white)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def fit_all(self):
        rect = self.scene().itemsBoundingRect().adjusted(-80, -80, 80, 80)
        if not rect.isEmpty():
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)


class ReactionCoordinateWidget(QWidget):
    """Project-scoped, direct-manipulation reaction-coordinate editor."""

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.controller = ReactionCoordinateController(database)
        self.project_key = ""
        self.project_modules: list[str] = []
        self.current: Diagram = Diagram()
        self.scene = ReactionScene(self.current)
        self.view = CanvasView(self.scene)
        self._updating_properties = False
        self._build_ui()
        self.scene.selectionChanged.connect(self._selection_changed)
        self.scene.model_changed.connect(self._model_changed)

    def _build_ui(self):
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.diagram_combo = QComboBox()
        self.diagram_combo.setMinimumWidth(220)
        self.module_combo = QComboBox()
        self.module_combo.setMinimumWidth(180)
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["chain", "circular", "branched", "freeform"])
        self.new_btn = QPushButton("새 그래프")
        self.template_btn = QToolButton()
        self.template_btn.setText("템플릿")
        self.template_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        template_menu = QMenu(self)
        for title, key in [("Linear pathway", "linear"), ("Circular mechanism", "circular"), ("Branched pathway", "branched"), ("Rebound / radical coupling", "two-branch")]:
            action = template_menu.addAction(title)
            action.triggered.connect(lambda _checked=False, template=key: self._new_from_template(template))
        self.template_btn.setMenu(template_menu)
        self.save_btn = QPushButton("저장")
        self.delete_diagram_btn = QPushButton("그래프 삭제")
        for label, widget in [("그래프", self.diagram_combo), ("모듈", self.module_combo), ("배치", self.layout_combo)]:
            top.addWidget(QLabel(label))
            top.addWidget(widget)
        top.addWidget(self.new_btn)
        top.addWidget(self.template_btn)
        top.addWidget(self.save_btn)
        top.addWidget(self.delete_diagram_btn)
        top.addStretch()
        root.addLayout(top)

        tools = QHBoxLayout()
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        for title, mode in [("선택", "select"), ("노드", "node"), ("TS", "ts"), ("연결", "edge")]:
            button = QPushButton(title)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, m=mode: self.scene.set_mode(m))
            self.tool_group.addButton(button)
            tools.addWidget(button)
            if mode == "select":
                button.setChecked(True)
        actions = [
            ("실행취소", self.scene.undo), ("다시실행", self.scene.redo), ("삭제", self.scene.delete_selected),
            ("복제", self.scene.duplicate_selected), ("자동배치", self._auto_layout), ("전체보기", self.view.fit_all),
        ]
        for title, slot in actions:
            button = QPushButton(title)
            button.clicked.connect(slot)
            tools.addWidget(button)
        align = QToolButton()
        align.setText("정렬")
        align.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self)
        specs = [
            ("왼쪽 맞춤", "x", "min"), ("가운데(세로축)", "x", "center"), ("오른쪽 맞춤", "x", "max"),
            ("위쪽 맞춤", "y", "min"), ("가운데(가로축)", "y", "center"), ("아래쪽 맞춤", "y", "max"),
        ]
        for title, axis, mode in specs:
            act = menu.addAction(title)
            act.triggered.connect(lambda _checked=False, a=axis, m=mode: self.scene.align_selected(a, m))
        menu.addSeparator()
        menu.addAction("가로 균등분배").triggered.connect(lambda: self.scene.distribute_selected(True))
        menu.addAction("세로 균등분배").triggered.connect(lambda: self.scene.distribute_selected(False))
        align.setMenu(menu)
        tools.addWidget(align)
        self.grid_check = QCheckBox("Grid snap")
        self.grid_check.toggled.connect(lambda value: self.scene.set_display_option("snap_to_grid", value))
        tools.addWidget(self.grid_check)
        tools.addStretch()
        self.png_btn = QPushButton("PNG")
        self.svg_btn = QPushButton("SVG")
        self.copy_image_btn = QPushButton("이미지 복사")
        self.json_btn = QPushButton("JSON")
        self.import_json_btn = QPushButton("JSON 불러오기")
        for button in [self.png_btn, self.svg_btn, self.copy_image_btn, self.json_btn, self.import_json_btn]:
            tools.addWidget(button)
        root.addLayout(tools)

        display = QHBoxLayout()
        display.addWidget(QLabel("표시:"))
        self.display_checks: dict[str, QCheckBox] = {}
        for title, key in [("에너지", "show_energy"), ("Local barrier", "show_barrier"), ("Spin/Multiplicity", "show_spin_multiplicity"), ("Subtitle", "show_subtitle"), ("Edge label", "show_edge_label"), ("화살표", "show_arrows"), ("연결선 곡선", "force_curved")]:
            check = QCheckBox(title)
            check.setChecked(key != "force_curved")
            check.toggled.connect(lambda value, k=key: self.scene.set_display_option(k, value))
            self.display_checks[key] = check
            display.addWidget(check)
        display.addStretch()
        root.addLayout(display)

        splitter = QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(self._make_property_panel())
        splitter.setSizes([1000, 300])
        root.addWidget(splitter, 1)

        self.diagram_combo.currentIndexChanged.connect(self._diagram_changed)
        self.layout_combo.currentTextChanged.connect(self._layout_changed)
        self.new_btn.clicked.connect(self._new_blank)
        self.save_btn.clicked.connect(self.save)
        self.delete_diagram_btn.clicked.connect(self._delete_diagram)
        self.png_btn.clicked.connect(self._export_png)
        self.svg_btn.clicked.connect(self._export_svg)
        self.copy_image_btn.clicked.connect(lambda: copy_as_image(self.scene))
        self.json_btn.clicked.connect(self._export_json)
        self.import_json_btn.clicked.connect(self._import_json)
        self._install_shortcuts()

    def _make_property_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("선택 항목 속성"))
        self.property_stack = QStackedWidget()
        self.empty_page = QLabel("노드 또는 연결선을 선택하세요.\n\n빈 공간을 더블클릭하면 노드가 추가됩니다.")
        self.empty_page.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.property_stack.addWidget(self.empty_page)

        node_page = QWidget()
        form = QFormLayout(node_page)
        self.node_label = QLineEdit()
        self.node_type = QComboBox(); self.node_type.addItems(["reactant", "intermediate", "transition_state", "product", "annotation"])
        self.energy = QDoubleSpinBox(); self.energy.setRange(-1000000, 1000000); self.energy.setDecimals(6); self.energy.setSpecialValueText("미입력")
        self.energy_unit = QComboBox(); self.energy_unit.addItems(["kcal/mol", "kJ/mol", "eV", "Eh"])
        self.spin = QLineEdit()
        self.multiplicity = QSpinBox(); self.multiplicity.setRange(0, 20); self.multiplicity.setSpecialValueText("미입력")
        self.subtitle = QLineEdit()
        self.notes = QTextEdit(); self.notes.setMaximumHeight(85)
        self.shape = QComboBox(); self.shape.addItems(["level", "annotation"])
        self.file_combo = QComboBox()
        self.file_combo.addItem("Gaussian file 연결 안 함", None)
        self.raw_energy_label = QLabel("-")
        self.link_file_btn = QPushButton("선택 파일 연결")
        self.apply_raw_btn = QPushButton("Raw Eh를 energy에 적용")
        for label, widget in [("Label", self.node_label), ("Type", self.node_type), ("Energy", self.energy), ("Unit", self.energy_unit), ("Spin", self.spin), ("Multiplicity", self.multiplicity), ("Subtitle", self.subtitle), ("Shape", self.shape), ("Gaussian file", self.file_combo), ("Linked raw energy", self.raw_energy_label), ("Notes", self.notes)]:
            form.addRow(label, widget)
        form.addRow(self.link_file_btn)
        form.addRow(self.apply_raw_btn)
        self.property_stack.addWidget(node_page)

        edge_page = QWidget()
        edge_form = QFormLayout(edge_page)
        self.edge_type = QComboBox(); self.edge_type.addItems(["normal", "curved", "dashed", "reversible", "no-arrow"])
        self.edge_label = QLineEdit()
        self.edge_barrier = QDoubleSpinBox(); self.edge_barrier.setRange(-1000000, 1000000); self.edge_barrier.setDecimals(4); self.edge_barrier.setSpecialValueText("미입력")
        edge_form.addRow("Type", self.edge_type)
        edge_form.addRow("Label", self.edge_label)
        edge_form.addRow("Barrier", self.edge_barrier)
        self.property_stack.addWidget(edge_page)
        layout.addWidget(self.property_stack)
        layout.addStretch()

        for widget in [self.node_label, self.spin, self.subtitle]:
            widget.editingFinished.connect(self._apply_node_properties)
        for widget in [self.node_type, self.energy_unit, self.shape]:
            widget.currentTextChanged.connect(lambda _value: self._apply_node_properties())
        self.energy.editingFinished.connect(self._apply_node_properties)
        self.multiplicity.editingFinished.connect(self._apply_node_properties)
        self.notes.textChanged.connect(self._apply_node_properties)
        self.link_file_btn.clicked.connect(lambda: self._link_file(False))
        self.apply_raw_btn.clicked.connect(lambda: self._link_file(True))
        self.edge_type.currentTextChanged.connect(lambda _value: self._apply_edge_properties())
        self.edge_label.editingFinished.connect(self._apply_edge_properties)
        self.edge_barrier.editingFinished.connect(self._apply_edge_properties)
        return panel

    def _install_shortcuts(self):
        for shortcut, slot in [(QKeySequence.StandardKey.Undo, self.scene.undo), (QKeySequence.StandardKey.Redo, self.scene.redo), (QKeySequence.StandardKey.Copy, self.scene.copy_selected), (QKeySequence.StandardKey.Paste, self.scene.paste), (QKeySequence.StandardKey.Delete, self.scene.delete_selected)]:
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            self.addAction(action)

    def set_project(self, project_key: str, modules: list[str]) -> None:
        if self.project_key and self.current.project_key == self.project_key and self.current.nodes:
            self.save(silent=True)
        self.project_key = project_key
        self.project_modules = list(modules)
        self.module_combo.clear()
        self.module_combo.addItems(self.project_modules or ["General"])
        self._refresh_file_combo()
        self._refresh_diagram_combo()

    def _refresh_file_combo(self):
        self.file_combo.clear()
        self.file_combo.addItem("Gaussian file 연결 안 함", None)
        if not self.project_key:
            return
        for row in self.controller.gaussian_files(self.project_key):
            energy = row.get("electronic_energy_hartree")
            suffix = "" if energy is None else f"  |  {energy:.8f} Eh"
            self.file_combo.addItem(f"{row['filename']}{suffix}", row)

    def _refresh_diagram_combo(self, select_id: str | None = None):
        self.diagram_combo.blockSignals(True)
        self.diagram_combo.clear()
        diagrams = self.controller.list_diagrams(self.project_key) if self.project_key else []
        for diagram in diagrams:
            self.diagram_combo.addItem(f"{diagram.module_name} / {diagram.name}", diagram.id)
        self.diagram_combo.blockSignals(False)
        if diagrams:
            index = next((i for i, d in enumerate(diagrams) if d.id == select_id), 0)
            self.diagram_combo.setCurrentIndex(index)
            self._load(diagrams[index])
        else:
            module = self.project_modules[0] if self.project_modules else "General"
            self._load(self.controller.new_diagram(self.project_key, module, layout_type="chain"))

    def _load(self, diagram: Diagram):
        self.current = diagram
        self.scene.load_diagram(diagram)
        self.layout_combo.blockSignals(True); self.layout_combo.setCurrentText(diagram.layout_type); self.layout_combo.blockSignals(False)
        self.module_combo.setCurrentText(diagram.module_name)
        self.grid_check.setChecked(bool(diagram.canvas.get("snap_to_grid", False)))
        for key, check in self.display_checks.items():
            check.blockSignals(True); check.setChecked(bool(diagram.canvas.get(key, key != "force_curved"))); check.blockSignals(False)
        self.view.fit_all()

    def _diagram_changed(self, index: int):
        if index < 0 or not self.project_key:
            return
        diagram_id = self.diagram_combo.itemData(index)
        if diagram_id:
            self._load(self.controller.store.load(self.project_key, diagram_id))

    def _new_blank(self):
        if not self.project_key:
            return
        name, ok = QInputDialog.getText(self, "새 Reaction Coordinate", "그래프 이름", text="New pathway")
        if not ok:
            return
        module = self.module_combo.currentText() or "General"
        diagram = self.controller.new_diagram(self.project_key, module, layout_type=self.layout_combo.currentText())
        diagram.name = name.strip() or "New pathway"
        self.controller.save(diagram)
        self._refresh_diagram_combo(diagram.id)

    def _new_from_template(self, template: str):
        if not self.project_key:
            return
        module = self.module_combo.currentText() or "General"
        diagram = self.controller.new_diagram(self.project_key, module, template=template)
        self.controller.save(diagram)
        self._refresh_diagram_combo(diagram.id)

    def save(self, silent: bool = False):
        if not self.project_key:
            return
        self.current.project_key = self.project_key
        self.current.module_name = self.module_combo.currentText() or "General"
        self.current.layout_type = self.layout_combo.currentText()
        self.controller.save(self.current)
        if not silent:
            self._refresh_diagram_combo(self.current.id)

    def _delete_diagram(self):
        if not self.current.id or not self.project_key:
            return
        if QMessageBox.question(self, "그래프 삭제", f"'{self.current.name}'을 삭제할까요?") != QMessageBox.StandardButton.Yes:
            return
        self.controller.delete(self.current)
        self._refresh_diagram_combo()

    def _layout_changed(self, value: str):
        if self._updating_properties:
            return
        self.current.layout_type = value

    def _auto_layout(self):
        self.scene.auto_layout(self.layout_combo.currentText())
        self.view.fit_all()

    def _selected_item(self):
        items = self.scene.selectedItems()
        return items[0] if len(items) == 1 else None

    def _selection_changed(self):
        item = self._selected_item()
        self._updating_properties = True
        try:
            if isinstance(item, NodeItem):
                node = item.node
                self.property_stack.setCurrentIndex(1)
                self.node_label.setText(node.label)
                self.node_type.setCurrentText(node.node_type)
                self.energy.setValue(0.0 if node.energy is None else node.energy)
                self.energy_unit.setCurrentText(node.energy_unit)
                self.spin.setText(node.spin)
                self.multiplicity.setValue(0 if node.multiplicity is None else node.multiplicity)
                self.subtitle.setText(node.subtitle)
                self.notes.setPlainText(node.notes)
                self.shape.setCurrentText(node.shape)
                row_index = next((i for i in range(self.file_combo.count()) if isinstance(self.file_combo.itemData(i), dict) and self.file_combo.itemData(i).get("id") == node.linked_file_id), 0)
                self.file_combo.setCurrentIndex(row_index)
                self.raw_energy_label.setText("-" if node.linked_electronic_energy_hartree is None else f"{node.linked_electronic_energy_hartree:.10f} Eh")
            elif isinstance(item, EdgeItem):
                self.property_stack.setCurrentIndex(2)
                self.edge_type.setCurrentText(item.edge.edge_type)
                self.edge_label.setText(item.edge.label)
                self.edge_barrier.setValue(0.0 if item.edge.barrier is None else item.edge.barrier)
            else:
                self.property_stack.setCurrentIndex(0)
        finally:
            self._updating_properties = False

    def _apply_node_properties(self):
        if self._updating_properties:
            return
        item = self._selected_item()
        if not isinstance(item, NodeItem):
            return
        self.scene.checkpoint()
        node = item.node
        node.label = self.node_label.text().strip() or node.label
        node.node_type = self.node_type.currentText()
        node.energy = float(self.energy.value())
        node.energy_unit = self.energy_unit.currentText()
        node.spin = self.spin.text().strip()
        node.multiplicity = self.multiplicity.value() or None
        node.subtitle = self.subtitle.text().strip()
        node.notes = self.notes.toPlainText()
        node.shape = self.shape.currentText()
        item.update()
        self.scene._emit_changed()

    def _apply_edge_properties(self):
        if self._updating_properties:
            return
        item = self._selected_item()
        if not isinstance(item, EdgeItem):
            return
        self.scene.checkpoint()
        item.edge.edge_type = self.edge_type.currentText()
        item.edge.label = self.edge_label.text().strip()
        item.edge.barrier = float(self.edge_barrier.value())
        item.update_path(); item.update(); self.scene._emit_changed()

    def _link_file(self, apply_raw: bool):
        item = self._selected_item()
        row = self.file_combo.currentData()
        if not isinstance(item, NodeItem) or not isinstance(row, dict):
            return
        self.scene.checkpoint()
        self.controller.link_node_to_file(self.current, item.node.id, row, apply_raw)
        item.update(); self._selection_changed(); self.scene._emit_changed()

    def _model_changed(self):
        self.current = self.scene.diagram

    def _export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "PNG 저장", f"{self.current.name}.png", "PNG (*.png)")
        if path:
            export_png(self.scene, Path(path))

    def _export_svg(self):
        path, _ = QFileDialog.getSaveFileName(self, "SVG 저장", f"{self.current.name}.svg", "SVG (*.svg)")
        if path:
            export_svg(self.scene, Path(path))

    def _export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "JSON 저장", f"{self.current.name}.json", "JSON (*.json)")
        if path:
            self.controller.store.export_json(self.current, Path(path))

    def _import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Reaction Coordinate JSON 불러오기", "", "JSON (*.json)")
        if path and self.project_key:
            diagram = self.controller.store.import_json(Path(path), self.project_key)
            self._refresh_diagram_combo(diagram.id)
