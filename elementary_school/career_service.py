"""
초등학생 진로 탐색 서비스 로직
"""

import uuid
import random
from datetime import datetime
from typing import Dict, Optional, Tuple
from .models import (
    CareerStage, CareerExplorationSession, StudentInfo, StepResponse,
    StageQuestionResponse, STAGE_QUESTIONS, ENCOURAGEMENT_MESSAGES,
    CareerRecommendationResponse
)

class CareerExplorationService:
    """진로 탐색 서비스"""
    
    def __init__(self):
        # 메모리 내 세션 저장소 (실제 환경에서는 Redis나 DB 사용)
        self.sessions: Dict[str, CareerExplorationSession] = {}
    
    def create_session(self) -> str:
        """새로운 탐색 세션 생성"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        session = CareerExplorationSession(
            session_id=session_id,
            current_stage=CareerStage.STEP_0,
            responses={},
            completed_stages=[],
            created_at=now,
            updated_at=now
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[CareerExplorationSession]:
        """세션 조회"""
        return self.sessions.get(session_id)
    
    def get_current_question(self, session_id: str) -> Optional[StageQuestionResponse]:
        """현재 단계의 질문 조회"""
        session = self.get_session(session_id)
        if not session or not session.current_stage:
            return None
        
        current_stage = session.current_stage
        stage_data = STAGE_QUESTIONS.get(current_stage)
        
        if not stage_data:
            return None
        
        # 응원 메시지 생성
        encouragement = self._generate_encouragement(session)
        
        # 0단계(기본정보)는 선택지가 없음
        if current_stage == CareerStage.STEP_0:
            return StageQuestionResponse(
                stage=current_stage,
                question=stage_data["question"],
                choices=None,
                encouragement=encouragement,
                student_name=session.student_info.name if session.student_info else None
            )
        
        # 5단계(진로 추천)는 AI 추천과 함께 반환
        if current_stage == CareerStage.STEP_5:
            return StageQuestionResponse(
                stage=current_stage,
                question=stage_data["question"],
                choices=None,
                encouragement=encouragement,
                student_name=session.student_info.name if session.student_info else None,
                ai_recommendation=session.ai_career_recommendation
            )
        
        # 1-4단계는 번호가 매겨진 선택지 반환
        numbered_choices = [
            f"{i+1}. {choice}" 
            for i, choice in enumerate(stage_data["choices"])
        ]
        
        return StageQuestionResponse(
            stage=current_stage,
            question=stage_data["question"],
            choices=numbered_choices,
            encouragement=encouragement,
            student_name=session.student_info.name if session.student_info else None
        )
    
    def submit_response(self, session_id: str, student_info: Optional[StudentInfo] = None, 
                       response: Optional[StepResponse] = None, 
                       career_response: Optional[CareerRecommendationResponse] = None) -> Tuple[bool, str, Optional[CareerStage]]:
        """응답 제출 및 다음 단계로 진행"""
        session = self.get_session(session_id)
        if not session:
            return False, "세션을 찾을 수 없습니다.", None
        
        current_stage = session.current_stage
        
        # 0단계: 학생 기본 정보 저장
        if current_stage == CareerStage.STEP_0:
            if not student_info:
                return False, "학생 정보를 입력해주세요.", None
            
            session.student_info = student_info
            session.completed_stages.append(current_stage)
            session.current_stage = CareerStage.STEP_1
            
        # 5단계: 진로 추천 확정/수정 처리
        elif current_stage == CareerStage.STEP_5:
            if not career_response:
                return False, "진로 추천에 대한 응답을 해주세요.", None
            
            if career_response.recommendation_accepted:
                # 추천 수락 - 최종 꿈 확정
                session.career_confirmed = True
                session.final_career_goal = session.ai_career_recommendation
                session.completed_stages.append(current_stage)
                session.current_stage = None  # 모든 단계 완료
                return True, "진로가 확정되었습니다! 드림로직을 생성할 준비가 되었어요.", None
            else:
                # 수정 요청
                if not career_response.modification_request:
                    return False, "수정하고 싶은 부분을 알려주세요.", None
                return True, f"수정 요청: {career_response.modification_request}", CareerStage.STEP_5
            
        # 1-4단계: 선택지 응답 저장
        else:
            if not response:
                return False, "응답을 입력해주세요.", None
            if not current_stage or not response.validate_response(current_stage):
                return False, "올바른 선택을 해주세요.", None
            
            session.responses[current_stage] = response
            session.completed_stages.append(current_stage)
            
            # 다음 단계 결정
            next_stage = self._get_next_stage(current_stage)
            session.current_stage = next_stage
        
        # 세션 업데이트
        session.updated_at = datetime.now().isoformat()
        self.sessions[session_id] = session
        
        return True, "응답이 저장되었습니다.", session.current_stage
    
    def _get_next_stage(self, current_stage: CareerStage) -> Optional[CareerStage]:
        """다음 단계 결정"""
        stage_order = [
            CareerStage.STEP_0,
            CareerStage.STEP_1, 
            CareerStage.STEP_2,
            CareerStage.STEP_3,
            CareerStage.STEP_4,
            CareerStage.STEP_5
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _generate_encouragement(self, session: CareerExplorationSession) -> str:
        """응원 메시지 생성"""
        base_message = random.choice(ENCOURAGEMENT_MESSAGES)
        
        if session.student_info and session.student_info.name:
            name = session.student_info.name
            
            # 단계별 맞춤 응원 메시지
            if session.current_stage == CareerStage.STEP_0:
                return f"안녕하세요! 진로 탐색을 함께 시작해볼까요? 😊"
            elif session.current_stage == CareerStage.STEP_1:
                return f"{name}님! 무엇을 좋아하는지 알아보는 시간이에요! {base_message} 🌟"
            elif session.current_stage == CareerStage.STEP_2:
                return f"{name}님의 멋진 장점을 찾아봐요! {base_message} ✨"
            elif session.current_stage == CareerStage.STEP_3:
                return f"{name}님이 행복을 느끼는 순간을 알려주세요! {base_message} 💝"
            elif session.current_stage == CareerStage.STEP_4:
                return f"{name}님이 생각하는 미래에 대해 들려주세요! {base_message} 🚀"
            elif session.current_stage == CareerStage.STEP_5:
                return f"{name}님! AI가 분석한 맞춤 진로예요! 마음에 드시나요? ✨🎯"
        
        return base_message
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """세션 요약 정보 조회"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        summary = {
            "session_id": session.session_id,
            "student_info": session.student_info.dict() if session.student_info else None,
            "current_stage": session.current_stage,
            "completed_stages": session.completed_stages,
            "total_stages": 5,
            "progress_percentage": (len(session.completed_stages) / 5) * 100,
            "responses_summary": {}
        }
        
        # 응답 요약
        for stage, response in session.responses.items():
            stage_question = STAGE_QUESTIONS.get(stage, {}).get("question", "")
            
            if response.choice_numbers and 11 in response.choice_numbers and response.custom_answer:
                answer = f"기타: {response.custom_answer}"
            elif response.choice_numbers and stage in STAGE_QUESTIONS:
                choices = STAGE_QUESTIONS[stage].get("choices", [])
                selected_answers = []
                for choice_num in response.choice_numbers:
                    if choice_num <= len(choices):
                        selected_answers.append(choices[choice_num - 1])
                    else:
                        selected_answers.append("알 수 없는 선택")
                answer = ", ".join(selected_answers)
            else:
                answer = "응답 없음"
            
            summary["responses_summary"][stage] = {
                "question": stage_question,
                "answer": answer,
                "choice_numbers": response.choice_numbers
            }
        
        return summary
    
    def is_session_completed(self, session_id: str) -> bool:
        """세션 완료 여부 확인"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        return len(session.completed_stages) == 5  # 0-4단계 모두 완료
    
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def set_ai_recommendation(self, session_id: str, recommendation: str) -> bool:
        """5단계를 위한 AI 추천 설정"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.ai_career_recommendation = recommendation
        session.current_stage = CareerStage.STEP_5
        session.updated_at = datetime.now().isoformat()
        self.sessions[session_id] = session
        return True
    
    def is_ready_for_step5(self, session_id: str) -> bool:
        """5단계 진행 가능 여부 확인 (1-4단계 완료)"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        required_stages = [CareerStage.STEP_0, CareerStage.STEP_1, CareerStage.STEP_2, CareerStage.STEP_3, CareerStage.STEP_4]
        return all(stage in session.completed_stages for stage in required_stages)
    
    def is_career_confirmed(self, session_id: str) -> bool:
        """진로 확정 여부 확인"""
        session = self.get_session(session_id)
        if not session:
            return False
        return session.career_confirmed
    
    def set_dream_logic(self, session_id: str, dream_logic: str) -> bool:
        """드림로직 저장"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.dream_logic = dream_logic
        session.updated_at = datetime.now().isoformat()
        self.sessions[session_id] = session
        return True

# 전역 서비스 인스턴스
career_service = CareerExplorationService()