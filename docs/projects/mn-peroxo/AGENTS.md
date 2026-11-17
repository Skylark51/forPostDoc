
# Mn 계산 및 시트 정리 규칙

- Gaussian input 파일명에 날짜를 넣지 않는다. 후속 output/checkpoint도 같은 stem을 사용한다. 충돌 시 짧은 retry 번호를 사용한다.
- 기존 TS 행을 가운데 두고 IRC reverse/forward endpoint를 바로 위와 아래에 배치한다. 각 기질의 기존 14-MTP 시트 방향 순서를 따른다.
- scan 입력 행과 다음 scan 입력 행 사이에는 빈 행 두 개를 둔다.
- 라이온 노드는 B열에 lion 접두사 없이 번호만 숫자로 입력한다.
- 진행 중인 계산의 베이지색은 **B열의 라이온 번호 셀에만** 적용한다. A열 파일명, C열 설명, D:S 데이터 셀이나 행 전체를 칠하지 않는다. 상태색은 기존 시트처럼 B열 노드 번호 셀로 표시한다.
- 실행 전 기존 시트의 행 배치·색상·노드 표기 규칙을 읽고 따른다.
- 실행 재시작이 필요하면 이번 작업에서 시작한 정확한 PID와 계산 stem만 대상으로 하고 다른 사용자·프로젝트 작업을 건드리지 않는다.

# Gaussian input 원본 양식

- 새 input은 동일 기질·계산 종류의 기존 input 템플릿을 복사해 작성한다. 임의로 헤더·route·제목·빈 줄 구성을 바꾸지 않는다.
- CPU는 기존 `%CPU=0-N`, 메모리는 해당 템플릿의 `%mem` 설정을 따른다. `%nprocshared`로 바꾸거나 자원을 일괄 통일하지 않는다.
- `%oldchk=/home/skylark/chk/<parent>.chk`, `%chk=/scratch/skylark/<stem>.chk` 경로를 사용한다. 해당 작업의 checkpoint만 정상 종료 후 archive 경로로 옮긴다.
- opt, freq, BB는 별도 input과 별도 출력으로 분리한다.
- integral=ultrafine, tight, maxcycles, calcfc 등 옵션을 임의로 추가하지 않는다. scan·IRC·TS 옵션은 해당 원본 템플릿을 따른다.
- 새 반응 좌표나 QST2·stable 진단처럼 목적상 필요한 계산 종류만 구분하고, 그 외 공통 형식과 계산 조건을 유지한다.


# Gaussian input conventions for this project

## 편집 전 필수 확인 — 2026-11-17 공통 지침

계산·시트·HTML 편집을 시작할 때 아래 순서로 확인하고 적용한다.

1. 이 파일과 Mn HTML의 작업 지침을 읽고, 대상 프로젝트·파일·시트 범위와
   사용자가 승인한 작업 범위를 확인한다. 계산 재시작과 새 계산 실행은 해당
   작업의 승인 범위를 따른다. 시트 추가·삭제는 사용자의 명시적 요청을 확인한다.
2. Lion에서 같은 단계의 원본 `.inp`, 실제 `wf` / `input.sh` 생성 방식,
   연결된 input/output/chk와 실행 중 프로세스를 읽는다. 후속 계산과 기질
   기준계도 해당 생성 방식 그대로 따른다.
3. 대상 시트의 열 정의·기준계·기존 그룹과 scan 간격을 읽고, 실제 파일명과
   참조 관계를 대조한다. 파일명 변경은 충돌과 참조, 실행 중 파일 보호를
   확인한 뒤 처리한다.
4. 공유 forPostDoc 저장소는 최신 원격 상태와 변경 목록을 확인한다.
   이 프로젝트 작업은 `docs/projects/mn-peroxo/` 안에서 수행한다.
5. 편집 후 변경 범위, 파일 참조, 행 배치, 원자료 값과 HTML 표시를 대조한다.
   계산 실행·시트 구조 변경·게시 여부를 실제 수행 결과에 맞춰 보고한다.

## Excel / Google Sheets 및 계산 공통 규칙

- 계산 input/output/chk 파일명에는 날짜를 붙이지 않는다. 날짜는 보고서와
  제어 기록에서 관리한다. 기존 날짜 제거는 충돌·참조·실행 상태 확인 후 수행한다.
- Dumbo와 Tachyon의 B열 값은 각각 `dumbo`, `tachyon`으로 기록한다.
  두 서버에 임의 scratch 번호를 부여하지 않는다.
- A열은 실제 파일명 또는 하단 계산의 성격을 나타내는 간결한 제목으로 쓴다.
  그룹 제목은 **bold**로 표시한다. 운영·복구 메모는 HTML에서 관리한다.
- 동일 구조의 freq와 BB는 한 행에 기록한다. A열은 freq 파일명,
  E열은 대응하는 BB 결과를 사용한다. 같은 구조를 freq/BB 별도 행으로 나누지 않는다.
- Scan 행의 위아래에 한 행씩 확보해 scan과 scan 사이에 두 행 간격을 유지한다.
  TS → IRC → IRC endpoint opt → freq → BB를 실제 wf 흐름과 파일 참조에 맞춰 연결한다.
- NBO/stable 등 사용자가 명시한 예외를 제외한 계산은 기존 함수·용매·조건과
  wf/input.sh의 route를 유지한다. 요청하지 않은 UltraFineGrid와 route 변경을 추가하지 않는다.
- Excel/Google Sheets에는 이해하기 쉬운 raw data를 기록한다.
  분석·복구 과정, 판단 근거와 실행 경과는 HTML에 기록한다.
- 보고와 지침은 사실·수치·현재 상태를 명료하게 설명한다.
  `~로 단정하지 않겠습니다`, `~라는 의미는 아닙니다` 같은 부정재진술을 피하고
  확인된 결과와 남은 검증을 직접 쓴다.

아래 Gaussian 형식은 이 프로젝트의 원본 템플릿 기준이다. 2026-11-16 FMM 항목은
당시 복구 작업의 기록이며, 이후 작업은 위 승인·원본 확인 절차를 먼저 적용한다.

The user requires their existing Gaussian input manner. Before creating inputs,
read the closest original `.inp` for the same calculation stage on Lion.

- Preserve the established scientific filename and append stage suffixes:
  `-scan-freq-ts-freq-ircfwd-opt-freq` / `-ircrev-opt-freq`, and `-bb` as applicable.
  For 12-MTP PPA use the existing `forCoord` / `AfterCoord-forPHA` naming families.
  Keep run dates and controller metadata outside scientific filenames.
- Use `%CPU=0-15`, `%mem=60Gb`, `%chk=/scratch/skylark/<stem>.chk`, and the
  original `%oldchk` convention. Preserve the closest template's header ordering.
- Use stage titles `opt`, `freq`, `TS opt`, `IRC forward`, `IRC reverse`,
  and `large basis set`; do not substitute filenames or custom prose titles.
- Preserve the original route keyword ordering. Normal settings in this project
  are UB3LYP/def2-SVP, CPCM(acetonitrile), GD3BJ,
  `scf=(xqc,maxconventionalcycles=60)`, `nosymm`. BB uses def2-TZVPP.
- For a scan-derived TS, follow the user's separate freq ->
  `opt=(ts,rcfc,nofreeze,noeigentest)` -> freq -> IRC -> opt -> freq workflow.
  The usual IRC template is `irc=(rcfc,forward/reverse,lqa,stepsize=25)`.
- Preserve atom order, coordinate formatting, charge and multiplicity from the
  source model. The present 12-MTP PPA model is charge +1, multiplicity 5.
- Do not silently add numerical settings such as UltraFine, `maxcycle=512`,
  or generic optimizer cycle/step limits. A necessary recovery change must be
  minimal, recorded separately, and explained with its concrete reason.
- The 2026-11-16 PPA recovery currently uses `int=fmmnatoms=1000` to avoid
  the FMM-enabled l703 path where the original Coord scan crashed. This is a
  documented recovery exception, not a new project-wide default.
- Do not rewrite an input while claiming it represents a running calculation.
  Preserve superseded files and checkpoint data, then restart with corrected
  inputs when a substantive input correction is required.
