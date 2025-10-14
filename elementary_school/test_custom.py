"""
기타 선택을 포함한 단일 사용자 테스트
각 단계에서 기타 옵션과 커스텀 답변을 사용
"""

import requests
import json

def test_with_custom_answers():
    print("기타 선택 포함 단일 사용자 테스트...")
    
    BASE_URL = "http://localhost:8000"
    
    # 1. 세션 시작
    response = requests.post(f"{BASE_URL}/career/start")
    data = response.json()
    session_id = data["data"]["session_id"]
    print(f"✅ 세션 시작: {session_id}")
    
    # 2. 학생 정보 (0단계) - 커스텀 답변
    payload = {
        "session_id": session_id,
        "student_info": {"name": "김소영", "age": 10},
        "response": {
            "choice_numbers": [],
            "custom_answer": "안녕하세요! 저는 김소영이에요. 책 읽기와 그림 그리기를 좋아하고, 친구들과 이야기하는 것도 재미있어요!"
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 0단계: 커스텀 학생 소개")
    
    # 3. 1단계: 흥미 탐색 (정규 선택 1개 + 기타 내용 포함)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [2, 7],  # 레고 만들기 + 책 읽기
            "custom_answer": "그리고 친구들과 함께 연극 연습하고 무대에서 공연하는 것도 정말 좋아해요!"
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 1단계: 레고+책읽기 (추가로 연극 좋아함)")
    
    # 4. 2단계: 장점 탐색 (기타 선택)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "저는 다른 사람의 마음을 잘 이해하고, 슬픈 친구를 위로해주는 것을 잘해요. 그리고 이야기를 재미있게 들려주는 것도 자신있어요!"
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 2단계: 기타(공감능력 + 스토리텔링)")
    
    # 5. 3단계: 가치관 탐색 (정규 선택)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [1],  # 누군가 도와주기
            "custom_answer": "특히 친구들이 웃고 즐거워할 때, 그리고 새로운 이야기를 만들어서 다른 사람들과 공유할 때 가장 행복해요!"
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 3단계: 누군가도와주기 (추가로 스토리텔링 행복)")
    
    # 6. 4단계: 미래 탐색 (기타 선택)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "사람들이 서로 이해하지 못하고 소통하지 않아서 갈등이 생기는 것이 가장 걱정돼요. 모두가 서로를 이해하고 마음을 나눌 수 있으면 좋겠어요."
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 4단계: 기타(소통 부족으로 인한 갈등)")
    
    # 7. 5단계: AI 추천 (첫 번째)
    print(f"\n🤖 김소영의 커스텀 답변으로 GPT 프롬프트 생성 중...")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={"regenerate": False})
    data = response.json()
    
    if data.get("success", False):
        recommendation = data["data"]["career_recommendation"]
        print(f"📝 GPT 첫 번째 추천: {recommendation}")
    else:
        print(f"❌ 추천 실패: {data}")
    
    # 8. 재추천
    print(f"\n🤖 재추천으로 다른 관점 확인...")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={"regenerate": True})
    data = response.json()
    
    if data.get("success", False):
        recommendation = data["data"]["career_recommendation"]
        print(f"📝 GPT 재추천: {recommendation}")
    else:
        print(f"❌ 재추천 실패: {data}")
    
    # 9. 추천 수락
    requests.post(f"{BASE_URL}/career/{session_id}/accept-recommendation")
    print("✅ 추천 수락")
    
    # 10. 6단계: 드림로직 (커스텀 답변 기반)
    print(f"\n🌈 김소영의 커스텀 답변으로 드림로직 GPT 프롬프트 생성 중...")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/dream-logic")
    data = response.json()
    
    if data.get("success", False):
        dream_logic = data["data"]["dream_logic"]
        print(f"📝 GPT 드림로직 (첫 200자): {dream_logic[:200]}...")
        print("\n📋 전체 드림로직:")
        print(dream_logic)
    else:
        print(f"❌ 드림로직 실패: {data}")
    
    print(f"\n✅ 김소영 기타 선택 테스트 완료!")

if __name__ == "__main__":
    test_with_custom_answers()