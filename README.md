# 🐝 위즈비 콘텐츠 대시보드 (Wizbee Dashboard)

위즈비의 인스타그램 카드 뉴스 콘텐츠를 직관적으로 관리하고 자동 발행 설정을 제어할 수 있는 전용 관리 도구입니다.

## 🚀 빠른 시작 방법 (Launch Guide)

1.  **터미널(Terminal)** 앱을 실행합니다.
2.  아래 명령어를 복사하여 붙여넣고 엔터를 누릅니다:
    ```bash
    cd /Users/ichangjun/Documents/GitHub/위즈비 && ./start_dashboard.sh
    ```
3.  브라우저(Chrome 등)를 열고 아래 주소로 접속합니다:
    > **[http://localhost:8000](http://localhost:8000)**

---

## 🌟 주요 기능 (Main Features)

### 1. 콘텐츠 통합 관리 (Content Management)
*   **수정(✎)**: 카드 뉴스의 Hook, 캡션, 해시태그를 즉시 편집할 수 있습니다.
*   **승인(☑)**: 발행할 포스트를 직접 골라 승인 상태로 전환합니다.
*   **삭제(🗑)**: 마음에 들지 않는 포스트를 목록에서 영구적으로 제거합니다.

### 2. 🪄 완전 자동 발행 모드 (Auto-Publish All)
*   좌측 사이드바의 **[Auto-Publish All]** 스위치를 켜면, 매번 승인 버튼을 누르지 않아도 시스템이 `book_data.json`에 있는 포스트를 매일 순차적으로 자동 발행합니다.
*   스위치를 끄면, 대시보드에서 **[APPROVED]** 표시가 된 포스트만 발행됩니다.

---

## 🛠️ 시스템 구성 (System Architecture)

*   **데이터**: `book_data.json` (콘텐츠 상세 정보 및 승인 상태 저장)
*   **설정**: `settings.json` (자동 발행 모드 온/오프 상태 저장)
*   **실행 환경**: 가상환경(`.venv`) 내 FastAPI 백엔드 + Vanilla JS 프론트엔드

---

## ⚠️ 주의 사항 (Important Notes)

*   **인코딩**: 데이터 파일(`book_data.json`)은 반드시 **UTF-8** 형식으로 유지되어야 합니다. (직접 수정보다는 대시보드 화면에서의 수정을 권장합니다.)
*   **네트워크**: 인스타그램 앱 발행 시 안정적인 인터넷 연결이 필요합니다.
*   **디스크 공간**: 시스템 여유 공간이 부족하면 대시보드가 정상적으로 작동하지 않을 수 있으니 주기적인 공간 확보를 권장합니다.

---
*Developed with ✨ by Antigravity for Wizbee.*
