from __future__ import annotations
import json
from pathlib import Path
from .models import ProjectDefinition, SheetBinding

class ProjectRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self._projects: dict[str, ProjectDefinition] = {}
        self.reload()

    def reload(self) -> None:
        projects: dict[str, ProjectDefinition] = {}
        for path in sorted(self.config_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            sheet = SheetBinding(title=data["sheet"]["title"], spreadsheet_id=data["sheet"]["spreadsheet_id"], sheet_names=data["sheet"].get("sheet_names", []))
            project = ProjectDefinition(key=data["key"], title=data["title"], drive_folder_id=data["drive_folder_id"], drive_folder_title=data["drive_folder_title"], sheet=sheet, aliases=data.get("aliases", []), modules=data.get("modules", []))
            if project.key in projects:
                raise ValueError(f"Duplicate project key: {project.key}")
            projects[project.key] = project
        self._projects = projects

    def all(self) -> list[ProjectDefinition]:
        return list(self._projects.values())

    def get(self, key: str) -> ProjectDefinition:
        return self._projects[key]

    def match_filename(self, filename: str) -> ProjectDefinition | None:
        lowered = filename.lower()
        candidates: list[tuple[int, ProjectDefinition]] = []
        for project in self._projects.values():
            for alias in [project.key, project.title, *project.aliases]:
                if alias.lower() in lowered:
                    candidates.append((len(alias), project))
        return max(candidates, default=(0, None), key=lambda x: x[0])[1]
