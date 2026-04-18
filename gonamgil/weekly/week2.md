# FOMO Crew W2: Skills + MCP — 프레임워크가 에이전트와 대화하는 법

> **"도구를 70개 만들었다. 그런데 AI가 뭘 써야 할지 모른다면?"**

---

## 1. 지난주 이후: 컨셉에서 구현으로

W1에서 Mandu의 철학을 이야기했다. "구조가 곧 API", "Guard가 아키텍처를 보호한다", "프레임워크가 하네스가 된다." 반응은 긍정적이었지만, 내 머릿속에 남은 건 하나였다:

**"그래서 실제로 AI가 이걸 잘 쓸 수 있어?"**

솔직히, 아니었다. MCP 도구를 70개 넘게 만들어놨는데, AI 에이전트가 상황에 맞는 도구를 골라 쓰는 건 별개의 문제였다. 도구가 많을수록 오히려 선택지가 넓어져서 AI가 헤매는 경우가 생겼다.

```
사람: "로그인 페이지 만들어줘"
AI: mandu.route.add? mandu.contract.create? mandu.generate? 뭐부터?
```

W1에서 "프레임워크가 강제력이 있다"고 했다. 맞다. 하지만 강제력만으로는 부족했다. **가이드가 필요했다.** AI가 "뭘 할 수 있는지"뿐 아니라 "뭘 해야 하는지"를 알아야 했다.

---

## 2. MCP 도구 — 프레임워크의 손과 발

먼저 현재 Mandu의 MCP 도구 체계를 정리하자. **17개 카테고리, 85개 도구**가 있다.

| 카테고리 | 대표 도구 | 하는 일 |
|:---:|:---|:---|
| **spec** | `mandu.route.add`, `mandu.validate` | 라우트 추가/검증 |
| **guard** | `mandu.guard.check`, `mandu.negotiate`, `mandu.guard.heal` | 구조 검증/협상/자동 수정 |
| **transaction** | `mandu.begin`, `mandu.commit`, `mandu.rollback` | 변경사항 원자적 관리 |
| **contract** | `mandu.contract.create`, `mandu.openapi.generate` | API 스키마 정의/OpenAPI 생성 |
| **ate** | `mandu.ate.auto_pipeline`, `mandu.ate.heal` | 테스트 자동 생성/실패 복구 |
| **brain** | `mandu.doctor`, `mandu.watch` | 아키텍처 진단/실시간 감시 |
| **composite** | `mandu.feature.create`, `mandu.diagnose` | 다단계 워크플로우 오케스트레이션 |
| **kitchen** | `mandu.kitchen.errors` | 실시간 에러 진단 |

각각의 도구는 **한 가지 일을 정확히** 한다. `mandu.route.add`는 라우트를 추가하고, `mandu.guard.check`는 구조를 검증한다. 유닉스 철학이다.

하지만 실제 개발은 "라우트 추가"가 아니라 **"기능 추가"**다. 로그인 기능을 만들려면 라우트 추가 → 컨트랙트 정의 → 코드 생성 → 가드 검증을 순서대로 해야 한다. AI가 이 순서를 매번 맞게 조합할까?

---

## 3. Skills — "뭘 해야 하는지"를 알려주는 레시피

여기서 **Skills**가 등장한다.

Skills는 MCP 도구들의 상위 레이어다. 도구가 "손과 발"이라면, 스킬은 **"레시피"**다. "로그인 페이지 만들기"라는 요리를 위해 어떤 재료(도구)를 어떤 순서로 써야 하는지 알려준다.

### 9개의 스킬, 3가지 분류

| 분류 | 스킬 | 역할 |
|:---:|:---|:---|
| **Workflow** | `mandu-create-feature` | 기능 풀 스캐폴드 (페이지 + API + 아일랜드) |
| | `mandu-create-api` | REST API + 컨트랙트 + 테스트 |
| | `mandu-debug` | 8가지 에러 카테고리별 진단 파이프라인 |
| **Knowledge** | `mandu-explain` | 18개 프레임워크 개념 설명 (수준별 적응) |
| | `mandu-guard-guide` | 6가지 아키텍처 프리셋 가이드 |
| | `mandu-deploy` | 배포 파이프라인 (Docker, CI/CD, nginx) |
| **Framework** | `mandu-slot` | Filling API & 라이프사이클 훅 |
| | `mandu-fs-routes` | 파일 라우팅 규칙 & 레이아웃 |
| | `mandu-hydration` | 아일랜드 하이드레이션 전략 |

**Workflow Skills**는 MCP 도구들을 체이닝한다. 예를 들어 `mandu-create-feature`는:

```
mandu.negotiate → mandu.route.add → mandu.contract.create → mandu.generate → mandu.guard.check
```

이 순서가 스킬 안에 정의되어 있다. AI는 이 레시피를 따르기만 하면 된다.

**Knowledge Skills**는 AI에게 맥락을 준다. `mandu-explain`은 "Guard가 뭐야?"라는 질문에 초급/중급/고급 수준으로 설명을 제공한다. AI가 프레임워크를 "이해"한 상태에서 코드를 짜게 만드는 것이다.

**Framework Skills**는 Mandu 고유의 패턴을 가르친다. Slot이 뭔지, 파일 라우팅이 어떻게 작동하는지, 하이드레이션 전략을 어떻게 선택하는지.

---

## 4. Composite Tools — 스킬과 도구 사이의 다리

그런데 한 가지 갭이 있었다. 스킬은 마크다운 가이드이고, MCP 도구는 실행 가능한 함수다. 스킬이 "이 순서로 하세요"라고 알려줘도, AI가 도구를 하나하나 호출하면 중간에 실수할 수 있다.

그래서 **Composite Tools**를 만들었다. 여러 도구를 하나의 호출로 묶는 오케스트레이션 도구다.

| Composite Tool | 체이닝하는 도구들 |
|:---|:---|
| `mandu.feature.create` | negotiate + route.add + contract.create + generate + guard.check |
| `mandu.diagnose` | kitchen.errors + guard.check + validate.contracts (병렬) |
| `mandu.island.add` | negotiate + island scaffold + hydration config |
| `mandu.middleware.add` | negotiate + middleware scaffold + runtime config |
| `mandu.test.route` | ate.generate + ate.run + ate.heal (실패 시) |

`mandu.feature.create` 하나로 기능 생성의 전체 흐름이 돌아간다. 중간에 Guard가 거부하면? negotiate부터 다시. 테스트가 실패하면? heal이 자동 수정을 시도한다.

---

## 5. relatedSkills — 도구가 스킬을 추천한다

마지막 퍼즐 조각. 도구와 스킬이 따로 놀면 안 된다.

최근 추가한 **relatedSkills 어노테이션**이 이 문제를 푼다. 모든 85개 MCP 도구에 "이 도구와 관련된 스킬"을 메타데이터로 붙였다.

```typescript
// guard.ts
{
  name: "mandu.guard.check",
  annotations: {
    relatedSkills: ["mandu-guard-guide", "mandu-debug"]
  }
}
```

AI가 `mandu.guard.check`를 쓰다가 위반이 발견되면? `relatedSkills`를 보고 `mandu-guard-guide`로 아키텍처 규칙을 확인하거나, `mandu-debug`로 진단 파이프라인을 탈 수 있다. **도구가 스킬을 추천하고, 스킬이 도구를 조합한다.** 양방향 연결이다.

```
Skills (레시피)
  ↕ relatedSkills 어노테이션
MCP Tools (실행)
  ↕ Composite Tools (오케스트레이션)
결과물 (검증된 코드)
```

---

## 6. 실제 시나리오: "로그인 기능 만들어줘"

이 전체 시스템이 어떻게 돌아가는지 시나리오로 보자.

**Before (W1 시점 — 도구만 있을 때):**
```
사람: "로그인 기능 만들어줘"
AI: (85개 도구 중 뭘 써야 하지...)
    → mandu.route.add("/login", "page") 
    → 컨트랙트 생성 까먹음
    → guard 검증 안 함
    → 나중에 구조 위반 발견
```

**After (W2 — Skills + Composite + relatedSkills):**
```
사람: "로그인 기능 만들어줘"
AI: → mandu-create-feature 스킬 참조
    → mandu.feature.create 호출 (composite)
      ├── negotiate: "/app/login/page.tsx 생성 가능?"  → ✅
      ├── route.add: 라우트 등록
      ├── contract.create: 로그인 스키마 정의
      ├── generate: 코드 생성
      └── guard.check: 구조 검증 → ✅
    → 완료. 트랜잭션 커밋.
```

도구 수는 같다. 하지만 **AI가 헤매지 않는다.** 스킬이 방향을 잡아주고, Composite가 실행을 묶어주고, relatedSkills가 맥락을 연결한다.

---

## 7. 배운 것: 도구를 만드는 것과 도구를 쓰게 만드는 것은 다르다

W1에서 W2까지 가장 크게 배운 점:

> **"AI에게 능력(도구)을 주는 것과, AI가 능력을 제대로 발휘하게 만드는 것은 완전히 다른 문제다."**

MCP 도구 85개를 만들었을 때, "이제 AI가 프레임워크랑 대화할 수 있겠다"고 생각했다. 하지만 현실은 달랐다. 도구가 많을수록 AI는 더 헤맸다.

이건 사람도 마찬가지다. 주방에 칼이 20개 있으면 전문 셰프는 상황에 맞는 칼을 고르지만, 초보는 어떤 칼을 써야 할지 모른다. **도구의 수가 아니라 도구를 사용하는 맥락과 순서가 중요하다.**

| 레이어 | 역할 | 비유 |
|:---:|:---|:---|
| **MCP Tools** | 개별 실행 단위 | 칼, 냄비, 프라이팬 |
| **Composite Tools** | 도구 체이닝 | 조리 과정을 하나로 묶은 자동 조리기 |
| **Skills** | 맥락 + 순서 가이드 | 레시피북 |
| **relatedSkills** | 양방향 연결 | "이 재료 쓸 때 이 레시피 참고" 메모 |

---

## 8. 고민 / 크루에게 던지는 질문

- **여러분의 에이전트 워크플로우에서 "도구는 있는데 AI가 잘 못 쓰는" 경험 있나요?**
- **MCP 도구 설계할 때, 세분화(많은 작은 도구) vs 통합(적은 큰 도구) 어디에 무게를 두나요?**
- **Skills 같은 "가이드 레이어"가 다른 프레임워크/도구에도 있다면 어떤 형태일까요?**

---

## 9. Retrospective

> "도구를 만드는 건 쉬웠다. 어려운 건 AI가 그 도구를 '올바르게' 쓰게 만드는 것이었다.
> MCP가 손과 발이라면, Skills는 뇌의 실행 계획이다.
> 결국 하네스 엔지니어링은 '무엇을 막을 것인가'에서 '어떻게 이끌 것인가'로 진화한다.
> W1의 Guard는 울타리였다. W2의 Skills는 길 안내다.
> 울타리와 길 안내, 둘 다 있어야 AI가 올바르게 걸을 수 있다."

---

*FOMO — 고민할 시간에 움직인다.*
