"""
_template.py — 새 콘텐츠 팩을 만들 때 복사해서 쓰는 빈 템플릿.

워크플로:
    1. Cowork에서 Claude에게 "위즈비 Day N~M 콘텐츠 팩 만들어줘" 라고 요청
    2. Claude가 이 파일을 복사해 `dayN_M.py`로 채워 넣음 (PACK dict 작성)
    3. `python content_packs/dayN_M.py --dry-run` 으로 미리보기
    4. OK 면 `python content_packs/dayN_M.py` 실행
    5. `python insta_autopilot.py --seed` 으로 RTDB 반영

이 파일 자체는 실행용이 아닙니다 (PACK 이 비어 있음).
"""

import json
import os
import sys

DATA_FILE = "book_data.json"

# ────────────────────────────────────────────────────────────────
# PACK — 각 포스트는 다음 5개 필드를 반드시 채울 것.
# 상태 필드 (approved / published / scheduled_date / scheduled_time) 는
# 절대 건드리지 말 것 — apply 가 알아서 보존함.
# ────────────────────────────────────────────────────────────────
# 보이스 규칙 (Days 1, 4, 5, 6, 10 기존 승인 포스트 기반):
#   book_title : "저자 <책제목>" (권장) 또는 "책제목 (저자)"
#   excerpt    : 실제 책의 원문 인용 한 문장
#   hook       : 이모지 + 단정형 한 문장, 20~45자 권장
#   caption    : excerpt + ✨ 또는 📖 + 책 정보 + 2~3문장 인사이트 + 인라인 해시태그
#                (hashtags 필드에 있는 태그는 caption 끝에도 동일하게 노출할 것)
#   hashtags   : 핵심 5~6개, '#위즈비' 또는 '#Wizbee' 하나는 꼭 포함
# ────────────────────────────────────────────────────────────────

PACK = {
    # 예시 — 실제 사용 시 아래 dict 는 지우고 덮어쓸 것.
    # 42: {
    #     "book_title": "저자 <책제목>",
    #     "excerpt": "원문 인용 한 문장.",
    #     "hook": "🔑 이모지 + 한 문장.",
    #     "caption": "인용문. ✨\n\n📖 \"책제목\" — 저자\n\n인사이트 두세 문장.\n\n#태그1 #태그2 #위즈비",
    #     "hashtags": "#태그1 #태그2 #위즈비",
    # },
}

# 아래 apply_pack/main 은 손대지 말 것. 표준 적용 로직입니다.
def apply_pack():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    applied = 0
    for post in data:
        d = post.get("day")
        if d in PACK:
            new = PACK[d]
            for field in ("book_title", "excerpt", "hook", "caption", "hashtags"):
                post[field] = new[field]
            applied += 1
    return data, applied


def main():
    if not PACK:
        print("ℹ️ PACK 이 비어있습니다. _template.py 그대로 실행하지 마세요.")
        sys.exit(0)

    dry = "--dry-run" in sys.argv
    if not os.path.exists(DATA_FILE):
        print(f"❌ {DATA_FILE} 이 현재 디렉터리에 없습니다. 프로젝트 루트에서 실행하세요.")
        sys.exit(1)

    data, applied = apply_pack()
    print(f"🧾 팩 적용: {applied}/{len(PACK)}개")

    if dry:
        print("[DRY RUN] 저장 생략.")
        return

    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)
    print(f"💾 {DATA_FILE} 갱신 완료.")


if __name__ == "__main__":
    main()
