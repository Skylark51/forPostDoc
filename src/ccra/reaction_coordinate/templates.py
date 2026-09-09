from __future__ import annotations

from .layout import apply_layout
from .models import Diagram, DiagramEdge, DiagramNode


def _edge(a: DiagramNode, b: DiagramNode, **kwargs) -> DiagramEdge:
    return DiagramEdge(source=a.id, target=b.id, **kwargs)


def linear_template(project_key: str, module_name: str) -> Diagram:
    r = DiagramNode(label="R", node_type="reactant", energy=0.0)
    ts = DiagramNode(label="TS1", node_type="transition_state", energy=15.0)
    p = DiagramNode(label="P", node_type="product", energy=-5.0)
    d = Diagram(project_key=project_key, module_name=module_name, name="Linear pathway", layout_type="chain", nodes=[r, ts, p], edges=[_edge(r, ts), _edge(ts, p)])
    apply_layout(d)
    return d


def circular_template(project_key: str, module_name: str) -> Diagram:
    nodes = [DiagramNode(label=label, node_type="intermediate") for label in ["A", "B", "C", "D"]]
    edges = [_edge(nodes[i], nodes[(i + 1) % len(nodes)], edge_type="curved") for i in range(len(nodes))]
    d = Diagram(project_key=project_key, module_name=module_name, name="Circular mechanism", layout_type="circular", nodes=nodes, edges=edges)
    apply_layout(d)
    return d


def branched_template(project_key: str, module_name: str) -> Diagram:
    r = DiagramNode(label="R", node_type="reactant", energy=0.0)
    i = DiagramNode(label="INT1", energy=-3.0)
    ts1 = DiagramNode(label="TS1", node_type="transition_state", energy=12.0)
    p1 = DiagramNode(label="P1", node_type="product", energy=-10.0)
    ts2 = DiagramNode(label="TS2", node_type="transition_state", energy=16.0)
    p2 = DiagramNode(label="P2", node_type="product", energy=-6.0)
    d = Diagram(project_key=project_key, module_name=module_name, name="Branched pathway", layout_type="branched", nodes=[r, i, ts1, p1, ts2, p2], edges=[_edge(r, i), _edge(i, ts1), _edge(ts1, p1), _edge(i, ts2), _edge(ts2, p2)])
    apply_layout(d)
    return d


def two_branch_template(project_key: str, module_name: str) -> Diagram:
    d = branched_template(project_key, module_name)
    d.name = "Rebound / radical coupling"
    d.nodes[-4].label = "TS-Rebound"
    d.nodes[-3].label = "Rebound P"
    d.nodes[-2].label = "TS-Coupling"
    d.nodes[-1].label = "Coupling P"
    return d


def blank_template(project_key: str, module_name: str, layout_type: str = "chain") -> Diagram:
    return Diagram(project_key=project_key, module_name=module_name, name="New diagram", layout_type=layout_type)
