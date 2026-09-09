from __future__ import annotations

from pathlib import Path

from .models import Diagram
from .storage import DiagramStore
from .templates import blank_template, branched_template, circular_template, linear_template, two_branch_template


class ReactionCoordinateController:
    def __init__(self, database, store: DiagramStore | None = None):
        self.database = database
        self.store = store or DiagramStore(Path.home() / ".ccra" / "reaction_diagrams")

    def list_diagrams(self, project_key: str) -> list[Diagram]:
        return self.store.list(project_key)

    def save(self, diagram: Diagram):
        return self.store.save(diagram)

    def delete(self, diagram: Diagram) -> bool:
        return self.store.delete(diagram.project_key, diagram.id)

    def new_diagram(self, project_key: str, module_name: str, template: str = "blank", layout_type: str = "chain") -> Diagram:
        factories = {
            "linear": linear_template,
            "circular": circular_template,
            "branched": branched_template,
            "two-branch": two_branch_template,
        }
        if template in factories:
            return factories[template](project_key, module_name)
        return blank_template(project_key, module_name, layout_type)

    def gaussian_files(self, project_key: str) -> list[dict]:
        return [dict(row) for row in self.database.list_gaussian_files(project_key)]

    def link_node_to_file(self, diagram: Diagram, node_id: str, file_row: dict, apply_raw_energy: bool = False) -> None:
        node = diagram.node(node_id)
        if node is None:
            raise KeyError(node_id)
        node.linked_file_id = int(file_row["id"])
        node.linked_filename = str(file_row["filename"])
        node.linked_electronic_energy_hartree = file_row.get("electronic_energy_hartree")
        if apply_raw_energy and node.linked_electronic_energy_hartree is not None:
            node.energy = float(node.linked_electronic_energy_hartree)
            node.energy_unit = "Eh"
        diagram.touch()
