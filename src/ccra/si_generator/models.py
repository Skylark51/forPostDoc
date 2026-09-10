from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

ABSOLUTE_HEADERS = [
    "Structure",
    "E Def2-SVP",
    "E Def2-TZVPP",
    "Z0",
    "E Thermal",
    "S",
    "Dispersion",
]
RELATIVE_HEADERS = [
    "Structure",
    "ΔE",
    "ΔΔEᵃ",
    "ΔE Total",
    "ΔZ0",
    "ΔΔE Thermalᵇ",
    "-TΔSᵇ",
    "ΔDispersion",
    "ΔComplexation",
    "ΔGᶜ",
]
SPIN_HEADERS = ["Structure", "Rest", "Sum"]
GEOMETRY_HEADERS = ["Structure"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class TableData:
    headers: list[str]
    rows: list[list[str]] = field(default_factory=list)

    def normalized_rows(self) -> list[list[str]]:
        width = len(self.headers)
        return [(list(row) + [""] * width)[:width] for row in self.rows]

    def to_dict(self) -> dict[str, Any]:
        return {"headers": list(self.headers), "rows": self.normalized_rows()}

    @classmethod
    def from_dict(cls, data: dict[str, Any], fallback_headers: list[str]) -> "TableData":
        headers = [str(v) for v in data.get("headers", fallback_headers)] or list(fallback_headers)
        rows = [["" if v is None else str(v) for v in row] for row in data.get("rows", [])]
        return cls(headers=headers, rows=rows)


@dataclass
class SIDocument:
    project_key: str
    module_name: str = "General"
    name: str = "SI document"
    mechanism_name: str = ""
    temperature_k: float = 298.15
    id: str = field(default_factory=lambda: uuid4().hex)
    absolute: TableData = field(default_factory=lambda: TableData(list(ABSOLUTE_HEADERS)))
    relative: TableData = field(default_factory=lambda: TableData(list(RELATIVE_HEADERS)))
    spin_density: TableData = field(default_factory=lambda: TableData(list(SPIN_HEADERS)))
    geometry: TableData = field(default_factory=lambda: TableData(list(GEOMETRY_HEADERS)))
    notes: str = ""
    drive_file_id: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def touch(self) -> None:
        self.updated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "id": self.id,
            "project_key": self.project_key,
            "module_name": self.module_name,
            "name": self.name,
            "mechanism_name": self.mechanism_name,
            "temperature_k": self.temperature_k,
            "absolute": self.absolute.to_dict(),
            "relative": self.relative.to_dict(),
            "spin_density": self.spin_density.to_dict(),
            "geometry": self.geometry.to_dict(),
            "notes": self.notes,
            "drive_file_id": self.drive_file_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], project_key: str | None = None) -> "SIDocument":
        return cls(
            id=str(data.get("id") or uuid4().hex),
            project_key=project_key or str(data.get("project_key", "")),
            module_name=str(data.get("module_name", "General")),
            name=str(data.get("name", "SI document")),
            mechanism_name=str(data.get("mechanism_name", "")),
            temperature_k=float(data.get("temperature_k", 298.15)),
            absolute=TableData.from_dict(data.get("absolute", {}), ABSOLUTE_HEADERS),
            relative=TableData.from_dict(data.get("relative", {}), RELATIVE_HEADERS),
            spin_density=TableData.from_dict(data.get("spin_density", {}), SPIN_HEADERS),
            geometry=TableData.from_dict(data.get("geometry", {}), GEOMETRY_HEADERS),
            notes=str(data.get("notes", "")),
            drive_file_id=data.get("drive_file_id"),
            created_at=str(data.get("created_at") or _now()),
            updated_at=str(data.get("updated_at") or _now()),
        )


def _number(value: str) -> float | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def recalculate_relative_derived(table: TableData) -> None:
    """Update only formulas explicitly defined by the SI template.

    ΔE Total = ΔE + ΔΔE
    ΔG = ΔE Total + ΔZ0 + ΔΔE Thermal + (-TΔS) + ΔDispersion + ΔComplexation
    Non-numeric or incomplete rows are left untouched for the affected derived cell.
    """
    header_index = {h: i for i, h in enumerate(table.headers)}
    required = ["ΔE", "ΔΔEᵃ", "ΔE Total", "ΔZ0", "ΔΔE Thermalᵇ", "-TΔSᵇ", "ΔDispersion", "ΔComplexation", "ΔGᶜ"]
    if not all(h in header_index for h in required):
        return
    table.rows = table.normalized_rows()
    for row in table.rows:
        de = _number(row[header_index["ΔE"]])
        dde = _number(row[header_index["ΔΔEᵃ"]])
        if de is not None and dde is not None:
            total = de + dde
            row[header_index["ΔE Total"]] = f"{total:.3f}"
        else:
            total = _number(row[header_index["ΔE Total"]])
        terms = [
            total,
            _number(row[header_index["ΔZ0"]]),
            _number(row[header_index["ΔΔE Thermalᵇ"]]),
            _number(row[header_index["-TΔSᵇ"]]),
            _number(row[header_index["ΔDispersion"]]),
            _number(row[header_index["ΔComplexation"]]),
        ]
        if all(v is not None for v in terms):
            row[header_index["ΔGᶜ"]] = f"{sum(v for v in terms if v is not None):.3f}"
