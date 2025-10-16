"""
OpenAI API를 사용한 진로 추천 서비스
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
import logging
from .models import CareerStage, STAGE_QUESTIONS

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

class CareerRecommendationService:
    """OpenAI API를 사용한 진로 추천 서비스"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 환경변수에 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # 비용 효율적인 모델 사용
        
    def generate_career_recommendation(self, student_name: str, responses: Dict[CareerStage, Dict], regenerate: bool = False) -> str:
        """학생의 응답을 바탕으로 진로 추천 생성 (5단계 형식)"""
        
        # 응답 데이터를 텍스트로 변환
        response_text = self._format_responses_for_ai(student_name, responses)
        
        # 5단계 전용 프롬프트 생성
        system_prompt = self._get_step5_system_prompt()
        user_prompt = self._get_step5_user_prompt(student_name, response_text)
        
        # 새로운 추천 요청 시 프롬프트 수정
        if regenerate:
            user_prompt += "\n\n중요: 이전과는 다른 새로운 관점에서 진로를 추천해주세요. 다양한 분야와 접근 방식을 고려해주세요."
        
        # 콘솔에 GPT 프롬프트 출력
        print(f"\n🤖 GPT-4에게 보내는 프롬프트 (5단계 - {'재생성' if regenerate else '첫 생성'}):")
        print("=" * 80)
        print("� 응답 데이터 구조 확인:")
        print(f"responses 타입: {type(responses)}")
        print(f"responses 내용: {responses}")
        print("\n�📋 System Prompt:")
        print(system_prompt)
        print("\n👤 User Prompt:")
        print(user_prompt)
        print("=" * 80)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9 if regenerate else 0.7,  # 새로운 추천 시 더 창의적으로
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "추천을 생성할 수 없습니다."
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 오류: {str(e)}")
            return self._get_fallback_recommendation(student_name)
    
    def modify_career_recommendation(self, original_recommendation: str, modification_request: str, student_name: str) -> str:
        """진로 추천 수정 (5-1단계 수정 루프)"""
        
        system_prompt = """당신은 초등학생 진로 상담사입니다. 
        학생이 제시한 수정 요청에 따라 진로 추천을 수정해주세요.
        
        수정 가능한 요소:
        1. 분야 (예: 로봇공학 → 의학)
        2. 문제 (예: 기후변화 → 의료문제)  
        3. 대상 (예: 어린이 → 어르신)
        4. 도구/방법 (예: 로봇 → 앱)
        
        출력 형식: 반드시 "[문제/가치]를 해결하는 [분야/역할] 전문가" 형식으로 한 문장만 작성
        """
        
        user_prompt = f"""
        원래 추천: {original_recommendation}
        학생 이름: {student_name}
        수정 요청: {modification_request}
        
        위 요청에 따라 진로 추천을 수정해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else original_recommendation
            
        except Exception as e:
            logger.error(f"진로 추천 수정 오류: {str(e)}")
            return original_recommendation
    
    def generate_dream_logic(self, student_name: str, responses: Dict[CareerStage, Dict], career_goal: str) -> str:
        """드림로직 생성 (상세한 실천 계획)"""
        
        response_text = self._format_responses_for_ai(student_name, responses)
        
        system_prompt = self._get_dream_logic_system_prompt()
        user_prompt = self._get_dream_logic_user_prompt(student_name, response_text, career_goal)
        
        # 콘솔에 GPT 프롬프트 출력
        print(f"\n🌈 GPT-4에게 보내는 프롬프트 (6단계 - 드림로직):")
        print("=" * 80)
        print("📋 System Prompt:")
        print(system_prompt)
        print("\n👤 User Prompt:")
        print(user_prompt)
        print("=" * 80)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "드림로직을 생성할 수 없습니다."
            
        except Exception as e:
            logger.error(f"드림로직 생성 오류: {str(e)}")
            return self._get_fallback_dream_logic(student_name, career_goal)
    
    def generate_encouragement_message(self, student_name: str, current_stage: CareerStage) -> str:
        """단계별 맞춤 응원 메시지 생성"""
        
        stage_descriptions = {
            CareerStage.STEP_0: "진로 탐색을 시작하는 단계",
            CareerStage.STEP_1: "흥미를 탐색하는 단계",
            CareerStage.STEP_2: "장점을 발견하는 단계", 
            CareerStage.STEP_3: "가치관을 탐색하는 단계",
            CareerStage.STEP_4: "미래에 대해 생각하는 단계"
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 초등학생들을 격려하는 친근한 진로 상담사입니다. 학생의 이름을 부르며 따뜻하고 긍정적인 응원 메시지를 만들어주세요. 50자 이내로 간결하게 작성해주세요."
                    },
                    {
                        "role": "user", 
                        "content": f"{student_name} 학생이 {stage_descriptions.get(current_stage, '진로 탐색')} 중입니다. 응원 메시지를 만들어주세요."
                    }
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else f"{student_name}님! 정말 잘하고 있어요! 💪✨"
            
        except Exception as e:
            logger.error(f"응원 메시지 생성 오류: {str(e)}")
            return f"{student_name}님! 정말 잘하고 있어요! 💪✨"
    
    def _format_responses_for_ai(self, student_name: str, responses: Dict[CareerStage, Dict]) -> str:
        """AI가 이해할 수 있도록 응답 데이터 포맷팅"""
        
        formatted_text = f"학생 이름: {student_name}\n\n"
        
        stage_names = {
            CareerStage.STEP_1: "흥미 탐색",
            CareerStage.STEP_2: "장점 탐색", 
            CareerStage.STEP_3: "가치관 탐색",
            CareerStage.STEP_4: "미래 탐색"
        }
        
        for stage, response_data in responses.items():
            stage_name = stage_names.get(stage, str(stage))
            question = STAGE_QUESTIONS.get(stage, {}).get("question", "")
            
            # 실제 선택지 텍스트 변환
            answer_texts = []
            choice_numbers = response_data.get("choice_numbers", [])
            custom_answer = response_data.get("custom_answer", "")
            
            # 선택지 번호를 실제 텍스트로 변환
            stage_choices = STAGE_QUESTIONS.get(stage, {}).get("choices", [])
            for choice_num in choice_numbers:
                if 1 <= choice_num <= len(stage_choices):
                    choice_text = stage_choices[choice_num - 1]
                    # 기타 선택지인지 확인
                    if choice_text == "기타" and custom_answer:
                        answer_texts.append(f"기타: {custom_answer}")
                    else:
                        answer_texts.append(choice_text)
            
            # 답변 텍스트 구성
            if answer_texts:
                answer = ", ".join(answer_texts)
            elif custom_answer:
                answer = custom_answer
            else:
                answer = ""
            
            formatted_text += f"{stage_name}:\n"
            formatted_text += f"질문: {question}\n"
            formatted_text += f"답변: {answer}\n\n"
        
        return formatted_text
    
    def _get_step5_system_prompt(self) -> str:
        """5단계 전용 시스템 프롬프트"""
        return """당신은 초등학생 전문 진로 상담사입니다.

역할:
- 초등학생의 1~4단계 응답을 종합적으로 분석하여 개인 맞춤 진로 추천
- 학생의 구체적인 관심사와 답변 내용을 정확히 반영
- 다양한 분야(과학기술, 예술, 스포츠, 교육, 의료, 환경, 사회복지 등)를 고려
- 특히 '기타' 응답의 구체적 내용을 중점적으로 반영

분석 순서:
1. 흥미 분야: 학생이 시간 가는 줄 모르고 하는 활동 (특히 기타 답변 주목)
2. 핵심 강점: 학생만의 특별한 장점과 능력
3. 가치관: 행복을 느끼는 순간과 중요하게 생각하는 가치
4. 사회적 관심: 미래에 해결하고 싶은 문제나 이슈

출력 규칙:
1. 반드시 "[문제/가치]를 해결하는 [분야/역할] 전문가" 형식으로만 작성
2. 대안 형식: "사람과 사회에 도움이 되는 [콘텐츠/도구]를 만드는 [직무]"
3. 한 문장만 제시 (추가 설명 금지)
4. 학생의 모든 답변을 종합적으로 고려하여 개별 맞춤형 추천

다양한 분야 예시:
- 스포츠: "팀워크와 전략으로 사람들을 하나로 만드는 스포츠 감독"
- 수학/과학: "복잡한 데이터 문제를 해결하는 AI 수학자"
- 게임: "건전한 게임 문화를 만드는 게임 기획자"
- 환경: "기후변화 문제를 해결하는 친환경 기술자"
- 교육: "아이들이 즐겁게 배울 수 있는 교육 콘텐츠 개발자"
"""
    
    def _get_step5_user_prompt(self, student_name: str, response_text: str) -> str:
        """5단계 사용자 프롬프트"""
        return f"""다음은 {student_name} 학생의 1~4단계 진로 탐색 결과입니다:

{response_text}

중요: 위 응답에서 '기타:' 로 표시된 학생의 구체적인 답변을 특히 주의깊게 분석하세요.
학생이 직접 작성한 기타 답변은 가장 중요한 개인적 관심사를 나타냅니다.

{student_name} 학생의 모든 답변을 종합하여 가장 적합한 미래 진로를 제안해주세요.
반드시 "[문제/가치]를 해결하는 [분야/역할] 전문가" 형식으로 한 문장만 작성하세요.

예시 분석:
- 기타: 축구 전술 분석 → 스포츠 데이터 분석가, 스포츠 과학자
- 기타: 수학 문제 해결 → 수학 연구자, 데이터 사이언티스트  
- 기타: 게임 스토리 창작 → 게임 기획자, 인터랙티브 미디어 디자이너"""

    def _get_system_prompt(self) -> str:
        """기본 진로 추천을 위한 시스템 프롬프트 (호환성 유지)"""
        return self._get_step5_system_prompt()
    
    def _get_user_prompt(self, response_text: str) -> str:
        """기본 사용자 프롬프트 (호환성 유지)"""
        return f"""다음은 초등학생의 진로 탐색 결과입니다:

{response_text}

이 학생에게 가장 적합한 미래 진로를 한 문장으로 추천해주세요.
반드시 "[문제/가치]를 해결하는 [분야/역할] 전문가" 형식으로 작성해주세요."""
    
    def _get_dream_logic_system_prompt(self) -> str:
        """드림로직 생성을 위한 시스템 프롬프트"""
        return """당신은 초등학생의 꿈을 실현하기 위한 구체적인 실천 계획을 세우는 전문가입니다.

역할:
- 최종 꿈을 이루기 위해 필요한 3가지 핵심 역량 제시
- 각 역량별로 학교생활과 개인 성장 관련 실천활동 2가지씩 제안
- 초등학생이 실제로 할 수 있는 구체적이고 실현 가능한 활동 제시
- 격려와 응원이 담긴 따뜻한 톤 유지

출력 형식:
[학생이름의 드림 로직]
최종꿈: [진로 목표]

[중간목표1] 역량명: 설명
• 실천활동1: 학교생활 
    1.구체적 활동
    2.구체적 활동
• 실천활동2: 개인 성장
    1.구체적 활동
    2.구체적 활동

[중간목표2] 역량명: 설명  
• 실천활동1: 학교생활 
    1.구체적 활동
    2.구체적 활동
• 실천활동2: 개인 성장
    1.구체적 활동
    2.구체적 활동

[중간목표3] 역량명: 설명
• 실천활동1: 학교생활 
    1.구체적 활동
    2.구체적 활동
• 실천활동2: 개인 성장
    1.구체적 활동
    2.구체적 활동

응원 메모: 학생의 장점을 칭찬하며 격려하는 메시지

드림로직 예시
[유진의 드림 로직]
최종꿈기후·쓰레기 문제를 해결하는 친환경 로봇 엔지니어


[중간목표1] 메이킹·설계 역량 키우기 (정밀 제작 & 구조 이해)
• 실천활동1: 학교생활
    1. 과학/실과 시간에 재활용 소재로 움직이는 장난감(기어·레버 구조) 만들기 도전
    2. 과학탐구대회·메이커 대회에 친구와 팀으로 참가해 보고서 작성
    3. 수학 시간에 도형·비율·분수 단원 문제를 주 3회 10분씩 꾸준히 풀기
실천활동2: 개인 성장
    1. 주 1회 레고/브릭으로 기계 구조(기어, 크랭크, 차동기어) 따라 만들고 사진·메모로 기록
    2. 드라이버·펜치 등 기본 공구 안전 사용법 익히고, 나사·부품 정리함 직접 만들기


[중간목표2] 환경·자원순환 이해 넓히기 (기후·쓰레기 문제의 원인과 해결)
• 실천활동1: 학교생활
    1. 교내 환경동아리 또는 학급 ‘분리배출 지킴이’ 활동 기획·실행
    2. 급식실 음식물쓰레기 줄이기 미니 프로젝트: 하루 배출량 계량→그래프로 정리→캠페인 발표
• 실천활동2: 개인 성장
    1. 주 2회 기후·쓰레기 관련 기사나 어린이 책 읽고 ‘한 줄 요약 + 왜 문제인지’ 노트 작성
    2. 집에서 업사이클 실험 1가지(예: 페트병 화분, 종이 분리함 제작) 진행하고 효과·느낌 기록


[중간목표3] 코딩·로봇 제어 능력 기르기 (센서로 문제 해결)
• 실천활동1: 학교생활
    1. 코딩 수업에서 블록코딩으로 모터·LED·초음파 센서 제어 미션 수행
    2. ‘분리배출 도우미 로봇’ 아이디어로 알고리즘(입력→판단→동작) 흐름도 만들어 보기
• 실천활동2: 개인 성장
    1. 월 1회 미니 프로젝트: 색 센서로 쓰레기 색상 분류→서보모터로 칸 이동 프로토타입 제작
    2. 결과를 가족/친구 앞에서 3분 발표(문제→아이디어→작동 방법→다음에 고칠 점)


작은 습관 체크리스트 (매주)
• 월: 레고/브릭 구조 만들기 30분 & 사진 기록
• 수: 환경 기사 1건 읽고 ‘한 줄 요약’
• 금: 블록코딩/센서 제어 30분 연습
• 주말: 업사이클/프로토타입 개선 1가지
응원 메모
유진의 '야무진 손'과 '새로운 것 만들기' 사랑은 큰 힘이야. 차근차근 해 보면, 유진만의 친환경 로봇이 세상을 더 깨끗하게 바꿀 거야! 😊💚
"""
    
    def generate_step4_issues(self, student_name: str, responses: Dict[CareerStage, Dict], regenerate: bool = False) -> List[str]:
        """Step 4: 1~3단계 응답 기반 AI 이슈 생성 (새로운 기능)"""
        
        # 1~3단계 응답 분석 - 실제 텍스트로 추출
        interests = self._extract_choices_text_with_stage(responses.get(CareerStage.STEP_1, {}), CareerStage.STEP_1)
        strengths = self._extract_choices_text_with_stage(responses.get(CareerStage.STEP_2, {}), CareerStage.STEP_2)
        values = self._extract_choices_text_with_stage(responses.get(CareerStage.STEP_3, {}), CareerStage.STEP_3)
        
        system_prompt = """당신은 초등학생 진로 상담사입니다.
학생의 흥미, 장점, 가치관을 분석하여 관심분야에서 미래사회에 대두될만한 문제 사항을 5가지 제시해주세요.

중요한 조건:
1. (적합성) 초등 눈높이 표현으로 친절한 말투, 모호어 금지
2. (다양성) 예술·과학·스포츠·공동체·자연 등 스펙트럼 균형
3. (선택성) 서로 다른 성향이 겹치지 않도록 중복 최소화

출력 형식: 
각 이슈를 한 문장으로 작성하고, 번호를 매기지 마세요.
예시:
AI와 함께하는 나만의 캐릭터 및 스토리 창작 (A.I. Co-Creation)
모두를 위한 캐릭터(Universal Character) 디자인 및 윤리
가상현실/증강현실(VR/AR) 속 인터랙티브 만화 제작
캐릭터 지적재산권(IP)을 활용한 다중 플랫폼 스토리 확장
친환경 및 사회 공헌 메시지를 담은 '착한 캐릭터' 개발"""

        user_prompt = f"""
학생 이름: {student_name}
흥미: {interests}
장점: {strengths}
가치관: {values}

위 정보를 바탕으로 {student_name}님이 관심을 가질 만한 관심분야에서 미래사회에 대두될만한 문제 사항을 5가지 제시해주세요.
각 이슈는 학생의 흥미, 장점, 가치관과 연결되어야 합니다.
"""

        if regenerate:
            user_prompt += "\n\n중요: 이전과는 완전히 다른 새로운 이슈들을 제시해주세요. 중복되지 않는 다양한 분야와 관점으로 접근해주세요."

        print(f"\n🤖 GPT-4에게 보내는 프롬프트 (Step 4 이슈 생성 - {'재생성' if regenerate else '첫 생성'}):")
        print("=" * 80)
        print("📋 System Prompt:")
        print(system_prompt)
        print("\n👤 User Prompt:")
        print(user_prompt)
        print("=" * 80)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9 if regenerate else 0.7,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            if not content:
                return self._get_fallback_step4_issues(student_name)
            
            # 응답을 줄 단위로 분할하고 정리
            lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
            
            # 번호나 불필요한 텍스트 제거
            cleaned_lines = []
            for line in lines:
                # 번호 제거 (1., 2., -, • 등)
                line = line.strip()
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '▪', '◦')):
                    line = line[2:].strip()
                elif line[0:1].isdigit() and line[1:2] in ['.', ')', ':']:
                    line = line[2:].strip()
                
                if line and len(line) > 10:  # 너무 짧은 줄 제외
                    cleaned_lines.append(line)
            
            # 정확히 5개 이슈 반환
            if len(cleaned_lines) >= 5:
                return cleaned_lines[:5]
            else:
                # 부족한 경우 대체 이슈 추가
                fallback_issues = self._get_fallback_step4_issues(student_name)
                while len(cleaned_lines) < 5:
                    for fallback in fallback_issues:
                        if fallback not in cleaned_lines:
                            cleaned_lines.append(fallback)
                            break
                    if len(cleaned_lines) >= 5:
                        break
                return cleaned_lines[:5]
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 오류 (Step 4 이슈): {str(e)}")
            return self._get_fallback_step4_issues(student_name)
    
    def _extract_choices_text(self, response_data: Dict) -> str:
        """응답 데이터에서 선택지 텍스트 추출"""
        if not response_data or 'choice_numbers' not in response_data:
            return "정보 없음"
        
        # custom_answer가 있으면 그것을 사용
        if response_data.get('custom_answer'):
            return response_data['custom_answer']
        
        choice_numbers = response_data.get('choice_numbers', [])
        if not choice_numbers:
            return "정보 없음"
        
        return f"선택지 {', '.join(map(str, choice_numbers))}"
    
    def _extract_choices_text_with_stage(self, response_data: Dict, stage: CareerStage) -> str:
        """단계별 응답 데이터에서 실제 선택지 텍스트 추출"""
        if not response_data or 'choice_numbers' not in response_data:
            return "정보 없음"
        
        # custom_answer가 있으면 그것을 사용
        if response_data.get('custom_answer'):
            return response_data['custom_answer']
        
        choice_numbers = response_data.get('choice_numbers', [])
        if not choice_numbers:
            return "정보 없음"
        
        # STAGE_QUESTIONS에서 실제 선택지 텍스트 가져오기
        stage_data = STAGE_QUESTIONS.get(stage)
        if not stage_data or 'choices' not in stage_data:
            return f"선택지 {', '.join(map(str, choice_numbers))}"
        
        choices = stage_data['choices']
        selected_texts = []
        
        for choice_num in choice_numbers:
            if 1 <= choice_num <= len(choices):
                selected_texts.append(choices[choice_num - 1])
            else:
                selected_texts.append(f"선택지 {choice_num}")
        
        return ", ".join(selected_texts)
    
    def _get_fallback_step4_issues(self, student_name: str) -> List[str]:
        """Step 4 이슈 생성 실패시 대체 이슈"""
        return [
            "AI와 함께하는 창의적인 콘텐츠 제작과 윤리적 사용 방법",
            "친환경 기술을 활용한 지속가능한 미래 도시 설계",
            "디지털 시대의 건강한 소통과 사이버 예절 문화 만들기",
            "로봇과 인간이 협력하는 새로운 일자리와 역할 분담",
            "다양성을 존중하는 포용적인 공동체 만들기와 갈등 해결"
        ]
    
    def _get_dream_logic_user_prompt(self, student_name: str, response_text: str, career_goal: str) -> str:
        """드림로직 사용자 프롬프트"""
        return f"""학생 정보:
{response_text}

최종 꿈: {career_goal}

{student_name} 학생이 이 꿈을 이루기 위한 구체적인 드림로직을 작성해주세요."""
    
    def _get_fallback_recommendation(self, student_name: str) -> str:
        """API 오류시 기본 추천 (5단계 형식)"""
        return "다양한 경험을 통해 세상을 더 좋게 만드는 창의적 문제해결 전문가"
    
    def _get_fallback_dream_logic(self, student_name: str, career_goal: str) -> str:
        """API 오류시 기본 드림로직"""
        return f"""[{student_name}의 드림 로직]
최종꿈: {career_goal}

[중간목표1] 기초 실력 쌓기
• 실천활동1: 학교생활 - 관련 과목에서 적극적으로 참여하기
• 실천활동2: 개인 성장 - 관련 책이나 자료 찾아보기

[중간목표2] 경험 넓히기  
• 실천활동1: 학교생활 - 동아리나 특별활동 참가하기
• 실천활동2: 개인 성장 - 관련 체험활동이나 견학 참여하기

[중간목표3] 소통 능력 기르기
• 실천활동1: 학교생활 - 친구들과 협력하여 프로젝트 진행하기
• 실천활동2: 개인 성장 - 자신의 생각을 정리하고 발표하는 연습하기

응원 메모: {student_name}님의 열정과 노력이 있다면 분명 멋진 꿈을 이룰 수 있을 거예요! 😊💪
드림로직 예시
[유진의 드림 로직]
최종꿈기후·쓰레기 문제를 해결하는 친환경 로봇 엔지니어


[중간목표1] 메이킹·설계 역량 키우기 (정밀 제작 & 구조 이해)
•
• 실천활동1: 학교생활
1. 과학/실과 시간에 재활용 소재로 움직이는 장난감(기어·레버 구조) 만들기 도전
2. 과학탐구대회·메이커 대회에 친구와 팀으로 참가해 보고서 작성
3. 수학 시간에 도형·비율·분수 단원 문제를 주 3회 10분씩 꾸준히 풀기
실천활동2: 개인 성장
1. 주 1회 레고/브릭으로 기계 구조(기어, 크랭크, 차동기어) 따라 만들고 사진·메모로 기록
2. 드라이버·펜치 등 기본 공구 안전 사용법 익히고, 나사·부품 정리함 직접 만들기


[중간목표2] 환경·자원순환 이해 넓히기 (기후·쓰레기 문제의 원인과 해결)
• 실천활동1: 학교생활
1. 교내 환경동아리 또는 학급 ‘분리배출 지킴이’ 활동 기획·실행
2. 급식실 음식물쓰레기 줄이기 미니 프로젝트: 하루 배출량 계량→그래프로 정리→캠페인 발표
실천활동2: 개인 성장
1. 주 2회 기후·쓰레기 관련 기사나 어린이 책 읽고 ‘한 줄 요약 + 왜 문제인지’ 노트 작성
2. 집에서 업사이클 실험 1가지(예: 페트병 화분, 종이 분리함 제작) 진행하고 효과·느낌 기록


[중간목표3] 코딩·로봇 제어 능력 기르기 (센서로 문제 해결)
• 실천활동1: 학교생활
1. 코딩 수업에서 블록코딩으로 모터·LED·초음파 센서 제어 미션 수행
2. ‘분리배출 도우미 로봇’ 아이디어로 알고리즘(입력→판단→동작) 흐름도 만들어 보기
실천활동2: 개인 성장
1. 월 1회 미니 프로젝트: 색 센서로 쓰레기 색상 분류→서보모터로 칸 이동 프로토타입 제작
2. 결과를 가족/친구 앞에서 3분 발표(문제→아이디어→작동 방법→다음에 고칠 점)


작은 습관 체크리스트 (매주)
• 월: 레고/브릭 구조 만들기 30분 & 사진 기록
• 수: 환경 기사 1건 읽고 ‘한 줄 요약’
• 금: 블록코딩/센서 제어 30분 연습
• 주말: 업사이클/프로토타입 개선 1가지
응원 메모
유진의 ‘야무진 손’과 ‘새로운 것 만들기’ 사랑은 큰 힘이야. 차근차근 해 보면, 유진만의 친환경 로봇이 세상을 더 깨끗하게 바꿀 거야! 😊💚
"""

# 전역 서비스 인스턴스  
try:
    ai_service = CareerRecommendationService()
    logger.info("OpenAI API 서비스가 성공적으로 초기화되었습니다.")
except Exception as e:
    logger.error(f"OpenAI API 서비스 초기화 실패: {str(e)}")
    ai_service = None