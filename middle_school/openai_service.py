"""
중학생 진로 탐색을 위한 OpenAI 서비스
중학생 개개인의 흥미·강점·가치·미래 관심을 연결하여
"현실적인 진로 목표 + 실행 가능한 실천 계획"을 도출
"""

import os
import logging
from typing import Dict, Optional, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MiddleSchoolAIService:
    """중학생 진로 탐색을 위한 AI 서비스"""
    
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4.1-2025-04-14"  # 비용 효율적인 모델 사용
        
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
        """AI 서비스 사용 가능 여부 확인
        
        Returns:
            bool: 서비스 사용 가능 여부
        """
        return self.client is not None
    
    def generate_middle_school_recommendation(self, student_name: str, responses: Dict, regenerate: bool = False) -> Optional[str]:
        """중학생용 진로 추천 생성 (5단계)
        
        Args:
            student_name (str): 학생 이름
            responses (Dict): 1-4단계 응답 데이터
            regenerate (bool): 새로운 추천 생성 여부
            
        Returns:
            Optional[str]: 생성된 진로 추천 또는 None
        """
        if not self.is_available() or not self.client:
            logger.warning("AI 서비스를 사용할 수 없습니다.")
            return None
        
        try:
            # 응답 데이터를 텍스트로 변환
            response_text = self._format_responses_for_ai(student_name, responses)
            
            # 5단계 전용 프롬프트 생성
            system_prompt = self._get_step5_system_prompt()
            user_prompt = self._get_step5_user_prompt(student_name, response_text)

            # 프롬프트 로깅 추가 (콘솔에 출력)
            logger.info("[LLM 프롬프트 - 5단계]")
            logger.info(f"System prompt: {system_prompt}")
            logger.info(f"User prompt: {user_prompt}")
            print("\n========== [LLM 프롬프트 - 5단계] ==========")
            print(f"System prompt:\n{system_prompt}\n")
            print(f"User prompt:\n{user_prompt}\n")
            print("===========================================\n")
            
            # 새로운 추천 요청 시 프롬프트 수정
            if regenerate:
                user_prompt += "\n\n중요: 이전과는 다른 새로운 관점에서 진로를 추천해주세요. 다양한 분야와 접근 방식을 고려해주세요."
            
            # 모델에 따라 max_tokens 파라미터명 분기 (명시적)
            if "gpt-5" in self.model.lower():
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_completion_tokens=200
                    # temperature 파라미터 생략 (기본값 1)
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.9 if regenerate else 0.7,
                    max_tokens=200
                )
            
            recommendation = response.choices[0].message.content
            if recommendation:
                recommendation = recommendation.strip()
            logger.info(f"중학생 진로 추천 생성 완료: {student_name}")
            return recommendation
            
        except Exception as e:
            logger.error(f"중학생 진로 추천 생성 오류: {str(e)}")
            return self._get_fallback_recommendation(student_name)
    
    def generate_step4_future_issues(self, student_name: str, responses: Dict, regenerate_count: int = 0, previous_issues: Optional[List[str]] = None) -> Optional[List[str]]:
        """4단계 미래 이슈 선택지 생성
        
        Args:
            student_name (str): 학생 이름
            responses (Dict): 1-3단계 응답 데이터
            regenerate_count (int): 재생성 횟수 (0-4)
            previous_issues (list): 이전에 생성된 이슈들 (중복 방지용)
            
        Returns:
            Optional[list]: 생성된 5가지 이슈 선택지 또는 None
        """
        if not self.is_available() or not self.client:
            logger.warning("AI 서비스를 사용할 수 없습니다.")
            return self._get_fallback_step4_choices()
        
        try:
            # 1-3단계 응답 데이터를 텍스트로 변환
            response_text = self._format_step123_responses_for_ai(student_name, responses)
            
            # 4단계 전용 프롬프트 생성
            system_prompt = self._get_step4_system_prompt()
            user_prompt = self._get_step4_user_prompt(student_name, response_text, regenerate_count, previous_issues)
            
            # 프롬프트 로깅
            logger.info("[LLM 프롬프트 - 4단계]")
            logger.info(f"System prompt: {system_prompt}")
            logger.info(f"User prompt: {user_prompt}")
            print("\n========== [LLM 프롬프트 - 4단계] ==========")
            print(f"System prompt:\n{system_prompt}\n")
            print(f"User prompt:\n{user_prompt}\n")
            print("===========================================\n")
            
            # OpenAI API 호출
            if "gpt-5" in self.model.lower():
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_completion_tokens=800
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.8 if regenerate_count > 0 else 0.7,
                    max_tokens=800
                )
            
            # 응답 파싱
            content = response.choices[0].message.content
            if content:
                content = content.strip()
                issues = self._parse_step4_issues(content)
                logger.info(f"4단계 미래 이슈 생성 완료: {len(issues)}개")
                return issues
            
            return self._get_fallback_step4_choices()
            
        except Exception as e:
            logger.error(f"4단계 미래 이슈 생성 오류: {str(e)}")
            return self._get_fallback_step4_choices()
    
    def generate_middle_school_dream_logic(self, student_name: str, responses: Dict, final_dream: str) -> Optional[str]:
        """중학생용 드림로직 생성 (6단계) - 학교생활·일상 실천 중심
        
        Args:
            student_name (str): 학생 이름
            responses (Dict): 1-4단계 응답 데이터
            final_dream (str): 최종 선택된 꿈
            
        Returns:
            Optional[str]: 생성된 드림로직 또는 None
        """
        if not self.is_available() or not self.client:
            logger.warning("AI 서비스를 사용할 수 없습니다.")
            return None
        
        try:
            # 응답 데이터를 텍스트로 변환
            response_text = self._format_responses_for_ai(student_name, responses)
            
            # 6단계 전용 프롬프트 생성
            system_prompt = self._get_dream_logic_system_prompt()
            user_prompt = self._get_dream_logic_user_prompt(student_name, response_text, final_dream)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            dream_logic = response.choices[0].message.content
            if dream_logic:
                dream_logic = dream_logic.strip()
            logger.info(f"중학생 드림로직 생성 완료: {student_name}")
            return dream_logic
            
        except Exception as e:
            logger.error(f"중학생 드림로직 생성 오류: {str(e)}")
            return self._get_fallback_dream_logic(student_name, final_dream)
    
    def _format_responses_for_ai(self, student_name: str, responses: Dict) -> str:
        """AI가 이해할 수 있도록 응답 데이터 포맷팅
        
        Args:
            student_name (str): 학생 이름
            responses (Dict): 1-4단계 응답 데이터
            
        Returns:
            str: 포맷팅된 응답 텍스트
        """
        formatted_text = f"학생 이름: {student_name}\n\n"
        
        # 중학생용 단계별 선택지 매핑
        stage_choices = {
            'step_1': [
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
            ],
            'step_2': [
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
            ],
            'step_3': [
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
            ],
            'step_4': [
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
        }
        
        stage_names = {
            'step_1': "흥미 탐색 (무엇을 할 때 시간이 빠르게 지나가나요?)",
            'step_2': "장점 탐색 (팀이나 프로젝트에서 특히 잘하는 부분은 무엇인가요?)",
            'step_3': "가치관 탐색 (어떤 순간에 가장 보람이나 행복을 느끼나요?)",
            'step_4': "미래 관심 (미래 사회에서 특히 걱정되는 주제를 골라 주세요)"
        }
        
        for stage_key, response_data in responses.items():
            stage_name = stage_names.get(stage_key, stage_key)
            choices = stage_choices.get(stage_key, [])
            
            # 실제 선택지 텍스트 변환
            answer_texts = []
            choice_numbers = response_data.get("choice_numbers", [])
            custom_answer = response_data.get("custom_answer", "")
            
            # 선택지 번호를 실제 텍스트로 변환
            for choice_num in choice_numbers:
                if 1 <= choice_num <= len(choices):
                    choice_text = choices[choice_num - 1]
                    # 기타 선택지인지 확인
                    if choice_text == "기타(직접 입력)" and custom_answer:
                        answer_texts.append(f"기타: {custom_answer}")
                    else:
                        answer_texts.append(choice_text)
            
            # 답변 텍스트 구성
            if answer_texts:
                answer = ", ".join(answer_texts)
            elif custom_answer:
                answer = f"기타: {custom_answer}"
            else:
                answer = ""
            
            formatted_text += f"{stage_name}\n"
            formatted_text += f"답변: {answer}\n\n"
        
        return formatted_text
    
    def _get_step5_system_prompt(self) -> str:
        """5단계 전용 시스템 프롬프트
        
        Returns:
            str: 시스템 프롬프트 텍스트
        """
        return """당신은 중학생 전문 진로 상담사입니다.

역할:
- 중학생의 1~4단계 응답을 종합적으로 분석하여 개인 맞춤 진로 추천
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
2. 대안 형식: "[대상]이 [가치]를 느끼도록 [콘텐츠/도구]를 만드는 [직무]"
3. 한 문장만 제시 (추가 설명 금지)
4. 학생의 모든 답변을 종합적으로 고려하여 개별 맞춤형 추천
5. 중학생이 이해하기 쉽고 구체적으로 표현
6. 가벼운 존댓말로 작성

다양한 분야 예시:
- AI/로봇: "AI·로봇과 사람의 협업 문제를 해결하는 스토리텔링 전문가"
- 게임: "건전한 게임 문화를 만드는 게임 기획자"
- 환경: "기후변화 문제를 해결하는 친환경 기술자"
- 교육: "청소년이 즐겁게 배울 수 있는 교육 콘텐츠 개발자"
"""
    
    def _get_step5_user_prompt(self, student_name: str, response_text: str) -> str:
        """5단계 사용자 프롬프트
        
        Args:
            student_name (str): 학생 이름
            response_text (str): 포맷팅된 응답 텍스트
            
        Returns:
            str: 사용자 프롬프트 텍스트
        """
        return f"""다음은 {student_name} 학생의 1~4단계 진로 탐색 결과입니다:

{response_text}

중요: 위 응답에서 '기타:' 로 표시된 학생의 구체적인 답변을 특히 주의깊게 분석하세요.
학생이 직접 작성한 기타 답변은 가장 중요한 개인적 관심사를 나타냅니다.

{student_name} 학생의 모든 답변을 종합하여 가장 적합한 미래 진로를 제안해주세요.
반드시 "[문제/가치]를 해결하는 [분야/역할] 전문가" 형식으로 한 문장만 작성하세요."""
    
    def _get_dream_logic_system_prompt(self) -> str:
        """드림로직 생성을 위한 시스템 프롬프트
        
        Returns:
            str: 드림로직 시스템 프롬프트 텍스트
        """
        return """당신은 중학생의 꿈을 실현하기 위한 구체적인 실천 계획을 세우는 전문가입니다.

역할:
- 최종 꿈을 이루기 위해 필요한 3가지 핵심 역량 제시
- 각 역량별로 학교생활과 일상생활 관련 실천활동 제안
- 중학생이 실제로 할 수 있는 구체적이고 실현 가능한 활동 제시
- 격려와 응원이 담긴 따뜻한 톤 유지

출력 형식을 정확히 따라주세요:

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

추천 활동: [예: 또래상담자, 리더십 캠프 등]

[중간목표 3] 핵심 역량 C (왜 필요한가)
설명: [윤리, 시민의식, 리터러시 등과의 연결]

실천활동(학교): [관련 교과 단원 공부, 기사 요약]

실천활동(일상): [대피 경로 확인, 뉴스 분석]

추천 활동: [예: 안전 체험관 등]

💬 응원 메모
"{student_name}의 [장점]은 진짜 강점이에요.
일상 속 작은 실천이 쌓이면 [최종꿈]에 한 걸음 다가설 거예요!"

각 중간목표에는 학교 과목·일상 루틴·참여 활동을 구체적으로 제시해야 합니다.
문장은 가벼운 존댓말로, 답변은 짧고 명확하게 정리해주세요."""
    
    def _get_dream_logic_user_prompt(self, student_name: str, response_text: str, final_dream: str) -> str:
        """드림로직 사용자 프롬프트
        
        Args:
            student_name (str): 학생 이름
            response_text (str): 포맷팅된 응답 텍스트
            final_dream (str): 최종 선택된 꿈
            
        Returns:
            str: 드림로직 사용자 프롬프트 텍스트
        """
        return f"""학생 정보:
{response_text}

최종 꿈: {final_dream}

{student_name} 학생이 이 꿈을 이루기 위한 구체적인 드림로직을 작성해주세요.

중간목표는 3개로 구성하되, 각각 다음과 같은 역량을 포함해야 합니다:
1. 핵심 역량 A: 기술적/창작적 능력
2. 핵심 역량 B: 협업/소통 능력  
3. 핵심 역량 C: 윤리적/사회적 책임감

각 중간목표에는 다음을 구체적으로 포함해주세요:
- 실천활동(학교): 교과 활동, 수업 시간 활용, 과제 등
- 실천활동(일상): 집에서 할 수 있는 활동, 생활 습관 등
- 추천 활동: 동아리, 캠프, 봉사 활동 등

응원 메모에는 {student_name}님의 가장 큰 장점을 언급하고 격려해주세요."""
    
    def _get_fallback_recommendation(self, student_name: str) -> str:
        """API 오류시 기본 추천
        
        Args:
            student_name (str): 학생 이름
            
        Returns:
            str: 기본 추천 메시지
        """
        return "다양한 경험을 통해 세상을 더 좋게 만드는 창의적 문제해결 전문가가 되어보는 건 어떨까요?"
    
    def _get_fallback_dream_logic(self, student_name: str, final_dream: str) -> str:
        """API 오류시 기본 드림로직
        
        Args:
            student_name (str): 학생 이름
            final_dream (str): 최종 선택된 꿈
            
        Returns:
            str: 기본 드림로직 메시지
        """
        return f"""[{student_name}의 드림 로직]
최종꿈: {final_dream}

[중간목표 1] 기초 실력 쌓기 (꿈의 기반 마련)
설명: 진로 목표 달성을 위한 기본 역량 개발

실천활동(학교): 관련 교과목에서 적극적으로 참여하고 질문하기

실천활동(일상): 관련 분야의 책이나 영상 자료 찾아보며 지식 넓히기

추천 활동: 관련 동아리나 특별활동 참가하기

[중간목표 2] 경험 넓히기 (실전 경험 쌓기)
설명: 다양한 활동을 통한 실무 감각 기르기

실천활동(학교): 친구들과 협력하여 프로젝트나 발표 진행하기

실천활동(일상): 관련 체험활동이나 견학 기회 찾아 참여하기

추천 활동: 봉사활동이나 캠프를 통해 사회경험 쌓기

[중간목표 3] 소통 능력 기르기 (리더십 개발)
설명: 타인과 협력하고 영향을 주는 능력 개발

실천활동(학교): 자신의 생각을 정리하고 발표하는 연습하기

실천활동(일상): 가족, 친구들과 자신의 꿈에 대해 대화하기

추천 활동: 또래 상담이나 멘토링 활동 참여하기

💬 응원 메모
"{student_name}의 열정과 노력이 있다면 분명 멋진 꿈을 이룰 수 있을 거예요!
일상 속 작은 실천이 쌓이면 꿈에 한 걸음 다가설 거예요!"
"""

    def _format_step123_responses_for_ai(self, student_name: str, responses: Dict) -> str:
        """1-3단계 응답 데이터를 AI가 이해할 수 있도록 포맷팅
        
        Args:
            student_name (str): 학생 이름
            responses (Dict): 1-3단계 응답 데이터
            
        Returns:
            str: 포맷팅된 응답 텍스트
        """
        formatted_text = f"학생 이름: {student_name}\n\n"
        
        # 중학생용 1-3단계 선택지 매핑
        stage_choices = {
            'step_1': [
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
            ],
            'step_2': [
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
            ],
            'step_3': [
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
        }
        
        stage_labels = {
            'step_1': '1단계 (흥미)',
            'step_2': '2단계 (장점)', 
            'step_3': '3단계 (가치관)'
        }
        
        # 1-3단계 응답만 처리
        for stage_key in ['step_1', 'step_2', 'step_3']:
            if stage_key in responses:
                response = responses[stage_key]
                choice_numbers = response.get('choice_numbers', [])
                custom_answer = response.get('custom_answer', '')
                
                formatted_text += f"{stage_labels[stage_key]}:\n"
                
                # 선택지 번호를 텍스트로 변환
                for choice_num in choice_numbers:
                    if choice_num <= len(stage_choices[stage_key]):
                        choice_text = stage_choices[stage_key][choice_num - 1]
                        formatted_text += f"  - {choice_text}\n"
                
                # 기타 선택시 직접 입력 내용 추가
                if custom_answer:
                    formatted_text += f"  - 기타: {custom_answer}\n"
                
                formatted_text += "\n"
        
        return formatted_text
    
    def _get_step4_system_prompt(self) -> str:
        """4단계 시스템 프롬프트"""
        return """너는 중학생 진로 탐색을 돕는 전문 어시스턴트야.
사용자의 흥미, 장점, 가치관을 바탕으로 미래에 관심을 가질 만한 사회적, 기술적 최신 이슈나 해결과제 5가지를 제시해줘.

조건:
1. 대한민국 중학생이 관심을 가질 수 있는 수준의 주제
2. 각 이슈는 간결하고 이해하기 쉽게 표현
3. 현실적이고 구체적인 문제들
4. 학생의 흥미, 장점, 가치관과 연결되는 내용
5. 번호 없이 단순히 이슈명만 나열

응답 형식:
- 스마트시티 교통/환경 문제를 해결하는 시뮬레이션 게임 개발
- 저전력/친환경 컴퓨팅을 위한 '그린 코딩' 및 게임 엔진 최적화
- 학교 폭력 예방 및 심리 지원을 위한 AI 기반 익명 소통 시스템
- 1인 개발자를 위한 자동화된 게임 테스트 및 버그 예측 시스템
- 디지털 격차 해소를 위한 코딩 교육 콘텐츠의 인터랙티브 재구성"""
    
    def _get_step4_user_prompt(self, student_name: str, response_text: str, regenerate_count: int, previous_issues: Optional[List[str]] = None) -> str:
        """4단계 사용자 프롬프트"""
        prompt = f"""학생 정보:
{response_text}

나는 중학생이야. 흥미, 장점, 가치관을 통해 미래에 관심을 가질 주제를 찾고 싶어.
위 1~3단계 응답과 관련한 사회, 기술적인 최신 이슈 또는 해결과제를 5가지 제시해줘."""

        if regenerate_count > 0 and previous_issues:
            prompt += f"\n\n중요: 아래 기존에 제시된 이슈들과는 완전히 다른 새로운 주제들로 제시해줘.\n기존 이슈들:\n"
            for issue in previous_issues:
                prompt += f"- {issue}\n"
        
        if regenerate_count > 0:
            prompt += f"\n가능한 중복되지 않는 주제로 5가지 새로 제시해줘. (재생성 {regenerate_count}회차)"
        
        return prompt
    
    def _parse_step4_issues(self, content: str) -> List[str]:
        """AI 응답에서 이슈 목록 파싱"""
        issues = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 다양한 형식의 리스트 처리
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                issue = line[1:].strip()
                if issue:
                    issues.append(issue)
            elif line and not line.startswith('#') and not line.startswith('**'):
                # 번호가 있는 경우 제거
                import re
                clean_line = re.sub(r'^\d+\.\s*', '', line)
                if clean_line and len(clean_line) > 10:  # 너무 짧은 텍스트 제외
                    issues.append(clean_line)
        
        # 5개로 제한
        return issues[:5] if len(issues) >= 5 else issues
    
    def _get_fallback_step4_choices(self) -> List[str]:
        """4단계 기본 선택지 (AI 서비스 실패시 사용)"""
        return [
            "기후변화와 환경 보호를 위한 지속가능한 기술 개발",
            "AI와 인간이 함께 살아가는 미래 사회 설계",
            "사이버 보안과 개인정보 보호 강화",
            "고령화 사회의 돌봄 서비스와 기술 혁신",
            "디지털 격차 해소와 정보 접근성 향상"
        ]


# 전역 AI 서비스 인스턴스
ai_service = MiddleSchoolAIService() if os.getenv('OPENAI_API_KEY') else None