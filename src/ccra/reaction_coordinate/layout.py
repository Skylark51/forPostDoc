from __future__ import annotations

import math
from collections import defaultdict, deque

from .models import Diagram


def _usable_energies(diagram: Diagram) -> bool:
    values = [float(node.energy) for node in diagram.nodes if node.energy is not None and node.energy_unit == "kcal/mol"]
    return len(values) >= 2 and max(values) - min(values) <= 120.0


def chain_layout(diagram: Diagram, origin=(170.0, 430.0), x_gap=190.0, energy_scale=6.0) -> dict[str, tuple[float, float]]:
    nodes = list(diagram.nodes)
    if not nodes:
        return {}
    use_energy = _usable_energies(diagram)
    reference = min((float(n.energy) for n in nodes if n.energy is not None and n.energy_unit == "kcal/mol"), default=0.0)
    positions: dict[str, tuple[float, float]] = {}
    for index, node in enumerate(nodes):
        x = origin[0] + index * x_gap
        if use_energy and node.energy is not None and node.energy_unit == "kcal/mol":
            y = origin[1] - (float(node.energy) - reference) * energy_scale
        else:
            y = origin[1] - (70.0 if node.node_type == "transition_state" else 0.0)
        positions[node.id] = (x, y)
    return positions


def circular_layout(diagram: Diagram, center=(700.0, 450.0), radius=270.0) -> dict[str, tuple[float, float]]:
    nodes = list(diagram.nodes)
    if not nodes:
        return {}
    start = -math.pi / 2
    step = 2 * math.pi / len(nodes)
    return {
        node.id: (
            center[0] + radius * math.cos(start + index * step),
            center[1] + radius * math.sin(start + index * step),
        )
        for index, node in enumerate(nodes)
    }


def branched_layout(diagram: Diagram, origin=(150.0, 470.0), x_gap=210.0, y_gap=170.0) -> dict[str, tuple[float, float]]:
    if not diagram.nodes:
        return {}
    node_ids = {node.id for node in diagram.nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming_count = {node.id: 0 for node in diagram.nodes}
    for edge in diagram.edges:
        if edge.source in node_ids and edge.target in node_ids:
            outgoing[edge.source].append(edge.target)
            incoming_count[edge.target] += 1
    roots = [node_id for node_id, degree in incoming_count.items() if degree == 0]
    if not roots:
        roots = [diagram.nodes[0].id]
    depth = {root: 0 for root in roots}
    queue = deque(roots)
    while queue:
        source = queue.popleft()
        for target in outgoing[source]:
            candidate = depth[source] + 1
            if target not in depth or candidate > depth[target]:
                depth[target] = candidate
                if candidate < len(diagram.nodes) + 2:
                    queue.append(target)
    next_depth = max(depth.values(), default=0) + 1
    for node in diagram.nodes:
        if node.id not in depth:
            depth[node.id] = next_depth
            next_depth += 1
    levels: dict[int, list[str]] = defaultdict(list)
    for node in diagram.nodes:
        levels[depth[node.id]].append(node.id)
    positions: dict[str, tuple[float, float]] = {}
    for level in sorted(levels):
        ids = levels[level]
        offset = (len(ids) - 1) / 2.0
        for lane, node_id in enumerate(ids):
            positions[node_id] = (origin[0] + level * x_gap, origin[1] + (lane - offset) * y_gap)
    return positions


def apply_layout(diagram: Diagram, layout_type: str | None = None) -> dict[str, tuple[float, float]]:
    layout_type = layout_type or diagram.layout_type
    if layout_type == "circular":
        positions = circular_layout(diagram)
    elif layout_type == "branched":
        positions = branched_layout(diagram)
    elif layout_type == "freeform":
        positions = {node.id: (node.x, node.y) for node in diagram.nodes}
    else:
        positions = chain_layout(diagram)
    for node in diagram.nodes:
        if node.id in positions:
            node.x, node.y = positions[node.id]
    diagram.layout_type = layout_type
    return positions
