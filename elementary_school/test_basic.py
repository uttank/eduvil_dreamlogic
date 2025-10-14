"""
매우 간단한 API 테스트
"""

import requests
import json

def test_basic():
    print("기본 API 테스트 시작...")
    
    # 1. 서버 연결 확인
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ 서버 연결: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 세션 시작
    try:
        response = requests.post("http://localhost:8000/career/start")
        data = response.json()
        session_id = data["data"]["session_id"]
        print(f"✅ 세션 시작: {session_id}")
    except Exception as e:
        print(f"❌ 세션 시작 실패: {e}")
        return
    
    # 3. 학생 정보 제출
    try:
        payload = {
            "session_id": session_id,
            "student_info": {"name": "테스트", "age": 10},
            "response": {
                "choice_numbers": [],
                "custom_answer": "테스트 사용자입니다."
            }
        }
        response = requests.post(f"http://localhost:8000/career/{session_id}/submit", json=payload)
        print(f"✅ 학생 정보: {response.status_code}")
    except Exception as e:
        print(f"❌ 학생 정보 실패: {e}")
        return
    
    # 4. 1-4단계 진행
    for stage in range(1, 5):
        try:
            payload = {
                "session_id": session_id,
                "response": {
                    "choice_numbers": [1, 2] if stage <= 2 else [1],
                    "custom_answer": ""
                }
            }
            response = requests.post(f"http://localhost:8000/career/{session_id}/submit", json=payload)
            print(f"✅ {stage}단계: {response.status_code}")
        except Exception as e:
            print(f"❌ {stage}단계 실패: {e}")
            return
    
    # 5. AI 추천
    try:
        print("\n🤖 OpenAI API 호출 중...")
        response = requests.post(f"http://localhost:8000/career/{session_id}/recommend", json={"regenerate": False})
        print(f"추천 API 응답: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                recommendation = data["data"]["career_recommendation"]
                print(f"📝 GPT 추천 결과: {recommendation[:100]}...")
            else:
                print(f"추천 응답: {data}")
        else:
            print(f"추천 에러: {response.text}")
    except Exception as e:
        print(f"❌ AI 추천 실패: {e}")
        return
    
    # 6. 재추천
    try:
        print("\n🤖 OpenAI API 재호출 중...")
        response = requests.post(f"http://localhost:8000/career/{session_id}/recommend", json={"regenerate": True})
        print(f"재추천 API 응답: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                recommendation = data["data"]["career_recommendation"]
                print(f"📝 GPT 재추천 결과: {recommendation[:100]}...")
            else:
                print(f"재추천 응답: {data}")
        else:
            print(f"재추천 에러: {response.text}")
    except Exception as e:
        print(f"❌ AI 재추천 실패: {e}")
    
    # 7. 추천 수락
    try:
        response = requests.post(f"http://localhost:8000/career/{session_id}/accept-recommendation")
        print(f"✅ 추천 수락: {response.status_code}")
    except Exception as e:
        print(f"❌ 추천 수락 실패: {e}")
    
    # 8. 드림로직
    try:
        print("\n🌈 OpenAI API 드림로직 호출 중...")
        response = requests.post(f"http://localhost:8000/career/{session_id}/dream-logic")
        print(f"드림로직 API 응답: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                dream_logic = data["data"]["dream_logic"]
                print(f"📝 GPT 드림로직 결과: {dream_logic[:200]}...")
            else:
                print(f"드림로직 응답: {data}")
        else:
            print(f"드림로직 에러: {response.text}")
    except Exception as e:
        print(f"❌ 드림로직 실패: {e}")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    test_basic()