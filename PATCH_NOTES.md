# insta-wizbee — P0/P1 Patch Notes
날짜: 2026-04-19
작업자: Claude

## 0. 안전한 백업 먼저
작업 전 전체 스냅샷을 보관했습니다. 문제가 생기면 이 파일로 언제든 복원 가능합니다.

- `dreamagent/insta-wizbee-backup-20260419_025850.tar.gz` (7.9MB, .git/__pycache__/.DS_Store 제외)
- 복원: `tar -xzf insta-wizbee-backup-20260419_025850.tar.gz -C /복원할경로`

---

## 1. P0 — 보안 긴급 수정

### 1-1. 하드코딩된 Instagram Access Token 제거
아래 3개 파일에서 장기 토큰이 소스코드에 그대로 박혀 있었습니다. 깃 히스토리에도 남아 있으므로 토큰 자체는 **노출된 것으로 간주하고 새로 발급**해야 합니다.

- `diagnose_insta.py` — 상단 상수 → `os.getenv("INSTA_ACCESS_TOKEN")`
- `host_and_upload.py` — 상단 상수 → `os.getenv("INSTA_ACCESS_TOKEN")`
- `insta_commenter.py` — `os.getenv(..., "IGAALM...")` fallback 리터럴 삭제

세 파일 모두 공통 패턴으로 통일:
```python
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("INSTA_ACCESS_TOKEN")
ACCOUNT_ID  = os.getenv("INSTA_ACCOUNT_ID")
if not ACCESS_TOKEN or not ACCOUNT_ID:
    raise RuntimeError("Missing INSTA_ACCESS_TOKEN or INSTA_ACCOUNT_ID.")
```

### 1-2. Firebase 보안 규칙 잠그기
이전: `read/write: if true` — 인터넷 어느 누구나 DB를 읽고/지우고/덮어쓸 수 있었음.

변경:
- `database.rules.json` (RTDB): 읽기 공개, 쓰기는 `auth != null` 필수. 포스트 필드별 type 검증 추가.
- `firestore.rules`: 전체 차단 (현재 Firestore 미사용). 사용 시작하면 그때 개방.

대시보드 쓰기가 안 깨지도록 `index.html`에 Firebase **Anonymous Auth** 자동 로그인을 심었습니다. 콘솔에서 Anonymous provider를 켜주시기만 하면 됩니다(아래 §3).

---

## 2. P1 — 기능 버그 수정

| # | 파일 | 문제 | 조치 |
|---|------|------|------|
| 1 | `.github/workflows/daily_post.yml` | cron 두 개 (`0 23 * * *` + `30 1 * * *`) → 하루 2회 발행 | 임시 크론 삭제. KST 08:00 1회만 유지. `TZ: Asia/Seoul` 추가 |
| 2 | `insta_autopilot.py` | `time.sleep(60)` 무조건 대기 → 큰 이미지는 실패, 작은 이미지는 시간 낭비 | `wait_for_container_ready()` 로 `status_code=FINISHED` 폴링 (5s 간격, 180s 타임아웃) |
| 3 | `insta_autopilot.py` (`seed_to_fb`) | `update()` 가 RTDB의 `approved/published` 플래그를 매번 덮어씀 → 대시보드 승인이 CI 실행마다 지워짐 | 시드 전에 기존 상태 읽어 sticky 플래그(`approved`, `published`, `scheduled_date`, `scheduled_time`) 유지 |
| 4 | `insta_autopilot.py` (`run_auto`) | `scheduled_date` 형식 자유 / 타입 오류 가능 | `_norm_date()` 로 `YYYY-MM-DD`/`YYYY/MM/DD` 검증, 실패 시 조용히 무시 후 fallback |
| 5 | `insta_approver.py` | `post['image_prompt']` 필드 없는 포스트에서 `KeyError` | `.get()` 패턴 + `scheduled_date` 도 지원, 없으면 `(프롬프트 없음)` |
| 6 | `app.js` (대시보드) | `<img src=".png">` 만 시도 → `.jpg` 파일은 바로 placeholder로 추락 | `handleImgFallback()` 체인: `day_N.jpg → day_N.png → test_image.png`, 루프 방지 |

---

## 3. 사용자 직접 해주셔야 할 작업 (★ 필수)

아래 4개는 제가 대신 못 합니다. 순서대로 꼭 해주세요.

### ① Facebook / Meta Developer Console — **기존 토큰 무효화**
1. https://developers.facebook.com/apps → 해당 앱
2. **App Settings → Basic** 에서 App Secret **Reset**
3. **System Users** 또는 **Marketing API → Tools** 에서 노출된 토큰 삭제
4. **새 토큰 발급** — Page Access Token을 장기(Long-lived)로 연장 권장
   - Short-lived → Long-lived User Token (60일) → 그 토큰으로 Page Access Token 획득(무기한)

### ② GitHub Secrets 재설정
Repository → Settings → **Secrets and variables → Actions** 에서 추가/갱신:

| Name | Value |
|---|---|
| `INSTA_ACCESS_TOKEN` | ①에서 새로 뽑은 토큰 |
| `INSTA_ACCOUNT_ID` | `17841427998042847` |
| `FIREBASE_SERVICE_ACCOUNT` | 서비스 계정 JSON **전체 내용** (경로 아님) |

로컬 `.env` 도 똑같이 새 토큰으로 덮어쓰세요 — 현재 `.env` 의 값은 무효가 됐다고 간주.

### ③ 깃 히스토리에서 토큰 지우기 (선택이지만 권장)
토큰이 과거 커밋에 박혀 있으면 스캐너 봇이 계속 발견합니다. 리포지토리가 public 이라면 **필수**:
```bash
# git-filter-repo 설치 (brew install git-filter-repo)
cd /Users/ichangjun/Documents/GitHub/위즈비
git filter-repo --replace-text <(echo '<LEAKED_INSTA_TOKEN>==>REDACTED')
git push origin --force --all
git push origin --force --tags
```
⚠️ force push 전에 팀원/CI가 있다면 공지.

### ④ Firebase Console — Anonymous Auth 활성화
https://console.firebase.google.com/project/insta-wizbee-cloud-2026
- **Authentication → Sign-in method → Anonymous → Enable**
- 이게 꺼져 있으면 새 RTDB Rules(`auth != null`) 아래 대시보드에서 **승인 토글/수정이 막힙니다**.

### ⑤ 새 Rules 배포
```bash
cd /Users/ichangjun/Documents/GitHub/위즈비
firebase deploy --only database    # database.rules.json 반영
firebase deploy --only firestore:rules   # firestore.rules 반영
```

---

## 4. 변경 파일 요약

```
diagnose_insta.py         (토큰 제거 + .env 로드)
host_and_upload.py        (토큰 제거 + .env 로드)
insta_commenter.py        (리터럴 fallback 제거 + 가드)
insta_autopilot.py        (polling, state-preserving seed, date 파서)
insta_approver.py         (get() 패턴으로 KeyError 제거)
app.js                    (이미지 fallback 체인 jpg→png→placeholder)
index.html                (Anonymous Auth 자동 로그인)
database.rules.json       (auth != null + validation)
firestore.rules           (전체 차단)
.github/workflows/daily_post.yml   (중복 cron 삭제, TZ 추가)
```

## 5. P2 — 운영/복원성 보강 (2026-04-19 추가)

### 5-1. 멱등성(idempotency) 가드
`insta_autopilot.py` `run_auto()` 가 발행 직전 RTDB 를 재조회해 `published=True` 면 **즉시 중단**합니다. 크론 중복 또는 수동 재실행 시 동일 포스트가 두 번 올라가지 않습니다.

### 5-2. Slack 실패 알림 훅
`notify_slack(message, level)` 헬퍼 추가. 다음 상황에서 자동 알림:

- 이미지 파일 없음(`warn`)
- catbox.moe 호스팅 실패(`error`)
- Instagram 발행 실패(`error`)
- 발행 성공(`success`)
- 스크립트가 예외로 중단(`error`) — 마지막 라인 200자 요약

환경 변수: `SLACK_ALERT_WEBHOOK_URL` (없으면 `SLACK_WEBHOOK_URL` 재사용, 둘 다 없으면 조용히 패스).

### 5-3. RTDB → `book_data.json` 역방향 동기화
신규 파일: `sync_from_firebase.py`

```bash
python sync_from_firebase.py --dry-run   # diff 미리보기
python sync_from_firebase.py             # 실제 덮어쓰기
git add book_data.json && git commit -m "chore: sync RTDB state"
```

`approved`/`published`/`scheduled_date` 변경 이력을 깃에 남길 수 있습니다.

### 5-4. `scheduled_date` 자동 배정 헬퍼
신규 파일: `assign_schedule.py`

```bash
python assign_schedule.py                          # 내일부터 순차 배정
python assign_schedule.py --start 2026-05-01
python assign_schedule.py --skip-weekends --rtdb   # 주말 건너뛰고 RTDB 도 반영
python assign_schedule.py --dry-run                # 미리보기
```

`approved=True AND published=False` 인 포스트만 타겟. 기존 `scheduled_date` 는 `--force` 없으면 유지.

---

## 6. P3 — Cowork 로컬 콘텐츠 생성 파이프라인 (2026-04-19 추가)

### 6-1. 문제
Days 16~40 의 25개 포스트가 `Wizbee Wisdom 16~40` placeholder 로만 채워져 있었음. 그간 `batch_generator.py` 는 Claude API 호출 없이 하드코딩된 `BOOK_LIST` + 템플릿 문장으로만 만들었기 때문에 품질이 낮음.

### 6-2. 해결: Claude Cowork 에서 직접 생성
**API 비용 0원**. Cowork 세션에서 Claude 가 직접 Days 1, 4, 5, 6, 10 의 기존 승인된 voice 를 분석해 25개 포스트를 고품질로 작성하고 그대로 `book_data.json` 에 merge.

**적용된 25개 포스트 (Day 16~40):**

| Day | 책 | 테마 |
|---|---|---|
| 16 | 니체 <차라투스트라는 이렇게 말했다> | 성장 |
| 17 | 키에르케고르 <죽음에 이르는 병> | 실존 |
| 18 | 칸트 <실천이성비판> | 윤리 |
| 19 | 소로 <월든> | 미니멀 |
| 20 | 공자 <논어> | 배움 |
| 21 | 노자 <도덕경> | 리더십 |
| 22 | 장자 <장자> | 지혜 |
| 23 | 스티븐 코비 <7가지 습관> | 자기주도 |
| 24 | 제임스 클리어 <아주 작은 습관의 힘> | 습관 |
| 25 | 칼 뉴포트 <딥 워크> | 몰입 |
| 26 | 카너먼 <생각에 관한 생각> | 의사결정 |
| 27 | 로버트 그린 <인간 본성의 법칙> | 심리 |
| 28 | 짐 콜린스 <위대한 기업으로> | 경영 |
| 29 | 피터 센게 <학습하는 조직> | 조직문화 |
| 30 | 글래드웰 <아웃라이어> | 성공 |
| 31 | 도스토옙스키 <카라마조프가의 형제들> | 진정성 |
| 32 | 톨스토이 <사람은 무엇으로 사는가> | 사랑 |
| 33 | 헤밍웨이 <노인과 바다> | 불굴 |
| 34 | C.S. 루이스 <스크루테이프의 편지> | 성찰 |
| 35 | 본회퍼 <나를 따르라> | 책임 |
| 36 | 이어령 <디지로그> | 공감 |
| 37 | 하라리 <사피엔스> | 비전 |
| 38 | 코엘료 <연금술사> | 꿈 |
| 39 | 두히그 <습관의 힘> | 습관 |
| 40 | 생텍쥐페리 <인간의 대지> | 관계 |

### 6-3. 재사용 구조 — content_packs/
앞으로 Day 41~ 추가 팩을 언제든 요청할 수 있도록 다음 구조를 세움:

```
content_packs/
├── README.md         # 워크플로 + voice 규칙
├── _template.py      # 빈 템플릿 (복사해서 새 팩 작성)
└── day16_40.py       # 방금 적용된 팩 (소스 보존)
```

### 6-4. 새 팩 생성 방법 (Cowork에서)
Claude 에게 자유로운 표현으로 요청하면 됩니다:

> "Day 41~55 콘텐츠 팩 만들어줘. 여성 리더십 관련 책 위주로."
>
> "한국 작가 10명으로 Day 41~50 채워줘."
>
> "기존 Day 20 을 다른 책으로 교체해줘."

Claude 는:
1. 현재 `book_data.json` 의 중복 book_title 확인
2. `content_packs/dayN_M.py` 를 `_template.py` 기반으로 생성
3. PACK dict 에 규칙대로 내용 채움

사용자는:
```bash
python content_packs/dayN_M.py --dry-run
python content_packs/dayN_M.py
python insta_autopilot.py --seed
```

### 6-5. 상태 필드 보존 보장
모든 팩 `apply_pack()` 은 `book_title / excerpt / hook / caption / hashtags` 5개 필드만 수정. `approved / published / scheduled_date / scheduled_time` 는 절대 건드리지 않음.

덕분에 이미 승인/발행된 포스트의 상태가 새 팩 적용으로 초기화되는 일이 없습니다.

### 6-6. 백업
P3 적용 전 스냅샷 자동 보관: `book_data.json.bak-before-pack` (프로젝트 루트).

---

## 7. 추가 권장 작업 (향후)

- 이미지 업로드 호스트를 `catbox.moe` (무료, 불안정) → Firebase Storage 또는 Cloudflare R2 로 전환 권장
- Day 7 ("Wizbee Insight") 과 Day 8/11 (중복 자유론/명상록) 도 content pack 으로 리네이밍 고려
- `sync_from_firebase.py` 를 GitHub Actions 야간 스케줄에 추가해 RTDB 상태를 매일 커밋
