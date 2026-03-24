#!/bin/bash
cd "$(dirname "$0")"

# 가상환경 활성화
source .venv/bin/activate

# 백그라운드 워커 (자동 발행 모니터링 로직 - 예시)
# python auto_worker.py &

echo "🚀 Wizbee Dashboard 켜는 중..."
echo "👉 브라우저에서 접속하세요: http://localhost:8000"
uvicorn dashboard_app:app --host 0.0.0.0 --port 8000 --reload
