#!/usr/bin/env python3
"""
1단계 선택지 개수 테스트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_step1_single_choice():
    """1단계에서 1개만 선택하는 테스트"""
    print("🧪 1단계 단일 선택 테스트")
    
    # 세션 시작
    start_resp = requests.post(f"{BASE_URL}/career/start").json()
    session_id = start_resp["data"]["session_id"]
    print(f"✅ 세션 ID: {session_id}")
    
    # 0단계 완료
    step0_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2}
    }).json()
    print(f"✅ 0단계 완료")
    
    # 1단계 - 1개만 선택
    print("\n--- 1단계: 1개 선택 테스트 ---")
    step1_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {"choice_numbers": [1]}  # 스토리 기획만 선택
    })
    
    print(f"📤 요청: 1개 선택 [1]")
    print(f"📥 응답 상태: {step1_resp.status_code}")
    
    if step1_resp.status_code == 200:
        data = step1_resp.json()
        print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if data.get("success"):
            print("✅ 1개 선택 성공!")
        else:
            print(f"❌ 1개 선택 실패: {data.get('message')}")
    else:
        print(f"❌ HTTP 오류: {step1_resp.text}")

def test_step1_double_choice():
    """1단계에서 2개 선택하는 테스트 (정상 케이스)"""
    print("\n🧪 1단계 다중 선택 테스트 (정상)")
    
    # 새 세션
    start_resp = requests.post(f"{BASE_URL}/career/start").json()
    session_id = start_resp["data"]["session_id"]
    
    # 0단계 완료
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트2", "grade": 1}
    })
    
    # 1단계 - 2개 선택
    print("\n--- 1단계: 2개 선택 테스트 ---")
    step1_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트2", "grade": 1},
        "response": {"choice_numbers": [1, 5]}  # 스토리 기획, 코딩
    })
    
    print(f"📤 요청: 2개 선택 [1, 5]")
    print(f"📥 응답 상태: {step1_resp.status_code}")
    
    if step1_resp.status_code == 200:
        data = step1_resp.json()
        if data.get("success"):
            print("✅ 2개 선택 성공!")
        else:
            print(f"❌ 2개 선택 실패: {data.get('message')}")
    else:
        print(f"❌ HTTP 오류: {step1_resp.text}")

def test_step1_triple_choice():
    """1단계에서 3개 선택하는 테스트 (오류 케이스)"""
    print("\n🧪 1단계 3개 선택 테스트 (오류 예상)")
    
    # 새 세션
    start_resp = requests.post(f"{BASE_URL}/career/start").json()
    session_id = start_resp["data"]["session_id"]
    
    # 0단계 완료
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트3", "grade": 3}
    })
    
    # 1단계 - 3개 선택 (제한 초과)
    print("\n--- 1단계: 3개 선택 테스트 (제한 초과) ---")
    step1_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트3", "grade": 3},
        "response": {"choice_numbers": [1, 5, 7]}  # 3개 선택
    })
    
    print(f"📤 요청: 3개 선택 [1, 5, 7]")
    print(f"📥 응답 상태: {step1_resp.status_code}")
    
    if step1_resp.status_code == 200:
        data = step1_resp.json()
        if data.get("success"):
            print("⚠️ 3개 선택이 성공했습니다 (예상과 다름)")
        else:
            print(f"✅ 3개 선택 거부됨: {data.get('message')}")
    else:
        print(f"✅ HTTP 오류로 거부됨: {step1_resp.text}")

def check_validation_logic():
    """유효성 검증 로직 확인"""
    print("\n🧪 모델 유효성 검증 로직 확인")
    
    try:
        from models import StepResponse, CareerStage
        
        # 1개 선택 테스트
        response1 = StepResponse(choice_numbers=[1], custom_answer=None)
        valid1 = response1.validate_response(CareerStage.STEP_1)
        print(f"1개 선택 유효성: {valid1}")
        
        # 2개 선택 테스트
        response2 = StepResponse(choice_numbers=[1, 5], custom_answer=None)
        valid2 = response2.validate_response(CareerStage.STEP_1)
        print(f"2개 선택 유효성: {valid2}")
        
        # 3개 선택 테스트
        response3 = StepResponse(choice_numbers=[1, 5, 7], custom_answer=None)
        valid3 = response3.validate_response(CareerStage.STEP_1)
        print(f"3개 선택 유효성: {valid3}")
        
    except Exception as e:
        print(f"❌ 모델 검증 테스트 실패: {e}")

def main():
    print("="*60)
    print(" 🧪 1단계 선택지 개수 테스트")
    print("="*60)
    print("📋 1단계는 '최대 2개까지' 선택 가능한 다중선택입니다")
    print("🎯 1개 선택도 허용되는지 확인해봅시다")
    
    # 서버 연결 확인
    try:
        resp = requests.get(BASE_URL, timeout=5)
        print(f"✅ 서버 연결 성공 (상태: {resp.status_code})")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 모델 유효성 검증 로직 확인
    check_validation_logic()
    
    # 1개 선택 테스트
    test_step1_single_choice()
    
    # 2개 선택 테스트 (정상)
    test_step1_double_choice()
    
    # 3개 선택 테스트 (오류)
    test_step1_triple_choice()
    
    print("\n" + "="*60)
    print(" 🎉 테스트 완료")
    print("="*60)
    print("📊 결과 요약:")
    print("   - 1개 선택: 허용되는지 확인")
    print("   - 2개 선택: 정상 허용 (설계대로)")
    print("   - 3개 선택: 거부되어야 함 (제한 초과)")

if __name__ == "__main__":
    main()