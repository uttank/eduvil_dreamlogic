"""
FastAPI 백엔드 기본 보일러플레이트
초등학교 관련 서비# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime
import logging

# 진로 탐색 관련 imports
from .models import (
    StudentInfo, StepResponse, NextStageRequest, ApiResponse,
    CareerStage, StageQuestionResponse, CareerRecommendationResponse
)
from .career_service import career_service
from .openai_service import ai_service
from .pdf_generator import ElementaryCareerPDFGenerator

# 추가 요청 모델
class RecommendationRequest(BaseModel):
    regenerate: Optional[bool] = False

class PDFDownloadRequest(BaseModel):
    student_name: str
    responses: Dict[CareerStage, Dict]
    final_recommendation: str
    dream_logic_result: Optional[str] = ""
    encouragement_message: Optional[str] = ""

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Elementary School API",
    description="초등학교 관련 서비스를 위한 백엔드 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (절대경로 사용)
import os
from pathlib import Path

current_dir = Path(__file__).parent
static_dir = current_dir / "static"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# 보안 설정
security = HTTPBearer()

# Pydantic 모델들
class StudentBase(BaseModel):
    name: str
    grade: int
    class_number: int

class Student(StudentBase):
    id: int
    created_at: datetime

class StudentCreate(StudentBase):
    pass

class ResponseModel(BaseModel):
    message: str
    data: Optional[dict] = None

# 임시 데이터베이스 (실제 프로젝트에서는 실제 DB 사용)
fake_students_db = []
student_id_counter = 1

# 의존성 함수들
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    인증 토큰 검증 (임시 구현)
    실제 프로젝트에서는 JWT 토큰 검증 로직 구현
    """
    # 임시로 토큰이 "valid-token"인 경우만 허용
    if credentials.credentials != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user": "authenticated"}

# 라우터들

@app.get("/")
async def root():
    """메인 페이지"""
    return FileResponse(static_dir / "index.html")

@app.get("/api", response_model=ResponseModel)
async def api_root():
    """API 루트 엔드포인트"""
    return ResponseModel(
        message="Elementary School API is running!",
        data={"version": "1.0.0", "status": "healthy"}
    )

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/students", response_model=List[Student])
async def get_students():
    """모든 학생 정보 조회"""
    return fake_students_db

@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int):
    """특정 학생 정보 조회"""
    student = next((s for s in fake_students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate):
    """새 학생 등록"""
    global student_id_counter
    
    new_student = {
        "id": student_id_counter,
        "name": student.name,
        "grade": student.grade,
        "class_number": student.class_number,
        "created_at": datetime.now()
    }
    
    fake_students_db.append(new_student)
    student_id_counter += 1
    
    logger.info(f"New student created: {new_student['name']}")
    return new_student

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, student: StudentCreate):
    """학생 정보 수정"""
    existing_student = next((s for s in fake_students_db if s["id"] == student_id), None)
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_student.update({
        "name": student.name,
        "grade": student.grade,
        "class_number": student.class_number
    })
    
    logger.info(f"Student updated: {existing_student['name']}")
    return existing_student

@app.delete("/students/{student_id}", response_model=ResponseModel)
async def delete_student(student_id: int):
    """학생 정보 삭제"""
    global fake_students_db
    
    student = next((s for s in fake_students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    fake_students_db = [s for s in fake_students_db if s["id"] != student_id]
    
    logger.info(f"Student deleted: {student['name']}")
    return ResponseModel(message=f"Student {student['name']} deleted successfully")

@app.get("/protected", dependencies=[Depends(get_current_user)])
async def protected_route():
    """인증이 필요한 보호된 라우트 예시"""
    return {"message": "This is a protected route", "data": "sensitive information"}

# =============================================================================
# 진로 탐색 API 엔드포인트들
# =============================================================================

@app.post("/career/start", response_model=ApiResponse)
async def start_career_exploration():
    """진로 탐색 세션 시작"""
    try:
        session_id = career_service.create_session()
        
        return ApiResponse(
            success=True,
            message="진로 탐색 세션이 시작되었습니다!",
            data={
                "session_id": session_id,
                "message": "안녕하세요! 초등학생 진로 탐색을 시작해볼까요? 🌟"
            }
        )
    except Exception as e:
        logger.error(f"세션 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 생성에 실패했습니다.")

@app.get("/career/{session_id}/question")
async def get_current_question(session_id: str):
    """현재 단계의 질문 조회"""
    try:
        question_data = career_service.get_current_question(session_id)
        
        if not question_data:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없거나 질문이 없습니다.")
        
        return ApiResponse(
            success=True,
            message="질문을 가져왔습니다.",
            data=question_data.dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"질문 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="질문 조회에 실패했습니다.")

@app.post("/career/{session_id}/submit", response_model=ApiResponse)
async def submit_response(session_id: str, request: NextStageRequest):
    """응답 제출 및 다음 단계로 진행"""
    try:
        # 요청 검증
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="세션 ID가 일치하지 않습니다.")
        
        # 현재 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        # 응답 제출
        success, message, next_stage = career_service.submit_response(
            session_id=session_id,
            student_info=request.student_info,
            response=request.response
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # 응답 데이터 구성
        response_data = {
            "message": message,
            "next_stage": next_stage,
            "completed": next_stage is None
        }
        
        # 다음 단계가 있으면 다음 질문도 함께 반환
        if next_stage:
            next_question = career_service.get_current_question(session_id)
            if next_question:
                response_data["next_question"] = next_question.dict()
        
        # 모든 단계 완료시 완료 메시지
        if next_stage is None:
            student_name = session.student_info.name if session.student_info else "친구"
            response_data["completion_message"] = f"{student_name}님! 🎉 모든 단계를 완료했어요! 정말 대단해요!"
        
        return ApiResponse(
            success=True,
            message="응답이 성공적으로 제출되었습니다!",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"응답 제출 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="응답 제출에 실패했습니다.")

@app.get("/career/{session_id}/summary")
async def get_session_summary(session_id: str):
    """세션 요약 정보 조회"""
    try:
        summary = career_service.get_session_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        return ApiResponse(
            success=True,
            message="세션 요약을 가져왔습니다.",
            data=summary
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 요약 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 요약 조회에 실패했습니다.")

@app.get("/career/{session_id}/status")
async def get_session_status(session_id: str):
    """세션 상태 조회"""
    try:
        session = career_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        is_completed = career_service.is_session_completed(session_id)
        progress = (len(session.completed_stages) / 5) * 100
        
        return ApiResponse(
            success=True,
            message="세션 상태를 가져왔습니다.",
            data={
                "session_id": session_id,
                "current_stage": session.current_stage,
                "completed_stages": session.completed_stages,
                "progress_percentage": progress,
                "is_completed": is_completed,
                "student_name": session.student_info.name if session.student_info else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 상태 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 상태 조회에 실패했습니다.")

@app.get("/career/{session_id}/data")
async def get_session_data(session_id: str):
    """세션 전체 데이터 조회 (PDF 생성용)"""
    try:
        session = career_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        return ApiResponse(
            success=True,
            message="세션 데이터를 가져왔습니다.",
            data={
                "session_id": session_id,
                "student_info": session.student_info.model_dump() if session.student_info else None,
                "responses": session.responses,
                "final_recommendation": session.ai_career_recommendation,
                "dream_logic": session.dream_logic
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 데이터 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 데이터 조회에 실패했습니다.")

@app.delete("/career/{session_id}", response_model=ApiResponse)
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        success = career_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        return ApiResponse(
            success=True,
            message="세션이 삭제되었습니다."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 삭제 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 삭제에 실패했습니다.")

# =============================================================================
# OpenAI API 기반 진로 추천 엔드포인트들
# =============================================================================

@app.post("/career/{session_id}/recommend", response_model=ApiResponse)
async def get_career_recommendation(session_id: str, request: RecommendationRequest = RecommendationRequest()):
    """AI 기반 진로 추천 생성 (5단계)"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        # 4단계까지 완료 확인
        if not career_service.is_ready_for_step5(session_id):
            raise HTTPException(status_code=400, detail="4단계까지 완료해야 진로 추천을 받을 수 있습니다.")
        
        # AI 진로 추천 생성
        student_name = session.student_info.name if session.student_info else "친구"
        responses_dict = {stage: response.dict() for stage, response in session.responses.items()}
        recommendation = ai_service.generate_career_recommendation(student_name, responses_dict, request.regenerate or False)
        if not recommendation:
            raise HTTPException(status_code=500, detail="진로 추천 생성에 실패했습니다.")
        
        # 세션에 추천 결과 저장
        career_service.set_ai_recommendation(session_id, recommendation)
        
        return ApiResponse(
            success=True,
            message="AI 진로 추천이 생성되었습니다!",
            data={
                "career_recommendation": recommendation,
                "stage": CareerStage.STEP_5.value,
                "next_actions": ["accept", "modify"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진로 추천 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="진로 추천 생성에 실패했습니다.")

@app.post("/career/{session_id}/accept-recommendation", response_model=ApiResponse)
async def accept_career_recommendation(session_id: str):
    """진로 추천 수락 (5단계 완료)"""
    try:
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if session.current_stage != CareerStage.STEP_5:
            raise HTTPException(status_code=400, detail="5단계 상태가 아닙니다.")
        
        if not session.ai_career_recommendation:
            raise HTTPException(status_code=400, detail="진로 추천이 없습니다. 먼저 추천을 생성해주세요.")
        
        # 진로 추천 확정 (세션에 확정 상태 기록)
        session.career_confirmed = True
        session.final_career_goal = session.ai_career_recommendation
        career_service.sessions[session_id] = session  # 세션 업데이트
        
        student_name = session.student_info.name if session.student_info else "친구"
        
        return ApiResponse(
            success=True,
            message=f"{student_name}님의 진로 탐색이 완료되었습니다! 🎉",
            data={
                "confirmed_career": session.ai_career_recommendation,
                "completion_status": "completed",
                "next_step": "dream_logic_generation"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진로 추천 수락 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="진로 추천 수락에 실패했습니다.")

@app.post("/career/{session_id}/dream-logic", response_model=ApiResponse)
async def create_dream_logic(session_id: str):
    """드림로직 생성 (6단계)"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if not session.career_confirmed or not session.final_career_goal:
            raise HTTPException(status_code=400, detail="진로가 확정되지 않았습니다.")
        
        # 드림로직 생성
        student_name = session.student_info.name if session.student_info else "친구"
        responses_dict = {stage: response.dict() for stage, response in session.responses.items()}
        dream_logic = ai_service.generate_dream_logic(student_name, responses_dict, session.final_career_goal)
        
        if not dream_logic:
            raise HTTPException(status_code=500, detail="드림로직 생성에 실패했습니다.")
        
        # 세션에 드림로직 저장
        career_service.set_dream_logic(session_id, dream_logic)
        
        return ApiResponse(
            success=True,
            message="드림로직이 성공적으로 생성되었습니다!",
            data={
                "dream_logic": dream_logic,
                "student_name": student_name,
                "final_career": session.final_career_goal
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"드림로직 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="드림로직 생성에 실패했습니다.")

@app.get("/career/{session_id}/download-pdf")
async def download_dream_logic_pdf(session_id: str):
    """드림로직 PDF 다운로드"""
    try:
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if not session.dream_logic:
            raise HTTPException(status_code=400, detail="드림로직이 생성되지 않았습니다.")
        
        # 간단한 텍스트 파일로 응답 (실제로는 PDF 생성 라이브러리 사용)
        student_name = session.student_info.name if session.student_info else "학생"
        content = f"{student_name}의 드림로직\n\n{session.dream_logic}"
        
        from fastapi.responses import Response
        return Response(
            content=content.encode('utf-8'),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={student_name}_드림로직.txt"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF 다운로드 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="PDF 다운로드에 실패했습니다.")

@app.post("/career/{session_id}/modify-recommendation", response_model=ApiResponse)
async def modify_career_recommendation(session_id: str, modification_request: str):
    """진로 추천 수정 요청 (5-1 루프)"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if session.current_stage != CareerStage.STEP_5:
            raise HTTPException(status_code=400, detail="5단계 상태가 아닙니다.")
        
        if not session.ai_career_recommendation:
            raise HTTPException(status_code=400, detail="수정할 진로 추천이 없습니다.")
        
        student_name = session.student_info.name if session.student_info else "친구"
        
        # AI로 추천 수정
        modified_recommendation = ai_service.modify_career_recommendation(
            student_name=student_name,
            original_recommendation=session.ai_career_recommendation,
            modification_request=modification_request
        )
        
        if not modified_recommendation:
            raise HTTPException(status_code=500, detail="진로 추천 수정에 실패했습니다.")
        
        # 수정된 추천 저장
        career_service.set_ai_recommendation(session_id, modified_recommendation)
        
        return ApiResponse(
            success=True,
            message="진로 추천이 수정되었습니다!",
            data={
                "modified_career_recommendation": modified_recommendation,
                "stage": CareerStage.STEP_5.value,
                "next_actions": ["accept", "modify_again"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진로 추천 수정 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="진로 추천 수정에 실패했습니다.")

class CareerGoalRequest(BaseModel):
    """진로 목표 요청"""
    career_goal: str = Field(..., description="최종 진로 목표")

@app.post("/career/{session_id}/dream-logic", response_model=ApiResponse)
async def generate_dream_logic(session_id: str, request: CareerGoalRequest):
    """드림로직 생성 (상세한 실천 계획) - 6단계"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        # 진로가 확정되었는지 확인
        if not session.career_confirmed:
            raise HTTPException(status_code=400, detail="진로 추천을 먼저 확정해주세요.")
        
        if not session.ai_career_recommendation:
            raise HTTPException(status_code=400, detail="확정된 진로 추천이 없습니다.")
        
        student_name = session.student_info.name if session.student_info else "친구"
        
        # 드림로직 생성
        responses_dict = {stage: response.dict() for stage, response in session.responses.items()}
        dream_logic = ai_service.generate_dream_logic(
            student_name=student_name,
            responses=responses_dict,
            career_goal=request.career_goal
        )
        
        if not dream_logic:
            raise HTTPException(status_code=500, detail="드림로직 생성에 실패했습니다.")
        
        # 최종 진로 목표 저장
        session.final_career_goal = request.career_goal
        
        return ApiResponse(
            success=True,
            message=f"{student_name}님만의 드림로직이 완성되었습니다! 🌟",
            data={
                "student_name": student_name,
                "career_goal": request.career_goal,
                "dream_logic": dream_logic,
                "completion_message": "모든 진로 탐색 과정이 완료되었습니다!"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"드림로직 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="드림로직 생성에 실패했습니다.")

@app.get("/career/{session_id}/ai-encouragement")
async def get_ai_encouragement(session_id: str):
    """AI 기반 맞춤 응원 메시지"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        session = career_service.get_session(session_id)
        if not session or not session.student_info:
            raise HTTPException(status_code=404, detail="세션 정보를 찾을 수 없습니다.")
        
        if not session.current_stage:
            raise HTTPException(status_code=400, detail="진행 중인 단계가 없습니다.")
        
        # AI로 맞춤 응원 메시지 생성 (간단한 응원 메시지)
        stage_messages = {
            CareerStage.STEP_0: f"{session.student_info.name}님! 진로 탐색을 시작하는 용기가 정말 멋져요! 🌟",
            CareerStage.STEP_1: f"좋아하는 것들을 찾아가고 있어요! {session.student_info.name}님의 관심사가 빛나네요! ✨",
            CareerStage.STEP_2: f"잘하는 것들을 발견하고 있어요! {session.student_info.name}님의 재능이 보여요! 💪",
            CareerStage.STEP_3: f"가치관을 생각해보는 {session.student_info.name}님, 정말 깊이 있어요! 🤔",
            CareerStage.STEP_4: f"진로를 구체적으로 생각하는 모습이 인상적이에요! {session.student_info.name}님 화이팅! 🚀",
            CareerStage.STEP_5: f"마지막 단계까지 왔어요! {session.student_info.name}님의 꿈이 현실이 되고 있어요! 🎉"
        }
        
        encouragement = stage_messages.get(
            session.current_stage, 
            f"{session.student_info.name}님! 진로 탐색을 열심히 하고 있어요! 👏"
        )
        
        return ApiResponse(
            success=True,
            message="AI 응원 메시지가 생성되었습니다.",
            data={
                "student_name": session.student_info.name,
                "current_stage": session.current_stage,
                "ai_encouragement": encouragement
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 응원 메시지 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="AI 응원 메시지 생성에 실패했습니다.")

@app.get("/career/ai/status")
async def get_ai_service_status():
    """AI 서비스 상태 확인"""
    try:
        if ai_service:
            return ApiResponse(
                success=True,
                message="AI 서비스가 정상 작동 중입니다.",
                data={
                    "ai_service_available": True,
                    "model": "gpt-4o-mini"
                }
            )
        else:
            return ApiResponse(
                success=False,
                message="AI 서비스를 사용할 수 없습니다.",
                data={
                    "ai_service_available": False,
                    "reason": "OpenAI API 키가 설정되지 않았거나 서비스에 문제가 있습니다."
                }
            )
    except Exception as e:
        logger.error(f"AI 서비스 상태 확인 오류: {str(e)}")
        return ApiResponse(
            success=False,
            message="AI 서비스 상태 확인에 실패했습니다.",
            data={"error": str(e)}
        )

# PDF 다운로드 엔드포인트 (기존 - ReportLab 웹 스타일)
@app.post("/career/download-pdf")
async def download_career_pdf(request: PDFDownloadRequest):
    """진로 탐색 결과 PDF 다운로드 (ReportLab 웹 스타일)"""
    try:
        logger.info(f"PDF 다운로드 요청 (웹 스타일): {request.student_name}")
        
        # PDF 생성기 초기화
        pdf_generator = ElementaryCareerPDFGenerator()
        
        # PDF 생성
        pdf_content = pdf_generator.generate_career_report(
            student_name=request.student_name,
            responses=request.responses,
            final_recommendation=request.final_recommendation,
            dream_logic_result=request.dream_logic_result or "",
            encouragement_message=request.encouragement_message or ""
        )
        
        # 파일명 생성 (한글 이름 포함)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{request.student_name}_진로탐색결과_웹스타일_{timestamp}.pdf"
        
        # URL 인코딩된 파일명 생성
        from urllib.parse import quote
        encoded_filename = quote(filename.encode('utf-8'))
        
        # PDF 응답 반환
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Content-Type": "application/pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}"
        )

# 예외 처리
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 예외 처리"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """일반 예외 처리"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# 서버 실행 함수
import os

def start_server():
    """서버 시작"""
    # 환경변수에서 포트 가져오기, 기본값은 8000
    port = int(os.getenv('PORT', 8000))
    
    uvicorn.run(
        "elementary_school:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()