# content_packs/ — 로컬 콘텐츠 생성 워크플로

Claude API를 사용하지 않고, **Cowork 세션에서 Claude가 직접** 책 기반 인스타 콘텐츠를 생성해 `book_data.json` 에 병합하는 구조입니다.

## 왜 이렇게 하나?

- **API 비용 0원**: 별도 Anthropic/Gemini 키가 필요 없음
- **재현성**: 생성된 내용이 `.py` 파일로 깃에 남아 이력 추적 가능
- **안전**: 상태 필드(`approved`, `published`, `scheduled_date`)를 절대 건드리지 않음
- **검토 가능**: dry-run 으로 미리보기 후 확정

## 디렉터리 구조

```
content_packs/
├── README.md          # 이 파일
├── _template.py       # 빈 템플릿 — 새 팩 만들 때 복사용
└── day16_40.py        # 2026-04-19 생성된 25개 포스트 팩
```

## 새 팩을 생성하는 방법

### 1) Cowork에서 요청
Claude에게 이렇게 말하세요:

> "위즈비 Day 41~55 콘텐츠 팩 만들어줘. 여성 리더십/교육 관련 책 위주로."

> "Day 41 부터 한국 작가 책으로 10개만 더 만들어줘. 기존 voice 유지."

> "기존 Day 20 (공자 논어) 와 Day 24 (아주 작은 습관의 힘) 을 다른 책으로 교체해줘."

### 2) Claude가 수행하는 작업
1. 현재 `book_data.json` 의 book_title 중복 확인
2. Days 1, 4, 5, 6, 10 의 승인된 voice 재확인
3. `content_packs/dayN_M.py` 파일 생성 (`_template.py` 복사 기반)
4. `PACK` dict 에 책별 `book_title / excerpt / hook / caption / hashtags` 작성

### 3) 사용자가 적용
```bash
# 프로젝트 루트에서
python content_packs/day41_55.py --dry-run   # 미리보기
python content_packs/day41_55.py             # 실제 적용

# 변경사항을 RTDB 에도 반영
python insta_autopilot.py --seed

# 필요하면 스케줄 배정
python assign_schedule.py --start 2026-05-10

# 변경 내용을 깃에 커밋
git add book_data.json content_packs/day41_55.py
git commit -m "feat(content): add Day 41-55 content pack"
```

## 보이스 규칙 (필수)

기존 승인된 Days 1, 4, 5, 6, 10 의 voice 에서 추출:

| 필드 | 규칙 |
|---|---|
| `book_title` | `"저자 <책제목>"` 권장. 예: `"에픽테토스 <담론록>"` |
| `excerpt` | 책의 실제 원문 인용 한 문장. 번역은 공식 번역 우선 |
| `hook` | 이모지 1개 + 단정형 한 문장. 20~45자. 예: `"🔥 지금의 나는 완성형이 아니라 다리입니다."` |
| `caption` | 구조: `excerpt ✨ \n\n📖 "책제목" — 저자 \n\n 2~3문장 인사이트 \n\n hashtags` |
| `hashtags` | 5~6개. `#위즈비` 또는 `#Wizbee` 하나 반드시 포함. 책/주제 태그 포함 |

**금지 사항:**
- ❌ 지어낸 인용문 (excerpt는 반드시 실제 책에 있는 문장)
- ❌ AI 티 나는 과도한 감탄사/굵은 글씨
- ❌ 기존 Days 1~15 과 중복되는 book_title
- ❌ hashtags 에 너무 많은 태그 (5~6개 권장)

## 이미 생성된 팩

| 파일 | Day 범위 | 생성일 | 테마 |
|---|---|---|---|
| `day16_40.py` | 16~40 (25개) | 2026-04-19 | 고전 철학 + 리더십 + 문학 + 품성교육 믹스 |

## 상태 필드 보존 보장

`apply_pack()` 함수는 이 5개 필드만 업데이트:
- `book_title`, `excerpt`, `hook`, `caption`, `hashtags`

다음 필드는 **절대** 건드리지 않음:
- `day`, `approved`, `published`, `scheduled_date`, `scheduled_time`, `image_prompt`

덕분에 이미 승인/발행된 포스트의 상태가 새 팩 적용으로 초기화되는 일이 없습니다.
