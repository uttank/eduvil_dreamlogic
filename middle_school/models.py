"""
중학생 진로 탐색 시스템 데이터 모델 (0~6단계 포함)
흥미·강점·가치·미래 관심을 연결하여 "현실적인 진로 목표 + 실행 가능한 실천 계획"을 도출
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

# 단계별 상수 정의
class CareerStage(str, Enum):
    """진로 탐색 단계"""
    STEP_0 = "step_0"  # 기본 정보 입력 (이름, 학년)
    STEP_1 = "step_1"  # 흥미 탐색
    STEP_2 = "step_2"  # 장점 탐색
    STEP_3 = "step_3"  # 가치관 탐색
    STEP_4 = "step_4"  # 미래 탐색
    STEP_5 = "step_5"  # 최종꿈 제안 및 확정
    STEP_6 = "step_6"  # 드림로직 생성

# 중학교 단계별 질문과 선택지 상수
STAGE_QUESTIONS = {
    CareerStage.STEP_0: {
        "question": "안녕하세요! 진로 탐색을 시작해볼까요? 이름과 학년을 알려주세요!",
        "fields": ["name", "grade"]
    },
    CareerStage.STEP_1: {
        "question": "무엇을 할 때 시간이 빠르게 지나가나요? 아래에서 번호 하나 골라 주세요. (2개까지 가능해요)",
        "choices": [
            "1. 스토리 기획·세계관 만들기",
            "2. 캐릭터/콘셉트 아트(드로잉·컬러)",
            "3. 2D 애니메이션(키프레임·타이밍)",
            "4. 3D/모션그래픽(카메라 워크·이펙트)",
            "5. 코딩·게임/앱 프로토타이핑",
            "6. 로봇·메이킹(하드웨어/센서)",
            "7. 과학 실험·탐구(자료 수집·그래프)",
            "8. 스포츠/피지컬 트레이닝",
            "9. 동물·자연 관찰·보호 활동",
            "10. 요리·푸드 디자인/영양",
            "11. 영상 촬영·편집·사운드",
            "12. 탐구·리서치·인터뷰(트렌드 조사)",
            "13. 기타(직접 입력)"
        ]
    },
    CareerStage.STEP_2: {
        "question": "팀이나 프로젝트에서 특히 잘하는 부분은 무엇인가요? 번호 하나 골라 주세요.",
        "choices": [
            "1. 문제정의(핵심을 빠르게 짚음)",
            "2. 창의발상(아이디어가 잘 떠오름)",
            "3. 리서치(근거·사례를 정확히 찾음)",
            "4. 스토리텔링/설득(쉽게 설명·이해시킴)",
            "5. 시각화/드로잉(그림·도식으로 표현)",
            "6. 기술실행(툴 숙련·구현력)",
            "7. 협업/리더십(소통·조율·분담)",
            "8. 발표/커뮤니케이션(무대/카메라 앞에서도 침착)",
            "9. 분석/개선(데이터 비교·피드백 반영)",
            "10. 자기관리(마감·계획·시간관리)",
            "11. 기타(직접 입력)"
        ]
    },
    CareerStage.STEP_3: {
        "question": "어떤 순간에 가장 보람이나 행복을 느끼나요? 번호 하나 골라 주세요.",
        "choices": [
            "1. 누군가에게 도움/서비스 제공",
            "2. 새로운 것을 만들어 세상에 내놓기",
            "3. 어려운 문제를 해결하며 성장하기",
            "4. 무대·스크린에서 표현·공유하기",
            "5. 자연/동물을 지키고 회복 돕기",
            "6. 팀 프로젝트로 공동 목표 달성하기",
            "7. 지식을 배우고 체계화·정리하기",
            "8. 사람들을 웃게 하거나 감동 주기",
            "9. 목표를 세우고 꾸준히 실천/관리하기",
            "10. 기타(직접 입력)"
        ]
    },
    CareerStage.STEP_4: {
        "question": "미래 사회에서 특히 걱정되는 주제를 골라 주세요.",
        "choices": [
            "1. 기후변화·자원순환",
            "2. 고령화·돌봄·1인 가구",
            "3. AI·로봇과 사람의 협업·일자리",
            "4. 사이버 괴롭힘·개인정보·디지털 웰빙",
            "5. 교통안전·보행 친화 도시",
            "6. 생물다양성·멸종위기 보호",
            "7. 우주 쓰레기·탐사 윤리",
            "8. 공중보건·신종 질병",
            "9. 가짜뉴스·정보 리터러시",
            "10. 재난 대비·구조 시스템",
            "11. 기타(직접 입력)"
        ]
    },
    CareerStage.STEP_5: {
        "question": "이전 선택을 바탕으로 '최종꿈 한 문장'을 제안해 주세요.",
        "description": "형식 A: [문제/가치]를 해결하는 [분야/역할] 전문가\n형식 B: [대상]이 [가치]를 느끼도록 [콘텐츠/도구]를 만드는 [직무]",
        "format": "학생이 '수정'이라 답하면, 조금 더 내용을 확장하여 다시 제시"
    },
    CareerStage.STEP_6: {
        "question": "결과 문서 자동 생성 (현실 밀착형)",
        "description": "학생의 선택을 반영해 중간목표와 실천활동을 구체적으로 제시",
        "format": "학교 과목·일상 루틴·참여 활동을 구체적으로 포함"
    }
}

# 응원 메시지 템플릿 (중학생용)
ENCOURAGEMENT_MESSAGES = [
    "좋아요! 정말 흥미로운 출발이에요 👍",
    "멋진 선택이에요!",
    "훌륭해요!",
    "대단한데요?",
    "너무 좋은 답변이에요!",
    "정말 깊이 생각했네요!",
    "완전 멋져요!",
    "정말 특별한 생각이에요!",
    "정말 잘하고 있어요!",
    "좋은 방향으로 가고 있어요!"
]

# Pydantic 모델들
class StudentInfo(BaseModel):
    """학생 기본 정보"""
    name: str = Field(..., description="학생 이름")
    grade: int = Field(..., ge=1, le=3, description="학년 (1학년, 2학년, 3학년)")
    school: str = Field(default="중학교", description="학교명")

class StepResponse(BaseModel):
    """각 단계별 응답"""
    choice_numbers: Optional[List[int]] = Field(None, description="선택지 번호들")
    custom_answer: Optional[str] = Field(None, description="기타 선택시 직접 입력")
    
    def validate_response(self, stage: CareerStage) -> bool:
        """응답 유효성 검증"""
        if not self.choice_numbers or len(self.choice_numbers) == 0:
            return False
        
        # 선택지 번호 범위 검증
        for choice in self.choice_numbers:
            if choice < 1:
                return False
            # 단계별 최대 선택지 개수 확인
            if stage == CareerStage.STEP_1 and choice > 13:  # 13개 선택지 (기타 포함)
                return False
            elif stage == CareerStage.STEP_2 and choice > 11:  # 11개 선택지 (기타 포함)
                return False
            elif stage == CareerStage.STEP_3 and choice > 10:  # 10개 선택지 (기타 포함)
                return False
            elif stage == CareerStage.STEP_4 and choice > 11:  # 11개 선택지 (기타 포함)
                return False
        
        # 단계별 선택 개수 제한
        if stage == CareerStage.STEP_1:
            # 1단계: 최대 2개 선택 가능
            if len(self.choice_numbers) > 2:
                return False
        elif stage in [CareerStage.STEP_2, CareerStage.STEP_3, CareerStage.STEP_4]:
            # 2,3,4단계: 1개만 선택 가능
            if len(self.choice_numbers) != 1:
                return False
        
        # 기타 선택 검증
        other_choice_nums = {
            CareerStage.STEP_1: 13,
            CareerStage.STEP_2: 11,
            CareerStage.STEP_3: 10,
            CareerStage.STEP_4: 11
        }
        
        if stage in other_choice_nums and other_choice_nums[stage] in self.choice_numbers:
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

class DreamLogicTemplate(BaseModel):
    """드림로직 템플릿 (6단계 결과)"""
    student_name: str
    final_dream: str
    middle_goals: List[dict]
    encouragement_memo: str

# 중학생용 드림로직 출력 템플릿
DREAM_LOGIC_TEMPLATE = """
[{student_name}의 드림 로직]
최종꿈: {final_dream}

{middle_goals}

💬 응원 메모
"{student_name}의 {strength}은 진짜 강점이에요.
일상 속 작은 실천이 쌓이면 {final_dream}에 한 걸음 다가설 거예요!"
"""

MIDDLE_GOAL_TEMPLATE = """
[중간목표 {goal_num}] {goal_title} (왜 필요한가)
설명: {goal_description}

실천활동(학교): {school_activities}

실천활동(일상): {daily_activities}

추천 활동: {recommended_activities}
"""