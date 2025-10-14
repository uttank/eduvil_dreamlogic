#!/usr/bin/env python3
"""
OpenAI API 기능 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_openai_integration():
    """OpenAI API 통합 기능 테스트"""
    
    print("=== OpenAI API 통합 테스트 ===\n")
    
    # 1. AI 서비스 상태 확인
    print("1. AI 서비스 상태 확인")
    response = requests.get(f"{BASE_URL}/career/ai/status")
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print("✅ AI 서비스 정상 작동")
            print(f"   모델: {data['data']['model']}")
            print(f"   테스트 응답: {data['data']['test_response']}")
        else:
            print("❌ AI 서비스 비활성화")
            print(f"   사유: {data['message']}")
            return
    else:
        print("❌ AI 서비스 상태 확인 실패")
        return
    
    print()
    
    # 2. 완전한 진로 탐색 세션 진행
    print("2. 완전한 진로 탐색 세션 진행")
    
    # 세션 시작
    response = requests.post(f"{BASE_URL}/career/start")
    session_id = response.json()["data"]["session_id"]
    print(f"   세션 시작: {session_id}")
    
    # 학생 정보 입력
    student_data = {
        "session_id": session_id,
        "student_info": {
            "name": "AI테스트",
            "age": 11
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=student_data)
    print("   ✅ 학생 정보 입력 완료")
    
    # 1단계 - 흥미 탐색
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [8, 9]  # 코딩 + 영상 편집
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    print("   ✅ 1단계 완료 (흥미: 코딩 + 영상편집)")
    
    # 2단계 - 장점 탐색  
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [5, 7]  # 창의성 + 계산력
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    print("   ✅ 2단계 완료 (장점: 창의성 + 계산력)")
    
    # 3단계 - 가치관 탐색
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [2]  # 새로운 것을 만들 때 행복
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    print("   ✅ 3단계 완료 (가치관: 새로운 것 만들기)")
    
    # 4단계 - 미래 탐색
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_numbers": [3]  # AI·로봇과 사람이 함께 일하는 법
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id}/submit", json=response_data)
    print("   ✅ 4단계 완료 (미래: AI·로봇 협업)")
    
    print("   🎉 모든 단계 완료!\n")
    
    # 3. AI 맞춤 응원 메시지 테스트 (완료 전 단계에서)
    print("3. AI 맞춤 응원 메시지 테스트")
    
    # 새 세션으로 중간 단계 테스트
    response = requests.post(f"{BASE_URL}/career/start")
    test_session_id = response.json()["data"]["session_id"]
    
    # 학생 정보만 입력하고 1단계 진행 중 상태 만들기
    student_data = {
        "session_id": test_session_id,
        "student_info": {
            "name": "응원테스트",
            "age": 9
        }
    }
    requests.post(f"{BASE_URL}/career/{test_session_id}/submit", json=student_data)
    
    # AI 응원 메시지 요청
    response = requests.get(f"{BASE_URL}/career/{test_session_id}/ai-encouragement")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ AI 응원 메시지 생성 성공")
        print(f"   메시지: {data['data']['ai_encouragement']}")
    else:
        print("   ❌ AI 응원 메시지 생성 실패")
        print(f"   오류: {response.text}")
    
    print()
    
    # 4. AI 진로 추천 생성
    print("4. AI 진로 추천 생성")
    print("   AI가 분석 중입니다... ⏳")
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ AI 진로 추천 생성 성공!")
        print(f"   학생: {data['data']['student_name']}")
        print(f"   추천 진로: {data['data']['career_recommendation']}")
        
        # 추천된 진로를 저장해서 드림로직에 사용
        career_recommendation = data['data']['career_recommendation']
    else:
        print("   ❌ AI 진로 추천 생성 실패")
        print(f"   오류: {response.text}")
        career_recommendation = "창의적인 기술 전문가"
    
    print()
    
    # 5. 드림로직 생성
    print("5. 드림로직 생성")
    print("   상세한 실천 계획을 생성하고 있습니다... ⏳")
    
    # career_goal 파라미터를 쿼리로 전달
    response = requests.post(
        f"{BASE_URL}/career/{session_id}/dream-logic",
        params={"career_goal": career_recommendation}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ 드림로직 생성 성공!")
        print(f"   학생: {data['data']['student_name']}")
        print(f"   목표: {data['data']['career_goal']}")
        print("   드림로직:")
        print("   " + "="*50)
        # 드림로직을 줄별로 출력
        for line in data['data']['dream_logic'].split('\n'):
            if line.strip():
                print(f"   {line}")
        print("   " + "="*50)
    else:
        print("   ❌ 드림로직 생성 실패")
        print(f"   오류: {response.text}")
    
    print()
    
    # 6. 기타 선택을 포함한 AI 분석 테스트
    print("6. 기타 선택 포함 AI 분석 테스트")
    
    # 새 세션으로 기타 선택 테스트
    response = requests.post(f"{BASE_URL}/career/start")
    custom_session_id = response.json()["data"]["session_id"]
    
    # 학생 정보
    student_data = {
        "session_id": custom_session_id,
        "student_info": {
            "name": "창의소녀",
            "age": 10
        }
    }
    requests.post(f"{BASE_URL}/career/{custom_session_id}/submit", json=student_data)
    
    # 모든 단계에서 기타 선택으로 진행
    stages_custom = [
        {
            "stage": "1단계",
            "custom_answer": "친구들과 함께 로봇을 만들고 프로그래밍하면서 문제를 해결하는 것을 좋아해요!"
        },
        {
            "stage": "2단계", 
            "custom_answer": "복잡한 문제를 단계별로 나누어서 체계적으로 해결하는 분석력이 있어요!"
        },
        {
            "stage": "3단계",
            "custom_answer": "과학기술로 환경 문제를 해결하고 지구를 보호할 때 가장 보람을 느껴요!"
        },
        {
            "stage": "4단계",
            "custom_answer": "AI가 잘못 사용되어서 사람들의 일자리가 없어지고 사회가 불공평해지는 것이 걱정돼요!"
        }
    ]
    
    for i, stage_info in enumerate(stages_custom):
        response_data = {
            "session_id": custom_session_id,
            "response": {
                "choice_numbers": [11],
                "custom_answer": stage_info["custom_answer"]
            }
        }
        
        response = requests.post(f"{BASE_URL}/career/{custom_session_id}/submit", json=response_data)
        if response.status_code == 200:
            print(f"   ✅ {stage_info['stage']} 기타 선택 완료")
        else:
            print(f"   ❌ {stage_info['stage']} 기타 선택 실패")
    
    # AI 분석
    print("   AI가 기타 응답들을 분석하고 있습니다... ⏳")
    response = requests.post(f"{BASE_URL}/career/{custom_session_id}/recommend")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ 기타 선택 기반 AI 분석 성공!")
        print(f"   맞춤 추천: {data['data']['career_recommendation']}")
    else:
        print("   ❌ 기타 선택 기반 AI 분석 실패")
    
    print("\n=== OpenAI API 통합 테스트 완료 ===")

if __name__ == "__main__":
    try:
        test_openai_integration()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()