import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ccra.reaction_coordinate.exporters import export_png, export_svg
from ccra.reaction_coordinate.lifecycle import detach_reaction_editor
from ccra.reaction_coordinate.storage import DiagramStore
from ccra.reaction_coordinate.widgets import ReactionCoordinateWidget


class FakeDB:
    def list_gaussian_files(self, project_key):
        return []


def test_reaction_editor_constructs_edits_and_exports(tmp_path):
    app = QApplication.instance() or QApplication([])
    widget = ReactionCoordinateWidget(FakeDB())
    widget.controller.store = DiagramStore(tmp_path / "diagrams")
    widget.set_project("feno6", ["Acid-first"])

    a = widget.scene.add_node(180, 300, "intermediate")
    ts = widget.scene.add_node(420, 220, "transition_state")
    edge = widget.scene.add_edge(a.node.id, ts.node.id)

    assert edge is not None
    assert len(widget.scene.diagram.nodes) == 2
    assert len(widget.scene.diagram.edges) == 1

    widget.scene.auto_layout("chain")
    png = export_png(widget.scene, tmp_path / "path.png", scale=1.0)
    svg = export_svg(widget.scene, tmp_path / "path.svg")

    assert png.exists() and png.stat().st_size > 0
    assert svg.exists() and svg.stat().st_size > 0

    detach_reaction_editor(widget)
    widget.close()
    app.processEvents()
