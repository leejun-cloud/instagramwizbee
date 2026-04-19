"""
sync_from_firebase.py — RTDB → book_data.json 역방향 동기화.

용도: Firebase RTDB 가 현재 '승인/발행' 상태의 소스 오브 트루스이지만,
    ↳ 그 상태가 로컬/깃에 남지 않으면 팀원이 볼 수도 없고 변경 이력을 추적할 수도 없습니다.
    ↳ 이 스크립트는 RTDB 에서 모든 posts 를 받아 book_data.json 에 병합(merge)한 뒤 덮어씁니다.
    ↳ cron 하루 한 번 혹은 수동 실행 후 `git commit book_data.json` 하면 이력 보존.

정책:
    - RTDB 에만 있고 파일에는 없는 day → 새로 추가
    - 파일에만 있고 RTDB 에는 없는 day → 파일 유지 (삭제하지 않음)
    - 양쪽 다 있으면 → RTDB 가 승인/발행 플래그에 대해 우선, 나머지 필드는 기존 파일값 유지 후 RTDB 가 덮어씀

실행:
    python sync_from_firebase.py               # 일반 실행 (book_data.json 덮어쓰기)
    python sync_from_firebase.py --dry-run     # diff 만 출력
"""

import json
import os
import sys
import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

load_dotenv()

DATABASE_URL = "https://insta-wizbee-cloud-2026-default-rtdb.firebaseio.com"
DATA_FILE = "book_data.json"


def init_fb():
    if not firebase_admin._apps:
        cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if cred_json:
            if os.path.exists(cred_json):
                cred = credentials.Certificate(cred_json)
            else:
                cred = credentials.Certificate(json.loads(cred_json))
            firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
        else:
            firebase_admin.initialize_app(options={"databaseURL": DATABASE_URL})
    return db.reference("posts")


def load_local():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_remote():
    snap = init_fb().get() or {}
    if isinstance(snap, list):
        return [p for p in snap if p]
    if isinstance(snap, dict):
        return list(snap.values())
    return []


def merge(local, remote):
    """local/remote 둘 다 list[dict] 형태. day 키로 매칭."""
    by_day = {p["day"]: dict(p) for p in local if p and "day" in p}
    for rp in remote:
        if not rp or "day" not in rp:
            continue
        d = rp["day"]
        if d in by_day:
            # 병합: RTDB 값이 우선 (최신 상태), 파일에만 있는 필드는 유지
            merged = dict(by_day[d])
            merged.update(rp)
            by_day[d] = merged
        else:
            by_day[d] = dict(rp)
    return sorted(by_day.values(), key=lambda p: p.get("day", 99999))


def diff_summary(before, after):
    before_map = {p["day"]: p for p in before if "day" in p}
    after_map = {p["day"]: p for p in after if "day" in p}
    added = sorted(set(after_map) - set(before_map))
    changed = []
    for d in sorted(set(before_map) & set(after_map)):
        if before_map[d] != after_map[d]:
            deltas = []
            for k in set(before_map[d]) | set(after_map[d]):
                if before_map[d].get(k) != after_map[d].get(k):
                    deltas.append(k)
            changed.append((d, deltas))
    return added, changed


def main():
    dry = "--dry-run" in sys.argv
    local = load_local()
    remote = fetch_remote()
    print(f"📥 Remote posts: {len(remote)} | 📄 Local posts: {len(local)}")

    merged = merge(local, remote)
    added, changed = diff_summary(local, merged)

    if added:
        print(f"\n➕ Added {len(added)} days: {added}")
    if changed:
        print(f"\n📝 Changed {len(changed)} days:")
        for d, deltas in changed[:20]:
            print(f"   Day {d}: fields {deltas}")
        if len(changed) > 20:
            print(f"   …and {len(changed) - 20} more")
    if not added and not changed:
        print("✅ No changes.")
        return

    if dry:
        print("\n[DRY RUN] book_data.json not modified.")
        return

    # Write atomically
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)
    print(f"\n💾 Wrote {DATA_FILE} ({len(merged)} posts) at {datetime.datetime.now().isoformat(timespec='seconds')}")
    print("👉 `git add book_data.json && git commit -m 'chore: sync RTDB state'` 으로 버전 보존하세요.")


if __name__ == "__main__":
    main()
