#!/bin/bash

echo "🚀 Wizbee Dashboard를 준비 중입니다..."

# 의존성 확인 및 설치
if ! python3 -c "import fastapi, uvicorn" &> /dev/null; then
    echo "📦 필수 패키지(FastAPI, Uvicorn)가 없습니다. 설치를 시작합니다..."
    python3 -m pip install fastapi uvicorn pydantic
fi

echo "🌐 대시보드 서버를 시작합니다: http://127.0.0.1:8000"
echo "💡 브라우저에서 위 주소를 입력해 접속하세요."

# 서버 실행
python3 -m uvicorn dashboard_app:app --host 127.0.0.1 --port 8000 --reload
