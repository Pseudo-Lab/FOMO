# Full-duplex 음성 AI, 해보니까 이렇더라

> 요즘 핫한 실시간 음성 AI(GPT Realtime, Gemini Live, Thinking Machines의 TML)가
> 어떻게 작동하는지 훑어보고, 막상 직접 만들어보면 부딪히는 현실
> (AEC, barge-in, 턴테이킹 등)을 같이 풀어보는 발표.

- **발표자**: 민정
- **대상**: 가짜연구소 12기 스터디
- **예상 시간**: 약 45분 (발표 40분 + Q&A 5분)
- **톤**: 진지빼고, 경험 나눔 위주

---

## 발표 개요

### 한 줄 메시지
"Full-duplex 음성 AI는 모델만의 문제가 아니라 시스템 전체의 문제다.
TML이 던진 'harness를 없애자'는 주장은 방향성으로는 맞지만,
현실의 제품은 여전히 AEC, barge-in, wake word, 비용, 배터리, 온디바이스 게이트에서 싸운다."

### 결론 미리보기
- 많은 기능은 점점 큰 interaction model 안으로 흡수될 것이다.
- 그래도 음성 AI는 하드웨어와 너무 가깝다.
  - 마이크/스피커/룸/네트워크/배터리/비용이 모델 품질만큼 중요하다.
- 그래서 production에서는 작은 모델들이 계속 필요하다.
  - wake word, VAD, endpointing, AEC 보조, background speech filter,
    safety gate, routing 같은 "문지기" 역할
- 미래는 "하나의 거대한 모델 vs 여러 컴포넌트"가 아니라,
  **큰 모델 + 하드웨어 가까운 작은 게이트 모델들의 계층 구조**일 가능성이 높다.

### 발표 흐름
1. 왜 지금 Full-duplex가 화제인가
2. 현재 지형도 — Cascaded에서 Interaction Model까지
3. TML-Interaction-Small 뜯어보기 (이론)
4. 그런데 실제로 만들면? (현실)
5. 한국어 음성 AI는 어떻게 될까

---

## 1부. 왜 지금 Full-duplex인가 (4분)

### 핵심 메시지
> 단순히 빨라진 게 아니라, 음성 인터랙션의 패러다임이 바뀌고 있다.

### 다룰 내용
- Cascaded 파이프라인(STT → LLM → TTS)의 한계
  - Latency, 끊김, paralinguistic 정보 손실
- "사람처럼 대화한다"는 게 왜 어려운가
  - Turn-taking, backchanneling, interruption
  - 그리고 감정 — 듣는 것보다 표현하는 게 훨씬 어렵다 (4부에서 회수)
- ChatGPT Advanced Voice Mode가 충격이었던 이유
- "Harness 문제" 개념 깔아두기 (3부에서 회수)

---

## 2부. 음성 AI 지형도 (7분)

### 스펙트럼으로 정리
```
Cascaded(STT+LLM+TTS) ─── VAD-free/Micro-turn Cascade ─── E2E S2S ─── Interaction Model
       harness 큼                 절충형                  모델 흡수 큼          harness 최소화
```

### 빠른 survey
| 모델 | 타입 | 특징 |
|------|------|------|
| GPT-Realtime-2 | Hybrid / Realtime voice | 상용, tool call/long context/reasoning effort, production voice agent 지향 |
| Gemini Live (3.1 Flash) | Hybrid / Live audio | 낮은 latency, tonal understanding, noisy 환경과 function calling 강조 |
| DuplexCascade | VAD-free cascade | ASR-LLM-TTS 유지 + micro-turn + control token으로 full-duplex 시도 |
| Moshi (Kyutai) | E2E S2S | 오픈소스, full-duplex, 12.5Hz codec, 약 200ms practical latency |
| Qwen3-Omni | Omni / E2E S2S | Apache 2.0 공개, Thinker-Talker MoE, speech generation 10개 언어 |
| Qwen3.5-Omni | Omni / realtime multimodal | 256k context, ARIA로 streaming speech 안정화, 장시간 audio/video 이해 |
| TML-Interaction-Small | Interaction Model | 200ms chunk, native multimodal |

### 한국어 지원 현황
- 대부분 영어/중국어/일본어 중심으로 먼저 진전
- 한국어는 TTS/ASR 데이터와 벤치마크는 늘고 있지만,
  full-duplex S2S 학습에 필요한 dual-channel, overlap, backchannel 데이터는 여전히 부족
- 2026년 5월 KVoiceBench/KOpenAudioBench/KMMAU 같은 한국어 SpeechLM 벤치마크가 등장
  - 단, 한국어 full-duplex interaction 자체를 평가하는 표준은 아직 빈칸
- TTS는 되는데 S2S는 왜 없는가
  - "말을 예쁘게 읽기"와 "상대가 말하는 중에 듣고, 판단하고, 끼어들지 말지 결정하기"는 다른 문제

---

## 3부. TML-Interaction-Small 뜯어보기 (10분) ★ 발표의 중심

### Thesis
> "Interactivity should scale with intelligence, not be bolted on."
> 인터랙티비티는 외부 컴포넌트로 덧붙이는 게 아니라 모델이 학습해야 한다.

### 아키텍처 deep dive

**Encoder-free early fusion**
- Whisper 같은 사전학습 인코더 안 씀
- 오디오: dMel + 경량 임베딩
- 비디오: 40×40 패치 → hMLP
- 오디오 출력: flow matching head (discrete codec 아님)
- 전부 처음부터 joint 학습

**Multi-stream micro-turn design**
- 200ms 청크 단위
- 각 청크가 audio/video/text 입출력을 인터리브
- Turn boundary, VAD, harness 자체가 없음
- Moshi(12.5Hz, 80ms frame)와의 비교

**Dual-model 구조**
- Frontend interaction model: 실시간 presence, 200ms 안에 응답
- Background async model: 깊은 추론, tool call
- Frontend가 background 결과를 대화에 weave-in
- → Agent 관점에서 재해석 가능

### 스펙
- 276B MoE, 12B active parameters
- FD-bench v1.5: 77.8 (vs GPT-Realtime-2 minimal 46.8, Gemini Live 54.3)
- Turn latency: 0.40초
- Audio MultiChallenge: 43.4%
  - Instant/non-thinking 설정 기준으로 강함
  - 단, GPT-Realtime-2 xhigh처럼 thinking/reasoning 설정을 켜면 지능 점수는 더 높아질 수 있음

### 한계와 열린 문제
- 현재 closed preview (외부 검증 불가)
- Long session context management 미해결
- Scaling 시 200ms latency 유지가 엔지니어링 챌린지
- Frontier 모델 대비 still small
- 더 큰 모델을 실시간으로 serving할 때 compute/cost가 제품 병목이 될 가능성

### 쉽게 설명할 포인트

**1. TML은 "오디오를 텍스트로 바꿔서 이해"하지 않으려 한다**
- 기존 방식: 음성 → 텍스트 → LLM → 텍스트 → 음성
- TML류 방식: 음성/영상/텍스트를 처음부터 같이 보고, 바로 반응하려는 방향
- 그래서 웃음, 망설임, 끼어듦 같은 정보가 중간에 덜 사라진다.

**2. 200ms chunk는 "사람이 말하는 중에도 계속 판단한다"는 뜻**
- 3초 듣고 한 번 판단하는 게 아니라, 짧은 조각마다 계속 업데이트한다.
- 그래서 "아... 그러니까..." 같은 발화에서도 바로 끼어들지 말지 판단할 여지가 생긴다.
- 대신 매 200ms마다 안정적으로 추론해야 해서 serving 비용과 엔지니어링 난도가 올라간다.

**3. Harness 제거는 주변 시스템 제거가 아니다**
- 모델 내부의 VAD/turn-taking harness는 줄어들 수 있다.
- 그래도 마이크 입력, 스피커 echo, 네트워크 지연, 비용 제어, safety, routing은 남는다.
- 이 지점이 발표의 연결고리:
  - 모델은 점점 똑똑해지지만, 제품은 여전히 하드웨어와 비용의 제약을 받는다.

---

## 4부. 그런데 실제로 만들면? (14분) ★ 발표의 차별점

### 한 줄로
> "Full-duplex는 모델 문제가 아니라 시스템-하드웨어-비용 문제다."

### 큰 모델이 흡수하는 것 vs 끝까지 남는 것

**큰 모델이 점점 흡수하는 것**
- 턴테이킹, backchannel, interruption 판단
- 감정/톤 이해와 응답 스타일 결정
- tool call 중에도 대화 presence 유지
- 텍스트 중간 표현 없이 speech-to-speech로 가는 흐름

**그래도 작은 모델/시스템이 필요한 것**
- wake word, VAD, endpointing, local safety gate
- background speech / self echo / TV 소리 / 가족 대화 필터링
- 네트워크로 보낼지 말지 결정하는 routing
- 배터리, 데이터 비용, GPU 비용을 줄이기 위한 front gate
- 장애 시 fallback: "큰 모델이 느리거나 죽었을 때" 최소 UX 유지

### 입력단 — 모델이 뭘 들을 것인가

**Wake word**
- 항상 듣고 있는 모델 vs 디바이스 게이팅의 충돌
- 대화 중 wake word를 또 부르는 경우
- False accept/reject trade-off
- 시니어 케어 같은 도메인은 "매번 호출"이 UX 실패
- 결론: wake word는 사라진다기보다 "항상 켜져 있는 작은 gate"로 재해석될 가능성

**Acoustic Echo Cancellation (AEC)**
- Full-duplex의 가장 큰 적
- 스피커 → 마이크 피드백 루프
- Reference signal 동기화, 클럭 드리프트, 비선형 왜곡
- WebRTC AEC3가 사실상 표준
- AEC 자체는 언어 문제라기보다 하드웨어/룸/동기화 문제
- 한국어 이슈는 AEC 이후 VAD, endpointing, backchannel 판단에서 더 크게 나타남
- 어디서 처리할 것인가: 디바이스 / OS / 앱 / 모델

**Noise suppression & background speech**
- TML이 FD-bench에서 "talking to others", "background speech"를
  평가축으로 둔 이유 — 실제 환경의 절반
- NS 강도와 paralinguistic 정보 보존의 trade-off

**VAD의 역설**
- TML은 "VAD 필요 없다"고 주장하지만 디바이스 단에선 어떤 형태로든 필요
- 네트워크 비용, 배터리, 프라이버시
- 클라이언트 lightweight VAD + 서버 native interaction 하이브리드가 현실
- VAD는 "턴 종료 판단기"로 쓰면 위험하지만,
  "업로드/추론을 시작할지 말지 정하는 비용 gate"로는 계속 유효

### 턴테이킹 & barge-in

**Barge-in (말 끊기)**
- 즉시 멈춤 + 버퍼링 처리 + 상태 롤백
- "어디까지 들었다고 가정"할 것인가

**Backchannel vs 끼어듦**
- "응", "어", "그래" 같은 짧은 반응은 끼어듦이 아님
- Cascaded는 거의 다 끼어듦으로 오인
- TML이 native하게 처리한다고 주장하는 지점

**턴 종료 감지의 모호성**
- "어... 그러니까... [긴 침묵] ...음..."
- VAD 침묵 임계값은 한국어 호흡 패턴에 안 맞음 (특히 시니어)
- Endpoint detection 모델의 latency 비용
- 최신 상용 realtime API는 이 문제를 단순 silence threshold만으로 풀지 않으려 함
  - 예: OpenAI Realtime API의 `semantic_vad`
  - 사용자가 말한 내용상 발화가 끝났는지를 의미적으로 추정하고,
    `eagerness`로 더 빨리/더 오래 기다릴지 조절
- 그래도 semantic VAD가 모든 문제를 없애는 것은 아님
  - background speech, TV 소리, 가족과의 대화, 한국어 filler, 도메인별 말버릇은 여전히 policy/gate 문제

**Overlap speech**
- 동시 발화 구간
- Cascaded 거의 불가, 모델은 native 가능하지만 학습 데이터 부족

**Micro-turn cascade라는 절충안**
- E2E가 아니어도 ASR-LLM-TTS를 chunk-wise micro-turn으로 쪼개면 full-duplex에 가까워질 수 있음
- DuplexCascade류 접근:
  - VAD-free streaming cascade
  - LLM에 special control token으로 응답 타이밍/턴테이킹을 조정
- production 관점에서는 매력적
  - 기존 LLM/tooling/TTS 인프라를 버리지 않아도 됨
  - 단, 컴포넌트 간 clock/state mismatch 문제는 계속 남음

### 출력단 & 시스템 레벨

**TTS streaming & first byte latency**
- First token → first audio byte
- Streaming 중 prosody 일관성 (앞만 보고 운율 결정의 위험)

**Network jitter & buffer**
- WebSocket/WebRTC 패킷 손실
- Buffer 크기와 latency의 trade-off
- 엣지(라즈베리파이)에서 더 빡셈

**Interruption recovery**
- 사용자가 끊은 시점 이후 모델 컨텍스트 처리
- "AI가 말했지만 사용자는 못 들은" 부분

**Clock drift & synchronization**
- 200ms 청크 처리의 시계 동기화
- 샘플레이트 일관성

**Cost & routing**
- 모든 오디오를 frontier realtime model로 보내면 비용이 터짐
- "대화인지, TV 소리인지, 혼잣말인지, 가족과의 대화인지"를 먼저 가르는 작은 모델 필요
- 온디바이스 gate → 저가 서버 모델 → 고성능 realtime model 순으로 escalation하는 구조가 현실적
- 작은 모델의 품질이 전체 UX와 원가를 동시에 결정

### 감정 표현과 페르소나 — 인식보다 표현이 어렵다

**한 줄로**
> 사용자 감정을 읽는 건 어느 정도 한다. 문제는 "그래서 AI가 어떻게 반응해야 하는가"다.

**입력 측 감정 인식 (상대적으로 쉬움)**
- Pitch, energy, tempo 같은 paralinguistic feature
- 요즘 모델은 coarse-grained 감정(긍정/부정, 화남/슬픔) 정도는 잘 잡음
- TML, gpt-realtime도 이 부분은 자랑하는 지점

**출력 측 감정 표현 (훨씬 어려움)**
- "사용자가 슬프다" → AI는 어떤 톤으로 답해야 하나?
  - 너무 다정 → patronizing, 어색
  - 너무 담담 → 차갑게 느껴짐
- "사용자가 화났다" → 차분해야 하지만 차갑지 않게
- 감정 미러링이 정답이 아님 — 사회적 지능이 필요한 문제
- 살짝 어긋난 감정은 무감정보다 더 unsettling (음성의 uncanny valley)

**페르소나와 함께 가야 한다**
- 페르소나가 감정의 baseline을 정함
  - 시니어 케어: 따뜻 + 차분 + 인내심, 절대 들뜨지 않음
  - 고객센터: 공감하되 솔루션 지향, 과한 감정 표현 금지
  - 친근한 컴패니언: 발랄하지만 진중함도 있어야
- 감정 표현이 페르소나와 어긋나면 신뢰가 깨짐
  - 콘텐츠가 틀리는 것보다 톤이 어긋나는 게 더 빨리 깨짐
- 장기 세션에서 페르소나/감정 arc 일관성 유지가 진짜 어려움

**기술적 현실**
- TTS 감정 제어는 여전히 원시적 (style token, reference audio, prompt 지시)
- Cascaded: LLM이 감정 라벨 결정 → TTS가 렌더링 — 매핑 자체가 lossy
- E2E S2S는 이걸 joint로 학습한다는 게 이론, 그런데 학습 데이터에
  "감정 + 컨텍스트 + 적절한 응답 감정" 페어가 거의 없음
- 한국어 특이성: 감정 표현이 영어보다 indirect, 맥락 의존적
  - 영어 SSML 감정 태그를 그대로 한국어에 못 가져옴

**평가의 어려움**
- 객관적 지표 거의 없음 → 주관 평가에 의존
- 문화적/개인적 편차 큼 (어떤 사람은 다정함, 어떤 사람은 부담)
- "이 감정 표현이 적절했는가"는 같은 발화에 대해서도 사람마다 다름

**발표에서 쓸 수 있는 관찰 포인트**
- 감정 표현은 "정답 라벨"보다 "상황에 맞는 강도 조절"이 어렵다.
  - 예: 위로해야 하는 상황에서도 너무 다정하면 부담스럽고, 너무 담담하면 차갑다.
- 같은 문장도 음성 톤에 따라 완전히 다르게 들린다.
  - "괜찮으세요?"가 위로처럼 들릴 수도 있고, 추궁처럼 들릴 수도 있음
- 텍스트 답변은 자연스러운데 음성으로 들으면 어색해지는 경우가 있다.
  - LLM의 문장 선택과 TTS의 운율/속도/강세가 따로 놀기 때문
- 페르소나는 "성격 설명"만으로 유지되지 않는다.
  - 장기 대화에서는 톤, 속도, 감정 강도, 농담 빈도 같은 음성 행동까지 일관되어야 한다.

### 평가 & 운영

- WER, MOS로는 인터랙티비티 측정 불가
- FD-Bench:
  - interruption, delay, noisy condition에서 full-duplex 시스템의 취약점 평가
- Full-Duplex-Bench-v2:
  - multi-turn, correction, entity tracking, safety까지 확장
- MTalk-Bench:
  - semantic, paralinguistic, ambient sound 차원에서 multi-turn S2S 평가
- SpeechParaling-Bench:
  - 감정/톤/상황 적응 같은 paralinguistic-aware speech generation 평가
- 한국어:
  - KVoiceBench/KOpenAudioBench/KMMAU가 등장했지만 full-duplex interaction 평가는 아직 부족
- Long session 누적 컨텍스트 (시니어 케어 매일 30분 시나리오)
- Failure mode: 무한 루프, 침묵, 환각 → watchdog/timeout/graceful degradation

### 실패 사례 시나리오 (슬라이드용)

> "할머니가 '아... 그러니까... [3초 침묵] ...어제 손주가...' 라고 말하는데,
> 단순 silence 기반 VAD는 침묵에서 턴이 끝났다고 보고 AI가 끼어들 수 있습니다.
> OpenAI Realtime API의 `semantic_vad` 같은 기능은 이걸 의미적으로 완화합니다.
> '음... 그러니까...'처럼 아직 말이 끝나지 않은 경우를 더 기다릴 수 있게 하는 거죠.
> 다만 실제 제품에서는 여전히 남는 문제가 있습니다.
> 이게 사용자의 말인지, TV 소리인지, 가족과의 대화인지, 혼잣말인지 먼저 가려야 하고,
> 그 판단은 하드웨어 가까운 작은 gate 모델과 policy의 몫으로 남습니다."

---

## 5부. 한국어 음성 AI는? (5분)

### 다룰 내용
- TML이 closed preview인 상황에서 현업이 할 수 있는 것
- 한국어 capable 오픈소스의 위치 (Qwen3-Omni/Qwen3.5-Omni 등)
- 데이터/평가/모델의 갭
- "Harness가 사라지는 시대"에도 음성 엔지니어 역할은 사라지지 않음
- 청중 토론 포인트 던지기

### 한국어 관점의 최신 포인트
- CoreaSpeech:
  - 한국어 TTS용 700시간/21,449명 규모 corpus
  - 숫자, 영어 차용어, 코드스위칭 등 한국어 전처리 이슈를 정면으로 다룸
- KVoiceBench/KOpenAudioBench/KMMAU:
  - 한국어 SpeechLM 평가가 본격화되는 신호
  - 하지만 spoken QA/audio understanding 중심이라 full-duplex turn-taking 평가는 아직 남은 문제
- J-Moshi:
  - 일본어 Moshi 기반 full-duplex 사례
  - 한국어도 "대규모 spoken dialogue pretraining + stereo dialogue fine-tuning + synthetic dialogue" 경로를 생각해볼 수 있음

### 최종 결론
> Full-duplex 음성 AI는 점점 모델 하나로 흡수되는 방향으로 간다.
> 하지만 제품에서는 하드웨어, 비용, latency 때문에 작은 모델들이 사라지지 않는다.
> 앞으로의 구조는 "거대한 interaction model 하나"가 아니라
> "큰 realtime 모델 + 온디바이스/엣지의 작은 gate 모델들"에 가까울 것이다.

### 청중 토론 질문
- 한국어 full-duplex를 만든다면 먼저 필요한 것은 모델일까, 데이터셋일까, 평가셋일까?
- wake word 없는 UX가 정말 좋은가, 아니면 privacy/cost 관점에서 위험한가?
- 시니어 케어에서는 "항상 듣는 AI"와 "필요할 때만 듣는 AI" 중 무엇이 신뢰를 얻을까?
- 작은 gate 모델이 잘못 판단했을 때의 UX 책임은 어디에 둘 것인가?

---

## Q&A (5분)

### 예상 질문 & 미리 준비
- TML 직접 써볼 방법? → 아직 closed preview
- 우리 회사에서 full-duplex 적용하려면? → 도메인/디바이스에 따라 다름
- Moshi 같은 오픈소스로 한국어 가능? → 파인튜닝 필요, 데이터 한계
- Cascaded는 정말 죽었나? → 아니요, production에선 여전히 주력
- 감정 표현 잘하는 모델은 어떤 게 있나? → 인식은 다 비슷, 표현은 다 어려움
- 페르소나는 시스템 프롬프트로 충분한가? → 짧은 대화는 OK, 장기는 깨짐
- 작은 gate 모델은 꼭 필요한가? → 비용/배터리/프라이버시/latency 때문에 당분간 필요
- TML처럼 harness를 없애면 wake word/VAD도 없어지나? → 모델 내부 turn-taking은 줄어도 디바이스 gate는 남음
- GPT-Realtime-2의 `semantic_vad`가 있으면 VAD 문제는 해결된 것 아닌가?
  → 침묵 기반 끼어들기는 많이 완화하지만, 어떤 소리를 모델로 보낼지/무시할지 정하는 gate 문제는 남음

---

## 참고 자료

### Thinking Machines Lab
- 블로그 포스트: "Interaction Models: A Scalable Approach to Human-AI Collaboration"
- URL: https://thinkingmachines.ai/blog/interaction-models/
- 발표: 2026년 5월 11일

### 관련 모델
- Moshi (Kyutai)
- Qwen3-Omni
- Qwen3.5-Omni
- DuplexCascade
- J-Moshi
- Nemotron VoiceChat
- MOSS-TTS-Nano
- GPT-Realtime-2 (OpenAI)
- Gemini 3.1 Flash Live (Google)

### 벤치마크
- FD-bench v1.5 — 인터랙티비티 평가
- Full-Duplex-Bench-v2 — multi-turn/correction/entity tracking/safety
- Audio MultiChallenge — 지능/instruction following
- MTalk-Bench — multi-turn S2S, semantic/paralinguistic/ambient sound
- SpeechParaling-Bench — paralinguistic-aware speech generation
- KVoiceBench, KOpenAudioBench, KMMAU — 한국어 SpeechLM 평가

### 한국어/동아시아 데이터셋
- CoreaSpeech — 한국어 TTS corpus, 700h/21,449 speakers
- KsponSpeech — 한국어 spontaneous speech ASR corpus
- J-Moshi / J-CHAT — 일본어 full-duplex 연구 참고 사례

### URL 메모
- TML Interaction Models: https://thinkingmachines.ai/blog/interaction-models/
- OpenAI GPT-Realtime-2: https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/
- OpenAI Realtime VAD / semantic_vad: https://platform.openai.com/docs/guides/realtime-vad
- Gemini 3.1 Flash Live: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-live/
- Moshi: https://arxiv.org/abs/2410.00037
- Qwen3-Omni: https://arxiv.org/abs/2509.17765
- Qwen3.5-Omni: https://arxiv.org/abs/2604.15804
- DuplexCascade: https://arxiv.org/abs/2603.09180
- FD-Bench: https://arxiv.org/abs/2507.19040
- Full-Duplex-Bench-v2: https://arxiv.org/abs/2510.07838
- MTalk-Bench: https://arxiv.org/abs/2508.18240
- SpeechParaling-Bench: https://arxiv.org/abs/2604.20842
- KVoiceBench/KOpenAudioBench/KMMAU: https://arxiv.org/abs/2605.27984
- CoreaSpeech: https://papers.neurips.cc/paper_files/paper/2025/hash/5b221bc040a287a255a0f311598aec61-Abstract-Datasets_and_Benchmarks_Track.html
- J-Moshi: https://arxiv.org/abs/2506.02979

---

## 발표 전 체크리스트

- [ ] 슬라이드 작성 (pptxgenjs로)
- [ ] TML 블로그 다시 정독, 인용 정확성 확인
- [ ] 4부 실패 시나리오 2-3개 더 구체화
- [ ] 데모 음성 클립 있으면 추가 검토 (공개 가능 범위 내)
- [ ] 한국어 SpeechLM/데이터셋 최신 논문 2-3편 추가 리뷰
- [ ] 작은 gate 모델 구조를 그림으로 정리
- [ ] 리허설 (시간 체크)

---
