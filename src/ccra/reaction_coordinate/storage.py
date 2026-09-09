from __future__ import annotations

import json
from pathlib import Path

from .models import Diagram


class DiagramStore:
    """Project-scoped JSON persistence. Research data remains local by default."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def project_dir(self, project_key: str) -> Path:
        path = self.root / project_key
        path.mkdir(parents=True, exist_ok=True)
        return path

    def path_for(self, diagram: Diagram) -> Path:
        return self.project_dir(diagram.project_key) / f"{diagram.id}.json"

    def save(self, diagram: Diagram) -> Path:
        if not diagram.project_key:
            raise ValueError("Diagram must belong to a project before saving.")
        diagram.touch()
        path = self.path_for(diagram)
        path.write_text(json.dumps(diagram.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load(self, project_key: str, diagram_id: str) -> Diagram:
        path = self.project_dir(project_key) / f"{diagram_id}.json"
        return Diagram.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self, project_key: str) -> list[Diagram]:
        diagrams: list[Diagram] = []
        for path in self.project_dir(project_key).glob("*.json"):
            try:
                diagrams.append(Diagram.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
        return sorted(diagrams, key=lambda item: item.updated_at, reverse=True)

    def delete(self, project_key: str, diagram_id: str) -> bool:
        path = self.project_dir(project_key) / f"{diagram_id}.json"
        if not path.exists():
            return False
        path.unlink()
        return True

    def export_json(self, diagram: Diagram, destination: Path) -> Path:
        destination = Path(destination)
        destination.write_text(json.dumps(diagram.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return destination

    def import_json(self, source: Path, project_key: str) -> Diagram:
        diagram = Diagram.from_dict(json.loads(Path(source).read_text(encoding="utf-8")))
        diagram.project_key = project_key
        self.save(diagram)
        return diagram
