from __future__ import annotations

import json
from pathlib import Path

from .models import SIDocument


class SIDocumentStore:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else Path.home() / ".ccra" / "si_documents"
        self.root.mkdir(parents=True, exist_ok=True)

    def _project_dir(self, project_key: str) -> Path:
        path = self.root / project_key
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, document: SIDocument) -> Path:
        document.touch()
        path = self._project_dir(document.project_key) / f"{document.id}.json"
        path.write_text(json.dumps(document.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load(self, project_key: str, document_id: str) -> SIDocument:
        path = self._project_dir(project_key) / f"{document_id}.json"
        return SIDocument.from_dict(json.loads(path.read_text(encoding="utf-8")), project_key=project_key)

    def list(self, project_key: str) -> list[SIDocument]:
        documents: list[SIDocument] = []
        for path in self._project_dir(project_key).glob("*.json"):
            try:
                documents.append(SIDocument.from_dict(json.loads(path.read_text(encoding="utf-8")), project_key=project_key))
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                continue
        return sorted(documents, key=lambda d: d.updated_at, reverse=True)

    def delete(self, document: SIDocument) -> None:
        path = self._project_dir(document.project_key) / f"{document.id}.json"
        if path.exists():
            path.unlink()

    def export_json(self, document: SIDocument, target: Path) -> Path:
        target = Path(target)
        target.write_text(json.dumps(document.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def import_json(self, source: Path, project_key: str) -> SIDocument:
        document = SIDocument.from_dict(json.loads(Path(source).read_text(encoding="utf-8")), project_key=project_key)
        document.drive_file_id = None
        self.save(document)
        return document
