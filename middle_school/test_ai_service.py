#!/usr/bin/env python3
"""
AI 서비스 상태 테스트
"""

import sys
import os
sys.path.append('/Users/yhpark/work/openai/career_dev/middle_school')

from openai_service import ai_service

def test_ai_service():
    print("=== AI 서비스 상태 테스트 ===")
    
    if ai_service is None:
        print("❌ ai_service가 None입니다")
        return False
    
    print(f"✅ ai_service 객체 존재: {type(ai_service)}")
    
    is_available = ai_service.is_available()
    print(f"📊 AI 서비스 사용 가능: {is_available}")
    
    if hasattr(ai_service, 'client'):
        print(f"🔗 OpenAI 클라이언트: {ai_service.client}")
    
    if hasattr(ai_service, 'api_key'):
        api_key_status = "설정됨" if ai_service.api_key else "설정되지 않음"
        print(f"🔑 API 키: {api_key_status}")
    
    # 간단한 추천 생성 테스트
    if is_available:
        print("\n=== 추천 생성 테스트 ===")
        test_responses = {
            "STEP_1": {"choice_numbers": [1], "custom_answer": ""},
            "STEP_2": {"choice_numbers": [2], "custom_answer": ""},
            "STEP_3": {"choice_numbers": [1], "custom_answer": ""},
            "STEP_4": {"choice_numbers": [3], "custom_answer": ""}
        }
        
        try:
            recommendation = ai_service.generate_middle_school_recommendation(
                "테스트학생", 
                test_responses, 
                regenerate=True
            )
            if recommendation:
                print(f"✅ 추천 생성 성공: {recommendation[:50]}...")
                return True
            else:
                print("❌ 추천 생성 결과가 None입니다")
                return False
        except Exception as e:
            print(f"❌ 추천 생성 오류: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
    else:
        print("⚠️ AI 서비스를 사용할 수 없어 추천 생성 테스트를 건너뜁니다")
        return False

if __name__ == "__main__":
    success = test_ai_service()
    exit(0 if success else 1)