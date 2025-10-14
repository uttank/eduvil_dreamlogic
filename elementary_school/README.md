# Elementary School FastAPI Backend

초등학교 관련 서비스를 위한 FastAPI 백엔드 보일러플레이트

## 📋 프로젝트 개요

이 프로젝트는 초등학교 관련 서비스를 위한 RESTful API 백엔드입니다. FastAPI를 사용하여 구축되었으며, 학생 관리, 인증, CORS 등의 기본 기능을 제공합니다.

## 🚀 빠른 시작

### 1. 가상환경 활성화

이 프로젝트는 `/Users/yhpark/work/openai/venv` 가상환경을 사용합니다.

### 2. 의존성 설치

```bash
/Users/yhpark/work/openai/venv/bin/pip install -r requirements.txt
```

### 3. 서버 실행

**방법 1: 스크립트 사용 (권장)**
```bash
./start_server.sh
```

**방법 2: 직접 실행**
```bash
cd /Users/yhpark/work/openai/elementary_school_dev
PYTHONPATH=/Users/yhpark/work/openai/elementary_school_dev \
/Users/yhpark/work/openai/venv/bin/uvicorn elementary_school:app \
--host 0.0.0.0 --port 8001 --reload
```

### 4. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## 📚 API 엔드포인트

### 기본 엔드포인트

- `GET /` - 서버 상태 확인
- `GET /health` - 헬스 체크

### 🌟 진로 탐색 API (메인 기능)

- `POST /career/start` - 진로 탐색 세션 시작
- `GET /career/{session_id}/question` - 현재 단계 질문 조회
- `POST /career/{session_id}/submit` - 응답 제출 및 다음 단계 진행
- `GET /career/{session_id}/summary` - 세션 요약 조회
- `GET /career/{session_id}/status` - 세션 상태 조회
- `DELETE /career/{session_id}` - 세션 삭제

### 학생 관리 엔드포인트

- `GET /students` - 모든 학생 조회
- `GET /students/{student_id}` - 특정 학생 조회
- `POST /students` - 새 학생 등록
- `PUT /students/{student_id}` - 학생 정보 수정
- `DELETE /students/{student_id}` - 학생 삭제

### 보안 엔드포인트

- `GET /protected` - 인증이 필요한 보호된 라우트 (Bearer 토큰 필요)

## 🔧 설정

### 환경 변수

필요한 경우 `.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다:

```env
# 서버 설정
HOST=0.0.0.0
PORT=8001
DEBUG=True

# 데이터베이스 설정 (향후 사용시)
# DATABASE_URL=sqlite:///./elementary_school.db

# 보안 설정 (향후 사용시)
# SECRET_KEY=your-secret-key-here
```

### CORS 설정

현재 모든 출처에서의 요청을 허용하도록 설정되어 있습니다. 프로덕션 환경에서는 구체적인 도메인으로 제한하세요:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 도메인으로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 테스트

### 진로 탐색 API 테스트

```bash
# 간단한 테스트 실행
python3 simple_test.py

# 전체 진로 탐색 과정 테스트
python3 test_career_api.py
```

### 진로 탐색 API 사용 예시

```bash
# 1. 세션 시작
curl -X POST "http://localhost:8001/career/start"

# 2. 현재 질문 조회 (응답에서 session_id 사용)
curl "http://localhost:8001/career/{session_id}/question"

# 3. 0단계 - 학생 정보 제출
curl -X POST "http://localhost:8001/career/{session_id}/submit" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "{session_id}",
       "student_info": {
         "name": "김철수",
         "age": 10
       }
     }'

# 4. 1단계 - 흥미 탐색 응답
curl -X POST "http://localhost:8001/career/{session_id}/submit" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "{session_id}",
       "response": {
         "choice_number": 2
       }
     }'

# 5. 세션 요약 조회
curl "http://localhost:8001/career/{session_id}/summary"
```

### 기존 학생 관리 API 테스트

```bash
# 서버 상태 확인
curl http://localhost:8001/

# 학생 목록 조회
curl http://localhost:8001/students

# 새 학생 등록
curl -X POST "http://localhost:8001/students" \
     -H "Content-Type: application/json" \
     -d '{"name": "김철수", "grade": 3, "class_number": 1}'

# 보호된 라우트 접근 (인증 토큰 필요)
curl -H "Authorization: Bearer valid-token" http://localhost:8001/protected
```

## 📦 프로젝트 구조

```
elementary_school_dev/
├── elementary_school.py    # 메인 FastAPI 애플리케이션
├── models.py              # 데이터 모델 및 상수 정의
├── career_service.py      # 진로 탐색 서비스 로직
├── start_server.sh        # 서버 실행 스크립트
├── test_career_api.py     # 진로 탐색 API 전체 테스트
├── simple_test.py         # 간단한 API 테스트
├── requirements.txt       # Python 의존성
├── README.md             # 프로젝트 문서
└── chatgpt_prompt.md      # ChatGPT 프롬프트 매뉴얼
```

## 🔄 개발 가이드

### 새로운 엔드포인트 추가

1. `elementary_school.py`에 새로운 라우터 함수 추가
2. Pydantic 모델이 필요한 경우 정의
3. 서버 재시작 (개발 모드에서는 자동 리로드)
4. `/docs`에서 새로운 API 확인

### 데이터베이스 연동

현재는 메모리 내 리스트를 사용하고 있습니다. 실제 데이터베이스 연동을 위해서는:

1. SQLAlchemy 설치: `pip install sqlalchemy alembic`
2. 데이터베이스 모델 정의
3. 데이터베이스 연결 설정
4. CRUD 작업 구현

## 📝 주요 기능

### 🌟 진로 탐색 시스템 (메인 기능)
- ✅ 0~4단계 체계적 진로 탐색 프로세스
- ✅ 학생 이름 맞춤형 응원 메시지
- ✅ 11개 선택지 + 기타 선택 지원
- ✅ 세션 기반 진행 상태 관리
- ✅ 실시간 진행률 추적
- ✅ 응답 요약 및 분석

### 🔧 기술적 기능
- ✅ FastAPI 기반 RESTful API
- ✅ 자동 API 문서 생성 (Swagger UI, ReDoc)
- ✅ CORS 지원
- ✅ 요청/응답 검증 (Pydantic)
- ✅ 에러 핸들링
- ✅ 로깅
- ✅ 인증 구조 (Bearer 토큰)
- ✅ 핫 리로드 개발 환경

## 🚧 향후 개선 사항

- [ ] 실제 데이터베이스 연동 (SQLite/PostgreSQL)
- [ ] JWT 토큰 기반 인증 시스템
- [ ] 사용자 권한 관리
- [ ] 테스트 코드 작성
- [ ] Docker 컨테이너화
- [ ] API 버전 관리
- [ ] 로그 파일 관리
- [ ] 배포 설정

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.