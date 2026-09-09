from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication
from .app_service import AppService
from .database import ResearchDatabase
from .gui import MainWindow
from .project_registry import ProjectRegistry
from .reaction_coordinate.lifecycle import detach_reaction_editor

def repo_root() -> Path: return Path(__file__).resolve().parents[2]
def main() -> int:
    app=QApplication(sys.argv); root=repo_root(); registry=ProjectRegistry(root/"config"/"projects"); db=ResearchDatabase(Path.home()/".ccra"/"research.db"); service=AppService(registry,db); win=MainWindow(service)
    app.aboutToQuit.connect(lambda: detach_reaction_editor(win.reaction_coordinate))
    win.show(); code=app.exec(); db.close(); return code
if __name__=="__main__": raise SystemExit(main())
