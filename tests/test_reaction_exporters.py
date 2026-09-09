from ccra.reaction_coordinate.exporters import export_model_svg
from ccra.reaction_coordinate.templates import linear_template

def test_model_svg_export_creates_readable_file(tmp_path):
    d=linear_template("feno6","Acid-first"); path=export_model_svg(d,tmp_path/"reaction.svg"); text=path.read_text(encoding="utf-8"); assert path.exists(); assert "<svg" in text and "TS1" in text and "kcal/mol" in text
