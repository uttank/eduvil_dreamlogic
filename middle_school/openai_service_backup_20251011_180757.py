"""
중학생 진로 탐색을 위한 OpenAI 서비스
중학생 개개인의 흥미·강점·가치·미래 관심을 연결하여
"현실적인 진로 목표 + 실행 가능한 실천 계획"을 도출

[백업 파일] - 2025년 10월 11일 18:07:57 생성
원본 파일: openai_service.py
"""

import os
import logging
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# 로깅 설정
logger = logging.getLogger(__name__)

class MiddleSchoolAIService:
    """중학생 진로 탐색을 위한 AI 서비스"""
    
    # OpenAI 모델 설정
    DEFAULT_MODEL = "gpt-4o-mini"
    
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = self.DEFAULT_MODEL  # 인스턴스에서 모델 변경 가능
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI 클라이언트가 성공적으로 초기화되었습니다.")
            except Exception as e:
                logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
                self.client = None
        else:
            logger.warning("OPENAI_API_KEY가 설정되지 않았습니다.")
    
    def is_available(self) -> bool:
        """AI 서비스 사용 가능 여부 확인"""
        return self.client is not None
    
    def set_model(self, model_name: str) -> None:
        """사용할 OpenAI 모델 설정"""
        self.model = model_name
        logger.info(f"OpenAI 모델이 {model_name}으로 변경되었습니다.")
    
    def get_model(self) -> str:
        """현재 사용 중인 모델 반환"""
        return self.model
    
    def generate_middle_school_recommendation(self, student_name: str, responses: Dict, regenerate: bool = False) -> Optional[str]:
        """중학생용 진로 추천 생성 (5단계)"""
        if not self.is_available() or not self.client:
            logger.warning("AI 서비스를 사용할 수 없습니다.")
            return None
        
        try:
            # 중학생용 프롬프트 구성
            prompt = self._build_middle_school_recommendation_prompt(student_name, responses, regenerate)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """당신은 중학생 진로상담 전문가입니다. 
중학생의 흥미·강점·가치·미래 관심을 분석하여 현실적이고 구체적인 진로를 제안해야 합니다.

응답 형식:
형식 A: [문제/가치]를 해결하는 [분야/역할] 전문가
형식 B: [대상]이 [가치]를 느끼도록 [콘텐츠/도구]를 만드는 [직무]

응답은 한 문장으로 간결하게 작성하되, 중학생이 이해하기 쉽고 구체적으로 표현해주세요.
문장은 가벼운 존댓말로, 짧고 명확하게 정리해주세요."""
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            recommendation = response.choices[0].message.content
            if recommendation:
                recommendation = recommendation.strip()
            logger.info(f"중학생 진로 추천 생성 완료: {student_name}")
            return recommendation
            
        except Exception as e:
            logger.error(f"중학생 진로 추천 생성 오류: {str(e)}")
            return None
    
    def modify_middle_school_dream(self, student_name: str, original_dream: str, modification_request: str) -> Optional[str]:
        """중학생용 꿈 수정 (5단계 수정 요청)"""
        if not self.is_available() or not self.client:
            logger.warning("AI 서비스를 사용할 수 없습니다.")
            return None
        
        try:
            prompt = f"""
{student_name}님의 원래 꿈: {original_dream}

{student_name}님의 수정 요청: {modification_request}

위 요청을 반영하여 꿈을 수정해주세요. 조금 더 내용을 확장하여 다시 제시해주세요.
응답은 한 문장으로 간결하게 작성하되, 중학생이 이해하기 쉽고 구체적으로 표현해주세요.

형식 A: [문제/가치]를 해결하는 [분야/역할] 전문가
형식 B: [대상]이 [가치]를 느끼도록 [콘텐츠/도구]를 만드는 [직무]
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """당신은 중학생 진로상담 전문가입니다. 
학생의 수정 요청을 반영하여 더 나은 진로를 제안해주세요.
문장은 가벼운 존댓말로, 짧고 명확하게 정리해주세요."""
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            modified_dream = response.choices[0].message.content
            if modified_dream:
                modified_dream = modified_dream.strip()
            logger.info(f"중학생 꿈 수정 완료: {student_name}")
            return modified_dream
            
        except Exception as e:
            logger.error(f"중학생 꿈 수정 오류: {str(e)}")
            return None
    
    def generate_middle_school_dream_logic(self, student_name: str, responses: Dict, final_dream: str) -> Optional[str]:
        """중학생용 드림로직 생성 (6단계) - 학교생활·일상 실천 중심"""
        if not self.is_available() or not self.client:
            logger.warning("AI 서비스를 사용할 수 없습니다.")
            return None
        
        try:
            # 중학생용 드림로직 프롬프트 구성
            prompt = self._build_middle_school_dream_logic_prompt(student_name, responses, final_dream)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """당신은 중학생 진로상담 전문가입니다. 
중학생의 꿈을 이루기 위한 구체적이고 실천 가능한 계획을 작성해야 합니다.

다음 형식을 정확히 따라주세요:

[{student_name}의 드림 로직]
최종꿈: {final_dream}

[중간목표 1] 핵심 역량 A (왜 필요한가)
설명: [문제 해결과의 연결]

실천활동(학교): [예: 체육 시간 달리기 기록 향상 / 과학 시간 응급처치 단원 복습 등]

실천활동(일상): [예: 스트레칭, 뉴스 시청 후 대화 나누기 등]

추천 활동: [예: 안전지킴이, 동아리 활동 등]

[중간목표 2] 핵심 역량 B (왜 필요한가)
설명: [작품 퀄리티 또는 협업력과의 연결]

실천활동(학교): [교과 활동, 조별 과제, 역할 제안 등]

실천활동(일상): [도움 주기, 리더십 사례 축적 등]

추천 활동: [또래상담자, 리더십 캠프 등]

[중간목표 3] 핵심 역량 C (왜 필요한가)
설명: [윤리, 시민의식, 리터러시 등과의 연결]

실천활동(학교): [관련 교과 단원 공부, 기사 요약]

실천활동(일상): [대피 경로 확인, 뉴스 분석]

추천 활동: [RCY, 안전 체험관 등]

💬 응원 메모
"{student_name}의 [장점]은 진짜 강점이에요.
일상 속 작은 실천이 쌓이면 [최종꿈]에 한 걸음 다가설 거예요!"

각 중간목표에는 학교 과목·일상 루틴·참여 활동을 구체적으로 제시해야 합니다.
문장은 가벼운 존댓말로, 답변은 짧고 명확하게 정리해주세요."""
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            dream_logic = response.choices[0].message.content
            if dream_logic:
                dream_logic = dream_logic.strip()
            logger.info(f"중학생 드림로직 생성 완료: {student_name}")
            return dream_logic
            
        except Exception as e:
            logger.error(f"중학생 드림로직 생성 오류: {str(e)}")
            return None
    
    def _build_middle_school_recommendation_prompt(self, student_name: str, responses: Dict, regenerate: bool) -> str:
        """중학생용 진로 추천 프롬프트 구성"""
        prompt = f"""
{student_name}님의 진로 탐색 응답을 분석하여 최종꿈 한 문장을 제안해주세요.

"""
        
        # 1단계 - 흥미 탐색 분석
        if 'step_1' in responses:
            step1 = responses['step_1']
            if step1.get('custom_answer'):
                prompt += f"1단계 흥미 탐색: 기타 - {step1['custom_answer']}\n"
            elif step1.get('choice_numbers'):
                choices = [
                    "스토리 기획·세계관 만들기",
                    "캐릭터/콘셉트 아트(드로잉·컬러)",
                    "2D 애니메이션(키프레임·타이밍)",
                    "3D/모션그래픽(카메라 워크·이펙트)",
                    "코딩·게임/앱 프로토타이핑",
                    "로봇·메이킹(하드웨어/센서)",
                    "과학 실험·탐구(자료 수집·그래프)",
                    "스포츠/피지컬 트레이닝",
                    "동물·자연 관찰·보호 활동",
                    "요리·푸드 디자인/영양",
                    "영상 촬영·편집·사운드",
                    "탐구·리서치·인터뷰(트렌드 조사)",
                    "기타(직접 입력)"
                ]
                selected_interests = []
                for choice_num in step1['choice_numbers']:
                    if 1 <= choice_num <= len(choices):
                        selected_interests.append(choices[choice_num - 1])
                
                prompt += f"1단계 흥미 탐색: {', '.join(selected_interests)}\n"
        
        # 2단계 - 장점 탐색 분석
        if 'step_2' in responses:
            step2 = responses['step_2']
            if step2.get('custom_answer'):
                prompt += f"2단계 장점 탐색: 기타 - {step2['custom_answer']}\n"
            elif step2.get('choice_numbers'):
                choices = [
                    "문제정의(핵심을 빠르게 짚음)",
                    "창의발상(아이디어가 잘 떠오름)",
                    "리서치(근거·사례를 정확히 찾음)",
                    "스토리텔링/설득(쉽게 설명·이해시킴)",
                    "시각화/드로잉(그림·도식으로 표현)",
                    "기술실행(툴 숙련·구현력)",
                    "협업/리더십(소통·조율·분담)",
                    "발표/커뮤니케이션(무대/카메라 앞에서도 침착)",
                    "분석/개선(데이터 비교·피드백 반영)",
                    "자기관리(마감·계획·시간관리)",
                    "기타(직접 입력)"
                ]
                selected_strengths = []
                for choice_num in step2['choice_numbers']:
                    if 1 <= choice_num <= len(choices):
                        selected_strengths.append(choices[choice_num - 1])
                
                prompt += f"2단계 장점 탐색: {', '.join(selected_strengths)}\n"
        
        # 3단계 - 가치관 탐색 분석
        if 'step_3' in responses:
            step3 = responses['step_3']
            if step3.get('custom_answer'):
                prompt += f"3단계 가치관 탐색: 기타 - {step3['custom_answer']}\n"
            elif step3.get('choice_numbers'):
                choices = [
                    "누군가에게 도움/서비스 제공",
                    "새로운 것을 만들어 세상에 내놓기",
                    "어려운 문제를 해결하며 성장하기",
                    "무대·스크린에서 표현·공유하기",
                    "자연/동물을 지키고 회복 돕기",
                    "팀 프로젝트로 공동 목표 달성하기",
                    "지식을 배우고 체계화·정리하기",
                    "사람들을 웃게 하거나 감동 주기",
                    "목표를 세우고 꾸준히 실천/관리하기",
                    "기타(직접 입력)"
                ]
                selected_values = []
                for choice_num in step3['choice_numbers']:
                    if 1 <= choice_num <= len(choices):
                        selected_values.append(choices[choice_num - 1])
                
                prompt += f"3단계 가치관 탐색: {', '.join(selected_values)}\n"
        
        # 4단계 - 미래 탐색 분석
        if 'step_4' in responses:
            step4 = responses['step_4']
            if step4.get('custom_answer'):
                prompt += f"4단계 미래 관심: 기타 - {step4['custom_answer']}\n"
            elif step4.get('choice_numbers'):
                choices = [
                    "기후변화·자원순환",
                    "고령화·돌봄·1인 가구",
                    "AI·로봇과 사람의 협업·일자리",
                    "사이버 괴롭힘·개인정보·디지털 웰빙",
                    "교통안전·보행 친화 도시",
                    "생물다양성·멸종위기 보호",
                    "우주 쓰레기·탐사 윤리",
                    "공중보건·신종 질병",
                    "가짜뉴스·정보 리터러시",
                    "재난 대비·구조 시스템",
                    "기타(직접 입력)"
                ]
                selected_concerns = []
                for choice_num in step4['choice_numbers']:
                    if 1 <= choice_num <= len(choices):
                        selected_concerns.append(choices[choice_num - 1])
                
                prompt += f"4단계 미래 관심: {', '.join(selected_concerns)}\n"
        
        if regenerate:
            prompt += "\n이전 추천과는 다른 새로운 관점으로 진로를 제안해주세요.\n"
        
        prompt += f"""
위 정보를 바탕으로 {student_name}님에게 가장 적합한 진로를 한 문장으로 제안해주세요.

형식 A: [문제/가치]를 해결하는 [분야/역할] 전문가
형식 B: [대상]이 [가치]를 느끼도록 [콘텐츠/도구]를 만드는 [직무]

응답은 간단한 칭찬을 덧붙여 주세요.
"""
        
        return prompt
    
    def _build_middle_school_dream_logic_prompt(self, student_name: str, responses: Dict, final_dream: str) -> str:
        """중학생용 드림로직 프롬프트 구성"""
        
        # 응답 분석
        interests = []
        strengths = []
        values = []
        concerns = []
        
        # 1단계 흥미
        if 'step_1' in responses:
            step1 = responses['step_1']
            if step1.get('custom_answer'):
                interests.append(f"기타 - {step1['custom_answer']}")
            elif step1.get('choice_numbers'):
                interest_choices = [
                    "스토리 기획·세계관 만들기",
                    "캐릭터/콘셉트 아트(드로잉·컬러)",
                    "2D 애니메이션(키프레임·타이밍)",
                    "3D/모션그래픽(카메라 워크·이펙트)",
                    "코딩·게임/앱 프로토타이핑",
                    "로봇·메이킹(하드웨어/센서)",
                    "과학 실험·탐구(자료 수집·그래프)",
                    "스포츠/피지컬 트레이닝",
                    "동물·자연 관찰·보호 활동",
                    "요리·푸드 디자인/영양",
                    "영상 촬영·편집·사운드",
                    "탐구·리서치·인터뷰(트렌드 조사)",
                    "기타(직접 입력)"
                ]
                for choice_num in step1['choice_numbers']:
                    if 1 <= choice_num <= len(interest_choices):
                        interests.append(interest_choices[choice_num - 1])
        
        # 2단계 장점
        if 'step_2' in responses:
            step2 = responses['step_2']
            if step2.get('custom_answer'):
                strengths.append(f"기타 - {step2['custom_answer']}")
            elif step2.get('choice_numbers'):
                strength_choices = [
                    "문제정의(핵심을 빠르게 짚음)",
                    "창의발상(아이디어가 잘 떠오름)",
                    "리서치(근거·사례를 정확히 찾음)",
                    "스토리텔링/설득(쉽게 설명·이해시킴)",
                    "시각화/드로잉(그림·도식으로 표현)",
                    "기술실행(툴 숙련·구현력)",
                    "협업/리더십(소통·조율·분담)",
                    "발표/커뮤니케이션(무대/카메라 앞에서도 침착)",
                    "분석/개선(데이터 비교·피드백 반영)",
                    "자기관리(마감·계획·시간관리)",
                    "기타(직접 입력)"
                ]
                for choice_num in step2['choice_numbers']:
                    if 1 <= choice_num <= len(strength_choices):
                        strengths.append(strength_choices[choice_num - 1])
        
        prompt = f"""
{student_name}님의 진로 탐색 결과:

흥미 분야: {', '.join(interests)}
주요 장점: {', '.join(strengths)}
최종 꿈: {final_dream}

위 정보를 바탕으로 {student_name}님이 꿈을 이루기 위한 구체적인 드림로직을 작성해주세요.

중간목표는 3개로 구성하되, 각각 다음과 같은 역량을 포함해야 합니다:
1. 핵심 역량 A: 기술적/창작적 능력
2. 핵심 역량 B: 협업/소통 능력  
3. 핵심 역량 C: 윤리적/사회적 책임감

각 중간목표에는 다음을 구체적으로 포함해주세요:
- 실천활동(학교): 교과 활동, 수업 시간 활용, 과제 등
- 실천활동(일상): 집에서 할 수 있는 활동, 생활 습관 등
- 추천 활동: 동아리, 캠프, 봉사 활동 등

응원 메모에는 {student_name}님의 가장 큰 장점을 언급하고 격려해주세요.
"""
        
        return prompt

# 전역 AI 서비스 인스턴스
ai_service = MiddleSchoolAIService() if os.getenv('OPENAI_API_KEY') else None