# Use Case: Support Ops Handoff Priority Algorithm

## 서비스 가설

이 서비스의 핵심 가치는 support ops lead가
오늘 가장 먼저 대응할 고객과 이슈를 빠르게 고르게 만드는 것이다.

그래서 알고리즘 가설도 아래처럼 서비스 판단 기준으로 적는다.

- baseline: severity만 보면 된다
- hypothesis: severity만으로는 부족하고, `SLA risk`, `VIP`, `overnight incident`, `revenue risk`를 함께 반영해야 첫 대응 선택이 더 정확해진다

즉 이 실험은
"스코어가 복잡해졌다"가 아니라
**"support lead의 첫 대응 선택이 더 정확해지는가"**를 검증한다.

## 객관적 실험 설계

- fixture: `fixtures/service_value/ops_handoff_priority_cases.tsv`
- 평가 단위: case별 gold 1위 항목
- baseline 비교: severity-only
- hypothesis 비교: SLA/VIP/overnight/revenue 반영
- metric:
  - `top1_accuracy`
  - `MRR`
  - `mean_gold_rank`

## 재현성 계약

- 고정 TSV fixture를 쓴다
- scorer는 결정론적이다
- tie-break는 `item_id` 사전순이다
- 같은 명령을 두 번 실행했을 때 완전히 같은 출력이 나와야 한다

## 실행

```bash
bash kimjungsu/code/service_value_eval.sh ops-handoff
bash kimjungsu/code/service_value_eval.sh --mode baseline ops-handoff
bash kimjungsu/code/verify_service_value_eval.sh
```
