"""
FastAPI 백엔드 - 중학교 진로탐색 서비스
중학생 개개인의 흥미·강점·가치·미래 관심을 연결하여
"현실적인 진로 목표 + 실행 가능한 실천 계획"을 도출
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
import uuid
import os
from pathlib import Path

# 중학교 진로 탐색 관련 imports
from .models import (
    StudentInfo, StepResponse, NextStageRequest, ApiResponse,
    CareerStage, StageQuestionResponse, CareerRecommendationResponse
)
from .career_service import career_service
from .openai_service import ai_service
from .pdf_generator_elementary_style import pdf_generator

# 추가 요청 모델
class RecommendationRequest(BaseModel):
    regenerate: Optional[bool] = False

class PDFDownloadRequest(BaseModel):
    student_name: str
    responses: Dict[CareerStage, Dict]
    final_recommendation: str
    dream_logic_result: Optional[str] = ""
    encouragement_message: Optional[str] = ""

class DreamConfirmationRequest(BaseModel):
    """5단계 꿈 확정/수정 요청"""
    action: str = Field(..., description="확정 또는 수정 (confirm/modify)")
    dream_statement: Optional[str] = Field(None, description="최종 꿈 문장")
    modification_request: Optional[str] = Field(None, description="수정 요청 내용")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Middle School Career Exploration API",
    description="중학교 진로탐색 서비스를 위한 백엔드 API",
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

# 정적 파일 서빙
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# 보안 설정
security = HTTPBearer()

# 임시 데이터베이스
fake_students_db = []
student_id_counter = 1

# 의존성 함수들
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """인증 토큰 검증 (임시 구현)"""
    if credentials.credentials != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user": "authenticated"}

# 기본 라우터들

@app.get("/")
async def root():
    """메인 페이지"""
    return FileResponse(static_dir / "index.html")

@app.get("/api", response_model=dict)
async def api_root():
    """API 루트 엔드포인트"""
    return {
        "message": "Middle School Career Exploration API is running!",
        "version": "1.0.0", 
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now()}

# =============================================================================
# 중학교 진로 탐색 API 엔드포인트들
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
                "message": "안녕하세요! 중학생 진로 탐색을 시작해볼까요? 🌟"
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
        
        # AI 진로 추천 생성 (중학생용)
        student_name = session.student_info.name if session.student_info else "친구"
        responses_dict = {stage: response.dict() for stage, response in session.responses.items()}
        recommendation = ai_service.generate_middle_school_recommendation(student_name, responses_dict, request.regenerate or False)
        
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
                "next_actions": ["confirm", "modify"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"진로 추천 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="진로 추천 생성에 실패했습니다.")

@app.post("/career/{session_id}/dream-confirm", response_model=ApiResponse)
async def confirm_or_modify_dream(session_id: str, request: DreamConfirmationRequest):
    """5단계 꿈 확정 또는 수정 처리"""
    try:
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if session.current_stage != CareerStage.STEP_5:
            raise HTTPException(status_code=400, detail="5단계 상태가 아닙니다.")
        
        if not session.ai_career_recommendation:
            raise HTTPException(status_code=400, detail="진로 추천이 없습니다. 먼저 추천을 생성해주세요.")
        
        student_name = session.student_info.name if session.student_info else "친구"
        
        if request.action == "confirm":
            # 꿈 확정
            dream_statement = request.dream_statement or session.ai_career_recommendation
            session.career_confirmed = True
            session.final_career_goal = dream_statement
            career_service.sessions[session_id] = session
            
            return ApiResponse(
                success=True,
                message=f"{student_name}님의 꿈이 확정되었습니다! 🎉",
                data={
                    "confirmed_dream": dream_statement,
                    "completion_status": "confirmed",
                    "next_step": "dream_logic_generation"
                }
            )
            
        elif request.action == "modify":
            # 꿈 수정 요청 - 바로 새로운 추천 생성
            if not ai_service:
                raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
            
            # 기존 답변으로 새로운 추천 생성 (regenerate=True)
            responses_dict = {stage: response.dict() for stage, response in session.responses.items()}
            new_recommendation = ai_service.generate_middle_school_recommendation(
                student_name, 
                responses_dict, 
                regenerate=True  # 다른 결과 생성을 위해 True
            )
            
            if not new_recommendation:
                raise HTTPException(status_code=500, detail="새로운 추천 생성에 실패했습니다.")
            
            # 새로운 추천 저장
            career_service.set_ai_recommendation(session_id, new_recommendation)
            
            return ApiResponse(
                success=True,
                message="새로운 진로 추천이 생성되었습니다!",
                data={
                    "career_recommendation": new_recommendation,
                    "stage": CareerStage.STEP_5.value,
                    "next_actions": ["confirm", "modify"]
                }
            )
        else:
            raise HTTPException(status_code=400, detail="올바르지 않은 액션입니다. confirm 또는 modify를 사용하세요.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"꿈 확정/수정 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="꿈 확정/수정에 실패했습니다.")

@app.post("/career/{session_id}/regenerate-with-changes", response_model=ApiResponse)
async def regenerate_recommendation_with_changes(session_id: str, request: dict):
    """특정 단계의 답변을 수정한 후 새로운 진로 추천 생성"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        # 수정할 단계와 새로운 답변 가져오기
        step_to_modify = request.get("step_to_modify")  # "step1", "step2", "step3", "step4"
        new_answer = request.get("new_answer")
        
        if not step_to_modify or not new_answer:
            raise HTTPException(status_code=400, detail="수정할 단계와 새로운 답변을 제공해주세요.")
        
        # 단계 매핑
        stage_mapping = {
            "step1": CareerStage.STEP_1,
            "step2": CareerStage.STEP_2,
            "step3": CareerStage.STEP_3,
            "step4": CareerStage.STEP_4
        }
        
        stage_to_modify = stage_mapping.get(step_to_modify)
        if not stage_to_modify:
            raise HTTPException(status_code=400, detail="유효하지 않은 단계입니다.")
        
        # 기존 응답을 복사하고 수정할 단계의 답변을 업데이트
        updated_responses = {}
        for stage, response in session.responses.items():
            if stage == stage_to_modify:
                # 수정된 답변으로 새로운 응답 객체 생성
                updated_response = StepResponse(
                    choice_numbers=new_answer.get('choice_numbers', []),
                    custom_answer=new_answer.get('custom_answer', '')
                )
                updated_responses[stage] = updated_response
            else:
                updated_responses[stage] = response
        
        # AI로 새로운 추천 생성
        student_name = session.student_info.name if session.student_info else "친구"
        responses_dict = {stage: response.dict() for stage, response in updated_responses.items()}
        
        new_recommendation = ai_service.generate_middle_school_recommendation(
            student_name, 
            responses_dict, 
            regenerate=True
        )
        
        if not new_recommendation:
            raise HTTPException(status_code=500, detail="새로운 진로 추천 생성에 실패했습니다.")
        
        # 세션에 새로운 추천 저장 (원본 응답은 유지, 추천만 업데이트)
        career_service.set_ai_recommendation(session_id, new_recommendation)
        
        return ApiResponse(
            success=True,
            message="수정된 답변을 바탕으로 새로운 진로 추천이 생성되었습니다!",
            data={
                "career_recommendation": new_recommendation,
                "modified_step": step_to_modify,
                "stage": CareerStage.STEP_5.value,
                "next_actions": ["confirm", "modify"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"수정된 추천 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="수정된 추천 생성에 실패했습니다.")

@app.post("/career/{session_id}/dream-logic", response_model=ApiResponse)
async def create_dream_logic(session_id: str):
    """드림로직 생성 (6단계) - 중학생용 실천 계획"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
        
        # 세션 상태 확인
        session = career_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if not session.career_confirmed or not session.final_career_goal:
            raise HTTPException(status_code=400, detail="꿈이 확정되지 않았습니다.")
        
        # 중학생용 드림로직 생성
        student_name = session.student_info.name if session.student_info else "친구"
        responses_dict = {stage: response.dict() for stage, response in session.responses.items()}
        
        dream_logic = ai_service.generate_middle_school_dream_logic(
            student_name=student_name,
            responses=responses_dict,
            final_dream=session.final_career_goal
        )
        
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
                "final_dream": session.final_career_goal
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"드림로직 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="드림로직 생성에 실패했습니다.")

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
        progress = (len(session.completed_stages) / 6) * 100  # 중학교는 6단계
        
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
                "final_dream": session.final_career_goal,
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

# PDF 다운로드 엔드포인트 (elementary_school 방식)
@app.post("/career/download-pdf")
async def download_career_pdf(request: PDFDownloadRequest):
    """진로 탐색 결과 PDF 다운로드 (elementary_school 방식)"""
    try:
        logger.info(f"PDF 다운로드 요청: {request.student_name}")
        
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
        filename = f"{request.student_name}_중학교진로탐색결과_{timestamp}.pdf"
        
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
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
def start_server():
    """서버 시작"""
    port = int(os.getenv('PORT', 8000))
    
    uvicorn.run(
        "middle_school:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()
