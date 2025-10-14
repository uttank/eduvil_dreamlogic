"""
구체적인 선택지로 GPT 프롬프트 확인 테스트
"""

import requests
import json

def test_with_real_choices():
    print("실제 선택지로 GPT 프롬프트 확인 테스트...")
    
    BASE_URL = "http://localhost:8000"
    
    # 1. 세션 시작
    response = requests.post(f"{BASE_URL}/career/start")
    data = response.json()
    session_id = data["data"]["session_id"]
    print(f"✅ 세션 시작: {session_id}")
    
    # 2. 학생 정보 (0단계)
    payload = {
        "session_id": session_id,
        "student_info": {"name": "김민수", "age": 10},
        "response": {
            "choice_numbers": [],
            "custom_answer": "안녕하세요! 저는 김민수이고 10살이에요. 만들기를 좋아해요!"
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 0단계: 학생 정보 제출")
    
    # 3. 1단계: 흥미 탐색 (만화 그리기 + 과학 실험)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [1, 3],  # 만화 그리기, 과학 실험
            "custom_answer": ""
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 1단계: 만화 그리기 + 과학 실험")
    
    # 4. 2단계: 장점 탐색 (창의성 + 손재주)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [5, 2],  # 창의성, 손재주
            "custom_answer": ""
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 2단계: 창의성 + 손재주")
    
    # 5. 3단계: 가치관 탐색 (새로운 것 만들기)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [2],  # 새로운 것 만들기
            "custom_answer": ""
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 3단계: 새로운 것 만들기")
    
    # 6. 4단계: 미래 탐색 (기후변화 문제)
    payload = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [1],  # 기후변화 문제
            "custom_answer": ""
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    print("✅ 4단계: 기후변화 문제")
    
    # 7. 5단계: AI 추천 (여기서 실제 프롬프트 확인)
    print(f"\n🤖 김민수의 실제 데이터로 GPT 프롬프트 생성 중...")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={"regenerate": False})
    data = response.json()
    
    if data.get("success", False):
        recommendation = data["data"]["career_recommendation"]
        print(f"📝 GPT 응답: {recommendation}")
    else:
        print(f"❌ 추천 실패: {data}")
    
    print("\n🤖 재추천으로 다른 프롬프트 확인...")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={"regenerate": True})
    data = response.json()
    
    if data.get("success", False):
        recommendation = data["data"]["career_recommendation"]
        print(f"📝 GPT 재응답: {recommendation}")
    else:
        print(f"❌ 재추천 실패: {data}")
    
    # 8. 추천 수락
    requests.post(f"{BASE_URL}/career/{session_id}/accept-recommendation")
    print("✅ 추천 수락")
    
    # 9. 6단계: 드림로직 (실제 데이터로 프롬프트 확인)
    print(f"\n🌈 김민수의 실제 데이터로 드림로직 GPT 프롬프트 생성 중...")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/dream-logic")
    data = response.json()
    
    if data.get("success", False):
        dream_logic = data["data"]["dream_logic"]
        print(f"📝 GPT 드림로직: {dream_logic[:200]}...")
    else:
        print(f"❌ 드림로직 실패: {data}")
    
    print(f"\n✅ 김민수 테스트 완료!")

if __name__ == "__main__":
    test_with_real_choices()