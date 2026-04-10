#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN_SCRIPT="$SCRIPT_DIR/project_scan.sh"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
USECASE="${1:-briefing-app}"

resolve_usecase_path() {
  case "$USECASE" in
    briefing-app)
      printf '%s\n' "$ROOT_DIR/fixtures/briefing_app"
      ;;
    ops-handoff)
      printf '%s\n' "$ROOT_DIR/fixtures/ops_handoff"
      ;;
    sample-app)
      printf '%s\n' "$ROOT_DIR/fixtures/sample_app"
      ;;
    docs-only)
      printf '%s\n' "$ROOT_DIR/fixtures/docs_only"
      ;;
    *)
      printf '%s\n' "$USECASE"
      ;;
  esac
}

print_usecase_header() {
  case "$USECASE" in
    briefing-app)
      cat <<'EOF'
== Use Case ==
name=briefing-app
scenario=하루 시작 전에 여러 도구를 훑어야 하는 팀 리드를 위한 morning briefing 서비스 저장소를 처음 인수인계받았다고 가정한다
decision=고객 가치가 어디서 만들어지고 어떤 영역부터 읽어야 그 가치를 빨리 복원할지 결정해야 한다
success_condition=stage별 결과만으로 고객, 가치 순간, 탐색 순서를 함께 설명할 수 있다
EOF
      ;;
    ops-handoff)
      cat <<'EOF'
== Use Case ==
name=ops-handoff
scenario=야간 이슈와 우선 대응 계정을 아침 5분 안에 파악해야 하는 support ops 리드를 위한 handoff 서비스 저장소를 처음 인수인계받았다고 가정한다
decision=고객이 체감하는 핵심 가치가 admin UI보다 digest engine에 더 가까운지, 어디부터 읽어야 그 가치를 빨리 복원할지 결정해야 한다
success_condition=stage별 결과만으로 고객, 가치 엔진, 탐색 순서를 함께 설명할 수 있다
EOF
      ;;
    *)
      cat <<EOF
== Use Case ==
name=$USECASE
scenario=사용자 정의 유즈케이스
decision=서비스 가치와 탐색 순서를 빠르게 복원해야 한다
success_condition=stage별 결과만으로 첫 탐색 순서를 설명할 수 있다
EOF
      ;;
  esac
  echo
}

print_service_lens() {
  case "$USECASE" in
    briefing-app)
      cat <<'EOF'
[service lens]
target_customer=10~80명 규모 스타트업의 팀 리드 또는 운영 리드
status_quo=아침마다 Google Calendar, Slack, Notion, 작업 목록을 따로 열어 오늘 우선순위를 수동으로 정리한다
pain=중요한 일정 준비를 놓치고, 팀 상황과 개인 우선순위를 연결하는 데 10~15분이 든다
service_goal=아침 2분 안에 오늘의 일정, 준비 포인트, 핵심 우선순위를 한 번에 파악하게 한다
core_job=하루 시작 전에 "무엇을 먼저 해야 하는가"를 빠르게 결정한다
value_moment=앱을 열자마자 오늘의 브리핑이 정리되어 바로 행동 순서가 보이는 순간
technology_role=web은 고객이 가치를 체감하는 접점이고, python service는 브리핑 품질과 우선순위 로직을 책임지는 도구다
non_goal=프로젝트 관리 도구 전체를 대체하거나, 프레임워크 취향 자체를 논하는 것이 목적이 아니다
hard_gate=기술 분석은 서비스 가치와 연결될 때만 의미가 있다
EOF
      ;;
    ops-handoff)
      cat <<'EOF'
[service lens]
target_customer=30~200명 규모 SaaS 회사의 support operations lead 또는 CX lead
status_quo=아침마다 Zendesk, Slack, 온콜 로그, VIP 고객 메모를 따로 열어 야간 이슈와 오늘의 우선 대응 계정을 수동으로 정리한다
pain=야간 이슈를 놓치거나, 중요한 고객 대응 순서를 늦게 잡아 첫 30분이 항상 복구 작업으로 소모된다
service_goal=아침 5분 안에 야간 이슈, 위험 계정, 오늘 먼저 대응할 항목을 자동 handoff로 정리해준다
core_job=오늘 가장 먼저 대응해야 할 고객과 이슈를 빠르게 결정한다
value_moment=출근 직후 handoff를 열었을 때 긴급도와 우선 대응 순서가 이미 정리되어 있는 순간
technology_role=python service는 digest 품질과 우선순위 산출을 책임지는 가치 엔진이고, admin web은 운영자가 결과를 점검하는 보조 도구다
non_goal=대시보드 화면 수를 늘리거나 운영 툴 전체를 대체하는 것이 목적이 아니다
hard_gate=기술 분석은 서비스 가치와 연결될 때만 의미가 있다
EOF
      ;;
    *)
      cat <<EOF
[service lens]
user=unknown
core_job=이 유즈케이스의 서비스 목적을 먼저 정의해야 한다
value_moment=unknown
technology_role=기술은 서비스 이해를 돕는 도구로만 해석한다
non_goal=기술 스택 자체를 목적화하지 않는다
hard_gate=service lens 없이 기술 해석을 확정하지 않는다
EOF
      ;;
  esac
  echo
}

print_stage_analysis() {
  local stage="$1"
  case "$USECASE:$stage" in
    briefing-app:1)
      cat <<'EOF'
[analysis stage 1]
question=이 서비스가 단순 UI 프로젝트인지, 고객 가치와 생성 엔진이 함께 있는 혼합형 서비스인지
decision_hint=markdown, python, typescript 비중을 보고 고객 접점과 브리핑 생성 로직이 함께 있는지 판단한다
failure_signal=총 파일 수나 언어 분포가 이상하면 이후 단계 해석이 모두 흔들린다
EOF
      ;;
    briefing-app:2)
      cat <<'EOF'
[analysis stage 2]
question=고객이 가치를 체감하는 접점과 그 가치를 만드는 엔진 anchor가 어디에 있는가
decision_hint=README, package.json, pyproject.toml, tsconfig.json이 모두 잡히면 고객 접점과 생성 엔진의 분리를 설명할 수 있다
failure_signal=anchor가 비어 있거나 잘못 분류되면 ecosystem 판단이 흔들린다
EOF
      ;;
    briefing-app:3)
      cat <<'EOF'
[analysis stage 3]
question=상위 영역 중 어디부터 파야 하는가
decision_hint=apps가 1위면 고객이 가치를 느끼는 화면부터 보고, services가 2위면 브리핑 품질을 만드는 로직은 그 다음에 본다
failure_signal=docs나 ROOT가 과도하게 상위로 뜨면 우선순위 휴리스틱을 재검토한다
EOF
      ;;
    briefing-app:4)
      cat <<'EOF'
[analysis stage 4]
question=지금 당장 열어야 할 파일 5개는 무엇인가
decision_hint=README -> 고객 접점 README -> 가치 엔진 README -> manifest/tooling 순서면 서비스 우선 탐색 흐름으로 적절하다
failure_signal=존재하지 않는 파일 추천, 이유 없는 추천, source 파일이 너무 이르게 뜨는 경우를 점검한다
EOF
      ;;
    ops-handoff:1)
      cat <<'EOF'
[analysis stage 1]
question=이 서비스가 단순 admin UI인지, 운영 가치의 핵심이 자동 분류 엔진에 있는 서비스인지
decision_hint=python 비중과 문서 구조를 보고 자동 handoff 엔진이 별도 존재하는지 판단한다
failure_signal=코드/문서 비중이 어색하면 서비스 가치가 어디서 만들어지는지 해석이 흔들린다
EOF
      ;;
    ops-handoff:2)
      cat <<'EOF'
[analysis stage 2]
question=고객 가치 엔진과 운영용 보조 UI의 anchor가 각각 어디에 있는가
decision_hint=service pyproject와 service README가 명확하면 digest 엔진이 별도 책임을 가진다고 볼 수 있다
failure_signal=service anchor가 약하면 admin UI 중심 저장소로 잘못 해석할 수 있다
EOF
      ;;
    ops-handoff:3)
      cat <<'EOF'
[analysis stage 3]
question=상위 영역 중 어디부터 파야 하는가
decision_hint=services가 1위면 handoff 품질을 만드는 엔진부터 보고, apps가 2위면 운영용 점검 UI는 그 다음에 본다
failure_signal=apps가 과도하게 상위로 뜨면 서비스 가치보다 보조 도구가 과대평가된 것일 수 있다
EOF
      ;;
    ops-handoff:4)
      cat <<'EOF'
[analysis stage 4]
question=지금 당장 열어야 할 파일 5개는 무엇인가
decision_hint=README -> 가치 엔진 README -> 보조 UI README -> service manifest 순서면 서비스 중심 탐색 흐름으로 적절하다
failure_signal=admin 관련 파일이 엔진 문서보다 먼저 나오면 서비스 목표 대비 추천 순서를 재검토한다
EOF
      ;;
    *:1)
      cat <<'EOF'
[analysis stage 1]
question=이 저장소가 문서 중심인지 코드 중심인지, 그리고 어떤 언어가 섞여 있는가
decision_hint=언어와 문서 분포를 보고 혼합형 저장소인지 판단한다
failure_signal=총 파일 수나 언어 분포가 이상하면 이후 단계 해석이 모두 흔들린다
EOF
      ;;
    *:2)
      cat <<'EOF'
[analysis stage 2]
question=핵심 진입점과 엔진 anchor가 어디에 있는가
decision_hint=README, manifest, config가 모두 잡히면 구조를 설명할 수 있다
failure_signal=anchor가 비어 있거나 잘못 분류되면 ecosystem 판단이 흔들린다
EOF
      ;;
    *:3)
      cat <<'EOF'
[analysis stage 3]
question=상위 영역 중 어디부터 파야 하는가
decision_hint=우선순위 1위 영역을 먼저 보고, 2위 영역으로 구현 상세를 따라간다
failure_signal=문서나 ROOT가 과도하게 상위로 뜨면 우선순위 휴리스틱을 재검토한다
EOF
      ;;
    *:4)
      cat <<'EOF'
[analysis stage 4]
question=지금 당장 열어야 할 파일 5개는 무엇인가
decision_hint=루트 설명 -> 핵심 영역 README -> 실행/설정 정보 순서면 온보딩용 탐색 흐름으로 적절하다
failure_signal=존재하지 않는 파일 추천, 이유 없는 추천이 나오면 추천 규칙을 점검한다
EOF
      ;;
  esac
  echo
}

TARGET="$(resolve_usecase_path)"

if [ ! -d "$TARGET" ]; then
  echo "error: use case target not found: $TARGET" >&2
  exit 1
fi

if [ "$USECASE" = "briefing-app" ] || [ "$USECASE" = "ops-handoff" ]; then
  print_usecase_header
else
  echo "== Use Case =="
  echo "name=$USECASE"
  echo "target=$TARGET"
  echo
fi

print_service_lens

for stage in 1 2 3 4; do
  bash "$SCAN_SCRIPT" --stage "$stage" "$TARGET"
  print_stage_analysis "$stage"
done
