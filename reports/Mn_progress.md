# Mn(III)–peroxo 계산 진행 및 후속 작업

확인 시각: 2026-11-16 23:07:35.492264 KST

[Google Sheets 원자료](https://docs.google.com/spreadsheets/d/1X-b8hEExl6dM5EWxFP1VLlNpp4cm4FOxN1PrlKWlweM/edit) · [계산 및 시트 작성 규칙](../AGENTS.md)

## 현재 상태

기존 12개 작업: 완료 9, 실행 중 1, 비정상 종료 1, 사용자 요청 중단 1. 46번 TMU C–O 후속 workflow는 별도로 전 단계 완료.

| 번호 | 계산 | 상태 |
|---|---|---|
| 21 | PPA-Coord-approach-scan | 비정상 종료 · 원인 미확정 |
| 22 | PPA-Coord-release-scan | 실행 중 |
| 25 | PPA-PHA-release-scan | 완료 |
| 42 | PPA-PHA-approach-scan | 완료 |
| 27 | PPA-bound-stable | 완료 |
| 43 | PPA-adduct-stable | 완료 |
| 45 | CBNone-conformer-bridge-qst2 | 완료 |
| 33 | CBNone-NAend-opt | 완료 |
| 35 | CBNone-PHAstart-opt | 완료 |
| 37 | TMU-CN-release-scan | 사용자 별도 요청으로 중단 · 재개 대기 |
| 46 | TMU-CO-release-scan | 완료 |
| 41 | TMU-CNalt-release-scan | 완료 |

- 21번: controller는 rc=1로 종료했다. 현재 출력에는 Gaussian의 Normal/Error termination 표식이 없어 종료 원인은 확정하지 않았다. 기존 출력을 보존했고 임의 재시작하지 않았다.
- 37번: 다른 사용자 요청에 따른 서버 반환으로 중단된 작업이다. 새 서버 지정 전 재개하지 않는다.

## 46번 TMU C–O 경로

- 최초 scan: 13점 모두 정상 종료. 최대점은 9번째, C5–O4 = 2.18415491 Å, SCF = −2449.81101828 Eh. 초기점 대비 ΔE(SB) = +19.19206430 kcal/mol.
- 이 최대점 좌표에서 freq → TS → freq → forward IRC → reverse IRC를 진행했다. 이후 TS BB와 양쪽 endpoint opt → freq → BB도 모두 정상 종료했다.
- 정밀화 TS: 허수진동 -141.7467 cm⁻¹ 한 개. C5–O4 = 2.14480162 Å.
- forward 최소점: 허수진동 0개, C5–O4 = 2.48129093 Å.
- reverse 최소점: 허수진동 0개, C5–O4 = 1.38413693 Å. 기존 NA adduct와 heavy-atom RMSD = 0.00188004 Å.
- 직전 reverse 최소점 기준 ΔE‡(BB) = 17.7289 kcal/mol. 현재 시트의 E(thermal) − T·S 정의에 따른 ΔG‡(298.15 K) = 16.7447 kcal/mol. 저주파·용액 표준상태 추가 보정은 새로 적용하지 않았다.

| 구조 | SCF-SB (Eh) | SCF-BB (Eh) | 허수진동 (cm⁻¹) |
|---|---:|---:|---|
| forward 최소점 | -2449.81171040 | -2451.41102377 | 0 |
| TS | -2449.81098629 | -2451.40896752 | -141.7467 |
| reverse 최소점 | -2449.84160410 | -2451.43722035 | 0 |

### 원본 템플릿 대조

- 원본: `5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan*.inp`.
- 원본의 route, CPU, 메모리, 제목, 빈 줄을 유지했다. 계산별 checkpoint 이름과 최초 freq의 좌표만 12-MTP 최대점에 맞췄다.
- `%CPU=0-11`, `%mem=30Gb`, `%oldchk=/home/skylark/chk/`, `%chk=/scratch/skylark/`.
- opt, freq, BB는 별도 input. 임의 integral=ultrafine, tight, maxcycles, calcfc 추가 없음.

| 후속 input | 원본 template | route·자원 일치 |
|---|---|---|
| 5-MnIII-12MTP-TMU-CO-release-scan-freq.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircfwd.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircfwd.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircrev.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircrev.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-bb.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-bb.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircfwd-opt.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircfwd-opt.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircfwd-opt-freq.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircfwd-opt-freq.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircfwd-opt-freq-bb.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircfwd-opt-freq-bb.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircrev-opt.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircrev-opt.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircrev-opt-freq.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircrev-opt-freq.inp | 확인 |
| 5-MnIII-12MTP-TMU-CO-release-scan-freq-ts-freq-ircrev-opt-freq-bb.inp | 5-MnIII-14MTP-TMU-AfterNA-forCOcleav-scan-freq-ts-freq-ircrev-opt-freq-bb.inp | 확인 |

<details>
<summary>최대점에서 시작한 최초 freq input 원문</summary>

```text
%oldchk=/home/skylark/chk/5-MnIII-12MTP-TMU-CO-release-scan.chk
%chk=/scratch/skylark/5-MnIII-12MTP-TMU-CO-release-scan-freq.chk
%CPU=0-11
%mem=30Gb
#p ub3lyp/def2svp scrf=(cpcm,solvent=acetonitrile) freq scf=(xqc,maxconventionalcycles=60) nosymm guess=read  EmpiricalDispersion=GD3BJ

freq

1 5
25      0.141781000     -0.280859000      0.006803000
8       2.404323000      1.268350000     -0.598317000
8       2.010247000     -0.117702000     -0.541300000
8      -0.192346000      1.288868000     -0.561279000
6       1.675096000      1.997666000     -1.444907000
7       1.518517000      1.609521000     -2.727010000
6       0.380914000      2.090842000     -3.495629000
6       2.269447000      0.499454000     -3.290703000
7       1.595834000      3.302222000     -1.107010000
6       1.364311000      3.684621000      0.277164000
6       1.759225000      4.375055000     -2.074172000
1      -0.124994000      1.234842000     -3.966915000
1       0.684146000      2.787946000     -4.293491000
1      -0.333168000      2.576729000     -2.822550000
1       2.510731000      0.738495000     -4.337948000
1       3.200157000      0.352937000     -2.733686000
1       1.694165000     -0.439642000     -3.260801000
1       0.915023000      2.832172000      0.794861000
1       2.296386000      3.998797000      0.776542000
1       0.653378000      4.525172000      0.304219000
1       2.262562000      3.999466000     -2.972416000
1       0.795177000      4.826617000     -2.364072000
1       2.387103000      5.162058000     -1.628717000
6       2.048871000      0.457114000      2.580389000
7       0.785208000     -0.266272000      2.403883000
6       0.907216000     -1.682955000      2.805073000
6       0.209288000     -2.659620000      1.861343000
7       0.607018000     -2.464470000      0.450313000
6       2.032828000     -2.790287000      0.259078000
6      -0.193413000     -3.319041000     -0.457660000
6      -1.587485000     -2.772991000     -0.705386000
7      -1.532167000     -1.396953000     -1.227227000
6      -1.227797000     -1.347209000     -2.657761000
6      -2.754692000     -0.653567000     -0.919962000
6      -2.862342000     -0.399926000      0.561745000
6      -4.078275000     -0.318020000      1.239492000
6      -4.063617000     -0.029191000      2.605940000
6      -2.843360000      0.179726000      3.248829000
6      -1.666684000      0.088316000      2.501341000
7      -1.696159000     -0.217658000      1.198508000
6      -0.313813000      0.419430000      3.079704000
1       1.934089000      1.487724000      2.222892000
1       2.372809000      0.479776000      3.638428000
1       2.826319000     -0.014850000      1.968043000
1       1.975025000     -1.930787000      2.855819000
1       0.509638000     -1.839688000      3.823687000
1      -0.878931000     -2.548059000      1.933034000
1       0.448767000     -3.690687000      2.183831000
1       2.663296000     -2.144334000      0.875562000
1       2.228765000     -3.847983000      0.512627000
1       2.306496000     -2.606580000     -0.786102000
1       0.351623000     -3.381300000     -1.409270000
1      -0.258737000     -4.349044000     -0.062631000
1      -2.164281000     -2.768287000      0.229268000
1      -2.127131000     -3.442514000     -1.400312000
1      -2.032596000     -1.799569000     -3.267029000
1      -0.291264000     -1.881595000     -2.864605000
1      -1.094666000     -0.299757000     -2.951569000
1      -3.660543000     -1.165110000     -1.293831000
1      -2.684611000      0.322314000     -1.425345000
1      -5.014545000     -0.486072000      0.705365000
1      -4.998782000      0.029493000      3.166473000
1      -2.796799000      0.411775000      4.313908000
1      -0.170323000      1.504043000      2.942689000
1      -0.312179000      0.236376000      4.170831000
```

</details>

## 완료 결과 시트 위치

| 시트 | 행 | 내용 |
|---|---|---|
| 6. 12-MTP (2-PPA) | 28, 31 | 안정성 확인 후 최소점 SB·BB·ZPE·E(thermal)·S |
| 8. 12-MTP (Cyclobutanone) | 30–32 | rev → TS → fwd QST2 결과 |
| 8. 12-MTP (Cyclobutanone) | 34, 37 | 두 기존 endpoint 재최적화 결과 |
| 10. 12-MTP (Tetramethylurea) | 13, 16 | 완료 scan |
| 10. 12-MTP (Tetramethylurea) | 19 | C–O scan 최대점 최초 freq |
| 10. 12-MTP (Tetramethylurea) | 21–23 | fwd → TS → rev C–O 결과 |

- 현재 TMU 시트의 fwd/TS/rev 순서를 유지했고, CBNone은 rev/TS/fwd 순서를 유지했다. TS는 항상 가운데다.
- 라이온 번호는 숫자만 입력한다. 상태색은 B열 번호 셀에만 적용한다. 완료는 보라색, 실행 중은 베이지색.
- scan 행 사이 빈 두 행을 유지한다. 원자료 D:H와 기존 기준점의 상대 에너지 수식 L:S를 구분한다.

## 남은 해석과 주의점

- CBNone QST2: TS 허수진동 −41.9017 cm⁻¹, 양방향 IRC 및 최소점·BB 완료. 다만 reverse 최소점이 원래 NA endpoint와 완전히 같은 구조는 아니므로, 기존 3단계 전체 경로가 완전히 연결됐다고 단정하지 않는다.
- PPA 안정성 검사 2개: 기존 wavefunction이 이미 stable이며, 재최적화 구조·에너지 변화가 거의 없다.
- PPA 양방향 scan은 서로 다른 에너지 변화를 보인다. 25번 전체 scan의 가장 높은 값은 마지막 점이므로, 이를 내부 TS 최대점으로 취급하지 않는다.
- TMU C–N 두 분기는 중단/완료 상태를 구분하며 C–O 경로와 별도 검증한다.

## 서버에서 이어 확인할 위치

`/home/skylark/AfterPhD/SeventhInnoCOREDHJ`

- 기존 12개 상태: `/home/skylark/skylark/mn-reconnect-20261115/`의 manifest와 각 `.status.json`.
- 46번 후속 상태: `/home/skylark/skylark/mn-tmu-co-followup/`.
- 결과를 보고할 때는 최신 상태 파일뿐 아니라 출력의 Normal termination, 주파수, 실제 프로세스도 함께 확인한다.
