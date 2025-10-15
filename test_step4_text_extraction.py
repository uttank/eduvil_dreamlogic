#!/usr/bin/env python3
"""
Step 4 텍스트 추출 테스트
"""

import sys
sys.path.append('.')

from elementary_school.models import CareerStage, STAGE_QUESTIONS
from elementary_school.openai_service import CareerRecommendationService

def test_text_extraction():
    """텍스트 추출 테스트"""
    print("🧪 Step 4 텍스트 추출 테스트 시작")
    
    # 테스트용 응답 데이터
    test_responses = {
        CareerStage.STEP_1: {
            "choice_numbers": [1, 3],
            "custom_answer": None
        },
        CareerStage.STEP_2: {
            "choice_numbers": [2, 5],
            "custom_answer": None
        },
        CareerStage.STEP_3: {
            "choice_numbers": [2],
            "custom_answer": None
        }
    }
    
    # 예상 결과 출력
    print("\n📋 STAGE_QUESTIONS 확인:")
    for stage in [CareerStage.STEP_1, CareerStage.STEP_2, CareerStage.STEP_3]:
        stage_data = STAGE_QUESTIONS.get(stage)
        if stage_data:
            print(f"\n{stage}:")
            print(f"  질문: {stage_data['question']}")
            print(f"  선택지:")
            for i, choice in enumerate(stage_data['choices'], 1):
                print(f"    {i}. {choice}")
    
    print("\n🔍 응답 데이터 분석:")
    
    try:
        # CareerRecommendationService 인스턴스가 없을 수 있으므로 직접 메서드 테스트
        from elementary_school.openai_service import ai_service
        
        if ai_service:
            for stage, response_data in test_responses.items():
                extracted_text = ai_service._extract_choices_text_with_stage(response_data, stage)
                choice_nums = response_data.get('choice_numbers', [])
                print(f"\n{stage}:")
                print(f"  선택 번호: {choice_nums}")
                print(f"  추출된 텍스트: {extracted_text}")
        else:
            print("❌ AI 서비스가 초기화되지 않았습니다.")
            
            # 수동으로 텍스트 추출 테스트
            print("\n🔧 수동 텍스트 추출 테스트:")
            
            for stage, response_data in test_responses.items():
                choice_numbers = response_data.get('choice_numbers', [])
                stage_data = STAGE_QUESTIONS.get(stage)
                
                if stage_data and 'choices' in stage_data:
                    choices = stage_data['choices']
                    selected_texts = []
                    
                    for choice_num in choice_numbers:
                        if 1 <= choice_num <= len(choices):
                            selected_texts.append(choices[choice_num - 1])
                        else:
                            selected_texts.append(f"선택지 {choice_num}")
                    
                    extracted_text = ", ".join(selected_texts)
                    print(f"\n{stage}:")
                    print(f"  선택 번호: {choice_numbers}")
                    print(f"  추출된 텍스트: {extracted_text}")
    
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_text_extraction()