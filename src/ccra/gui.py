from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .app_service import AppService
from .reaction_coordinate.widgets import ReactionCoordinateWidget
from .si_generator.widgets import SIGeneratorWidget


class ImportWorker(QThread):
    done = Signal(dict)

    def __init__(self, service, project_key, paths):
        super().__init__()
        self.service = service
        self.project_key = project_key
        self.paths = paths

    def run(self):
        self.done.emit(self.service.import_outputs(self.project_key, self.paths))


class MainWindow(QMainWindow):
    def __init__(self, service: AppService):
        super().__init__()
        self.service = service
        self.current_project = None
        self.setWindowTitle("Computational Chemistry Report Assistant")
        self.resize(1450, 900)
        self.setAcceptDrops(True)
        self._build()

    def _build(self):
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Projects")
        for project in self.service.registry.all():
            item = QTreeWidgetItem([project.title])
            item.setData(0, Qt.UserRole, project.key)
            self.project_tree.addTopLevelItem(item)
            for module in project.modules:
                child = QTreeWidgetItem([module])
                child.setFlags(child.flags() & ~Qt.ItemIsSelectable)
                item.addChild(child)
        self.project_tree.itemSelectionChanged.connect(self._project_changed)

        self.tabs = QTabWidget()
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.files = QTableWidget(0, 7)
        self.files.setHorizontalHeaderLabels(["ID", "File", "OK", "Charge", "Mult", "Method/Basis", "Energy (Eh)"])
        self.raw = QTextEdit(); self.raw.setReadOnly(True)
        self.drive = QTextEdit(); self.drive.setReadOnly(True)
        self.sheets = QTextEdit(); self.sheets.setReadOnly(True)
        self.reaction_coordinate = ReactionCoordinateWidget(self.service.database)
        self.si_generator = SIGeneratorWidget()

        for name, widget in [
            ("Summary", self.summary),
            ("Files", self.files),
            ("Raw Data", self.raw),
            ("Drive", self.drive),
            ("Sheets", self.sheets),
            ("Reaction Coordinate", self.reaction_coordinate),
            ("SI Generator", self.si_generator),
            ("Energy", QTextEdit()),
            ("Spin Density", QTextEdit()),
            ("Geometry", QTextEdit()),
            ("TD-DFT / Frequency", QTextEdit()),
            ("Future Work", QTextEdit()),
        ]:
            self.tabs.addTab(widget, name)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(130)

        center = QWidget()
        layout = QVBoxLayout(center)
        bar = QHBoxLayout()
        self.import_btn = QPushButton("Import Gaussian Outputs")
        self.open_drive_btn = QPushButton("Open Project Drive")
        self.open_sheet_btn = QPushButton("Open Google Sheet")
        for button in [self.import_btn, self.open_drive_btn, self.open_sheet_btn]:
            bar.addWidget(button)
        bar.addStretch()
        layout.addLayout(bar)
        layout.addWidget(self.tabs)
        layout.addWidget(self.console)

        splitter = QSplitter()
        splitter.addWidget(self.project_tree)
        splitter.addWidget(center)
        splitter.setSizes([260, 1190])
        self.setCentralWidget(splitter)

        self.import_btn.clicked.connect(self._choose_outputs)
        self.open_drive_btn.clicked.connect(lambda: self._open_url("drive"))
        self.open_sheet_btn.clicked.connect(lambda: self._open_url("sheet"))

    def _project_changed(self):
        items = self.project_tree.selectedItems()
        if not items or items[0].parent() is not None:
            return
        self.current_project = self.service.registry.get(items[0].data(0, Qt.UserRole))
        project = self.current_project
        self.summary.setPlainText(
            f"{project.title}\n\nProject key: {project.key}\nDrive folder: {project.drive_folder_title}\n"
            f"Google Sheet: {project.sheet.title}\nModules: {', '.join(project.modules)}"
        )
        self.drive.setPlainText(project.drive_url)
        self.sheets.setPlainText(project.sheet.url + "\n\nTabs:\n" + "\n".join(f"• {x}" for x in project.sheet.sheet_names))
        self.reaction_coordinate.set_project(project.key, project.modules)
        self.si_generator.set_project(project)
        self._refresh_files()

    def _refresh_files(self):
        if not self.current_project:
            return
        rows = self.service.database.list_gaussian_files(self.current_project.key)
        self.files.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [
                row["id"], row["filename"], "YES" if row["normal_termination"] else "NO",
                row["charge"], row["multiplicity"], row["method_basis"], row["electronic_energy_hartree"],
            ]
            for c, value in enumerate(values):
                self.files.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))
        self.files.resizeColumnsToContents()
        self.reaction_coordinate._refresh_file_combo()

    def _choose_outputs(self):
        if not self.current_project:
            QMessageBox.information(self, "Project required", "Select a project first.")
            return
        names, _ = QFileDialog.getOpenFileNames(self, "Import Gaussian outputs", "", "Gaussian Output (*.out *.log);;All files (*)")
        if names:
            self._start_import([Path(x) for x in names])

    def _start_import(self, paths):
        self.worker = ImportWorker(self.service, self.current_project.key, paths)
        self.worker.done.connect(self._import_done)
        self.worker.start()

    def _import_done(self, stats):
        self.console.append(f"{self.current_project.title}: {stats}")
        self._refresh_files()

    def _open_url(self, which):
        if not self.current_project:
            return
        import webbrowser
        webbrowser.open(self.current_project.drive_url if which == "drive" else self.current_project.sheet.url)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and self.current_project:
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
            if Path(url.toLocalFile()).suffix.lower() in {".out", ".log"}
        ]
        if paths:
            self._start_import(paths)
