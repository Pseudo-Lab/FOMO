# FOMO Crew W1: OT & 하네스 엔지니어링 입문

> **"흘러가는 데로 두자. 트렌드만 놓치지 말자."**

---

## 1. 지식의 입력 (W1 Input Flow)

|       구분        | 활동 내용                                                                   |                  관리 상태                  |
| :---------------: | :-------------------------------------------------------------------------- | :-----------------------------------------: |
|  **Weekly Sync**  | [OT] FOMO 크루 킥오프 - 자기소개, 그라운드 룰, 하네스 엔지니어링 발표       |                   ✅ 참석                    |
| **Daily Insight** | [아티클] Anthropic 76개 출시 달력 분석 — 수직통합 전략 읽기                 |                   ✅ 완료                    |
| **Daily Insight** | [아티클] 하네스 진화 방향 - 모델 개선 시 하네스는 어떻게 바뀌어야 하나      |                   ✅ 완료                    |
| **Daily Insight** | [아티클] 코드 0줄로 100만 줄 기여 - 하네스 기반 개발의 실전 사례            |                   ✅ 완료                    |
|   **Deep-Dive**   | [세미나] 진짜 AX - 새로운 시대의 기업구조 (Delta Society Monthly Delta 3월) | ✅ [후기 작성](delta-ax-seminar-20260326.md) |
|   **Hands-On**    | 맥미니 M4에 OpenClaw 설치 및 개인 에이전트 환경 구축 테스트                 |                   ✅ 완료                    |

### 공유 아티클 목록

#### 하네스 엔지니어링

1. [모델이 개선될때마다 하네스는 어떻게 바뀌어야하나 - 황현태](https://www.linkedin.com/feed/update/urn:li:activity:7442713503385227264)
   - 하네스는 모델이 똑똑해져도 불필요해지지 않고, 더 고차원적 작업을 가능케 하는 방향으로 진화해야함, Planner/Generator/Evaluator 역할 분담 구조 제안

2. [6개월간 코드를 한 줄도 안 쓰고 100만 줄을 기여했습니다 - Byeongchan Park (채널톡)](https://www.linkedin.com/feed/update/urn:li:activity:7440547681854406656)
   - 22개 저장소, 560+ PR, 97만 줄 수정. "비결은 AI가 아니라 시스템(하네스)." 자연어 지침 대신 결정론적 제어 메커니즘 활용

3. [100가지 실전 하네스를 만들었습니다 - Minho Hwang (카카오)](https://www.linkedin.com/feed/update/urn:li:activity:7441618374075252736)
   - 489개 에이전트, 315개 스킬, 100개 도메인. OWASP, Bloom's Taxonomy 등 실전 프레임워크 내장. 아직 실효성은 검증 전

#### Claude Code & 도구 생태계

4. [Anthropic 76개 출시 목록을 달력에 찍어봤습니다 - Jeongmin Lee (Smoretalk)](https://www.linkedin.com/posts/jyoung105_anthropic-76%EA%B0%9C-%EC%B6%9C%EC%8B%9C-%EB%AA%A9%EB%A1%9D%EC%9D%84-%EB%8B%AC%EB%A0%A5%EC%97%90-%EC%B0%8D%EC%96%B4%EB%B4%A4%EC%8A%B5%EB%8B%88%EB%8B%A4-%EB%A7%A4%EC%9D%BC-%EB%AC%B4%EC%96%B8%EA%B0%80-ugcPost-7443117208785993730-hWxz)
   - 54일간 76개 기능 출시. Claude Code가 단순 코드 도구에서 자동화 레이어(Dispatch, Cloud Tasks)로 전환

5. [Claude Code 기억력을 10배 올리는 Auto-dream - Seungpil Lee (사용성연구소)](https://www.linkedin.com/feed/update/urn:li:activity:7442348326420754432)
   - Auto Memory의 중복/오래된 메모 문제를 해결하는 Auto-dream 기능. 수면 중 기억 정리처럼, 작업 종료 후 Claude가 메모를 자동 정리

6. [한국인에게 참 좋은 스킬 모음집 (케이-스킬) - Jeffrey Kim](https://www.linkedin.com/feed/update/urn:li:activity:7442684241856966656)
   - SRT 예매, KBO 결과 조회, 지하철 도착 정보 등 한국 맞춤형 Claude Code 스킬

#### AI 보안 & 생태계

7. [Andrej Karpathy 경고: pip install 한 줄이면 끝 - Seungpil Lee (사용성연구소)](https://www.linkedin.com/feed/update/urn:li:activity:7443084381780426752)
   - litellm 패키지 악성 코드 사건. 공급망 공격으로 AWS 키, API 키 탈취 가능. AI 코딩 도구 사용 시 패키지 출처 검증 필수
   - 회사 내부망에 설치해서 내부에서만 쓰는 용도로 쓰고 있었는데 혹시나 보안팀에서 뭐라할까봐 k8s에서 내렸음
8. [LiteParse: 500 PDF Pages in 2 Seconds Locally - Fahd Mirza](https://www.linkedin.com/feed/update/urn:li:activity:7442688292468424704)
   - LlamaIndex에서 SaaS 형 LlamaParse 말고 OpenSource Parse를 출시 하였음
   - GPU/API 키 없이 로컬에서 2초 만에 500페이지 PDF 파싱. 표 레이아웃 보존, 50+ 파일 형식 지원, Claude Code 호환

#### AI 에이전트 실전 사례

9. [나는 AI에게 아무것도 설명하지 않는다 - 문건기 (해치랩스)](https://www.kianmoon.com/posts/ai-assistant-system)
   - 6개월간 개발한 AI 비서 'JARVIS' 시스템. 단기/장기 이중 기억 구조 + 이메일·메시지·통화 자동 싱크로 "AI한테 브리핑하는 시간 제거". Delta 세미나에서 직접 들은 내용의 원문

#### AI 시대 변화

10. [한국은 아직도 현장 모른다: AI 발전 속도 못 따라가 - 황현태 (SpaceY)](https://www.linkedin.com/feed/update/urn:li:activity:7442371682155089920)
    - AI 시대 인재 수요 변화에 제도가 못 따라감. "인재를 오래 붙잡는 것"이 아닌 "효율적으로 연결할 수 있느냐"가 경쟁력

---

## 2. 기술의 축적 (W1 Output Archive)

### W1 OT 핵심 정리 — 하네스 엔지니어링

김재현 님의 하네스 엔지니어링 발표

**1. 하네스 4계층 모델**

|   계층    | 핵심 요소          | 역할                                           |
| :-------: | :----------------- | :--------------------------------------------- |
| 통제 계층 | Rules, Context     | 동적 규칙 라우팅, 컨텍스트 압축                |
| 실행 계층 | Skills, Sandbox    | 스킬 v2 (YAML 프론트매터에 훅 삽입)            |
| 품질 계층 | Hooks, Evaluation  | 물리적 차단 (프롬프트가 아닌 훅으로 제약 구현) |
| 구조 계층 | Sub-agents, Memory | 컨텍스트 격리                                  |

**2. 코더 → 오케스트레이터(빌더)**

- "어떻게 짜느냐"는 무의미. "무엇을 시킬 것인가"가 핵심
- 개발자 팀장의 역할 - AI 에이전트 코더를 지휘하는 마인드셋

**3. 피터 레슨 - 하네스에서 벗어날 수 있는 하네스**

- 모델이 발전하면 촘촘한 제어가 오히려 "똑똑한 모델에게 무거운 갑옷"이 됨
- 하네스는 고정이 아니라 지속적으로 관찰하고 경량화해야 함

### 세미나 참석

#### 진짜 AX - 새로운 시대의 기업구조

Delta Society 주최 Monthly Delta 3월 세미나에 참석. 인티그레이션(170명), 채널코퍼레이션(240명), 해치랩스, 매스프레소(콴다) 4개사의 AX 전환 실전기를 청취

> 상세 후기: [delta-ax-seminar-20260326.md](delta-ax-seminar-20260326.md)

**스터디와 연결되는 핵심 포인트**

- 채널코퍼레이션: 전사 240명 클로드 코드 도입, 2주 만에 CX팀장이 직접 개발 시작
- 인티그레이션: 개발자 0명인 팀에서 프로덕트 배포, "짬통(Playground)" 시스템으로 바이브코딩 안전 환경 구축
- 해치랩스 문건기 대표: OpenClaw 기반 "자비스" 시스템 - 녹음→전사→장기기억 파이프라인으로 "AI한테 브리핑하는 30분이 사라짐"
- 매스프레소: 신규 프로덕트 전부 1인 개발 체제, 전사 하네스 레이어 자체 구축

### Hands-On

#### 맥미니 M4에 OpenClaw 설치

맥미니 M4에 OpenClaw를 설치하여 개인 에이전트 환경을 테스트

- **환경**: Mac Mini M4
- **설치**: OpenClaw 로컬 설치, OpenAI OAuth로 구성
- **테스트**: 텔레그램 연동, 기본 대화 및 명령 실행, 스킬 생성 테스트
- **소감**: 로컬에서 돌아가는 개인 AI 에이전트의 가능성을 직접 체감, 문건기 대표의 아티클을 참고 해서 발전시켜보려고 함

### Retrospective

> "OT에서 하네스 4계층을 배우고, 세미나에서 실제로 그것을 운영하는 기업들을 만났다.
> 맥미니에 OpenClaw를 깔아보니, '개인 에이전트'가 더 이상 먼 이야기가 아니라는 걸 체감했다.
> 다음 주부터는 팀 공통 하네스 규칙의 프로토타입을 하나 만들어 보고 싶다."

---

*FOMO — 고민할 시간에 움직인다.*
