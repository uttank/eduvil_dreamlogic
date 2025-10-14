#!/usr/bin/env python3
"""
간단한 백엔드 테스트 스크립트
서버가 실행 중일 때 실행하는 단순화된 버전
"""

import requests
import json
import time
import random

# 설정
BASE_URL = "http://localhost:8000"
USERS = [
    {"name": "김민수", "age": 10},
    {"name": "이수진", "age": 9},
    {"name": "박지훈", "age": 11},
    {"name": "최하영", "age": 10}
]

CHOICES = {
    1: [[1, 3], [4, 9], [7, 10], [2, 5]],
    2: [[2, 5], [4, 6], [8, 9], [1, 10]],
    3: [[2], [4], [8], [1]],
    4: [[1], [8], [3], [6]]
}

def test_single_user(user, choices):
    print(f"\n🚀 {user['name']} 테스트 시작")
    print("=" * 50)
    
    try:
        # 1. 세션 시작
        response = requests.post(f"{BASE_URL}/career/start")
        if response.status_code != 200:
            print(f"❌ 세션 시작 실패: {response.status_code}")
            return False
            
        session_data = response.json()
        session_id = session_data["data"]["session_id"]
        print(f"✅ 세션 시작: {session_id}")
        
        # 2. 0단계: 학생 정보
        payload = {
            "session_id": session_id,
            "student_info": user,
            "response": {
                "choice_numbers": [],
                "custom_answer": f"안녕하세요! 저는 {user['name']}이고 {user['age']}살이에요."
            }
        }
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
        if response.status_code != 200:
            print(f"❌ 0단계 실패: {response.status_code}")
            return False
        print("✅ 0단계 완료: 학생 정보")
        
        # 3. 1-4단계
        for stage in range(1, 5):
            stage_choices = choices[stage]
            
            # 20% 확률로 기타 선택
            if random.random() < 0.2:
                payload = {
                    "session_id": session_id,
                    "response": {
                        "choice_numbers": [11],  # 기타
                        "custom_answer": f"{user['name']}의 {stage}단계 특별한 답변"
                    }
                }
                print(f"✅ {stage}단계 완료: 기타 선택")
            else:
                payload = {
                    "session_id": session_id,
                    "response": {
                        "choice_numbers": stage_choices,
                        "custom_answer": ""
                    }
                }
                print(f"✅ {stage}단계 완료: 선택지 {stage_choices}")
            
            response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
            if response.status_code != 200:
                print(f"❌ {stage}단계 실패: {response.status_code}")
                return False
                
        # 4. 5단계: AI 추천 (첫 번째)
        print(f"\n🤖 OpenAI API 호출 중... (첫 번째 추천)")
        print("=" * 50)
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={"regenerate": False})
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                recommendation = data["data"]["career_recommendation"]
                print(f"📝 GPT 5단계 추천 결과:")
                print(f"   {recommendation}")
                print("=" * 50)
            else:
                print(f"❌ 추천 실패: {data}")
        else:
            print(f"❌ 추천 API 실패: {response.status_code} - {response.text}")
            
        # 5. 5단계: AI 추천 재시도
        time.sleep(1)
        print(f"\n🤖 OpenAI API 호출 중... (재시도)")
        print("=" * 50)
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={"regenerate": True})
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                recommendation = data["data"]["career_recommendation"]
                print(f"📝 GPT 5단계 재추천 결과:")
                print(f"   {recommendation}")
                print("=" * 50)
            else:
                print(f"❌ 재추천 실패: {data}")
        else:
            print(f"❌ 재추천 API 실패: {response.status_code} - {response.text}")
        
        # 6. 추천 수락
        response = requests.post(f"{BASE_URL}/career/{session_id}/accept-recommendation")
        if response.status_code == 200:
            print("✅ 추천 수락 완료")
        else:
            print(f"❌ 추천 수락 실패: {response.status_code} - {response.text}")
            
        # 7. 6단계: 드림로직 생성
        time.sleep(1)
        print(f"\n🌈 OpenAI API 드림로직 생성 호출 중...")
        print("=" * 50)
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/dream-logic")
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                dream_logic = data["data"]["dream_logic"]
                print(f"📝 GPT 6단계 드림로직 결과:")
                print(dream_logic)
                print("=" * 50)
            else:
                print(f"❌ 드림로직 실패: {data}")
        else:
            print(f"❌ 드림로직 API 실패: {response.status_code} - {response.text}")
            
        print(f"🎉 {user['name']} 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ {user['name']} 테스트 중 오류: {e}")
        return False

def main():
    print("🎯 초등학생 진로 탐색 시스템 간단 테스트")
    print("=" * 70)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            return
        print("✅ 서버 연결 확인")
    except:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return
    
    success_count = 0
    for i, user in enumerate(USERS):
        user_choices = {stage: CHOICES[stage][i] for stage in range(1, 5)}
        if test_single_user(user, user_choices):
            success_count += 1
        time.sleep(2)  # 사용자 간 대기
    
    print("\n" + "=" * 70)
    print("📊 테스트 결과 요약")
    print("=" * 70)
    print(f"👥 총 사용자: {len(USERS)}명")
    print(f"✅ 성공: {success_count}명 ({success_count/len(USERS)*100:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    main()

import requests
import json

def simple_test():
    BASE_URL = "http://localhost:8001"
    
    try:
        # 1. 서버 상태 확인
        print("1. 서버 상태 확인...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 서버 정상 동작")
        else:
            print("❌ 서버 오류")
            return
        
        # 2. 세션 시작
        print("\n2. 진로 탐색 세션 시작...")
        response = requests.post(f"{BASE_URL}/career/start")
        if response.status_code == 200:
            data = response.json()
            session_id = data["data"]["session_id"]
            print(f"✅ 세션 생성: {session_id}")
            print(f"메시지: {data['data']['message']}")
            return session_id
        else:
            print("❌ 세션 생성 실패")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return None

if __name__ == "__main__":
    session_id = simple_test()
    if session_id:
        print(f"\n✅ 기본 테스트 완료! 세션 ID: {session_id}")
        print("📖 API 문서: http://localhost:8001/docs")
    else:
        print("❌ 테스트 실패")