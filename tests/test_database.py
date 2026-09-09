from pathlib import Path
from ccra.database import ResearchDatabase
from ccra.models import GaussianRecord,ProjectDefinition,SheetBinding
def test_database_deduplicates(tmp_path):
    db=ResearchDatabase(tmp_path/"x.db"); p=ProjectDefinition("p","P","folder","F",SheetBinding("S","sid")); db.upsert_project(p)
    r=GaussianRecord("p",Path("a.out"),"a.out","hash",True,0,1,"UB3LYP/def2SVP",["Opt"],-100.0,"1\nx\nH 0 0 0\n")
    assert db.add_gaussian_record(r)[0] is True
    assert db.add_gaussian_record(r)[0] is False
    assert len(db.list_gaussian_files("p")) == 1
    db.close()
