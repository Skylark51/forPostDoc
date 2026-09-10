import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

from types import SimpleNamespace
from PySide6.QtWidgets import QApplication

from ccra.si_generator.storage import SIDocumentStore
from ccra.si_generator.widgets import SIGeneratorWidget


def test_si_generator_widget_project_local_save(tmp_path):
    app=QApplication.instance() or QApplication([])
    widget=SIGeneratorWidget()
    widget.store=SIDocumentStore(tmp_path/'si')
    project=SimpleNamespace(key='feno6',modules=['FeNO6 / FeNO7'],drive_folder_id='folder')
    widget.set_project(project)
    widget.absolute.add_row()
    widget.absolute.table.item(0,0).setText('A')
    widget.save_local()
    loaded=widget.store.list('feno6')
    assert len(loaded)==1
    assert loaded[0].absolute.rows[0][0]=='A'
    widget.close()
    app.processEvents()
