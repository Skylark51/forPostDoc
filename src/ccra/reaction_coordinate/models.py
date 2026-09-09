from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass(slots=True)
class DiagramNode:
    id: str = field(default_factory=lambda: new_id("node"))
    label: str = "INT"
    node_type: str = "intermediate"
    energy: float | None = None
    energy_unit: str = "kcal/mol"
    spin: str = ""
    multiplicity: int | None = None
    subtitle: str = ""
    notes: str = ""
    x: float = 0.0
    y: float = 0.0
    color: str = "#202124"
    shape: str = "level"
    linked_file_id: int | None = None
    linked_filename: str = ""
    linked_electronic_energy_hartree: float | None = None
    style: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DiagramNode":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value for key, value in data.items() if key in allowed})


@dataclass(slots=True)
class DiagramEdge:
    id: str = field(default_factory=lambda: new_id("edge"))
    source: str = ""
    target: str = ""
    edge_type: str = "normal"
    label: str = ""
    barrier: float | None = None
    style: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DiagramEdge":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value for key, value in data.items() if key in allowed})


@dataclass(slots=True)
class Diagram:
    id: str = field(default_factory=lambda: new_id("diagram"))
    project_key: str = ""
    module_name: str = "General"
    name: str = "Reaction Coordinate"
    layout_type: str = "chain"
    nodes: list[DiagramNode] = field(default_factory=list)
    edges: list[DiagramEdge] = field(default_factory=list)
    canvas: dict[str, Any] = field(default_factory=lambda: {
        "width": 1600,
        "height": 1000,
        "grid_size": 20,
        "snap_to_grid": False,
        "show_energy": True,
        "show_barrier": True,
        "show_spin_multiplicity": True,
        "show_subtitle": True,
        "show_edge_label": True,
        "show_arrows": True,
        "force_curved": False,
    })
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def node(self, node_id: str) -> DiagramNode | None:
        return next((node for node in self.nodes if node.id == node_id), None)

    def edge(self, edge_id: str) -> DiagramEdge | None:
        return next((edge for edge in self.edges if edge.id == edge_id), None)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "project_key": self.project_key,
            "module_name": self.module_name,
            "name": self.name,
            "layout_type": self.layout_type,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "canvas": dict(self.canvas),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Diagram":
        diagram = cls(
            id=data.get("id") or new_id("diagram"),
            project_key=data.get("project_key", ""),
            module_name=data.get("module_name", "General"),
            name=data.get("name", "Reaction Coordinate"),
            layout_type=data.get("layout_type", "chain"),
            nodes=[DiagramNode.from_dict(item) for item in data.get("nodes", [])],
            edges=[DiagramEdge.from_dict(item) for item in data.get("edges", [])],
            canvas=dict(data.get("canvas", {})),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )
        defaults = cls().canvas
        defaults.update(diagram.canvas)
        diagram.canvas = defaults
        return diagram
