from pathlib import Path
from ccra.project_registry import ProjectRegistry
CONFIG=Path(__file__).resolve().parents[1]/"config"/"projects"
def test_current_projects_loaded():
    r=ProjectRegistry(CONFIG)
    assert set(p.key for p in r.all()) == {"deformylation","feno6","cono7","co_sidearm","mn_dichloride"}
    assert "7. 전자를 먼저 넣는 경우" in r.get("feno6").sheet.sheet_names
def test_drive_ids_are_bound():
    r=ProjectRegistry(CONFIG)
    assert all(p.drive_folder_id and p.sheet.spreadsheet_id for p in r.all())
