"""Build the BODIPY snapshot and enrich the existing portal and Ni result table.

Usage: python tools/build-progress.py --audit <workbook_data.json>
Only an explicitly supplied audit snapshot is used; this does not query live jobs.
"""
import argparse
import json
import re
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def build_bodipy(audit):
    raw = json.loads(Path(audit).read_text(encoding='utf-8'))
    # Publish the review evidence, omitting raw server paths, inputs and coordinates.
    groups = []
    for g in raw['groups']:
        compact = {k: g[k] for k in ['id', 'element', 'phase', 'title', 'notes']}
        compact['states'] = []
        for s in g['states']:
            r, bb = s.get('r') or {}, s.get('bb') or {}
            compact['states'].append({
                'state': s['state'], 'relG': s.get('relG'), 'Gcomp': s.get('Gcomp'),
                'file': r.get('name'), 'normal': r.get('normal'),
                'imag': r.get('imag'), 's2': r.get('s2'),
                'bbFile': bb.get('name'), 'bbNormal': bb.get('normal'),
            })
        groups.append(compact)
    data = {k: raw[k] for k in ['checked', 'source_url', 'summary']}
    data['issues'] = [{ 'id':f'B{i+1:02}', 'priority':r[0], 'title':r[1],
                      'source':r[2].split('/')[-1], 'fact':r[3], 'action':r[4]}
                     for i, r in enumerate(raw['issues'])]
    data['groups'] = groups
    write(DOCS/'projects/bodipy/progress.json', json.dumps(data, ensure_ascii=False, indent=2))
    html = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="BODIPY Se/Te 계산 경과와 반응 경로 검증 현황"><title>BODIPY · Se / Te 연구 대시보드</title>
<link rel="stylesheet" href="../../assets/progress.css"><link rel="stylesheet" href="../../assets/portal-nav.css"></head>
<body style="--accent:#be426b"><nav class="portal-nav" aria-label="프로젝트 이동"><a href="../../">← 프로젝트</a><span>BODIPY · Se / Te</span><div><a href="../ni-dithiocarbazate/">Ni</a><a href="../v-oxo-peroxo/#dashboard">V</a></div></nav>
<main><span class="eyebrow">BODIPY / MECHANISM REVIEW</span><h1>Se · Te 반응 경로</h1>
<p class="muted">자료 확인 <time>__CHECKED__</time> · 게시된 검토 스냅샷 · 전체 노드의 현재 실행 상태는 미확인</p>
<div class="toolbar"><a href="#pathways">경로별 진행</a> · <a href="#tasks">남은 작업</a> · <a href="__SHEET__" target="_blank" rel="noopener">원본 구글 시트 ↗</a> · <a href="progress.json" download>검토 데이터 JSON ↓</a></div>
<section class="panel notice"><h2>현재 판단 · 전반과 후반 연결 검증이 남음</h2><p>Se의 hydride → proton 순서가 두 번 반복되는 구조를 확인했습니다. 최신 forEEbreak 결과도 proton 이동이며 Se–Se 결합은 유지됩니다. E–E cleavage 완료로 집계하지 않습니다.</p><p class="hint">Gcomp = E(def2-TZVPP) + Gcorr(def2-SVP), B3LYP/CPCM(MeCN), 298.15 K. 외부 D3 제외. 각 단계의 RC = 0이며 단계 사이 에너지를 이어 붙이지 않습니다.</p></section>
<div class="metrics"><div class="metric"><span>검토한 RC / TS / PC 세트</span><strong>13</strong><span>Se 8 · Te 5</span></div><div class="metric"><span>Se 전반 H-transfer 세트</span><strong>4 / 4</strong><span>기구 연결 전체 완료와 구분</span></div><div class="metric"><span>Annulation 세트 확보</span><strong>6 / 6</strong><span>Se-A1 PC 작은 허수진동 잔존</span></div><div class="metric"><span>후속 검토 항목</span><strong>18</strong><span>__HIGH__개 높은 우선순위</span></div></div>
<section class="panel"><h2>최근 경과와 다음 단계</h2><p><span class="badge ok">11/16 01:26 KST</span> Se forEEbreak endpoint TZVPP 정상 종료 → 실제 반응은 proton transfer, Se–Se 2.386–2.388 Å 유지.</p><p><span class="badge warn">다음 검증</span> E–E 절단 / E–C 형성 TS 및 양방향 IRC 확보 → 후반 출발 구조와 연결 대조.</p><p><span class="badge warn">Te 복구</span> checkpoint 확장자 오류로 손상된 입력과 FileIO 실패 endpoint 복구, CS/OS 전자상태 안정성 확인.</p></section>
<section id="pathways"><h2>경로별 계산 경과</h2><p class="hint">세트 확보는 전체 반응 경로 검증 완료를 뜻하지 않습니다. 에너지 단위 kcal/mol. Te-P2는 전자상태가 달라 장벽으로 해석하지 않습니다.</p>
<div class="toolbar"><label>원소 <select id="element"><option value="">전체</option><option>Se</option><option>Te</option></select></label><label>구간 <select id="phase"><option value="">전체</option><option>전반</option><option>후반</option></select></label><label>검색 <input id="query" type="search" placeholder="단계·반응명·파일"></label><span id="count" class="hint" role="status"></span></div><div id="groups" class="cols">__GROUPS__</div></section>
<section class="panel" id="tasks"><h2>남은 검토 · 후속 작업</h2><p class="hint">체크와 메모는 이 브라우저의 개인 작업 기록입니다. 서버 계산 상태와 과학적 판정은 자동으로 바뀌지 않습니다.</p><p id="task-count" role="status"></p><div class="toolbar"><button id="export">작업 기록 백업 ↓</button><label>기록 불러오기 <input id="import" type="file" accept="application/json,.json"></label></div><div id="storage-message" class="hint" role="status"></div>__TASKS__
<h3 style="margin-top:25px">진행 메모</h3><label for="memo" class="hint">검토한 내용과 다음 확인 사항</label><textarea id="memo" placeholder="진행 기록을 입력하세요"></textarea></section>
<footer>자료: 2026-11-16 BODIPY Se/Te 검토 · 구글 5개 탭 / 로컬 63개 out / 서버 선택 348개 out 대조. 상태 갱신 시 확인 시각과 근거를 함께 갱신합니다.</footer></main>
<script src="dashboard.js" defer></script></body></html>'''
    cards = []
    for g in groups:
        caution = g['id'] in ['Se-P5','Se-A1','Te-P2']
        label = '전자상태 검증 필요' if g['id']=='Te-P2' else ('추가 검증 필요' if caution else '계산 세트 확보')
        energy = ''.join(f'<div><small>{e(s["state"])}</small><b>{s["relG"]:.2f}</b></div>' for s in g['states'])
        rows = ''.join(f'<tr><td>{e(s["state"])}</td><td><code>{e(s["file"] or "미확인")}</code></td><td>{"정상 종료" if s["normal"] else "미확인"}</td><td>{e(str(s["imag"]))}</td><td>{e(str(s["s2"]))}</td></tr>' for s in g['states'])
        cards.append(f'<article class="stage" data-element="{g["element"]}" data-phase="{g["phase"]}"><header><span class="eyebrow">{g["id"]} · {g["phase"]}</span><span class="badge {"warn" if caution else "ok"}">{label}</span></header><h3>{e(g["title"])}</h3><div class="energy" aria-label="각 상태 상대 자유에너지">{energy}</div><p class="hint">{e(g["notes"])}</p><details><summary>출력·허수진동·스핀 근거</summary><div class="scroll"><table><thead><tr><th>상태</th><th>출력 파일</th><th>종료</th><th>허수 / cm⁻¹</th><th>⟨S²⟩</th></tr></thead><tbody>{rows}</tbody></table></div></details></article>')
    tasks = ''.join(f'<div class="task"><label><input type="checkbox" data-task="{i["id"]}"><span><span class="badge {"warn" if i["priority"]=="높음" else ""}">{i["priority"]}</span> {e(i["title"])}</span></label><p>{e(i["fact"])}</p><p><b>다음 행동</b> · {e(i["action"])}</p></div>' for i in data['issues'])
    for k,v in {'__CHECKED__':raw['checked'].replace('T',' ')[:19]+' KST','__SHEET__':e(raw['source_url']), '__GROUPS__':''.join(cards),'__TASKS__':tasks,'__HIGH__':str(sum(i['priority']=='높음' for i in data['issues']))}.items():
        html=html.replace(k,v)
    write(DOCS/'projects/bodipy/index.html',html)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--audit',required=True)
    build_bodipy(p.parse_args().audit)
