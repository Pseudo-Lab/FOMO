### 260403_week2_commit
1. 공용 하네스 웹/앱 서비스 평가 모드 확장
   1. WebProblem 스키마 설계 (endpoint / method / test_cases 기반)
   2. 실제 LLM API 연결 (Anthropic Claude SDK, OpenAI SDK 분기)
   3. FastAPI TestClient 기반 웹 샌드박스 구현
      - LLM 생성 코드 exec() → app 객체 추출
      - HTTP 수준 요청/응답 테스트 (상태 코드 + 응답 스키마)
   4. HTTP 다차원 채점 (상태코드 0.3 / 응답 스키마 0.4 / 보안 0.3)
   5. 정적 보안 검사 (하드코딩 시크릿 / SQL Injection / eval / 셸 인젝션)
