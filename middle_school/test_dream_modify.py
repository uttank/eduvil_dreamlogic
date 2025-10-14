#!/usr/bin/env python3
"""
5단계 수정 기능 전체 테스트
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dream_modify():
    print("🎯 5단계 수정 기능 테스트 시작")
    
    # 1. 세션 생성
    print("\n1️⃣ 세션 생성")
    create_response = requests.post(f"{BASE_URL}/career/start")
    print(f"세션 생성 응답 상태: {create_response.status_code}")
    print(f"세션 생성 응답 내용: {create_response.text}")
    
    if create_response.status_code != 200:
        print(f"❌ 세션 생성 실패")
        return False
        
    session_data = create_response.json()
    if "data" not in session_data or "session_id" not in session_data["data"]:
        print(f"❌ 응답에 session_id가 없습니다: {session_data}")
        return False
        
    session_id = session_data["data"]["session_id"]
    print(f"✅ 세션 생성됨: {session_id}")
    
    # 2. 학생 정보 제출
    print("\n2️⃣ 학생 정보 제출")
    student_info = {
        "name": "테스트학생",
        "grade": 2
    }
    
    student_info_request = {
        "session_id": session_id,
        "student_info": student_info,
        "response": {
            "choice_numbers": [],
            "custom_answer": f"안녕하세요! 저는 {student_info['name']}이고 {student_info['grade']}학년이에요."
        }
    }
    
    info_response = requests.post(
        f"{BASE_URL}/career/{session_id}/submit",
        json=student_info_request
    )
    
    if info_response.status_code == 200:
        print(f"✅ 학생 정보 제출 완료")
    else:
        print(f"❌ 학생 정보 제출 실패: {info_response.status_code}")
        print(f"응답: {info_response.text}")
        return False
    
    # 3. 1-4단계 진행
    stages_data = {
        "STEP_1": {
            "choice_numbers": [1],
            "custom_answer": ""
        },
        "STEP_2": {
            "choice_numbers": [2],
            "custom_answer": ""
        },
        "STEP_3": {
            "choice_numbers": [1],
            "custom_answer": ""
        },
        "STEP_4": {
            "choice_numbers": [3],
            "custom_answer": ""
        }
    }
    
    for stage, responses in stages_data.items():
        print(f"\n3️⃣ {stage} 진행")
        stage_request = {
            "session_id": session_id,
            "response": responses
        }
        
        stage_response = requests.post(
            f"{BASE_URL}/career/{session_id}/submit",
            json=stage_request
        )
        if stage_response.status_code == 200:
            print(f"✅ {stage} 완료")
        else:
            print(f"❌ {stage} 실패: {stage_response.status_code}")
            print(f"응답: {stage_response.text}")
            return False
    
    # 4. 5단계 AI 추천 받기
    print("\n4️⃣ 5단계 AI 추천 생성")
    recommendation_response = requests.post(
        f"{BASE_URL}/career/{session_id}/recommend",
        json={"regenerate": False}
    )
    
    if recommendation_response.status_code == 200:
        recommendation_data = recommendation_response.json()
        print(f"✅ AI 추천 생성 완료")
        print(f"추천: {recommendation_data['data']['career_recommendation']}")
        
        # 4.5. 5단계 추천 수락 (꿈 확정)
        print("\n4️⃣.5 추천 수락 (꿈 확정)")
        accept_response = requests.post(
            f"{BASE_URL}/career/{session_id}/submit",
            json={
                "session_id": session_id,
                "career_response": {
                    "recommendation_accepted": True,
                    "modification_request": None
                }
            }
        )
        
        if accept_response.status_code == 200:
            print(f"✅ 추천 수락 완료 (꿈 확정됨)")
        else:
            print(f"❌ 추천 수락 실패: {accept_response.status_code}")
            print(f"응답: {accept_response.text}")
        
        # 5. 5단계 수정 테스트 (드림로직 생성)
        print("\n5️⃣ 드림로직 생성 테스트")
        modify_response = requests.post(
            f"{BASE_URL}/api/middle-school/dream-confirm?regenerate=true",
            json={
                "session_id": session_id
            }
        )
        
        if modify_response.status_code == 200:
            modify_data = modify_response.json()
            print(f"✅ 꿈 수정 성공!")
            print(f"새로운 추천: {modify_data['data']['career_recommendation']}")
            return True
        else:
            print(f"❌ 꿈 수정 실패: {modify_response.status_code}")
            print(f"응답: {modify_response.text}")
            return False
    else:
        print(f"❌ AI 추천 생성 실패: {recommendation_response.status_code}")
        print(f"응답: {recommendation_response.text}")
        return False

def main():
    try:
        # 서버 연결 확인
        health_response = requests.get(f"{BASE_URL}/")
        if health_response.status_code != 200:
            print(f"❌ 서버 연결 실패: {BASE_URL}")
            return
        
        success = test_dream_modify()
        
        if success:
            print("\n🎉 5단계 수정 기능 테스트 성공!")
        else:
            print("\n💥 5단계 수정 기능 테스트 실패")
            
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {str(e)}")

if __name__ == "__main__":
    main()