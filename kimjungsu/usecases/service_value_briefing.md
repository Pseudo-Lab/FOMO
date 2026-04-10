# Use Case: Briefing Priority Algorithm

## 서비스 가설

이 서비스의 핵심 가치는 "오늘 무엇을 먼저 해야 하는가"를
아침 2분 안에 결정하게 만드는 것이다.

따라서 알고리즘 가설도 기술 언어보다 서비스 언어로 적는다.

- baseline: urgency만 보면 된다
- hypothesis: urgency만으로는 부족하고, `due time`, `prep need`, `team impact`, `user visibility`를 함께 반영해야 첫 행동 선택이 더 정확해진다

즉 이 실험은
"더 복잡한 점수식이 좋은가"가 아니라
**"사용자가 첫 행동을 더 맞게 고르게 되는가"**를 검증한다.

## 객관적 실험 설계

- fixture: `fixtures/service_value/briefing_priority_cases.tsv`
- 평가 단위: case별 gold 1위 항목
- baseline 비교: urgency-only
- hypothesis 비교: due/prep/team/user-visible 반영
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
bash kimjungsu/code/service_value_eval.sh briefing
bash kimjungsu/code/service_value_eval.sh --mode baseline briefing
bash kimjungsu/code/verify_service_value_eval.sh
```
