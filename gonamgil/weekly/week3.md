# FOMO Crew W3: 하네스 엔지니어링 — 도구를 엮어 실패해도 복구되는 루프를 만들다

> **"도구를 만드는 건 W2에서 끝났다. 이제 도구들이 '함께 일하는 법'을 설계할 차례다."**

---

## 1. W1 → W2 → W3: 지금까지의 여정

| 주차 | 질문 | 답 |
|:---:|:---|:---|
| **W1** | AI와 개발하면 왜 구조가 무너지나? | 프레임워크가 하네스가 되면 된다 |
| **W2** | 도구 85개를 만들었는데 AI가 헤맨다? | Skills + Composite로 가이드한다 |
| **W3** | 개별 도구가 잘 돌아가면 끝인가? | **아니다. 도구들이 하나의 루프로 엮여야 한다** |

W2까지는 "이 도구를 이 순서로 쓰면 된다"였다. 하지만 현실 개발에서는 **중간에 실패한다.** Guard가 위반을 잡고, 테스트가 깨지고, 생성된 코드에 문제가 있다. 각각의 도구가 아무리 잘 작동해도, 실패했을 때 어떻게 복구하고 재시도하는지가 설계되어 있지 않으면 결국 사람이 개입해야 한다.

**W3의 핵심 질문: 실패가 발생했을 때, 사람 없이 루프가 돌아갈 수 있는가?**

---

## 2. 하네스 엔지니어링이란 무엇인가

하네스(Harness)의 원래 의미는 **안전벨트, 마구**다. 말이 달려도 마차에서 벗어나지 않게 하는 장치. AI 개발에서 하네스 엔지니어링은:

> **AI가 자유롭게 코드를 생성하되, 구조를 벗어나지 않고, 실패해도 안전하게 복구되는 시스템을 설계하는 것**

W1에서 말한 Guard는 하네스의 **제약(Constraint)** 측면이었다. "여기서 벗어나면 안 돼." W2에서 말한 Skills는 하네스의 **유도(Guidance)** 측면이었다. "이 순서로 해." 

W3에서는 하네스의 세 번째 측면을 다룬다: **복원(Recovery)**. "실패하면 이렇게 돌아와."

```
하네스 엔지니어링 = 제약(Guard) + 유도(Skills) + 복원(Recovery)
```

이 세 가지가 합쳐져야 비로소 **"사람이 빠져도 돌아가는 루프"**가 완성된다.

---

## 3. Transaction — 모든 변경은 되돌릴 수 있다

하네스의 기반은 **Transaction 시스템**이다. AI가 여러 파일을 수정하는 작업은 본질적으로 위험하다. 라우트 추가 → 컨트랙트 생성 → 코드 제너레이션 → Guard 검증, 이 4단계 중 3단계에서 실패하면? 1~2단계의 변경은 이미 파일시스템에 반영되어 있다. 반쯤 만들어진 기능이 프로젝트에 남는다.

### 동작 원리

```
mandu.begin()          ← 현재 상태 스냅샷 생성
  ├── route.add()      ← 파일 변경 1
  ├── contract.create() ← 파일 변경 2
  ├── generate()       ← 파일 변경 3 ... 여기서 실패!
  └── 실패 감지
mandu.rollback()       ← 스냅샷 시점으로 완전 복원
```

핵심 설계:

| 도구 | 역할 |
|:---|:---|
| `mandu.begin()` | 변경 전 스냅샷 생성. 변경 ID 자동 부여 (`YYYYMMDD-HHmmss-xxx`) |
| `mandu.commit()` | 모든 변경을 확정. 히스토리에 기록 |
| `mandu.rollback()` | 스냅샷 시점으로 완전 복원. 변경 ID로 선택적 롤백도 가능 |
| `mandu.tx_status()` | 현재 트랜잭션 상태 조회 |

스냅샷은 `.mandu/history/`에 저장된다. `changes.json`이 감사 추적(audit trail)을, `active.json`이 현재 트랜잭션 상태를 관리한다.

**이게 왜 하네스인가?** AI가 아무리 복잡한 작업을 해도, 실패하면 "처음부터 다시"가 아니라 **"스냅샷으로 돌아가기"**가 된다. 데이터베이스의 트랜잭션처럼, 코드 변경도 원자적(atomic)으로 관리된다.

---

## 4. Guard — 위반을 잡고, 협상하고, 자동으로 고친다

W1에서 Guard를 "울타리"로 소개했다. 하지만 Guard의 진짜 힘은 단순한 검증이 아니라 **3단계 자기 교정 루프**에 있다.

### Phase 1: Detection — 위반 탐지

```typescript
mandu.guard.check()
// → violations: [
//     { type: "FORBIDDEN_IMPORT", file: "app/login/page.tsx", 
//       detail: "infra 모듈을 page에서 직접 import" }
//   ]
```

Guard는 계층 위반, 순환 참조, 크로스 슬라이스 import, 과도한 중첩 등을 탐지한다. 각 위반에는 타입과 심각도가 붙는다.

### Phase 2: Healing — 수정 제안

탐지만 하면 린터와 다를 게 없다. Guard는 **치유 제안(healing suggestion)**을 함께 생성한다.

```
위반: "infra 모듈을 page에서 직접 import"

Primary Fix:
  - Label: "허용된 계층으로 이동"
  - Before: import { db } from '@/infra/database'
  - After:  import { db } from '@/shared/database'

Alternatives:
  - "shared로 추출"
  - "facade 패턴 사용"
```

하나의 위반에 대해 **주요 수정안 + 대안**을 모두 제시한다. AI가 상황에 맞는 선택을 할 수 있다.

### Phase 3: Auto-Fix — 자동 적용

`autoFix: true`로 호출하면 `healAll()`이 주요 수정안을 자동 적용한다.

```
결과: { fixed: 3, failed: 1, remaining: 1 }
```

고쳐진 것, 실패한 것, 남은 것을 명확히 리포트한다. 실패한 위반은 다음 루프에서 재시도하거나, 사람에게 에스컬레이션된다.

### negotiate — 코드 짜기 "전에" 물어보기

Guard의 가장 독특한 도구. AI가 코드를 작성하기 전에 "이렇게 해도 되나?"를 먼저 물어본다.

```
AI: mandu.negotiate({ 
  action: "create", 
  path: "app/admin/users/page.tsx" 
})

Guard: ✅ 허용. 단, 이 위치에는 server component만 가능.
// 또는
Guard: ❌ 거부. app/admin/은 인증 가드 필수. 
       대안: app/(auth)/admin/users/page.tsx
```

**사전 협상**이 핵심이다. 코드를 다 짜고 나서 "안 됩니다"가 아니라, 짜기 전에 "여기에 이렇게 하면 됩니다"를 알려준다. 린터는 사후 검증이지만, negotiate는 **사전 합의**다.

---

## 5. ATE — 테스트를 자동 생성하고, 실패하면 스스로 고친다

**ATE(Automation Test Engine)**는 Mandu의 테스트 하네스다. 개발자가 테스트를 직접 작성하는 게 아니라, 프레임워크가 코드를 분석해서 테스트를 자동 생성한다.

### 4단계 파이프라인

```
Extract → Generate → Run → Heal
```

| 단계 | 하는 일 | 산출물 |
|:---:|:---|:---|
| **Extract** | 코드베이스 스캔, 인터랙션 그래프 구축 | 라우트/핸들러/의존성 맵 |
| **Generate** | 시나리오 기반 테스트 케이스 생성 | L1(스모크) + L2(기능 커버리지) |
| **Run** | Playwright로 테스트 실행 | JSON 리포트 + 실패 트레이스 |
| **Heal** | 실패 분석 → 셀렉터 대안 생성 → diff 제안 | 수정 diff (자동 적용 아님) |

특히 **Heal 단계**가 중요하다. 테스트가 깨졌을 때:

1. Playwright 트레이스를 파싱해서 어떤 셀렉터가 실패했는지 분석
2. 대안 셀렉터를 생성 (CSS → data-testid → ARIA 등)
3. **diff 형태로 제안** — 자동 적용하지 않는다

```
실패: button[data-action="login"] 을 찾을 수 없음

Heal 제안:
  - Before: await page.click('button[data-action="login"]')
  - After:  await page.click('[data-testid="login-submit"]')
  - 신뢰도: 0.87
```

**비파괴적(non-destructive) 치유**가 핵심 설계 원칙이다. Guard의 auto-fix와 달리, ATE는 반드시 사람이 리뷰한 뒤 적용한다. 테스트 수정은 비즈니스 의도와 맞는지 확인이 필요하기 때문이다.

---

## 6. Self-Correction Loop — 모든 것을 엮는 루프

지금까지 나온 것들을 하나로 엮으면, Mandu의 **Self-Correction Loop**가 된다.

```
┌─────────────────────────────────────────────────┐
│                 Self-Correction Loop              │
│                                                   │
│  ① Plan: Skills가 워크플로우 순서 결정             │
│     ↓                                             │
│  ② Begin: Transaction 스냅샷 생성                  │
│     ↓                                             │
│  ③ Negotiate: Guard에게 사전 합의                   │
│     ↓ (거부 시 대안 수용 후 재시도)                  │
│  ④ Execute: Composite Tool로 일괄 실행              │
│     ↓                                             │
│  ⑤ Verify: Guard.check + ATE.run                  │
│     ↓                                             │
│  ⑥-a 성공 → Commit + 완료                          │
│  ⑥-b 실패 → Heal → ⑤로 재시도                      │
│  ⑥-c 치유 실패 → Rollback + 사람에게 에스컬레이션    │
│                                                   │
└─────────────────────────────────────────────────┘
```

### 각 단계의 역할

| 단계 | 담당 시스템 | 실패 시 |
|:---:|:---:|:---|
| ① Plan | Skills | — |
| ② Begin | Transaction | — |
| ③ Negotiate | Guard | 대안 제시 → 재협상 |
| ④ Execute | Composite Tools | Rollback |
| ⑤ Verify | Guard + ATE | Heal → 재시도 |
| ⑥ Finalize | Transaction | Commit 또는 Rollback |

이 루프의 핵심은 **실패 지점마다 복구 경로가 설계되어 있다**는 것이다.

- **③에서 거부?** → 대안 수용 후 재시도. 코드를 짜기 전이라 비용이 거의 없다.
- **④에서 에러?** → Transaction rollback. 파일시스템이 깨끗하게 복원된다.
- **⑤에서 위반?** → Guard heal 또는 ATE heal. 자동 수정 후 재검증.
- **치유도 실패?** → Rollback + 사람에게 에스컬레이션. 최소한 프로젝트는 안전하다.

**"사람이 빠져도 루프가 돈다. 루프가 스스로 해결 못 하면, 깨끗한 상태로 사람을 부른다."**

---

## 7. Decision Memory — 루프가 학습한다

루프가 돌아갈 때마다 의사결정이 생긴다. "이 파일은 이 위치에 둬야 한다", "이 패턴은 facade로 감싸야 한다." 이 결정들을 날려버리면 다음에 같은 실수를 반복한다.

Mandu의 **Decision Memory**가 이를 방지한다.

| 도구 | 역할 |
|:---|:---|
| `mandu.save_decision()` | 아키텍처 결정을 ADR(Architecture Decision Record)로 저장 |
| `mandu.get_decisions()` | 특정 영역의 과거 결정 조회 |
| `mandu.check_consistency()` | 새 변경이 과거 결정과 충돌하는지 검증 |

```
AI: "app/admin에 직접 DB 접근 코드를 넣으려고 합니다"
Decision Memory: "ADR-007에서 DB 접근은 infra 계층에서만으로 결정됨"
→ 자동 거부 + 이유 제시
```

Self-Correction Loop가 **매 실행마다 학습**하는 것이다. 같은 실수는 두 번 하지 않는다.

---

## 8. 실제 시나리오: 기능 추가의 전체 여정

"사용자 프로필 페이지를 만들어줘"라는 요청이 들어왔을 때, 전체 루프가 어떻게 돌아가는지:

```
① Skills 참조: mandu-create-feature → 워크플로우 확인

② Transaction 시작: mandu.begin() → 스냅샷 #2024-0412-001

③ 사전 협상:
   negotiate("app/profile/page.tsx") → ✅ 허용
   negotiate("app/profile/api/route.ts") → ❌ 거부
     → 대안: "app/api/profile/route.ts" → 수용

④ 일괄 실행: mandu.feature.create("profile")
   ├── route.add: 2개 라우트 등록
   ├── contract.create: ProfileSchema 정의
   ├── generate: 페이지 + API 핸들러 생성
   └── ✅ 성공

⑤ 검증:
   guard.check() → 위반 1건: "page.tsx에서 직접 fetch 사용"
   → guard.heal(autoFix: true) → ✅ fetch를 서버 액션으로 변환
   → guard.check() → ✅ 통과
   
   ate.run("profile") → 테스트 2/3 통과, 1건 실패
   → ate.heal() → 셀렉터 수정 diff 제안 → 적용
   → ate.run("profile") → ✅ 3/3 통과

⑥ 완료: mandu.commit() → 변경 확정
   save_decision("프로필 API는 app/api/profile/에 위치") → ADR 기록
```

중간에 2번 실패했지만(Guard 위반 1건, 테스트 실패 1건), **사람 개입 없이 루프가 스스로 해결했다.** 그리고 "프로필 API 위치" 결정이 ADR로 남아서, 다음에 비슷한 기능을 만들 때 같은 논쟁을 반복하지 않는다.

---

## 9. W1 → W2 → W3: 하네스의 3층 구조가 완성되다

| 주차 | 하네스 측면 | Mandu 구현 | 비유 |
|:---:|:---:|:---|:---|
| **W1** | 제약 (Constraint) | Guard, 파이프라인, Filesystem-First | 울타리 |
| **W2** | 유도 (Guidance) | Skills, Composite Tools, relatedSkills | 길 안내 |
| **W3** | 복원 (Recovery) | Transaction, Heal, ATE, Self-Correction Loop | 안전망 |

**울타리만 있으면** — AI가 막혀서 멈춘다.
**길 안내만 있으면** — 실패했을 때 대처를 모른다.
**안전망만 있으면** — 애초에 방향을 잘못 잡는다.

셋 다 있어야 비로소 **"사람이 설계하고, AI가 구현하되, 아키텍처가 무너지지 않는"** 시스템이 된다.

---

## 10. 고민 / 크루에게 던지는 질문

- **여러분의 AI 워크플로우에서 "실패 복구"는 어떻게 설계되어 있나요? 아니면 실패하면 사람이 직접 수습하나요?**
- **"사전 협상(negotiate)"이라는 개념, 다른 도구/프레임워크에서 본 적 있나요?**
- **Self-Correction Loop가 무한 루프에 빠지지 않으려면 어떤 안전장치가 필요할까요?**

---

## 11. Retrospective

> "W1에서 울타리를 쳤다. W2에서 길을 닦았다. W3에서 안전망을 깔았다.
> 하네스 엔지니어링은 이 셋의 합이다 — 제약, 유도, 복원.
> AI에게 자유를 주되, 실패해도 괜찮은 환경을 만드는 것.
> 결국 좋은 하네스란, AI가 실패를 두려워하지 않게 만드는 시스템이다.
> 실패할 수 있어야 도전할 수 있고, 도전할 수 있어야 좋은 코드가 나온다."

---

*FOMO — 고민할 시간에 움직인다.*
