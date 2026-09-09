from ccra.reaction_coordinate.layout import apply_layout,branched_layout,circular_layout,chain_layout
from ccra.reaction_coordinate.models import Diagram,DiagramEdge,DiagramNode

def make_chain():
    nodes=[DiagramNode(label="R",energy=0),DiagramNode(label="TS",node_type="transition_state",energy=10),DiagramNode(label="P",energy=-5)]
    return Diagram(project_key="p",nodes=nodes,edges=[DiagramEdge(source=nodes[0].id,target=nodes[1].id),DiagramEdge(source=nodes[1].id,target=nodes[2].id)])

def test_chain_layout_is_left_to_right_and_energy_sensitive():
    d=make_chain(); p=chain_layout(d)
    assert p[d.nodes[0].id][0] < p[d.nodes[1].id][0] < p[d.nodes[2].id][0]
    assert p[d.nodes[1].id][1] < p[d.nodes[0].id][1]

def test_circular_layout_positions_every_node():
    d=make_chain(); p=circular_layout(d); assert set(p)=={n.id for n in d.nodes}; assert len(set(p.values()))==3

def test_branched_layout_separates_same_depth_nodes():
    r=DiagramNode(); a=DiagramNode(); b=DiagramNode(); d=Diagram(nodes=[r,a,b],edges=[DiagramEdge(source=r.id,target=a.id),DiagramEdge(source=r.id,target=b.id)])
    p=branched_layout(d); assert p[a.id][0]==p[b.id][0]; assert p[a.id][1]!=p[b.id][1]

def test_apply_layout_updates_model():
    d=make_chain(); apply_layout(d,"circular"); assert d.layout_type=="circular"; assert any(n.x or n.y for n in d.nodes)
