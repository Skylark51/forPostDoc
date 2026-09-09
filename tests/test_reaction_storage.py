from ccra.reaction_coordinate.models import Diagram,DiagramNode
from ccra.reaction_coordinate.storage import DiagramStore

def test_project_scoped_save_load_and_delete(tmp_path):
    store=DiagramStore(tmp_path); d=Diagram(project_key="co_sidearm",module_name="Rebound",name="Test",nodes=[DiagramNode(label="A")]); path=store.save(d)
    assert path.exists(); loaded=store.load("co_sidearm",d.id); assert loaded.name=="Test"; assert len(store.list("co_sidearm"))==1; assert store.list("feno6")==[]; assert store.delete("co_sidearm",d.id); assert store.list("co_sidearm")==[]

def test_json_import_rebinds_to_current_project(tmp_path):
    store=DiagramStore(tmp_path/"store"); original=Diagram(project_key="old",name="Imported"); exported=store.export_json(original,tmp_path/"diagram.json"); loaded=store.import_json(exported,"new"); assert loaded.project_key=="new"; assert store.load("new",loaded.id).name=="Imported"
