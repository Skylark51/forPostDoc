
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
