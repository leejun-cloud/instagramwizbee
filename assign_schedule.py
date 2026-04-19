"""
assign_schedule.py — 승인되었지만 발행 전인 포스트들에 순차 발행일 자동 배정.

기본 동작:
    - approved=True AND published=False 인 포스트를 day 번호 오름차순으로 정렬
    - 시작일 (기본: 내일) 부터 하루에 1개씩 `scheduled_date` 를 채움
    - 이미 `scheduled_date` 가 있어도 --force 옵션 없으면 건드리지 않음
    - 로컬 book_data.json 과 RTDB 둘 다 업데이트 (선택)

사용법:
    python assign_schedule.py                          # 내일부터, 기존 날짜 유지
    python assign_schedule.py --start 2026-05-01       # 시작일 지정
    python assign_schedule.py --force                  # 기존 scheduled_date 덮어쓰기
    python assign_schedule.py --rtdb                   # 로컬뿐 아니라 RTDB 도 업데이트
    python assign_schedule.py --dry-run                # 변경사항만 출력
"""

import argparse
import datetime
import json
import os
import sys

DATA_FILE = "book_data.json"


def load_local():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_local(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def iter_targets(data, force):
    """Returns sorted list of posts that need a scheduled_date."""
    pending = []
    for p in data:
        if not p.get("approved"):
            continue
        if p.get("published"):
            continue
        if p.get("scheduled_date") and not force:
            continue
        pending.append(p)
    return sorted(pending, key=lambda x: x.get("day", 99999))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", help="YYYY-MM-DD (default: tomorrow)")
    ap.add_argument("--force", action="store_true", help="기존 scheduled_date 덮어쓰기")
    ap.add_argument("--rtdb", action="store_true", help="RTDB도 업데이트")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-weekends", action="store_true", help="토/일 제외")
    args = ap.parse_args()

    start = (
        datetime.date.fromisoformat(args.start)
        if args.start
        else datetime.date.today() + datetime.timedelta(days=1)
    )

    data = load_local()
    targets = iter_targets(data, args.force)
    if not targets:
        print("✅ 배정할 대상 없음 (approved=True AND published=False AND scheduled_date 비어있음).")
        return

    assignments = []
    cursor = start
    for p in targets:
        if args.skip_weekends:
            while cursor.weekday() >= 5:  # 5=Sat, 6=Sun
                cursor += datetime.timedelta(days=1)
        assignments.append((p["day"], cursor.isoformat(), p.get("scheduled_date")))
        p["scheduled_date"] = cursor.isoformat()
        cursor += datetime.timedelta(days=1)

    print(f"📅 배정 미리보기 ({len(assignments)}건):")
    for day, new, old in assignments:
        if old and old != new:
            print(f"  Day {day:>2} : {old}  →  {new}  (변경)")
        else:
            print(f"  Day {day:>2} : {new}")

    if args.dry_run:
        print("\n[DRY RUN] 파일/RTDB 저장 생략.")
        return

    save_local(data)
    print(f"\n💾 {DATA_FILE} 저장 완료.")

    if args.rtdb:
        from dotenv import load_dotenv
        import firebase_admin
        from firebase_admin import credentials, db

        load_dotenv()
        if not firebase_admin._apps:
            cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
            url = "https://insta-wizbee-cloud-2026-default-rtdb.firebaseio.com"
            if cred_json:
                if os.path.exists(cred_json):
                    cred = credentials.Certificate(cred_json)
                else:
                    cred = credentials.Certificate(json.loads(cred_json))
                firebase_admin.initialize_app(cred, {"databaseURL": url})
            else:
                firebase_admin.initialize_app(options={"databaseURL": url})

        posts_ref = db.reference("posts")
        for day, new, _ in assignments:
            posts_ref.child(str(day)).update({"scheduled_date": new})
        print(f"☁️  RTDB 에도 {len(assignments)}건 반영 완료.")


if __name__ == "__main__":
    main()
