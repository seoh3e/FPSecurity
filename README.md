---

# FPSecurity – Frontend (Admin Dashboard)

## 📌 Frontend Overview

FPSecurity 프로젝트의 프론트엔드는
**FPS 게임 보안 관제용 관리자(Admin) 대시보드**를 목표로 구현되었습니다.

관리자는 이 대시보드를 통해

* 비정상 행위가 탐지된 이벤트를 한눈에 확인하고
* 특정 플레이어 단위로 위험도(Risk) 및 분석 결과를 조회할 수 있습니다.

현재 프론트엔드는 **백엔드 연동 전 단계**로,
UI/UX 설계와 화면 흐름 검증을 위해 **Mock 데이터 기반**으로 구현되어 있습니다.

---

## 🛠️ Tech Stack (Frontend)

* **Next.js (App Router)**
* **React**
* **TypeScript**
* **Tailwind CSS**
* **Client Components (`use client`)**

---

## 📂 Frontend Directory Structure

```
src/app
├── components
│   └── RiskBadge.tsx        # 위험도(Risk) 시각화 컴포넌트
│
├── events
│   └── page.tsx             # 보안 탐지 이벤트 목록 페이지
│
├── players
│   └── [id]
│       └── page.tsx         # 플레이어 상세 분석 페이지 (Dynamic Route)
│
├── layout.tsx               # 공통 레이아웃
├── page.tsx                 # 메인 페이지
└── globals.css              # 글로벌 스타일
```

---

## 📊 주요 화면 구성

### 1️⃣ Security Events – 탐지 이벤트 목록 (`/events`)

관리자가 가장 먼저 확인하는 **탐지 이벤트 리스트 화면**입니다.

**표시 정보**

* 탐지 유형 (Speed Hack, Fire Rate, Teleport 등)
* 플레이어 ID
* 위험도(Risk Level)
* 탐지 시각
* 상세 페이지 이동 버튼

**특징**

* 위험도에 따라 시각적으로 구분된 Badge 사용
* 실제 운영 환경을 고려한 관리자 테이블 UI 구성
* 추후 백엔드 API 연동을 고려한 구조 설계

---

### 2️⃣ Player Detail – 플레이어 상세 페이지 (`/players/[id]`)

특정 플레이어의 **보안 분석 결과를 집중적으로 확인하는 화면**입니다.

**구성 요소**

* URL 기반 Dynamic Route (`/players/1023`)
* 현재 조회 중인 플레이어 ID 표시
* 최근 탐지 이벤트 목록
* 위험도(Risk) Badge 시각화
* AI 분석 요약 (예시 데이터)

**구현 포인트**

* `useParams()`를 사용해 URL에서 플레이어 ID 추출
* Client Component 기반으로 화면 렌더링
* 실제 보안 분석 시스템 UI를 가정한 정보 배치

---

## 🎨 UI/UX 설계 의도

* **관리자 관점에서 빠른 판단이 가능하도록 구성**
* Risk Level을 숫자 + 색상으로 직관적으로 표현
* 이벤트 목록 → 플레이어 상세로 자연스럽게 이어지는 흐름
* “보안 관제 시스템” 느낌을 살린 다크 UI 기반 디자인

---

## 🔮 향후 프론트엔드 확장 계획

* 백엔드 API 연동 (실제 탐지 데이터 수신)
* 실시간 이벤트 업데이트
* 필터링 / 정렬 기능 (Risk, 시간, 유형 기준)
* 관리자 액션 UI (경고, 제한, 차단 등)
* 차트 기반 시각화 (Risk 추이, 반복 탐지 패턴)

---

## ℹ️ Note

현재 프론트엔드는 **Mock 데이터 기반 프로토타입**이며,
백엔드 연동을 전제로 구조 및 컴포넌트가 설계되었습니다.

---

