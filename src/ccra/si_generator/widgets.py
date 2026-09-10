from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .docx_export import export_docx
from .models import SIDocument, TableData, recalculate_relative_derived
from .storage import SIDocumentStore


class TableEditor(QWidget):
    def __init__(self, dynamic_columns: bool = False, protected_tail: int = 0, parent=None):
        super().__init__(parent)
        self.dynamic_columns = dynamic_columns
        self.protected_tail = protected_tail
        self.table = QTableWidget(0, 0)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        add_row = QPushButton("+ Structure")
        remove_row = QPushButton("선택 행 삭제")
        add_row.clicked.connect(self.add_row)
        remove_row.clicked.connect(self.remove_selected_rows)
        bar.addWidget(add_row)
        bar.addWidget(remove_row)
        if dynamic_columns:
            add_col = QPushButton("+ Column")
            add_col.clicked.connect(self.add_column)
            bar.addWidget(add_col)
        bar.addStretch()
        layout.addLayout(bar)
        layout.addWidget(self.table)

    def load(self, data: TableData) -> None:
        self.table.blockSignals(True)
        self.table.clear()
        self.table.setColumnCount(len(data.headers))
        self.table.setHorizontalHeaderLabels(data.headers)
        self.table.setRowCount(len(data.rows))
        for r, row in enumerate(data.normalized_rows()):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(value))
        self.table.blockSignals(False)
        self.table.resizeColumnsToContents()

    def dump(self) -> TableData:
        headers = [self.table.horizontalHeaderItem(c).text() if self.table.horizontalHeaderItem(c) else "" for c in range(self.table.columnCount())]
        rows = []
        for r in range(self.table.rowCount()):
            rows.append([self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())])
        return TableData(headers=headers, rows=rows)

    def add_row(self) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c in range(self.table.columnCount()):
            self.table.setItem(r, c, QTableWidgetItem(""))
        self.table.setCurrentCell(r, 0)

    def remove_selected_rows(self) -> None:
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def add_column(self) -> None:
        if not self.dynamic_columns:
            return
        from PySide6.QtWidgets import QInputDialog
        label, ok = QInputDialog.getText(self, "Column", "Column label")
        if not ok or not label.strip():
            return
        insert_at = max(1, self.table.columnCount() - self.protected_tail)
        self.table.insertColumn(insert_at)
        self.table.setHorizontalHeaderItem(insert_at, QTableWidgetItem(label.strip()))
        for r in range(self.table.rowCount()):
            self.table.setItem(r, insert_at, QTableWidgetItem(""))


class SIGeneratorWidget(QWidget):
    """Project-scoped SI table/document editor with local JSON and DOCX export."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = SIDocumentStore()
        self.project = None
        self.current = SIDocument(project_key="")
        self._loading = False
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.document_combo = QComboBox()
        self.module_combo = QComboBox()
        self.name_edit = QLineEdit()
        self.mechanism_edit = QLineEdit()
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.0, 5000.0)
        self.temperature.setDecimals(2)
        self.temperature.setValue(298.15)
        for label, widget in [("SI document", self.document_combo), ("Module", self.module_combo), ("Name", self.name_edit), ("Mechanism", self.mechanism_edit), ("T / K", self.temperature)]:
            top.addWidget(QLabel(label))
            top.addWidget(widget)
        root.addLayout(top)

        actions = QHBoxLayout()
        specs = [
            ("New", self.new_document), ("Save local", self.save_local), ("Delete", self.delete_local),
            ("Recalculate", self.recalculate), ("Export DOCX", self.export_docx_dialog),
            ("Export JSON", self.export_json_dialog), ("Import JSON", self.import_json_dialog),
            ("Drive connect/save", self.save_drive), ("Drive load", self.load_drive),
        ]
        for text, slot in specs:
            b = QPushButton(text)
            b.clicked.connect(slot)
            actions.addWidget(b)
        actions.addStretch()
        root.addLayout(actions)

        self.tabs = QTabWidget()
        self.absolute = TableEditor()
        self.relative = TableEditor()
        self.spin = TableEditor(dynamic_columns=True, protected_tail=2)
        self.geometry = TableEditor(dynamic_columns=True)
        self.notes = QTextEdit()
        self.tabs.addTab(self.absolute, "Absolute Energy")
        self.tabs.addTab(self.relative, "Relative Energy")
        self.tabs.addTab(self.spin, "Spin Density")
        self.tabs.addTab(self.geometry, "Geometry")
        self.tabs.addTab(self.notes, "Notes")
        root.addWidget(self.tabs)
        self.status = QLabel("Ready")
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.status)
        self.document_combo.currentIndexChanged.connect(self._document_changed)

    def set_project(self, project) -> None:
        if self.project is not None and self.current.project_key:
            self._capture()
        self.project = project
        self.module_combo.clear()
        self.module_combo.addItems(project.modules or ["General"])
        self._refresh_documents()

    def _capture(self) -> None:
        if self._loading:
            return
        self.current.module_name = self.module_combo.currentText() or "General"
        self.current.name = self.name_edit.text().strip() or "SI document"
        self.current.mechanism_name = self.mechanism_edit.text().strip()
        self.current.temperature_k = self.temperature.value()
        self.current.absolute = self.absolute.dump()
        self.current.relative = self.relative.dump()
        self.current.spin_density = self.spin.dump()
        self.current.geometry = self.geometry.dump()
        self.current.notes = self.notes.toPlainText()

    def _load(self, document: SIDocument) -> None:
        self._loading = True
        try:
            self.current = document
            self.module_combo.setCurrentText(document.module_name)
            self.name_edit.setText(document.name)
            self.mechanism_edit.setText(document.mechanism_name)
            self.temperature.setValue(document.temperature_k)
            self.absolute.load(document.absolute)
            self.relative.load(document.relative)
            self.spin.load(document.spin_density)
            self.geometry.load(document.geometry)
            self.notes.setPlainText(document.notes)
        finally:
            self._loading = False

    def _refresh_documents(self, selected_id: str | None = None) -> None:
        self.document_combo.blockSignals(True)
        self.document_combo.clear()
        docs = self.store.list(self.project.key) if self.project else []
        for d in docs:
            self.document_combo.addItem(f"{d.module_name} / {d.name}", d.id)
        self.document_combo.blockSignals(False)
        if docs:
            idx = next((i for i, d in enumerate(docs) if d.id == selected_id), 0)
            self.document_combo.setCurrentIndex(idx)
            self._load(docs[idx])
        elif self.project:
            self._load(SIDocument(project_key=self.project.key, module_name=self.project.modules[0] if self.project.modules else "General"))

    def _document_changed(self, index: int) -> None:
        if index < 0 or not self.project:
            return
        document_id = self.document_combo.itemData(index)
        if document_id:
            self._load(self.store.load(self.project.key, document_id))

    def new_document(self) -> None:
        if not self.project:
            return
        self._load(SIDocument(project_key=self.project.key, module_name=self.module_combo.currentText() or "General"))
        self.status.setText("New SI document")

    def save_local(self) -> None:
        if not self.project:
            return
        self._capture()
        self.store.save(self.current)
        self._refresh_documents(self.current.id)
        self.status.setText("Saved locally")

    def delete_local(self) -> None:
        if not self.project or not self.current.id:
            return
        if QMessageBox.question(self, "Delete", "Delete current local SI document?") != QMessageBox.StandardButton.Yes:
            return
        self.store.delete(self.current)
        self._refresh_documents()
        self.status.setText("Deleted")

    def recalculate(self) -> None:
        self._capture()
        recalculate_relative_derived(self.current.relative)
        self.relative.load(self.current.relative)
        self.status.setText("ΔE Total / ΔG recalculated")

    def export_docx_dialog(self) -> None:
        self._capture()
        path, _ = QFileDialog.getSaveFileName(self, "Export SI DOCX", f"{self.current.name}.docx", "Word (*.docx)")
        if path:
            export_docx(self.current, Path(path))
            self.status.setText(path)

    def export_json_dialog(self) -> None:
        self._capture()
        path, _ = QFileDialog.getSaveFileName(self, "Export SI JSON", f"{self.current.name}.json", "JSON (*.json)")
        if path:
            self.store.export_json(self.current, Path(path))
            self.status.setText(path)

    def import_json_dialog(self) -> None:
        if not self.project:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Import SI JSON", "", "JSON (*.json)")
        if path:
            doc = self.store.import_json(Path(path), self.project.key)
            self._refresh_documents(doc.id)
            self.status.setText("Imported JSON")

    def _drive_client(self):
        from ccra.google_drive import GoogleDriveClient
        candidates = [Path.cwd() / "credentials.json", Path.home() / ".ccra" / "credentials.json"]
        credentials = next((p for p in candidates if p.exists()), None)
        if credentials is None:
            raise RuntimeError("credentials.json not found in current directory or ~/.ccra")
        client = GoogleDriveClient(credentials, Path.home() / ".ccra" / "token.json")
        client.connect()
        return client

    def save_drive(self) -> None:
        if not self.project:
            return
        try:
            self._capture()
            client = self._drive_client()
            payload = json.dumps(self.current.to_dict(), ensure_ascii=False, indent=2)
            name = f"CCRA-SI-{self.current.id}.json"
            self.current.drive_file_id = client.upload_text(self.project.drive_folder_id, name, payload, file_id=self.current.drive_file_id)
            self.store.save(self.current)
            self._refresh_documents(self.current.id)
            self.status.setText("Saved to project Google Drive")
        except Exception as exc:
            QMessageBox.warning(self, "Google Drive", str(exc))

    def load_drive(self) -> None:
        if not self.project:
            return
        try:
            from PySide6.QtWidgets import QInputDialog
            client = self._drive_client()
            files = client.si_json_files(self.project.drive_folder_id)
            if not files:
                QMessageBox.information(self, "Google Drive", "No CCRA SI documents in this project folder.")
                return
            labels = [f"{f['name']}  |  {f.get('modifiedTime','')}" for f in files]
            choice, ok = QInputDialog.getItem(self, "Google Drive", "SI document", labels, 0, False)
            if not ok:
                return
            file = files[labels.index(choice)]
            data = json.loads(client.download_text(file["id"]))
            doc = SIDocument.from_dict(data, project_key=self.project.key)
            doc.drive_file_id = file["id"]
            self.store.save(doc)
            self._refresh_documents(doc.id)
            self.status.setText("Loaded from project Google Drive")
        except Exception as exc:
            QMessageBox.warning(self, "Google Drive", str(exc))
