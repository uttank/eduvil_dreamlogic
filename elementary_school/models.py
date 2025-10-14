"""
초등학생 진로 탐색 시스템 데이터 모델 (0~5단계 포함)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

# 단계별 상수 정의
class CareerStage(str, Enum):
    """진로 탐색 단계"""
    STEP_0 = "step_0"  # 기본 정보 입력
    STEP_1 = "step_1"  # 흥미 탐색
    STEP_2 = "step_2"  # 장점 탐색
    STEP_3 = "step_3"  # 가치관 탐색
    STEP_4 = "step_4"  # 미래 탐색
    STEP_5 = "step_5"  # 진로 추천

# 단계별 질문과 선택지 상수
STAGE_QUESTIONS = {
    CareerStage.STEP_0: {
        "question": "안녕하세요! 진로 탐색을 시작해볼까요? 이름과 학년을 알려주세요!",
        "fields": ["name", "grade"]
    },
    CareerStage.STEP_1: {
        "question": "무엇을 할 때 시간이 빨리 가나요? (최대 2개까지 선택 가능)",
        "choices": [
            "만화 그리거나 캐릭터 만들 때",
            "레고·블록으로 건물·로봇 만들 때",
            "과학 실험·슬라임·키트 해볼 때",
            "공원에서 축구·농구·달리기 할 때",
            "동물 돌보고 산책 시킬 때",
            "요리·간식 레시피 따라 만들 때",
            "책·추리소설 읽고 기록할 때",
            "코딩 앱으로 간단한 게임 만들 때",
            "영상 찍고 편집해서 올릴 때",
            "퍼즐·보드게임으로 문제 풀 때",
            "기타"
        ]
    },
    CareerStage.STEP_2: {
        "question": "다른 사람에게 자랑 할만한 나만의 장점이 무엇인가요? (최대 2개까지 선택 가능)",
        "choices": [
            "설명을 쉽게 잘 해요(친구를 잘 이해시켜요)",
            "손이 야무져요(정밀하게 만들기 잘해요)",
            "끝까지 포기 안 해요(끈기 있어요)",
            "친구와 사이좋게 협력해요(팀워크)",
            "아이디어가 톡톡 떠올라요(창의성)",
            "앞에서 발표해도 떨지 않아요(발표력)",
            "숫자·계산이 빠르고 정확해요",
            "작은 차이를 잘 찾아요(관찰력)",
            "남의 마음을 잘 알아줘요(공감)",
            "계획 세우고 시간대로 실천해요(자기관리)",
            "기타"
        ]
    },
    CareerStage.STEP_3: {
        "question": "어떤 일을 할 때 행복함을 느끼나요? (1개만 선택)",
        "choices": [
            "누군가를 도와줄 때 행복해요",
            "새로운 것을 만들 때 행복해요",
            "어려운 문제를 해결할 때 행복해요",
            "몸을 움직이며 활동할 때 행복해요",
            "무대에서 표현할 때 행복해요",
            "자연·동물을 지킬 때 행복해요",
            "친구들과 함께 목표를 이룰 때 행복해요",
            "새 지식을 배우고 정리할 때 행복해요",
            "사람들을 웃게 할 때 행복해요",
            "목표를 세우고 저축·관리할 때 행복해요",
            "기타"
        ]
    },
    CareerStage.STEP_4: {
        "question": "미래 사회에서 가장 걱정되는 것은 무엇인가요? (1개만 선택)",
        "choices": [
            "기후변화와 쓰레기 문제",
            "어르신 돌봄과 1인 가구 늘어남",
            "AI·로봇과 사람이 함께 일하는 법",
            "사이버 괴롭힘·개인정보 안전",
            "교통안전·걷기 좋은 도시 만들기",
            "멸종위기 동물 보호",
            "우주쓰레기·우주 탐사 윤리",
            "건강·새로운 병 예방과 치료",
            "가짜뉴스 구별과 바른 정보 찾기",
            "지진·홍수 등 재난 대비와 구조",
            "기타"
        ]
    },
    CareerStage.STEP_5: {
        "question": "AI가 분석한 맞춤 진로를 확인해주세요!",
        "description": "1~4단계 응답을 바탕으로 최종꿈을 제시합니다.",
        "format": "[문제/가치]를 해결하는 [분야/역할] 전문가"
    }
}

# 응원 메시지 템플릿
ENCOURAGEMENT_MESSAGES = [
    "정말 잘하고 있어요!",
    "멋진 선택이에요!",
    "훌륭해요!",
    "대단한데요?",
    "너무 좋은 답변이에요!",
    "정말 깊이 생각했네요!",
    "완전 멋져요!",
    "정말 특별한 생각이에요!"
]

# Pydantic 모델들
class StudentInfo(BaseModel):
    """학생 기본 정보"""
    name: str = Field(..., description="학생 이름")
    grade: int = Field(..., ge=5, le=6, description="학년 (5학년, 6학년)")
    school: str = Field(default="초등학교", description="학교명")

class StepResponse(BaseModel):
    """각 단계별 응답"""
    choice_numbers: Optional[List[int]] = Field(None, description="선택지 번호들 (1-11, 1단계/2단계는 최대 2개, 3단계/4단계는 1개)")
    custom_answer: Optional[str] = Field(None, description="기타 선택시 직접 입력")
    
    def validate_response(self, stage: CareerStage) -> bool:
        """응답 유효성 검증"""
        if not self.choice_numbers or len(self.choice_numbers) == 0:
            return False
        
        # 선택지 번호 범위 검증
        for choice in self.choice_numbers:
            if choice < 1 or choice > 11:
                return False
        
        # 단계별 선택 개수 제한
        if stage in [CareerStage.STEP_1, CareerStage.STEP_2]:
            # 1, 2단계: 최대 2개 선택 가능
            if len(self.choice_numbers) > 2:
                return False
        elif stage in [CareerStage.STEP_3, CareerStage.STEP_4]:
            # 3, 4단계: 1개만 선택 가능
            if len(self.choice_numbers) != 1:
                return False
        
        # 기타 선택 검증
        if 11 in self.choice_numbers:
            # 기타 선택시 다른 선택지와 함께 선택할 수 없음
            if len(self.choice_numbers) > 1:
                return False
            # 기타 선택시 custom_answer 필수
            return self.custom_answer is not None and len(self.custom_answer.strip()) > 0
        
        return True

class CareerRecommendationResponse(BaseModel):
    """5단계 진로 추천 응답"""
    recommendation_accepted: bool = Field(..., description="추천 수락 여부")
    modification_request: Optional[str] = Field(None, description="수정 요청 내용 (거절시)")

class CareerExplorationSession(BaseModel):
    """진로 탐색 세션 전체 데이터"""
    session_id: str = Field(..., description="세션 ID")
    student_info: Optional[StudentInfo] = None
    current_stage: Optional[CareerStage] = CareerStage.STEP_0
    responses: Dict[CareerStage, StepResponse] = {}
    completed_stages: List[CareerStage] = []
    # 5단계 관련 필드
    ai_career_recommendation: Optional[str] = None
    career_confirmed: bool = False
    final_career_goal: Optional[str] = None
    # 6단계 관련 필드
    dream_logic: Optional[str] = None
    created_at: str
    updated_at: str

class StageQuestionResponse(BaseModel):
    """단계별 질문 응답"""
    stage: CareerStage
    question: str
    choices: Optional[List[str]] = None
    encouragement: str
    student_name: Optional[str] = None
    # 5단계 전용 필드
    ai_recommendation: Optional[str] = None

class NextStageRequest(BaseModel):
    """다음 단계 요청"""
    session_id: str
    response: Optional[StepResponse] = None
    student_info: Optional[StudentInfo] = None
    # 5단계 관련
    career_response: Optional[CareerRecommendationResponse] = None

class ApiResponse(BaseModel):
    """API 응답 기본 형태"""
    success: bool
    message: str
    data: Optional[dict] = None
