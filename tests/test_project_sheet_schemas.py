import json
from pathlib import Path
CONFIG=Path(__file__).resolve().parents[1]/"config"/"projects"
EXPECTED={"deformylation":{"Fe","Mn","Co","1. Normal Mechanism","2. Protonated Mechanism","3. Hydroperoxo Formation","4. Hydroperoxo Reactivity"},"feno6":{"0. FeNO6 & FeNO7","1. HNO2 binding","2. HNO2 protonation by HOTf","3. N-O bond cleavage by HOTf","3-2. (TPADP) N-O bond cleavage","4. FeNO spin surfaces","5. Fe-NO2 / Fe-HNO2 binding mode change","6. TD-DFT","P1. FeII(Me3-TPADP) fragment spin ladder","7. 전자를 먼저 넣는 경우"},"cono7":{"1. CoNO7  Co-Nitrite"},"co_sidearm":{"Main Mechanism","Sub 1. Rebound","Sub 2. Radical Coupling","받은 구조에서 investigation","메커니즘 검증","TD-DFT"},"mn_dichloride":{"Main","TD-DFT"}}
def test_uploaded_workbook_schemas_are_encoded():
    for path in CONFIG.glob("*.json"):
        d=json.loads(path.read_text(encoding="utf-8")); assert set(d["sheet"]["sheet_names"]) == EXPECTED[d["key"]]
