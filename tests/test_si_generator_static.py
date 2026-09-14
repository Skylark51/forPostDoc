import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_catalog_matches_real_project_configs():
    expected=[]
    for path in sorted((ROOT/'config'/'projects').glob('*.json')):
        data=json.loads(path.read_text(encoding='utf-8'))
        expected.append({'key':data['key'],'title':data['title'],'drive_folder_id':data['drive_folder_id'],'modules':data.get('modules',[])})
    expected=sorted(expected,key=lambda item:item['title'])
    actual=json.loads((ROOT/'docs'/'project-catalog.json').read_text(encoding='utf-8'))
    assert actual == expected


def test_homepage_is_korean_workspace_with_clickable_si_generator():
    html=(ROOT/'docs'/'index.html').read_text(encoding='utf-8')
    assert '<html lang="ko">' in html
    assert '계산화학 연구 워크스페이스' in html
    assert 'href="si-generator.html"' in html
    assert '>SI 생성기<' in html or 'SI 생성기 열기' in html
    assert 'Computational Chemistry Report Assistant' not in html


def test_deployed_si_generator_has_no_user_facing_dummy_rows_or_heavy_framework():
    html=(ROOT/'docs'/'si-generator.html').read_text(encoding='utf-8')
    js=(ROOT/'docs'/'assets'/'si-generator.js').read_text(encoding='utf-8')
    assert '1.049' not in html+js
    assert '3.192' not in html+js
    assert '어떤 메커니즘' not in html+js
    assert 'react' not in html.lower()
    assert 'vue' not in html.lower()
    assert 'jquery' not in html.lower()
    assert 'assets/si-generator.js' in html
