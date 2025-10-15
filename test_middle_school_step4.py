"""
중학교 진로 탐색 4단계 동적 선택지 기능 테스트
"""

import requests
import json
import time

# 서버 URL
BASE_URL = "http://localhost:8000/middle_school"

def test_middle_school_step4_dynamic():
    """4단계 동적 선택지 생성 및 재생성 테스트"""
    print("🧪 중학교 진로 탐색 4단계 동적 선택지 테스트 시작")
    print("=" * 60)
    
    # 1. 세션 시작
    print("\n1️⃣ 세션 시작")
    response = requests.post(f"{BASE_URL}/career/start")
    if response.status_code != 200:
        print(f"❌ 세션 시작 실패: {response.status_code}")
        return
    
    data = response.json()
    session_id = data["data"]["session_id"]
    print(f"✅ 세션 생성 성공: {session_id}")
    
    # 2. 0단계 - 학생 정보 입력
    print("\n2️⃣ 0단계 - 학생 정보 입력")
    student_data = {
        "session_id": session_id,
        "student_info": {
            "name": "테스트학생",
            "grade": 2,
            "school": "테스트중학교"
        }
    }
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=student_data)
    if response.status_code == 200:
        print("✅ 학생 정보 입력 성공")
    else:
        print(f"❌ 학생 정보 입력 실패: {response.status_code} - {response.text}")
        return
    
    # 3. 1단계 - 흥미 탐색 (코딩, 게임 프로토타이핑)
    print("\n3️⃣ 1단계 - 흥미 탐색")
    step1_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [5],  # 코딩·게임/앱 프로토타이핑
            "custom_answer": ""
        }
    }
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=step1_data)
    if response.status_code == 200:
        print("✅ 1단계 응답 성공: 코딩·게임/앱 프로토타이핑")
    else:
        print(f"❌ 1단계 응답 실패: {response.status_code} - {response.text}")
        return
    
    # 4. 2단계 - 장점 탐색 (창의발상)
    print("\n4️⃣ 2단계 - 장점 탐색")
    step2_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [2],  # 창의발상(아이디어가 잘 떠오름)
            "custom_answer": ""
        }
    }
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=step2_data)
    if response.status_code == 200:
        print("✅ 2단계 응답 성공: 창의발상")
    else:
        print(f"❌ 2단계 응답 실패: {response.status_code} - {response.text}")
        return
    
    # 5. 3단계 - 가치관 탐색 (어려운 문제 해결)
    print("\n5️⃣ 3단계 - 가치관 탐색")
    step3_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [3],  # 어려운 문제를 해결하며 성장하기
            "custom_answer": ""
        }
    }
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=step3_data)
    if response.status_code == 200:
        print("✅ 3단계 응답 성공: 어려운 문제를 해결하며 성장하기")
    else:
        print(f"❌ 3단계 응답 실패: {response.status_code} - {response.text}")
        return
    
    # 6. 4단계 질문 조회 (동적 선택지 확인)
    print("\n6️⃣ 4단계 - 동적 선택지 조회")
    response = requests.get(f"{BASE_URL}/career/{session_id}/question")
    if response.status_code == 200:
        data = response.json()
        question_data = data["data"]
        print(f"✅ 4단계 질문: {question_data['question']}")
        
        if "dynamic_choices" in question_data and question_data["dynamic_choices"]:
            print("🎯 AI가 생성한 동적 선택지:")
            for i, choice in enumerate(question_data["dynamic_choices"], 1):
                print(f"   {i}. {choice}")
            
            print(f"재생성 가능 횟수: {question_data.get('regenerate_count', 0)}/{question_data.get('max_regenerate', 5)}")
            
            # 7. 4단계 재생성 테스트
            print("\n7️⃣ 4단계 - 선택지 재생성 테스트")
            response = requests.post(f"{BASE_URL}/career/{session_id}/regenerate-step4")
            if response.status_code == 200:
                regen_data = response.json()
                print("✅ 재생성 성공!")
                print(f"메시지: {regen_data['message']}")
                print("🔄 새로 생성된 선택지:")
                for i, choice in enumerate(regen_data["data"]["choices"], 1):
                    print(f"   {i}. {choice}")
            else:
                print(f"❌ 재생성 실패: {response.status_code}")
            
            # 8. 4단계 응답 제출
            print("\n8️⃣ 4단계 - 첫 번째 선택지 선택")
            step4_data = {
                "session_id": session_id,
                "response": {
                    "choice_numbers": [1],  # 첫 번째 동적 선택지 선택
                    "custom_answer": ""
                }
            }
            response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=step4_data)
            if response.status_code == 200:
                print("✅ 4단계 응답 성공")
                result_data = response.json()
                if "next_stage" in result_data["data"]:
                    print(f"다음 단계: {result_data['data']['next_stage']}")
            else:
                print(f"❌ 4단계 응답 실패: {response.status_code} - {response.text}")
                print(f"응답: {response.text}")
                
        else:
            print("❌ 동적 선택지가 생성되지 않았습니다. 기본 선택지 사용됨.")
            if "choices" in question_data:
                print("기본 선택지:")
                for i, choice in enumerate(question_data["choices"], 1):
                    print(f"   {i}. {choice}")
    else:
        print(f"❌ 4단계 질문 조회 실패: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    try:
        test_middle_school_step4_dynamic()
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")