# 서비스 이해와 가치 검증을 재현 실험으로 만들기

김정수 / FOMO Crew W2

> 핵심 메시지: 감으로 읽고 감으로 튜닝하던 일을, 단계와 검증이 있는 실험으로 바꿨다.

발표 시간: 7~10분

---

## 1. 문제

처음 보는 프로젝트와 서비스 알고리즘은 보통 이렇게 다뤄지기 쉽다.

- 파일이 많아서 어디부터 읽어야 할지 감으로 정한다
- 기술 스택을 보고 서비스의 핵심 가치를 성급하게 추측한다
- 알고리즘 점수식은 좋아 보이는 조합으로 튜닝한다
- 실제로 baseline보다 나아졌는지, 같은 입력에서 재현되는지 확인하기 어렵다

발표 멘트:
> 이번 작업은 프로젝트 분석과 알고리즘 튜닝을 감각의 영역에서 실험의 영역으로 옮긴 작업입니다.

---

## 2. 목표

> 서비스 관점 프로젝트 이해와 서비스 가치 알고리즘 평가를, fixture에서 실제 저장소와 실제 로그로 확장 가능한 재현 실험 하네스로 만든다.

이번 목표는 두 갈래다.

| 축 | 질문 | 산출물 |
|:---|:---|:---|
| 프로젝트 이해 | 서비스 가치를 빨리 복원하려면 어디부터 읽어야 하는가 | `project_scan.sh` |
| 알고리즘 평가 | 서비스 판단 기준이 baseline보다 실제 선택 품질을 높이는가 | `service_value_eval.sh` |
| 정답 검증 | silver label을 human gold로 승격할 수 있는가 | review/adjudication workflow |

---

## 3. 만든 구조

```text
Service Lens
  -> project_scan stages
  -> read-first recommendation
  -> verify_project_scan.sh

Service Hypothesis
  -> fixed cases / external dataset
  -> baseline vs hypothesis ranking
  -> verify_service_value_eval.sh

Public Real Logs
  -> prepared silver TSV
  -> blind human review pack
  -> reviewer adjudication
  -> gold-ready evaluation TSV
```

발표 멘트:
> 핵심은 문서만 만든 것이 아니라, 실행 스크립트와 검증 스크립트를 같이 붙였다는 점입니다.

---

## 4. 프로젝트 이해 하네스

`project_scan.sh`는 저장소를 네 단계로 읽는다.

| stage | 질문 | 출력 |
|:---:|:---|:---|
| 1 | 무엇이 얼마나 있는가 | 파일 수, 언어별 분포 |
| 2 | 진입점과 anchor는 무엇인가 | README, package, pyproject, env |
| 3 | 어느 영역부터 볼 것인가 | top-level area priority |
| 4 | 어떤 파일부터 열 것인가 | read-first file order |

추가한 점:

- `--profile real-repo`로 `fixtures/`, `usecases/`, `datasets/`, `reports/`, 생성물 제외
- `--report path.md`로 실행 결과를 Markdown 보고서로 저장
- stage 4 뒤에 서비스 관점의 읽기 이유를 출력

---

## 5. 프로젝트 이해 사례

같은 스캐너라도 서비스의 핵심 가치가 다르면 읽기 순서가 달라져야 한다.

| usecase | 서비스 핵심 | 기대 읽기 흐름 | 검증 결과 |
|:---|:---|:---|:---|
| `briefing-app` | 사용자가 아침 2분 안에 우선순위를 보는 web 접점 | `apps > services` | 통과 |
| `ops-handoff` | 야간 이슈를 정리하는 digest engine | `services > apps` | 통과 |
| `biz-planning` | 매출 가정과 리스크를 정렬하는 forecast engine | `services > apps` | 통과 |

예시 결과:

```text
biz-planning stage 4
README.md
services/forecasting/README.md
apps/planning-console/README.md
```

---

## 6. 서비스 가치 알고리즘 평가 하네스

`service_value_eval.sh`는 알고리즘을 점수식이 아니라 서비스 가설로 평가한다.

| stage | 질문 | 검증 |
|:---:|:---|:---|
| 0 | 어떤 서비스 결정을 더 잘 만들려는가 | hypothesis/baseline 문장화 |
| 1 | 어떤 고정 case set으로 평가하는가 | schema, rows, gold rank |
| 2 | 결정론적 순위를 내는가 | score, tie-break |
| 3 | baseline보다 나아졌는가 | top1 accuracy, MRR |
| 4 | 같은 입력에서 재현되는가 | repeated run equality |

발표 멘트:
> 알고리즘이 복잡한지가 아니라, 서비스가 중요하다고 말한 판단을 더 정확하게 재현하는지가 기준입니다.

---

## 7. 알고리즘 평가 결과

| usecase | baseline | hypothesis | 결과 |
|:---|:---|:---|:---|
| `briefing` | urgency만 본다 | due time, prep need, team impact, visibility 반영 | `top1 1.00` vs `0.33` |
| `ops-handoff` | severity만 본다 | SLA risk, VIP, overnight incident, revenue risk 반영 | `top1 1.00` vs `0.00` |
| `biz-planning` | forecast gap만 본다 | deadline, dependency, exec visibility, revenue impact 반영 | `top1 1.00` vs `0.20` |

중요한 점:

- `biz-planning` fixture는 baseline을 무조건 틀리게 만든 toy dataset이 아니다.
- gap-only가 맞는 case도 넣었고, 그래도 hypothesis가 전체 품질을 올리는지 봤다.

---

## 8. 실제 입력으로 확장

fixture만으로는 부족해서 공개 데이터셋으로 확장했다.

| dataset | 성격 | rows/cases | hypothesis | baseline |
|:---|:---|---:|:---|:---|
| Maven CRM Sales Opportunities | 공개 CRM pipeline, fictitious company | 32 rows / 8 cases | `top1=0.50`, `mrr=0.69` | `top1=0.25`, `mrr=0.53` |
| Olist Marketing Funnel + E-Commerce | 실제 익명화/샘플링 funnel/order 로그 | 48 rows / 12 cases | `top1=0.83`, `mrr=0.90` | `top1=0.33`, `mrr=0.54` |

해석:

- Olist는 실제 공개 로그라 fixture보다 현실성은 높다.
- 하지만 `expected_rank`는 사람이 찍은 gold가 아니라 deterministic silver label이다.
- 따라서 “실제 로그 proxy에서도 하네스가 동작했다”까지만 말해야 한다.

---

## 9. 실서비스 정답 검증으로 가는 길

Olist silver label을 바로 gold라고 부르지 않기 위해 human review workflow를 만들었다.

```text
olist_biz_planning_silver.tsv
  -> build_gold_review_pack.py
  -> olist_biz_planning_review_pack.tsv
     - expected_rank hidden
     - reviewer_rank blank
     - reviewer_rationale blank
  -> reviewer completed TSV
  -> apply_gold_review_labels.py
  -> olist_biz_planning_gold.tsv
```

Review pack:

- 12 cases
- 48 items
- `expected_rank` 비노출
- reviewer가 case별 1..N rank를 직접 입력

---

## 10. 복수 reviewer adjudication

실서비스 정답은 단일 reviewer보다 복수 reviewer 합의가 더 안전하다.

그래서 `adjudicate_gold_reviews.py`를 추가했다.

```text
reviewer A completed TSV
reviewer B completed TSV
  -> adjudicate_gold_reviews.py
  -> consensus cases: reviewer_rank 자동 prefill
  -> disagreement cases: reviewer_rank blank
  -> final adjudicator가 빈 rank를 채운 뒤 gold 적용
```

Contract test 결과:

| scenario | consensus | disagreement | guard |
|:---|---:|---:|:---|
| 완전 합의 | 12 | 0 | gold 적용 가능 |
| 일부 불일치 | 11 | 1 | final rank 전에는 적용 거부 |

발표 멘트:
> 아직 실제 human gold 파일은 없지만, 사람이 라벨을 주면 합의와 불일치를 분리해 과장 없이 gold로 승격할 수 있는 경로를 만들었습니다.

---

## 11. 검증 결과

실행한 주요 검증:

```bash
./kimjungsu/code/verify_project_scan.sh
./kimjungsu/code/verify_service_value_eval.sh
./kimjungsu/code/verify_dataset_preparation.sh
./kimjungsu/code/verify_gold_review_workflow.sh
git diff --check
```

통과한 범위:

- project scan fixture/usecase/boundary/baseline/smoke 검증
- service value algorithm reproducibility와 baseline 비교
- Maven CRM/Olist dataset 변환 재현성
- Olist review pack 재현성, `expected_rank` 비노출
- consensus/disagreement adjudication workflow
- invalid label reject

---

## 12. 한계

이번 결과를 말할 때 과장하면 안 되는 부분:

- 아직 실제 사업기획팀이 직접 찍은 human gold label 파일은 없다.
- Olist는 실제 로그지만 현재 평가는 silver label 기반이다.
- `real-repo` profile의 제외 규칙은 현재 저장소와 fixture에서는 검증됐지만, 더 큰 실제 저장소에서는 조정이 필요할 수 있다.
- metric은 현재 `top1_accuracy`, `MRR`, `mean_gold_rank` 중심이다.

그래서 현재 단계의 정확한 의미:

> 실서비스 검증을 완료한 것이 아니라, 실서비스 검증으로 갈 수 있는 재현 가능한 하네스와 검증 계약을 만들었다.

---

## 13. 데모 순서

짧게 보여줄 때:

```bash
bash kimjungsu/code/run_project_scan_usecase.sh biz-planning
bash kimjungsu/code/service_value_eval.sh biz-planning
bash kimjungsu/code/service_value_eval.sh --mode baseline biz-planning
./kimjungsu/code/verify_gold_review_workflow.sh
```

전체 검증을 보여줄 때:

```bash
./kimjungsu/code/verify_project_scan.sh
./kimjungsu/code/verify_service_value_eval.sh
./kimjungsu/code/verify_dataset_preparation.sh
./kimjungsu/code/verify_gold_review_workflow.sh
```

---

## 14. 마무리

이번 작업의 핵심은 기술을 더 많이 붙인 것이 아니다.

서비스 이해와 가치 검증을 아래 흐름으로 바꾼 것이다.

```text
서비스 가설
  -> 단계별 실행
  -> baseline 비교
  -> 실제 입력 확장
  -> human gold 준비
  -> 자동 검증
```

마지막 한 문장:

> 좋은 알고리즘은 복잡한 알고리즘이 아니라, 서비스가 중요하다고 말한 판단을 더 정확하게 재현하는 알고리즘입니다.
