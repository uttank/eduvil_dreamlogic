"""
간단한 기타 답변 테스트 스크립트
"""

from models import CareerStage
from openai_service import CareerRecommendationService

def test_other_responses():
    """기타 답변 테스트"""
    
    # 축구 관련 테스트
    soccer_responses = {
        CareerStage.STEP_1: {
            "choice_numbers": [11],
            "custom_answer": "축구 경기 보고 전술 분석하기"
        },
        CareerStage.STEP_2: {
            "choice_numbers": [11],
            "custom_answer": "팀원들과 협력해서 승리 전략 세우기"
        },
        CareerStage.STEP_3: {
            "choice_numbers": [11],
            "custom_answer": "축구로 사람들을 하나로 만들 때"
        },
        CareerStage.STEP_4: {
            "choice_numbers": [11],
            "custom_answer": "스포츠를 통한 사회 통합과 건강 증진"
        }
    }
    
    # 수학 관련 테스트
    math_responses = {
        CareerStage.STEP_1: {
            "choice_numbers": [11],
            "custom_answer": "복잡한 수학 문제를 단계별로 풀어나가기"
        },
        CareerStage.STEP_2: {
            "choice_numbers": [11],
            "custom_answer": "논리적으로 문제를 분석하고 해결책 찾기"
        },
        CareerStage.STEP_3: {
            "choice_numbers": [11],
            "custom_answer": "수학으로 실생활 문제를 해결할 때"
        },
        CareerStage.STEP_4: {
            "choice_numbers": [11],
            "custom_answer": "AI와 빅데이터로 인한 수학적 사고의 중요성"
        }
    }
    
    # 게임 관련 테스트
    game_responses = {
        CareerStage.STEP_1: {
            "choice_numbers": [11],
            "custom_answer": "게임 스토리 만들고 캐릭터 디자인하기"
        },
        CareerStage.STEP_2: {
            "choice_numbers": [11],
            "custom_answer": "상상을 현실로 만드는 창의적 아이디어"
        },
        CareerStage.STEP_3: {
            "choice_numbers": [11],
            "custom_answer": "게임으로 사람들에게 즐거움을 줄 때"
        },
        CareerStage.STEP_4: {
            "choice_numbers": [11],
            "custom_answer": "게임 중독과 건전한 게임 문화 만들기"
        }
    }
    
    try:
        service = CareerRecommendationService()
        
        test_cases = [
            ("축구_테스트", soccer_responses),
            ("수학_테스트", math_responses), 
            ("게임_테스트", game_responses)
        ]
        
        print("🧪 기타 답변 진로 추천 테스트")
        print("=" * 60)
        
        for test_name, responses in test_cases:
            print(f"\n🎯 {test_name}:")
            print("-" * 30)
            
            # 응답 데이터 확인
            formatted = service._format_responses_for_ai(test_name, responses)
            print("📋 전송되는 데이터:")
            print(formatted)
            
            # 추천 결과
            recommendation = service.generate_career_recommendation(
                student_name=test_name,
                responses=responses
            )
            print(f"💡 추천 결과: {recommendation}")
            print("-" * 30)
    
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_other_responses()