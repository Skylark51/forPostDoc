from pathlib import Path
from .database import ResearchDatabase
from .gaussian_parser import parse_gaussian
from .project_registry import ProjectRegistry
class AppService:
    def __init__(self, registry: ProjectRegistry, database: ResearchDatabase):
        self.registry=registry; self.database=database
        for p in registry.all(): database.upsert_project(p)
    def import_outputs(self, project_key: str, paths: list[Path]) -> dict[str,int]:
        stats={"imported":0,"duplicates":0,"failed":0}
        for path in paths:
            try:
                rec=parse_gaussian(path,project_key); created,_=self.database.add_gaussian_record(rec); stats["imported" if created else "duplicates"]+=1
            except Exception: stats["failed"]+=1
        return stats
