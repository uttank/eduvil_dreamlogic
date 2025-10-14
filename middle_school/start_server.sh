#!/bin/bash

# 중학교 진로탐색 서버 시작 스크립트

echo "🌟 중학교 진로탐색 서버를 시작합니다..."

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 작업 디렉토리: $SCRIPT_DIR"

# Python 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "🐍 Python 가상환경 활성화 중..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "🐍 상위 디렉토리의 Python 가상환경 활성화 중..."
    source ../venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "📦 필요한 패키지 설치 확인 중..."
pip install -r requirements.txt

# OpenAI API 키 확인
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
    echo "💡 AI 기능을 사용하려면 OpenAI API 키를 설정해주세요:"
    echo "   export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "🔄 API 키 없이도 앱의 기본 기능은 사용할 수 있습니다."
else
    echo "✅ OpenAI API 키가 설정되어 있습니다."
fi

# 포트 설정
PORT=${PORT:-8001}
echo "🚀 서버를 포트 $PORT 에서 시작합니다..."

# 서버 시작
echo "🌟 중학교 진로탐색 서버 실행 중..."
echo "📱 브라우저에서 http://localhost:$PORT 로 접속하세요!"
echo "🛑 서버를 중지하려면 Ctrl+C 를 누르세요."
echo ""

python -m uvicorn middle_school:app --host 0.0.0.0 --port $PORT --reload