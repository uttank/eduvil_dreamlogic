# FastAPI 기본 형을 작성해 주세요. 가장 기본이 되는 app 와 '/' url 애 대한 사항만 적용함
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
# openai 의 OpenAI API를 사용하기 위한 라이브러리 import
from openai import OpenAI
# python-dotenv를 사용하여 환경변수 로드
from dotenv import load_dotenv
import os
from datetime import datetime


# OpenAI API 키 설정
load_dotenv()
_key = os.getenv("OPENAI_API_KEY")
#openai.api_key = _key
client = OpenAI(api_key=_key) # Or it will pick from environment variable

app = FastAPI()
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)
# 정적 파일(static) 경로 등록
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def index():
    return RedirectResponse(url="/career/flow")

# 진로 탐색을 위한 career 목록을 저장하기 위한 데이터 구조
# 진로 탐색 1단계 원하는 직업선택

# 파이썬 리스트 형식의 자료구조 를 사용하여 career 목록을 저장
# 진로 가치 탐색 2단계 프롬프트와 선택지를 리스트 구조로 정의
career_value_prompt = "2단계 왜 이 {career} 을 희망하나요? (복수 선택 가능)"
career_value_choices = [
    {"id": 1, "label": "경제적 가치", "description": "높은 수입, 안정적인 직업"},
    {"id": 2, "label": "사회적 가치", "description": "사회에 긍정적인 영향, 봉사"},
    {"id": 3, "label": "공동체적 가치", "description": "사람들과 협력, 소통"},
    {"id": 4, "label": "능력 발휘", "description": "나의 재능과 역량을 최대한 발휘"},
    {"id": 5, "label": "자율·창의성", "description": "독립적으로 일하고 새로운 아이디어 창출"},
    {"id": 6, "label": "미래 비전", "description": "성장 가능성, 혁신적인 분야"},
]

# 진로 가치 탐색 3단계 프롬프트 정의 (선택지는 예시로만 주석에 명시, 실제로는 매번 생성)
career_issue_prompt = (
    """
    3단계.
    당신이 선택한 '{career}' 직업과 관련된 최신 이슈 또는 해결 과제 중 가장 관심 있는 것은 5가지 제시해 주세요.
    # 예시: 기후 위기에 대응하는 지속 가능한 건축 기술 부족, 고령화 사회의 돌봄 시스템 개선, 인공지능 윤리 문제 해결,
    # 디지털 격차 해소 방안, 문화 콘텐츠의 글로벌 경쟁력 강화
    """
)
# 실제 선택지는 OpenAI API를 통해 career에 따라 동적으로 생성

# 진로 가치 탐색 4단계 프롬프트 정의 (선택지는 예시로만 주석에 명시, 실제로는 매번 생성)
career_topic_prompt = (
    """
    4단계.
    앞서 선택한 '{career}' 직업과 관련된 이슈 중 '{issue}' 이슈에 대해 
    선택된 문제에 대해 구체적으로 탐구 가능한 주제 5가지 제시해주세요.
    # 기술/정책/심리/교육/데이터 분석 등 다양한 방법론 제시
    # 중복 없이 새로운 시선 강조
    """
)

# 진로 가치 탐색 5단계 프롬프트 정의 (선택지는 예시로만 주석에 명시, 실제로는 매번 생성)
career_goal_prompt = (
    """
    5단계.
    지금까지 선택한 직업: '{career}', 이유: {reasons}, 이슈: '{issue}', 탐구 주제: '{topic}'를 바탕으로
    사용자에게 진로 목표를 한 문장으로 제시해 주세요.
    {reasons} 에서 선택한 값을 참고해서 가치관이 잘 드러나도록 구체적으로 표현해 주세요.
    # 예시: '기후 위기 대응을 위한 친환경 건축 시스템을 설계하여 지속가능한 미래 주거 형태를 실현하는 것
    """
)

# 진로 가치 탐색 6단계 프롬프트 정의 (선택지는 예시로만 주석에 명시, 실제로는 매번 생성)
career_midgoal_prompt = (
    """
    6단계.
    지금까지 선택한 직업: '{career}', 이유: {reasons}, 이슈: '{issue}', 탐구 주제: '{topic}', 최종 목표: '{goal}'을(를) 바탕으로
    최종 목표를 실현하기 위해 고등학생 수준에서 길러야 할 핵심 역량 기반 중간 목표 3개를 제시해 주세요
    
    [1] 학업역량을 포함하는 내용으로 제시
    [2] 진로역량를 포함하는 내용으로 제시
    [3] 공동체역량를 포함하는 내용으로 제시
    # 예시: 친환경 기술 역량 강화 / 설계 능력 향상 / 공동체적 실천의식 함양
    """
)

# 진로 가치 탐색 7단계 프롬프트 정의 (최종 통합 정리)
career_final_summary_prompt = (
    """
    7단계.
    지금까지 선택한 직업: '{career}', 이유: {reasons}, 이슈: '{issue}', 탐구 주제: '{topic}',
    최종 목표: '{goal}', 중간 목표: {midgoals}, 을(를) 바탕으로 아래 형식으로 모든 내용을 통합하여 정리해 주세요.
    최종목표, 중간목표, 실천활동에만 이모지를 사용해서 시각적으로 매력적이고 읽기 쉽게 만들어주세요.
    제한조건은 결과에 표시하지 말고 내부적으로만 참고하세요:
    아래는 건축가를 희망하는 고등학생의 진로 탐색 결과 예시입니다.
    
    # 예시:
        🎯 [최종 목표(꿈)] 기후 위기 대응을 위한 친환경 건축 시스템 설계하여 지속가능한 미래 주거 형태를 실현하는 건축가

        📚 [중간목표1] 친환경 건축 기술 역량
        🔬 실천활동1:
                    탐구보고서: "제로에너지 건축 기술의 실제 적용 사례 분석" 등
                    고1 교과 활동: 공통 과학 - '에너지 전환' 단원 [심화]
                    고1 비교과: 에너지 창의 설계 캠프 참가 - [문제 해결력 성장과 관련]
        🔬 실천활동2:
                    탐구보고서:
                    고2 교과 활동: 생명
                    고2 비교과:
        🔬 실천활동3:
                    탐구보고서:  
                    고3 교과 활동: 유전자와~~
                    고3 비교과:  
        
        🎨 [중간목표2] 설계 능력 향상
        🔬 실천활동1:
                    탐구보고서: "건축 설계의 기초와 실제" 등
                    고1 교과 활동: 공통 기술 - '기초 설계 원리'
                    고1 비교과: 건축 설계 워크숍 참가 - [창의적 문제 해결력 성장과 관련]
        🔬 실천활동2:
                    탐구보고서: "건축 설계의 기초와 실제" 등
                    고2 교과 활동: 공통 기술 - '고급 설계 기법'
                    고2 비교과: 건축 설계 경진대회 참가 - [창의적 문제 해결력 성장과 관련]
        🔬 실천활동3:
                    탐구보고서: "건축 설계의 기초와 실제" 등
                    고3 교과 활동: 공통 기술 - '건축 설계 프로젝트'
                    고3 비교과: 건축 설계 프로젝트 발표회 참가 - [창의적 문제 해결력 성장과 관련]
        
        🤝 [중간목표3] 공동체적 실천의식 함양
        🔬 실천활동1:
        
        제한 조건 (결과에 표시하지 말고 내부적으로만 참고):
        1. 학년별 교과 활동의 경우 '2022 교육개편중 고등학교 교육과정' 반영하여 활동 제시
        2. 학교외에 대회나 공모전은 언급하지 않기. 학교에서 이루어질 수 있는 활동으로만 실천활동 제시하기
        3. 자소서 등은 언급하지 않기
        4. 고등학생 수준에서 이해 할 수 있는 탐구활동 주제 제시
            "각 항목은 실제 입력값에 맞게 구체적으로 작성해 주세요."
    """
)



@app.get("/career/flow", response_class=HTMLResponse)
async def career_flow_get(request: Request):
    now = datetime.now().timestamp()
    return templates.TemplateResponse("career_flow_allinone.html", {"request": request, "step": 1, "start_time": now, "step_start_time": now})

@app.post("/career/flow", response_class=HTMLResponse)
async def career_flow_post(
    request: Request,
    step: int = Form(1),
    career: Optional[str] = Form(None),
    reasons: Optional[List[str]] = Form(None),
    issue: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    goal: Optional[str] = Form(None),
    midgoals: Optional[List[str]] = Form(None),
    midgoal_details: Optional[str] = Form(None),
    practices: Optional[str] = Form(None),
    start_time: Optional[float] = Form(None),
    step_start_time: Optional[float] = Form(None),
):
    now = datetime.now().timestamp()
    context = {"request": request, "step": step}
    # start_time 관리
    if not start_time:
        start_time = now
    context["start_time"] = start_time
    # step_start_time 관리 (단계별 소요 시간 삭제, current_step_time도 삭제)
    if not step_start_time:
        step_start_time = now
    context["step_start_time"] = step_start_time
    chatbot_message = None
    # 1단계: 직업 입력
    if step == 1:
        if not career:
            context.update({"error": "직업을 입력하세요."})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        choices = career_value_choices
        chatbot_message = f"'{career}'(을)를 선택하셨군요. 이 직업을 선택한 이유를 알려주세요!"
        context.update({"step": 2, "career": career, "choices": choices, "chatbot_message": chatbot_message})
        return templates.TemplateResponse("career_flow_allinone.html", context)
    # 2단계: 이유 복수 선택
    elif step == 2:
        if not (career and reasons):
            context.update({"step": 2, "career": career, "choices": career_value_choices, "error": "이유를 한 가지 이상 선택하세요."})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        chatbot_message = f"{', '.join(reasons)}(을)를 선택하셨군요. 이제 {career}와 관련된 최신 이슈를 골라볼까요?"
        # 3단계로 이동 (OpenAI API로 이슈 생성)
        issues = call_gpt_list(
            prompt=career_issue_prompt.format(career=career),
            system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자가 선택한 직업과 관련된 최신 이슈나 해결 과제 5가지를 한국어로 간결하게 제시해줘.",
            max_tokens=1000,
            fallback=["이슈를 불러오지 못했습니다."],
            strip_chars='-• '
        )
        context.update({"step": 3, "career": career, "reasons": reasons, "issues": issues, "chatbot_message": chatbot_message})
        return templates.TemplateResponse("career_flow_allinone.html", context)
    # 3단계: 이슈 선택
    elif step == 3:
        form = await request.form()
        regenerate = form.get("regenerate")
        # 다중 선택 지원: issues는 리스트
        issues_selected = [str(x) for x in form.getlist("issues")]
        # '다시 생성' 버튼 처리
        if regenerate == "yes":
            issues = call_gpt_list(
                prompt=career_issue_prompt.format(career=career),
                system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자가 선택한 직업과 관련된 최신 이슈나 해결 과제 5가지를 한국어로 간결하게 제시해줘.",
                max_tokens=1000,
                fallback=["이슈를 불러오지 못했습니다."],
                strip_chars='-• '
            )
            chatbot_message = f"이슈를 새로 제안합니다. 원하는 이슈를 모두 선택하세요."
            context.update({"step": 3, "career": career, "reasons": reasons, "issues": issues, "chatbot_message": chatbot_message, "issues_selected": []})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        if not (career and reasons and issues_selected):
            context.update({"step": 3, "career": career, "reasons": reasons, "issues": context.get("issues", []), "error": "이슈를 한 가지 이상 선택하세요.", "issues_selected": issues_selected})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        chatbot_message = f"{', '.join(issues_selected)}(을)를 선택하셨군요. 이 이슈들에 대해 탐구하고 싶은 주제를 골라주세요!"
        # 4단계로 이동 (OpenAI API로 탐구 주제 생성, 첫 번째 이슈만 사용)
        topics = call_gpt_list(
            prompt=career_topic_prompt.format(career=career, issue=issues_selected[0]),
            system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자가 선택한 이슈에 대해 구체적으로 탐구 가능한 주제 3가지를 한국어로 간결하게 제시해줘.",
            max_tokens=1000,
            fallback=["주제를 불러오지 못했습니다."],
            strip_chars='-•[]1234567890. '
        )
        context.update({"step": 4, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topics": topics, "chatbot_message": chatbot_message})
        return templates.TemplateResponse("career_flow_allinone.html", context)
    # 4단계: 탐구 주제 선택
    elif step == 4:
        form = await request.form()
        regenerate = form.get("regenerate")
        topic = form.get("topic") # type: ignore
        # issues_selected를 hidden input에서 받아옴
        issues_selected = form.getlist("issues_selected")
        
        # '다시 생성' 버튼 처리
        if regenerate == "yes":
            topics = call_gpt_list(
                prompt=career_topic_prompt.format(career=career, issue=issues_selected[0]),
                system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자가 선택한 이슈에 대해 구체적으로 탐구 가능한 주제 3가지를 한국어로 간결하게 제시해줘.",
                max_tokens=1000,
                fallback=["주제를 불러오지 못했습니다."],
                strip_chars='-•[]1234567890. '
            )
            chatbot_message = f"주제를 새로 제안합니다. 원하는 주제를 선택하세요."
            context.update({"step": 4, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topics": topics, "chatbot_message": chatbot_message})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        
        # 주제 선택 검증 (재생성이 아닌 경우에만)
        if not (career and reasons and issues_selected):
            context.update({"step": 4, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topics": ["주제를 불러오지 못했습니다."], "error": "이전 단계 정보가 누락되었습니다."})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        
        if not topic:
            # 주제가 선택되지 않은 경우, 기본 topics 생성
            topics = call_gpt_list(
                prompt=career_topic_prompt.format(career=career, issue=issues_selected[0]),
                system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자가 선택한 이슈에 대해 구체적으로 탐구 가능한 주제 3가지를 한국어로 간결하게 제시해줘.",
                max_tokens=1000,
                fallback=["주제를 불러오지 못했습니다."],
                strip_chars='-•[]1234567890. '
            )
            context.update({"step": 4, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topics": topics, "error": "주제를 선택하세요."})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        # 5단계: GPT가 제시하는 진로 목표
        suggested_goal = call_gpt_list(
            prompt=career_goal_prompt.format(career=career, reasons=reasons, issue=issues_selected[0], topic=topic),
            system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자의 선택을 바탕으로 적절한 진로 목표를 한 문장으로 제시해줘.",
            max_tokens=100,
            fallback=["진로 목표를 불러오지 못했습니다."],
            strip_chars=''  # 한 문장만 반환
        )[0]
        chatbot_message = f"아래와 같은 진로 목표를 제안합니다. 마음에 들지 않으면 '다시 생성'을 눌러주세요."
        context.update({"step": 5, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topic": topic, "suggested_goal": suggested_goal, "chatbot_message": chatbot_message})
        return templates.TemplateResponse("career_flow_allinone.html", context)
    # 5단계: 진로 목표 확인 및 재생성
    elif step == 5:
        form = await request.form()
        suggested_goal = form.get("suggested_goal")
        regenerate = form.get("regenerate")
        issues_selected = form.getlist("issues_selected")
        if regenerate == "yes":
            # 목표 재생성
            suggested_goal = call_gpt_list(
                prompt=career_goal_prompt.format(career=career, reasons=reasons, issue=issues_selected[0], topic=topic),
                system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자의 선택을 바탕으로 적절한 진로 목표를 한 문장으로 제시해줘.",
                max_tokens=100,
                fallback=["진로 목표를 불러오지 못했습니다."],
                strip_chars=''
            )[0]
            chatbot_message = "아래와 같이 새롭게 진로 목표를 제안합니다. 마음에 들지 않으면 다시 생성할 수 있습니다."
            context.update({"step": 5, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topic": topic, "suggested_goal": suggested_goal, "chatbot_message": chatbot_message})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        # 사용자가 목표를 수락
        goal = str(suggested_goal) if suggested_goal is not None else None
        chatbot_message = f"'{goal}'(을)를 목표로 하셨군요. 이제 중간 목표 3가지를 제시해드릴게요."
        # 6단계로 이동 (OpenAI API로 중간 목표 생성)
        midgoals = call_gpt_list(
            prompt=career_midgoal_prompt.format(career=career, reasons=reasons, issue=issues_selected[0], topic=topic, goal=goal),
            system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자의 최종 목표를 실현하기 위한 중간 목표 3가지를 한국어로 간결하게 제시해줘.",
            max_tokens=1000,
            fallback=["중간 목표를 불러오지 못했습니다."],
            strip_chars='-•[]1234567890. '
        )
        context.update({"step": 6, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topic": topic, "goal": goal, "midgoals": midgoals, "chatbot_message": chatbot_message})
        return templates.TemplateResponse("career_flow_allinone.html", context)
    # 6단계: 중간 목표 제시 및 재생성 (선택 아님, 제시만)
    elif step == 6:
        form = await request.form()
        regenerate = form.get("regenerate")
        issues_selected = form.getlist("issues_selected")
        # 재생성 요청 시 midgoals 새로 생성
        if regenerate == "yes":
            midgoals = call_gpt_list(
                prompt=career_midgoal_prompt.format(career=career, reasons=reasons, issue=issues_selected[0], topic=topic, goal=goal),
                system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자의 최종 목표를 실현하기 위한 중간 목표 3가지를 한국어로 간결하게 제시해줘.",
                max_tokens=1000,
                fallback=["중간 목표를 불러오지 못했습니다."],
                strip_chars='-•[]1234567890. '
            )
            chatbot_message = "아래와 같이 새롭게 중간 목표를 제안합니다. 마음에 들지 않으면 다시 생성할 수 있습니다."
            context.update({"step": 6, "career": career, "reasons": reasons, "issues_selected": issues_selected, "topic": topic, "goal": goal, "midgoals": midgoals, "chatbot_message": chatbot_message})
            return templates.TemplateResponse("career_flow_allinone.html", context)
        
        # "다음" 버튼을 누르면 7단계로 이동
        chatbot_message = "드림로직이 모두 완료되었습니다! 아래는 당신의 진로 탐색 결과입니다."
        # 최종 요약 생성
        final_summary_text = call_gpt_list(
            prompt=career_final_summary_prompt.format(
                career=career, 
                reasons=reasons, 
                issue=issues_selected[0] if issues_selected else "", 
                topic=topic, 
                goal=goal, 
                midgoals=midgoals
            ),
            system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자의 진로 탐색 결과를 종합하여 체계적으로 정리해줘. 최종목표, 중간목표, 실천활동에만 이모지를 사용하고, 제한조건은 결과에 표시하지 말고 내부적으로만 참고해서 작성해줘.",
            max_tokens=2000,
            fallback=["최종 요약을 불러오지 못했습니다."],
            strip_chars=''
        )
        final_summary = '\n'.join(final_summary_text) if final_summary_text else "최종 요약을 불러오지 못했습니다."
        
        context.update({
            "step": 7, 
            "career": career, 
            "reasons": reasons, 
            "issues_selected": issues_selected, 
            "topic": topic, 
            "goal": goal, 
            "midgoals": midgoals,
            "final_summary": final_summary,
            "chatbot_message": chatbot_message
        })
        return templates.TemplateResponse("career_flow_allinone.html", context)
        
    # 7단계: 최종 통합 요약 재생성
    elif step == 7:
        form = await request.form()
        regenerate = form.get("regenerate")
        issues_selected = form.getlist("issues_selected")
        
        # 재생성 요청 시에만 처리
        if regenerate == "yes":
            # 최종 요약 재생성
            final_summary_text = call_gpt_list(
                prompt=career_final_summary_prompt.format(
                    career=career, 
                    reasons=reasons, 
                    issue=issues_selected[0] if issues_selected else "", 
                    topic=topic, 
                    goal=goal, 
                    midgoals=midgoals
                ),
                system_message="너는 진로 탐색을 돕는 어시스턴트야. 사용자의 진로 탐색 결과를 종합하여 체계적으로 정리해줘. 최종목표, 중간목표, 실천활동에만 이모지를 사용하고, 제한조건은 결과에 표시하지 말고 내부적으로만 참고해서 작성해줘.",
                max_tokens=2000,
                fallback=["최종 요약을 불러오지 못했습니다."],
                strip_chars=''
            )
            final_summary = '\n'.join(final_summary_text) if final_summary_text else "최종 요약을 불러오지 못했습니다."
            
            chatbot_message = "아래와 같이 새롭게 최종 요약을 제안합니다."
            context.update({
                "step": 7, 
                "career": career, 
                "reasons": reasons, 
                "issues_selected": issues_selected, 
                "topic": topic, 
                "goal": goal, 
                "midgoals": midgoals,
                "final_summary": final_summary,
                "chatbot_message": chatbot_message
            })
            return templates.TemplateResponse("career_flow_allinone.html", context)

def call_gpt_list(prompt, system_message, max_tokens=1000, fallback=None, strip_chars='-•[]1234567890. '):
    """
    GPT-4 Turbo로 리스트 형태의 응답을 받아 파싱하는 헬퍼 함수
    """
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens
        )
        content = chat_completion.choices[0].message.content or ""
        lines = content.split('\n')
        
        # 설명 문장 제거: 콜론(:)이 포함된 첫 번째 줄들은 제외
        items = []
        for line in lines:
            line = line.strip()
            if not line:  # 빈 줄 건너뛰기
                continue
            # 설명 문장 패턴 제거 (콜론이 포함되고 "가지", "입니다", "다음과 같습니다" 등이 포함된 경우)
            if ':' in line and any(word in line for word in ['가지', '입니다', '다음과 같습니다', '제시', '관련된']):
                continue
            # strip_chars로 불필요한 문자 제거
            cleaned_line = line.strip(strip_chars).strip()
            if cleaned_line:  # 정리된 후에도 내용이 있으면 추가
                items.append(cleaned_line)
        
        if not items and fallback:
            items = fallback
        return items
    except Exception as e:
        return [f"에러: {str(e)}"] + (fallback if fallback else [])

