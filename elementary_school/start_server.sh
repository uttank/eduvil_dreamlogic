#!/bin/bash

# FastAPI 서버 실행 스크립트
# 가상환경: /Users/yhpark/work/openai/venv

echo "Starting Elementary School FastAPI Server..."
echo "Virtual Environment: /Users/yhpark/work/openai/venv"
echo "Server will be available at: http://localhost:8001"
echo "API Documentation: http://localhost:8001/docs"
echo "Alternative Documentation: http://localhost:8001/redoc"
echo ""

# 프로젝트 디렉토리로 이동
cd /Users/yhpark/work/openai/elementary_school_dev

# PYTHONPATH 설정하여 uvicorn 실행
PYTHONPATH=/Users/yhpark/work/openai/elementary_school_dev \
/Users/yhpark/work/openai/venv/bin/uvicorn elementary_school:app \
--host 0.0.0.0 \
--port 8001 \
--reload \
--log-level info