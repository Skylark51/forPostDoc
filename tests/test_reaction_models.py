from ccra.reaction_coordinate.models import Diagram, DiagramEdge, DiagramNode

def test_diagram_round_trip_preserves_scientific_fields():
    node=DiagramNode(label="TS1",node_type="transition_state",energy=12.34,spin="S=1",multiplicity=3,linked_file_id=7,linked_filename="3-ts.out",linked_electronic_energy_hartree=-100.123)
    edge=DiagramEdge(source=node.id,target="p",edge_type="curved",barrier=12.34)
    d=Diagram(project_key="feno6",module_name="Acid-first",name="Path",nodes=[node],edges=[edge])
    restored=Diagram.from_dict(d.to_dict())
    assert restored.project_key=="feno6"
    assert restored.nodes[0].multiplicity==3
    assert restored.nodes[0].linked_filename=="3-ts.out"
    assert restored.edges[0].barrier==12.34
