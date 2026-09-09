from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class SheetBinding:
    title: str
    spreadsheet_id: str
    sheet_names: list[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit"

@dataclass(slots=True)
class ProjectDefinition:
    key: str
    title: str
    drive_folder_id: str
    drive_folder_title: str
    sheet: SheetBinding
    aliases: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)

    @property
    def drive_url(self) -> str:
        return f"https://drive.google.com/drive/folders/{self.drive_folder_id}"

@dataclass(slots=True)
class GaussianRecord:
    project_key: str
    source_path: Path
    filename: str
    sha256: str
    normal_termination: bool
    charge: int | None
    multiplicity: int | None
    method_basis: str | None
    job_types: list[str]
    electronic_energy_hartree: float | None
    xyz: str | None
    raw_metadata: dict[str, Any] = field(default_factory=dict)
