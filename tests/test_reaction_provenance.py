from ccra.reaction_coordinate.controller import ReactionCoordinateController
from ccra.reaction_coordinate.models import Diagram,DiagramNode
from ccra.reaction_coordinate.storage import DiagramStore

class DB:
    def list_gaussian_files(self,project_key): return []

def test_gaussian_provenance_can_be_attached_without_losing_relative_energy(tmp_path):
    c=ReactionCoordinateController(DB(),DiagramStore(tmp_path)); node=DiagramNode(energy=5.2,energy_unit="kcal/mol"); d=Diagram(project_key="feno6",nodes=[node]); row={"id":9,"filename":"3-TS.out","electronic_energy_hartree":-222.123456}
    c.link_node_to_file(d,node.id,row,apply_raw_energy=False)
    assert node.energy==5.2 and node.linked_file_id==9 and node.linked_electronic_energy_hartree==-222.123456
    c.link_node_to_file(d,node.id,row,apply_raw_energy=True)
    assert node.energy==-222.123456 and node.energy_unit=="Eh"
