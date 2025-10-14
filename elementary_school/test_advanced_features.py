#!/usr/bin/env python3
"""
진로 탐색 API 다중 선택 및 기타 선택 테스트
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_multiple_choice_and_custom():
    """다중 선택 및 기타 선택 테스트"""
    
    print("=== 진로 탐색 다중선택 & 기타선택 테스트 ===\n")
    
    # 1. 세션 시작
    print("1. 세션 시작")
    response = requests.post(f"{BASE_URL}/career/start")
    if response.status_code != 200:
        print(f"❌ 세션 시작 실패: {response.status_code}")
        return
    
    session_id = response.json()["data"]["session_id"]
    print(f"✅ 세션 생성: {session_id}\n")
    
    # 2. 0단계 - 학생 정보 입력
    print("2. 학생 정보 입력")
    student_data = {
        "session_id": session_id,
        "student_info": {
            "name": "박다중",
            "age": 11
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=student_data)
    if response.status_code != 200:
        print(f"❌ 학생 정보 입력 실패: {response.text}")
        return
    
    print("✅ 학생 정보 입력 완료\n")
    
    # 3. 1단계 - 다중 선택 테스트 (2개 선택)
    print("3. 1단계 - 흥미 탐색 (다중 선택: 레고 + 과학실험)")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [2, 3]  # 레고·블록 + 과학 실험
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    if response.status_code != 200:
        print(f"❌ 1단계 다중선택 실패: {response.text}")
        return
    
    print("✅ 1단계 다중선택 성공!\n")
    
    # 4. 2단계 - 단일 선택 테스트
    print("4. 2단계 - 장점 탐색 (단일 선택: 끈기)")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [3]  # 끝까지 포기 안 해요
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    if response.status_code != 200:
        print(f"❌ 2단계 선택 실패: {response.text}")
        return
    
    print("✅ 2단계 선택 성공!\n")
    
    # 5. 3단계 - 단일 선택만 허용 (1개)
    print("5. 3단계 - 가치관 탐색 (1개만 선택: 새로운 것 만들기)")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [2]  # 새로운 것을 만들 때 행복해요
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    if response.status_code != 200:
        print(f"❌ 3단계 선택 실패: {response.text}")
        return
    
    print("✅ 3단계 선택 성공!\n")
    
    # 6. 4단계 - 단일 선택만 허용 (1개)
    print("6. 4단계 - 미래 탐색 (1개만 선택: 기후변화)")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [1]  # 기후변화와 쓰레기 문제
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    if response.status_code != 200:
        print(f"❌ 4단계 선택 실패: {response.text}")
        return
    
    print("✅ 4단계 선택 성공!\n")
    
    # 7. 세션 요약 확인
    print("7. 세션 요약 확인")
    response = requests.get(f"{BASE_URL}/career/{session_id}/summary")
    if response.status_code == 200:
        summary = response.json()["data"]
        print(f"👤 학생: {summary['student_info']['name']}")
        print("📝 응답 요약:")
        for stage, info in summary["responses_summary"].items():
            print(f"  {stage}: {info['answer']}")
    print()
    
    # === 기타 선택 테스트 ===
    print("=== 기타 선택 테스트 ===\n")
    
    # 8. 새 세션 시작 - 기타 선택 테스트
    response = requests.post(f"{BASE_URL}/career/start")
    session_id_2 = response.json()["data"]["session_id"]
    print(f"8. 새 세션 시작: {session_id_2}")
    
    # 학생 정보 입력
    student_data = {
        "session_id": session_id_2,
        "student_info": {
            "name": "김기타",
            "age": 10
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id_2}/submit", json=student_data)
    
    # 9. 1단계 - 기타 선택 테스트
    print("9. 1단계 - 기타 선택 테스트")
    response_data = {
        "session_id": session_id_2,
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "친구들과 함께 보드게임을 하며 전략을 세우는 것을 좋아해요!"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_2}/submit", json=response_data)
    if response.status_code != 200:
        print(f"❌ 기타 선택 실패: {response.text}")
        return
    
    print("✅ 1단계 기타 선택 성공!")
    
    # 10. 2단계 - 기타 선택 테스트
    print("10. 2단계 - 기타 선택 테스트")
    response_data = {
        "session_id": session_id_2,
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "복잡한 문제를 차근차근 분석해서 해결하는 능력이 있어요!"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_2}/submit", json=response_data)
    if response.status_code == 200:
        print("✅ 2단계 기타 선택 성공!")
    else:
        print(f"❌ 2단계 기타 선택 실패: {response.text}")
    
    # 11. 3단계 - 기타 선택 테스트
    print("11. 3단계 - 기타 선택 테스트")
    response_data = {
        "session_id": session_id_2,
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "어려운 상황에 있는 사람들에게 실질적인 도움을 줄 때 가장 보람을 느껴요!"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_2}/submit", json=response_data)
    if response.status_code == 200:
        print("✅ 3단계 기타 선택 성공!")
    else:
        print(f"❌ 3단계 기타 선택 실패: {response.text}")
    
    # 12. 4단계 - 기타 선택 테스트
    print("12. 4단계 - 기타 선택 테스트")
    response_data = {
        "session_id": session_id_2,
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "사람들이 서로를 이해하지 못해서 생기는 갈등과 소통 부족 문제가 걱정돼요!"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_2}/submit", json=response_data)
    if response.status_code == 200:
        print("✅ 4단계 기타 선택 성공!")
        
        # 완료 메시지 확인
        result = response.json()
        if result["data"]["completed"]:
            print(f"🎉 {result['data']['completion_message']}")
    else:
        print(f"❌ 4단계 기타 선택 실패: {response.text}")
    
    # 13. 기타 선택 세션 요약 확인
    print("\n13. 기타 선택 세션 요약 확인")
    response = requests.get(f"{BASE_URL}/career/{session_id_2}/summary")
    if response.status_code == 200:
        summary = response.json()["data"]
        print(f"👤 학생: {summary['student_info']['name']}")
        print("📝 기타 응답 요약:")
        for stage, info in summary["responses_summary"].items():
            print(f"  {stage}: {info['answer']}")
    
    print("\n=== 에러 케이스 테스트 ===")
    
    # 14. 잘못된 선택 테스트
    response = requests.post(f"{BASE_URL}/career/start")
    session_id_3 = response.json()["data"]["session_id"]
    
    # 학생 정보 입력
    student_data = {"session_id": session_id_3, "student_info": {"name": "테스트", "age": 9}}
    requests.post(f"{BASE_URL}/career/{session_id_3}/submit", json=student_data)
    
    # 1단계에서 3개 선택 (에러 케이스)
    print("14. 1단계에서 3개 선택 (에러 예상)")
    response_data = {
        "session_id": session_id_3,
        "response": {
            "choice_numbers": [1, 2, 3]  # 3개 선택 (최대 2개만 허용)
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_3}/submit", json=response_data)
    if response.status_code != 200:
        print("✅ 정상적으로 에러 처리됨")
    else:
        print("❌ 에러가 발생하지 않음 (문제 있음)")
    
    # 15. 기타 선택시 custom_answer 없음 (에러 케이스)
    print("15. 기타 선택시 설명 없음 (에러 예상)")
    response_data = {
        "session_id": session_id_3,
        "response": {
            "choice_numbers": [11]  # custom_answer 없음
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_3}/submit", json=response_data)
    if response.status_code != 200:
        print("✅ 정상적으로 에러 처리됨")
    else:
        print("❌ 에러가 발생하지 않음 (문제 있음)")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    try:
        test_multiple_choice_and_custom()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()