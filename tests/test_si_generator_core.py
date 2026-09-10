import zipfile

from ccra.si_generator.docx_export import export_docx
from ccra.si_generator.models import SIDocument, TableData, recalculate_relative_derived
from ccra.si_generator.storage import SIDocumentStore


def test_blank_document_has_no_dummy_rows():
    doc = SIDocument(project_key="feno6")
    assert doc.absolute.rows == []
    assert doc.relative.rows == []
    assert doc.spin_density.rows == []
    assert doc.geometry.rows == []


def test_save_load_project_binding(tmp_path):
    store = SIDocumentStore(tmp_path)
    doc = SIDocument(project_key="feno6", module_name="HOTf protonation", mechanism_name="Acid-first")
    doc.absolute.rows.append(["A", "-1", "-2", "0", "0", "0", "0"])
    store.save(doc)
    loaded = store.load("feno6", doc.id)
    assert loaded.project_key == "feno6"
    assert loaded.module_name == "HOTf protonation"
    assert loaded.absolute.rows[0][0] == "A"


def test_relative_derived_values():
    table = TableData(headers=["Structure","ΔE","ΔΔEᵃ","ΔE Total","ΔZ0","ΔΔE Thermalᵇ","-TΔSᵇ","ΔDispersion","ΔComplexation","ΔGᶜ"], rows=[["TS","2","3","","1","1","1","1","1",""]])
    recalculate_relative_derived(table)
    assert table.rows[0][3] == "5.000"
    assert table.rows[0][9] == "10.000"


def test_docx_export_contains_template_sections(tmp_path):
    doc = SIDocument(project_key="co_sidearm", mechanism_name="Rebound")
    doc.absolute.rows.append(["INT1", "", "", "", "", "", ""])
    path = export_docx(doc, tmp_path / "si.docx")
    assert path.exists() and path.stat().st_size > 0
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "Absolute energy values of Rebound" in xml
    assert "Mulliken Spin Density Distributions of Rebound" in xml
    assert "Selected Geometries of Rebound" in xml
