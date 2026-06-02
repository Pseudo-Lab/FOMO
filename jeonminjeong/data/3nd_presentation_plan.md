# Full-Duplex 음성 AI, 두 번째 이야기 — 빠름의 대가와 "들으면서 생각하기"

> 가짜연구소 12기 스터디 발표 골격 (논문 리뷰 / 약 45분 + Q&A 10분, 19장)
> 작성 기준일: 2026-06-02
> 내용 검증 기준: 2026-06-02 기준 공개 원문/공식 페이지/벤치마크 기사 확인
> 발표 표기 권장: "본 발표의 논문·벤치마크 수치는 2026-06-02 기준입니다."

---

## 핵심 주장 (Thesis)

Full-duplex 음성 모델은 **빠름(fast) vs 똑똑함(smart)의 본질적 긴장** 위에 있다.
오픈소스 세대(Moshi → PersonaPlex → Nemotron 3 VoiceChat)는 `ASR → LLM → TTS` 캐스케이드를 **하나의 빠른 단일 모델**로 합치는 데 *수렴*했지만, 그 대가로 추론 능력을 잃었다.
지금 프런티어는 "지연을 늘리지 않고 사고를 되돌리는" 방향으로 갈라지며, 그 가장 활발한 갈래가 **think-while-listening(들으면서 생각하기)** 이다.

> ⚠️ 검증 메모: 흔히 오해되는 지점 — "interaction model + background model(빠른/느린 경로) 분리"는 Moshi/PersonaPlex/Nemotron 3 VoiceChat이 도달한 수렴점이 **아니라**, Thinking Machines가 기존 full-duplex 모델들을 반례 또는 선행 사례로 깔며 새로 제안한 구조다. 발표에서는 이 점을 명확히 구분한다(슬라이드 5~7 참조).

---

## 발표 흐름 한눈에

| 부 | 내용 | 장수 | 시간 |
|----|------|------|------|
| 1부 | 리마인더 (지난주 회수) | 1 | 2분 |
| 2부 | 지도 — 진짜 수렴과 그 대가 | 6 | 16분 |
| 3부 | think-while-listening, 네 갈래 (펀치라인) | 9 | 22분 |
| 4부 | takeaway & 열린 질문 | 3 | 5분 |

**복선 회수 구조:** 슬라이드 14(종합 비교표)가 슬라이드 9~13의 다섯 논문을 한 장으로 모으고, 그 표의 "추가 지연" 열이 슬라이드 5(fast-vs-smart Pareto)와 다시 연결된다.

---

## 슬라이드별 구성 정리 (제작용)

> 원칙: 각 슬라이드는 **한 문장 주장 + 근거 2~3개 + 시각 요소 1개**로 구성한다. 세부 설명은 발표자가 말로 보충하고, 슬라이드는 청중이 길을 잃지 않게 해주는 지도 역할에 집중한다.

### 슬라이드 1. 지난주에서 오늘로

- **한 장의 메시지:** 지난주는 "왜 어려운가", 오늘은 "어떻게 풀 것인가"를 본다.
- **화면 구성:** 좌우 2분할.
  - 왼쪽: 지난주 키워드 `barge-in`, `backchannel`, `silence`
  - 오른쪽: 오늘 질문 `빠르게 말하려면, 생각할 시간은 어디서 얻는가?`
- **발표 포인트:** 문제 정의에서 해법 구조로 넘어가는 속편임을 짧게 회수한다.

### 슬라이드 2. 캐스케이드의 한계

- **한 장의 메시지:** `ASR → LLM → TTS`는 대화가 아니라 순차 처리다.
- **화면 구성:** 3단 파이프라인 그림.
  - ASR 아래: `latency`
  - LLM 아래: `text bottleneck`
  - TTS 아래: `turn-based`
- **발표 포인트:** full-duplex의 핵심 난점은 "빠른 응답"만이 아니라 끼어들기, 중첩 발화, 비언어 정보 보존이다.

### 슬라이드 3. 진짜 수렴 = 하나의 빠른 단일 모델

- **한 장의 메시지:** 오픈소스 full-duplex는 하나의 빠른 end-to-end 모델로 수렴했다.
- **화면 구성:** 계보도 `Moshi → PersonaPlex → Nemotron 3 VoiceChat`.
  - Moshi: `inner monologue + multi-stream`
  - PersonaPlex: `Moshi 기반 + persona/voice conditioning`
  - Nemotron: `conformer + LLM backbone + TTS decoder`
- **발표 포인트:** Thinking Machines의 2-model split과 혼동하지 않는다. 여기서 말하는 수렴은 "단일 모델화"다.

### 슬라이드 4. 단일 모델 안의 토큰 전략 taxonomy

- **한 장의 메시지:** 단일 모델 안에서도 텍스트와 음성 토큰을 엮는 방식은 갈린다.
- **화면 구성:** 3열 표 또는 3개 카드.
  - `Thinker-Talker`
  - `Interleaved / Parallel Token`
  - `Cascaded-with-Controller`
- **발표 포인트:** taxonomy 자체를 깊게 설명하기보다, 뒤의 think-while-listening 논문들을 분류하기 위한 지도 역할로 둔다.

### 슬라이드 5. 그 대가 — fast vs smart

- **한 장의 메시지:** 빠르고 자연스러운 모델일수록 추론은 약해지는 경향이 있다.
- **화면 구성:** Pareto 산점도 필수.
  - x축: conversational dynamics
  - y축: speech reasoning
  - 강조점: PersonaPlex, Moshi, Freeze-Omni, Nemotron 3 VoiceChat
- **발표 포인트:** 단일 모델 수렴은 성공했지만 문제가 끝난 것이 아니다. Nemotron은 open weights 모델 중 양 축 top 3에 드는 균형형 예외로 제시한다.

### 슬라이드 6. 그래서 질문

- **한 장의 메시지:** 지연을 늘리지 않고 추론을 되돌릴 수 있을까?
- **화면 구성:** 두 갈래 비교.
  - 왼쪽: `interaction model + background model`
  - 오른쪽: `think-while-listening`
- **발표 포인트:** 오늘 발표는 오른쪽, 즉 단일 모델 안에서 listening 시간을 추론 시간으로 바꾸는 흐름에 집중한다.

### 슬라이드 7. 인간의 답 — 들으면서 생각하기

- **한 장의 메시지:** 사람은 듣고 나서 생각하지 않는다. 들으면서 생각한다.
- **화면 구성:** timeline.
  - `user speech`
  - `model listening`
  - `model thinking`이 user speech 중간부터 겹쳐 시작
  - `response latency` 감소
- **발표 포인트:** TM의 2-model 구조는 기존 모델들의 수렴점이 아니라 별도 제안이라는 구분을 한 번 더 짚는다.

### 슬라이드 8. 공통 gap

- **한 장의 메시지:** 기존 모델은 듣는 동안 사실상 멈춰 있다.
- **화면 구성:** before/after timeline.
  - 기존: `silence, silence, silence`
  - 목표: `partial reasoning, partial reasoning`
- **발표 포인트:** 3부 전체의 문제 정의다. listening 구간을 idle로 버리지 않는 것이 공통 목표다.

### 슬라이드 9. 갈래 A-1 — Can Speech LLMs Think while Listening?

- **한 장의 메시지:** 질문이 충분해지는 순간부터 텍스트 CoT를 시작한다.
- **화면 구성:** speech input timeline 위에 entropy/question completeness threshold 표시.
- **핵심 키워드:** `text CoT`, `question completeness`, `DPO`, `latency 70% 감소`
- **발표 포인트:** accuracy-latency trade-off를 명시적으로 제어하는 사례로 소개한다.

### 슬라이드 10. 갈래 A-2 — SHANKS

- **한 장의 메시지:** 턴이 끝나기 전, chunk마다 숨은 CoT를 만든다.
- **화면 구성:** chunked input → unspoken CoT → interruption/tool-call/action.
- **핵심 키워드:** `unspoken CoT`, `interruption`, `tool-call`
- **발표 포인트:** 추론 정확도뿐 아니라 끼어들기와 tool-call 타이밍으로 연결되는 점을 강조한다.

### 슬라이드 11. 갈래 B — Chronological Thinking

- **한 장의 메시지:** 사고를 한 번에 몰아서 하지 않고 listening window에 분산한다.
- **화면 구성:** listening window 안에 reasoning block들이 분산된 timeline.
- **핵심 키워드:** `amortized reasoning`, `strictly causal`, `no additional latency`
- **발표 포인트:** "무엇을 생각하나"보다 "언제 생각하나"에 초점이 있는 논문으로 배치한다.

### 슬라이드 12. 갈래 C — FLAIR / The Silent Thought

- **한 장의 메시지:** 생각은 꼭 텍스트일 필요가 없다.
- **화면 구성:** latent embedding이 다음 step으로 재귀 입력되는 순환 도식.
- **핵심 키워드:** `latent reasoning`, `recursive embedding`, `ELBO`, `no explicit CoT annotation`
- **발표 포인트:** 텍스트 CoT 계열과 가장 대비되는 갈래로, 해석성 vs 확장성 토론을 여는 장이다.

### 슬라이드 13. 갈래 D — GoT-duplex

- **한 장의 메시지:** 추론 대상이 답변이 아니라 대화 행동일 수도 있다.
- **화면 구성:** `perception → thought graph → action` 그래프.
- **핵심 키워드:** `Graph-of-Thoughts`, `behavior reasoning`, `interpretable rationale`
- **발표 포인트:** QA reasoning에서 conversational behavior reasoning으로 문제 범위를 확장한다.

### 슬라이드 14. 종합 비교표

- **한 장의 메시지:** 공통 목표는 latency budget을 깨지 않고 reasoning을 앞당기는 것이다.
- **화면 구성:** 5행 × 5열 비교표. 각 셀은 1~3단어로 줄인다.
- **강조 열:** `추가 지연`
- **발표 포인트:** 슬라이드 5의 Pareto와 다시 연결한다. "빠름을 유지하면서 smart를 회복하려는 시도"로 회수한다.

### 슬라이드 15. 공통 인사이트

- **한 장의 메시지:** 차이는 표현형식, 공통점은 post-hoc 사고 거부다.
- **화면 구성:** 2축 매트릭스.
  - x축: timing control 약함 → 강함
  - y축: thought representation `text → latent/structured`
  - 다섯 논문을 점으로 배치
- **발표 포인트:** 논문 나열이 아니라 하나의 연구 지형도로 보이게 만든다.

### 슬라이드 16. 미해결 과제

- **한 장의 메시지:** 아직 표준 답은 없다.
- **화면 구성:** 질문 3개만 크게 배치.
  - `Text CoT vs latent reasoning`
  - `Accuracy-latency joint benchmark`
  - `Korean paralinguistic benchmark`
- **발표 포인트:** 본인 연구와 연결할 수 있는 지점을 여기서 자연스럽게 제시한다.

### 슬라이드 17. 한 문장 결론

- **한 장의 메시지:** Full-duplex는 빠름의 대가로 추론을 잃었고, 들으면서 생각하기가 그 절충안으로 떠올랐다.
- **화면 구성:** 큰 결론 문장 + 작은 흐름도.
  - `single model convergence → reasoning collapse → think-while-listening`
- **발표 포인트:** 2부와 3부를 한 문장으로 회수한다.

### 슬라이드 18. 열린 질문

- **한 장의 메시지:** 다음 질문은 "무엇을 생각하나"와 "언제 말하나"다.
- **화면 구성:** Q&A 유도 질문 3~4개.
  - 사고는 텍스트여야 하나?
  - 언제 생각을 멈추고 말할까?
  - 멀티모달까지 가면 어떻게 확장될까?
  - 한국어 대화 신호는 어떻게 평가할까?
- **발표 포인트:** 청중에게 선택지를 던지는 장으로 사용한다.

### 슬라이드 19. 참고문헌

- **한 장의 메시지:** 근거 논문과 자료는 세 그룹으로 나뉜다.
- **화면 구성:** 그룹별 reference list.
  - 오픈소스 단일 모델
  - interaction + background 프레임
  - think-while-listening
- **발표 포인트:** 세부 URL을 다 읽지 말고, QR 코드나 공유 문서 링크가 있으면 함께 제공한다.

---

## 1부 — 리마인더 (1장)

### 슬라이드 1. 지난주에서 오늘로

- 지난주(12기): 풀듀플렉스가 *왜* 어려운가 — barge-in, backchannel, 침묵. (회수 한 줄)
- 오늘의 질문: "*어떻게* 푸는가 — 그런데 빠르게 풀면 똑똑함을 잃는다."
- 프레임: "문제편 → 해법편"의 속편.
- *출처: 직전 발표(자체 자료)*

---

## 2부 — 지도: 진짜 수렴과 그 대가 (6장)

### 슬라이드 2. 캐스케이드의 한계

- `ASR → LLM → TTS`의 문제: 단계마다 지연 누적, 비언어 정보 손실, 턴 기반이라 끼어들기·중첩 발화 붕괴.
- Moshi는 기존 파이프라인의 latency, text bottleneck, turn segmentation 문제를 명시한다.
- Step-Audio 계열도 ASR+LLM+TTS 파이프라인의 지연·오류 누적과 paralinguistic modeling 한계를 문제로 둔다.
- *출처: Moshi (arXiv:2410.00037); Step-Audio 2 (arXiv:2507.16632; stepfun.ai/docs/en/step-audio2)*
- *최신성 주석: 2026-05-22 기준 StepAudio 2.5 Technical Report(arXiv:2605.23463)도 공개되어 있다. taxonomy 근거는 Step-Audio 2로 충분하지만, "최신 Step-Audio"라고 말할 때는 2.5를 함께 언급한다.*

### 슬라이드 3. 진짜 수렴 = "하나의 빠른 단일 모델"

- Moshi 계보: inner monologue(텍스트 토큰을 오디오의 prefix로 예측) + multi-stream(사용자/시스템 음성 병렬, 턴 제거).
- PersonaPlex: Moshi 기반, Moshi 가중치로 초기화된 7B full-duplex 모델. Role conditioning과 voice conditioning을 추가해 페르소나/음성 제어를 확장.
- Nemotron 3 VoiceChat: conformer speech encoder → Nemotron Nano V2 LLM backbone(텍스트 예측) → TTS decoder. PersonaPlex의 persona/voice control 계열을 이어받아 12B open model로 확장.
- 메시지: 다들 "캐스케이드 → 단일 end-to-end full-duplex 모델"로 모였다 = 진짜 수렴은 여기.
- *출처: Moshi (arXiv:2410.00037); PersonaPlex (arXiv:2602.06053, research.nvidia.com/labs/adlr/personaplex); Nemotron 3 VoiceChat (build.nvidia.com/nvidia/nemotron-voicechat/modelcard)*
- *검증 주석: NVIDIA 프로젝트 페이지는 PersonaPlex가 Moshi architecture 기반 7B 모델이며 underlying language model이 Helium이라고 설명한다. 논문/발표에서는 "Moshi architecture 기반, Moshi weights로 초기화"를 기본 표현으로 두고, Helium은 Moshi 계열 백본 설명으로 보조 언급한다.*

### 슬라이드 4. 단일 모델 안의 토큰 전략 3분류 (taxonomy)

- **Thinker-Talker**: 텍스트 추론(Thinker)이 음향 합성(Talker)에 선행 — Qwen2.5-Omni / Qwen3-Omni 등.
- **Interleaved / parallel token**: 텍스트·오디오 토큰을 고정 비율 또는 병렬 스트림으로 교차 — Moshi, Step-Audio 2.
- **Cascaded-with-controller**: 외부 모듈이 듣기/말하기 상태 판단 — Freeze-Omni 등.
- *출처: Covo-Audio Technical Report (arXiv:2602.09823); Step-Audio 2 (arXiv:2507.16632)*

### 슬라이드 5. 그 대가 — fast vs smart (★ 2부 클라이맥스)

- Pareto 산점도: 가로 conversational dynamics(Full-Duplex-Bench) × 세로 speech reasoning(Big Bench Audio).
- 확인 수치:
  - PersonaPlex: dynamics 91.0% / reasoning 12.6%
  - Moshi: reasoning 1.7%
  - Freeze-Omni: reasoning 33.9%
  - Nemotron 3 VoiceChat: dynamics 77.8% / reasoning 29.2%
- 메시지: 빠르고 자연스러운 대화 역학을 얻을수록 추론이 무너지는 경향이 보인다 = fast vs smart 긴장의 증거.
- 단, Nemotron 3 VoiceChat은 open weights 모델 중 양 축 모두 top 3에 드는 균형형 모델로 보고된다.
- *출처: Artificial Analysis, "Nemotron 3 VoiceChat: Conversational Dynamics vs Speech Reasoning" (artificialanalysis.ai/articles/nemotron-3-voicechat-leader-speech-pareto)*

### 슬라이드 6. 그래서 질문

- "지연을 늘리지 않고 추론을 되돌릴 수 있을까?"
- 두 갈래 예고:
  - (a) Thinking Machines식 interaction model + background model 분리
  - (b) 단일 모델 내 think-while-listening
- 오늘은 (b)에 집중.
- *출처: Thinking Machines (thinkingmachines.ai/blog/interaction-models)*

### 슬라이드 7. 인간의 답 — "우린 들으면서 생각한다"

- 인지과학적 직관: 인간은 상대 발화가 끝나기 전부터 듣는 동시에 사고하며, 이는 적시 반응·끼어들기·응답 준비를 가능하게 한다.
- 3부로 가는 다리: 모델도 listening 구간을 idle로 두지 않고, 그 시간에 추론을 앞당길 수 있을까?
- ⚠️ 구분 강조: interaction model + background model 분리는 Thinking Machines의 *새 제안*이지 슬라이드 3 모델들의 수렴점이 아니다.
- *출처: SHANKS (arXiv:2510.06917); Thinking Machines (thinkingmachines.ai/blog/interaction-models); 외부 분석 seangoedecke.com/interaction-models*

---

## 3부 — think-while-listening, 네 갈래 (9장, 펀치라인)

> 조직 원리: **전제는 하나(들으며 사고), 해법은 둘로 분기 — (1) '생각'을 어떤 형태로 표현하나, (2) 언제 사고를 시작/종료하나.**

### 슬라이드 8. 공통 gap

- 기존 full-duplex spoken dialogue language model은 listening 구간에 silence token을 반복 예측하며 사실상 idle 상태가 되기 쉽다.
- 인간 행동과의 괴리 = think-while-listening 계열이 메우려는 빈틈.
- *출처: Chronological Thinking in Full-Duplex Spoken Dialogue Language Models (OpenReview id=ofJYlbzoqn; arXiv:2510.05150)*

### 슬라이드 9. 갈래 A-1 — 텍스트 CoT 겹치기

- **Can Speech LLMs Think while Listening?**
- 멀티스트림 speech LLM에 CoT 파인튜닝 → 음성 추론 정확도 평균 2.4배.
- question completeness(엔트로피 기반)로 *언제* 추론을 시작할지 결정, 정확도-지연 trade-off 제어.
- DPO로 Pareto를 더 밀어 정확도 손실 없이 지연 70% 감소, ARC-Easy +4%.
- *출처: arXiv:2510.07497 (OpenReview id=dFVenZdVbX)*

### 슬라이드 10. 갈래 A-2 — 듣기와 사고 동시

- **SHANKS (Simultaneous Hearing and Thinking)**
- chunk 단위로 듣는 동안 unspoken CoT를 생성해 턴 종료 전부터 사고를 시작.
- 적시 끼어들기, tool-call, 응답 준비를 앞당기는 데 사용.
- 보고 수치: 37.1% higher interruption accuracy, 56.9% tool calls before user finishes turn.
- 갈래 A의 짝으로 배치(둘 다 텍스트 CoT 진영).
- *출처: arXiv:2510.06917 (OpenReview id=4Jnev8rWaq)*

### 슬라이드 11. 갈래 B — 타이밍 제어

- **Chronological Thinking**
- 추론을 listening 구간에 분산(amortize) → 사용자가 멈추면 추가 지연 없이 즉시 발화.
- "무엇을 생각하나"보다 "언제 생각하나"에 초점.
- strictly causal 구조로 과거와 현재 발화만 사용하며, 미래 정보를 훔쳐보지 않는 설정을 강조.
- *출처: OpenReview id=ofJYlbzoqn; arXiv:2510.05150*

### 슬라이드 12. 갈래 C — latent reasoning (텍스트 없는 사고)

- **FLAIR / The Silent Thought**
- 직전 step의 latent embedding을 다음 step으로 재귀 입력 → 인과성 유지, 추가 지연 없는 연속 추론.
- ELBO 기반 목적함수와 teacher forcing으로 명시적 추론 주석 없이 학습.
- 텍스트 CoT 진영과 가장 대비되는 갈래(토론 포인트).
- 공저자에 Yoshua Bengio.
- *출처: arXiv:2603.17837*
- *최신성 주석: 2026-05-20 v4 기준 ICML 2026 accepted로 표기되어 있다.*

### 슬라이드 13. 갈래 D — 구조화된 행동 추론

- **GoT-duplex (Graph-of-Thoughts)**
- perception → 내적 chain/graph-of-thought → action 루프를 인과 그래프로 모델링, 해석 가능한 rationale 생성.
- QA 정확도가 아니라 "대화 행동(끼어들지·침묵할지·기다릴지) 추론" — 분류 폭 확장.
- 행동 검출과 해석 가능한 reasoning chain을 함께 평가한다.
- *출처: arXiv:2512.21706; 프로젝트: got-duplex.github.io*

### 슬라이드 14. 종합 비교표 (★ 3부 클라이맥스)

다섯 논문을 5축으로 한 장에 회수:

| 논문 | 사고 표현형식 | 타이밍 트리거 | 학습 objective | 추가 지연 | 평가 |
|------|--------------|---------------|----------------|-----------|------|
| Can Speech LLMs Think while Listening? | 텍스트 CoT | question completeness(엔트로피) | CoT FT + DPO | 거의 없음 / DPO로 70% 감소 | ARC-Easy 등 음성 추론 |
| SHANKS | 텍스트 CoT | chunk 단위, 턴 종료 전 시작 | CoT 기반 학습 | 절감 | 추론 + interruption/tool-call |
| Chronological Thinking | 텍스트 사고 | listening window에 분산 | chronological thinking 학습 | 없음 | 객관지표 + 휴먼평가 |
| FLAIR / The Silent Thought | **latent**(비언어) | 발화 중 연속 재귀 | ELBO + teacher forcing | 없음 | speech bench + full-duplex |
| GoT-duplex | **그래프(GoT)** | perception 단위 | 인과 그래프 기반 행동 추론 | 명시 수치보다 행동 판단 중심 | 행동 검출 + 해석성 |

- "추가 지연" 열 → 슬라이드 5의 Pareto와 연결(빠름을 안 깨고 추론 회복).
- *출처: 위 각 논문*

### 슬라이드 15. 공통 인사이트

- 전제는 수렴(들으며 사고), 해법은 **표현형식(텍스트 vs latent vs 그래프) × 타이밍 제어**에서 분기.
- 모두 "post-hoc 사고"(턴 종료 후 사고)를 거부한다는 공통점.
- listening 구간을 silence/idle로 버리지 않고, 추론 예산으로 재활용한다.

### 슬라이드 16. 미해결 과제

- latent vs 텍스트 CoT — 어느 쪽이 확장성·해석성에서 이기나(미정).
- think-while-listening 전용 평가 지표 부재(정확도-지연을 함께 보는 표준 벤치 부족).
- 대화 행동 평가와 QA형 speech reasoning 평가를 어떻게 하나의 Pareto로 묶을지 아직 불명확.
- 한국어 paralinguistic 벤치 공백 → 본인 연구와 연결 가능한 지점.

---

## 4부 — takeaway & 열린 질문 (3장)

### 슬라이드 17. 한 문장 결론

- "Full-duplex는 빠름의 대가로 추론을 잃었고, *들으면서 생각하기*가 그 절충안으로 떠올랐다."
- 2부 회수: 단일 모델 수렴 → 추론 붕괴(Pareto) → think-while-listening.
- 단, Nemotron 3 VoiceChat처럼 Pareto 양 축을 동시에 끌어올리려는 균형형 시도도 등장했다.

### 슬라이드 18. 열린 질문 (토론 유도)

- 사고는 텍스트여야 하나, latent여도 되나?
- "언제 생각을 멈추고 말할까"를 학습으로 풀 수 있나?
- 멀티모달(영상)까지 가면 think-while-listening은 어떻게 확장되나?
- 한국어 대화에서 backchannel, 침묵, 끼어들기, 망설임 같은 paralinguistic cue를 어떻게 벤치마크할까?

### 슬라이드 19. 참고문헌

- 아래 References 절 참조.

---

## References

### 오픈소스 단일 모델 (2부)

- Moshi: a speech-text foundation model for real-time dialogue — arXiv:2410.00037  
  https://arxiv.org/abs/2410.00037
- PersonaPlex: Voice and Role Control for Full Duplex Conversational Speech Models — arXiv:2602.06053  
  https://arxiv.org/abs/2602.06053  
  https://research.nvidia.com/labs/adlr/personaplex
- Nemotron 3 VoiceChat — NVIDIA model card  
  https://build.nvidia.com/nvidia/nemotron-voicechat/modelcard
- Step-Audio 2 Technical Report — arXiv:2507.16632  
  https://arxiv.org/abs/2507.16632  
  https://stepfun.ai/docs/en/step-audio2
- StepAudio 2.5 Technical Report — arXiv:2605.23463  
  https://arxiv.org/abs/2605.23463
- Covo-Audio Technical Report — arXiv:2602.09823  
  https://arxiv.org/abs/2602.09823
- Artificial Analysis, "Nemotron 3 VoiceChat: Conversational Dynamics vs Speech Reasoning"  
  https://artificialanalysis.ai/articles/nemotron-3-voicechat-leader-speech-pareto

### interaction + background 프레임 (2부, 구분용)

- Thinking Machines Lab, "Interaction Models: A Scalable Approach to Human-AI Collaboration"  
  https://thinkingmachines.ai/blog/interaction-models
- Sean Goedecke, "Thinking Machines and interaction models"  
  https://www.seangoedecke.com/interaction-models

### think-while-listening (3부)

- Can Speech LLMs Think while Listening? — arXiv:2510.07497; OpenReview id=dFVenZdVbX  
  https://arxiv.org/abs/2510.07497  
  https://openreview.net/forum?id=dFVenZdVbX
- SHANKS: Simultaneous Hearing and Thinking for Spoken Language Models — arXiv:2510.06917; OpenReview id=4Jnev8rWaq  
  https://arxiv.org/abs/2510.06917  
  https://openreview.net/forum?id=4Jnev8rWaq
- Chronological Thinking in Full-Duplex Spoken Dialogue Language Models — arXiv:2510.05150; OpenReview id=ofJYlbzoqn  
  https://arxiv.org/abs/2510.05150  
  https://openreview.net/forum?id=ofJYlbzoqn
- The Silent Thought: Modeling Internal Cognition in Full-Duplex Spoken Dialogue Models via Latent Reasoning — arXiv:2603.17837  
  https://arxiv.org/abs/2603.17837
- Enabling Conversational Behavior Reasoning in Full-Duplex Speech — arXiv:2512.21706  
  https://arxiv.org/abs/2512.21706  
  https://got-duplex.github.io

---

## 발표 직전 재확인 체크리스트

> 본 문서는 2026-06-02 기준 검증본이다. 발표 자료에는 "논문·벤치마크 수치는 2026-06-02 기준"이라고 표기한다.

- Artificial Analysis의 Pareto 수치가 변경되었는지 확인한다.
- Can Speech LLMs Think while Listening?의 2.4x / 70% / ARC-Easy +4% 수치가 최신 arXiv 버전에서도 유지되는지 확인한다.
- StepAudio 2.5를 본문에 어느 정도까지 반영할지 결정한다.
- FLAIR / The Silent Thought의 최신 버전 번호와 ICML 2026 표기를 확인한다.
- GoT-duplex 프로젝트 페이지가 접근 가능한지 확인한다.
