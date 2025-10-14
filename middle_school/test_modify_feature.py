#!/usr/bin/env python3
"""
5단계 수정 기능 간단 테스트
LLM에서 새로운 추천을 받아오는지 확인
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_modify_feature():
    """5단계 수정 기능 테스트"""
    print("🧪 5단계 수정 기능 테스트 시작")
    
    try:
        # 1. 세션 시작
        print("\n1️⃣ 세션 시작...")
        response = requests.post(f"{BASE_URL}/career/start")
        data = response.json()
        
        if not data["success"]:
            print(f"❌ 세션 시작 실패: {data.get('message')}")
            return
        
        session_id = data["data"]["session_id"]
        print(f"✅ 세션 시작 성공: {session_id}")
        
        # 2. 0단계 - 학생 정보 입력
        print("\n2️⃣ 학생 정보 입력...")
        student_info = {"name": "테스트수정", "grade": 2}
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
            "session_id": session_id,
            "student_info": student_info
        })
        
        if not response.json()["success"]:
            print(f"❌ 학생 정보 입력 실패")
            return
        
        print("✅ 학생 정보 입력 성공")
        
        # 3. 1-4단계 빠르게 완료
        print("\n3️⃣ 1-4단계 빠르게 완료...")
        
        # 1단계: 흥미 (다중선택)
        requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
            "session_id": session_id,
            "student_info": student_info,
            "response": {"choice_numbers": [1, 5]}  # 스토리 기획, 코딩
        })
        
        # 2단계: 장점 (단일선택)
        requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
            "session_id": session_id,
            "student_info": student_info,
            "response": {"choice_numbers": [2]}  # 창의발상
        })
        
        # 3단계: 가치관 (단일선택)
        requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
            "session_id": session_id,
            "student_info": student_info,
            "response": {"choice_numbers": [3]}  # 어려운 문제 해결하며 성장
        })
        
        # 4단계: 미래 관심 (단일선택)
        requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
            "session_id": session_id,
            "student_info": student_info,
            "response": {"choice_numbers": [3]}  # AI·로봇과 사람의 협업·일자리
        })
        
        print("✅ 1-4단계 완료")
        
        # 4. 첫 번째 진로 추천 생성
        print("\n4️⃣ 첫 번째 진로 추천 생성...")
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={})
        data = response.json()
        
        if not data["success"]:
            print(f"❌ 첫 번째 추천 생성 실패: {data.get('message')}")
            return
        
        first_recommendation = data["data"]["career_recommendation"]
        print(f"✅ 첫 번째 추천: {first_recommendation}")
        
        # 5. 수정 요청 (새로운 추천 생성)
        print("\n5️⃣ 수정 요청으로 새로운 추천 생성...")
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/dream-confirm", json={
            "action": "modify"
        })
        data = response.json()
        
        if not data["success"]:
            print(f"❌ 수정 요청 실패: {data.get('message')}")
            return
        
        second_recommendation = data["data"]["career_recommendation"]
        print(f"✅ 두 번째 추천: {second_recommendation}")
        
        # 6. 추천 비교
        print("\n6️⃣ 추천 비교...")
        
        if first_recommendation != second_recommendation:
            print("🎉 SUCCESS: 수정 요청으로 다른 추천이 생성되었습니다!")
            print(f"📋 첫 번째: {first_recommendation}")
            print(f"📋 두 번째: {second_recommendation}")
        else:
            print("⚠️ WARNING: 수정 전후 추천이 동일합니다.")
            print("💡 이는 AI의 일관성 때문일 수 있으나, 일반적으로는 다른 추천이 나와야 합니다.")
        
        # 7. 여러 번 수정 테스트
        print("\n7️⃣ 추가 수정 테스트...")
        
        for i in range(3):
            response = requests.post(f"{BASE_URL}/career/{session_id}/dream-confirm", json={
                "action": "modify"
            })
            
            if response.json()["success"]:
                new_rec = response.json()["data"]["career_recommendation"]
                print(f"✅ {i+3}번째 추천: {new_rec[:50]}...")
            else:
                print(f"❌ {i+3}번째 수정 실패")
        
        print("\n🎉 5단계 수정 기능 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modify_feature()