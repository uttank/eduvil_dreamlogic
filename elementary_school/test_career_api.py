#!/usr/bin/env python3
"""
진로 탐색 API 테스트 스크립트
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def test_career_exploration():
    """진로 탐색 API 전체 흐름 테스트"""
    
    print("=== 초등학생 진로 탐색 API 테스트 ===\n")
    
    # 1. 세션 시작
    print("1. 세션 시작 테스트")
    response = requests.post(f"{BASE_URL}/career/start")
    
    if response.status_code != 200:
        print(f"❌ 세션 시작 실패: {response.status_code}")
        return
    
    data = response.json()
    session_id = data["data"]["session_id"]
    print(f"✅ 세션 생성 성공: {session_id}")
    print(f"💬 메시지: {data['data']['message']}\n")
    
    # 2. 0단계 - 현재 질문 조회 (이름, 나이 입력)
    print("2. 0단계 - 기본 정보 입력")
    response = requests.get(f"{BASE_URL}/career/{session_id}/question")
    
    if response.status_code != 200:
        print(f"❌ 질문 조회 실패: {response.status_code}")
        return
    
    question_data = response.json()["data"]
    print(f"📝 질문: {question_data['question']}")
    print(f"💪 응원: {question_data['encouragement']}\n")
    
    # 3. 0단계 - 학생 정보 제출
    print("3. 0단계 - 학생 정보 제출")
    student_data = {
        "session_id": session_id,
        "student_info": {
            "name": "김철수",
            "age": 10
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", 
                           json=student_data)
    
    if response.status_code != 200:
        print(f"❌ 정보 제출 실패: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    print(f"✅ 학생 정보 제출 성공!")
    print(f"💬 다음 단계: {result['data']['next_stage']}")
    
    if "next_question" in result["data"]:
        next_q = result["data"]["next_question"]
        print(f"📝 다음 질문: {next_q['question']}")
        print(f"💪 응원: {next_q['encouragement']}")
        print("📋 선택지:")
        for i, choice in enumerate(next_q["choices"], 1):
            print(f"  {choice}")
        print()
    
    # 4. 1단계 - 흥미 탐색 (예: 레고 선택)
    print("4. 1단계 - 흥미 탐색 응답")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_number": 2  # 레고·블록으로 건물·로봇 만들 때
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", 
                           json=response_data)
    
    if response.status_code != 200:
        print(f"❌ 1단계 응답 실패: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    print(f"✅ 1단계 응답 제출 성공!")
    
    if "next_question" in result["data"]:
        next_q = result["data"]["next_question"]
        print(f"📝 다음 질문: {next_q['question']}")
        print(f"💪 응원: {next_q['encouragement']}")
        print("📋 선택지:")
        for choice in next_q["choices"]:
            print(f"  {choice}")
        print()
    
    # 5. 2단계 - 장점 탐색 (예: 손재주 선택)
    print("5. 2단계 - 장점 탐색 응답")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_number": 2  # 손이 야무져요
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", 
                           json=response_data)
    
    result = response.json()
    print(f"✅ 2단계 응답 제출 성공!")
    
    if "next_question" in result["data"]:
        next_q = result["data"]["next_question"]
        print(f"📝 다음 질문: {next_q['question']}")
        print(f"💪 응원: {next_q['encouragement']}")
        print()
    
    # 6. 3단계 - 가치관 탐색 (예: 새로운 것 만들기)
    print("6. 3단계 - 가치관 탐색 응답")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_number": 2  # 새로운 것을 만들 때 행복해요
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", 
                           json=response_data)
    
    result = response.json()
    print(f"✅ 3단계 응답 제출 성공!")
    
    if "next_question" in result["data"]:
        next_q = result["data"]["next_question"]
        print(f"📝 다음 질문: {next_q['question']}")
        print(f"💪 응원: {next_q['encouragement']}")
        print()
    
    # 7. 4단계 - 미래 탐색 (예: 기후변화 문제)
    print("7. 4단계 - 미래 탐색 응답")
    response_data = {
        "session_id": session_id,
        "response": {
            "choice_number": 1  # 기후변화와 쓰레기 문제
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", 
                           json=response_data)
    
    result = response.json()
    print(f"✅ 4단계 응답 제출 성공!")
    
    if result["data"]["completed"]:
        print(f"🎉 {result['data']['completion_message']}")
    print()
    
    # 8. 세션 요약 조회
    print("8. 세션 요약 조회")
    response = requests.get(f"{BASE_URL}/career/{session_id}/summary")
    
    if response.status_code == 200:
        summary = response.json()["data"]
        print(f"👤 학생: {summary['student_info']['name']} ({summary['student_info']['age']}세)")
        print(f"📊 진행률: {summary['progress_percentage']:.0f}%")
        print("📝 응답 요약:")
        
        for stage, response_info in summary["responses_summary"].items():
            print(f"  {stage}: {response_info['answer']}")
        print()
    
    # 9. 기타 선택 테스트 (새 세션)
    print("9. 기타 선택 테스트")
    response = requests.post(f"{BASE_URL}/career/start")
    session_id_2 = response.json()["data"]["session_id"]
    
    # 학생 정보 입력
    student_data = {
        "session_id": session_id_2,
        "student_info": {
            "name": "이영희",
            "age": 9
        }
    }
    requests.post(f"{BASE_URL}/career/{session_id_2}/submit", json=student_data)
    
    # 1단계에서 기타 선택
    response_data = {
        "session_id": session_id_2,
        "response": {
            "choice_number": 11,  # 기타
            "custom_answer": "친구들과 함께 노는 것을 좋아해요!"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id_2}/submit", 
                           json=response_data)
    
    if response.status_code == 200:
        print("✅ 기타 선택 테스트 성공!")
        
        # 요약에서 기타 응답 확인
        response = requests.get(f"{BASE_URL}/career/{session_id_2}/summary")
        if response.status_code == 200:
            summary = response.json()["data"]
            step1_answer = summary["responses_summary"]["step_1"]["answer"]
            print(f"📝 기타 응답: {step1_answer}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    try:
        test_career_exploration()
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        print("서버 실행: cd /Users/yhpark/work/openai/elementary_school_dev && ./start_server.sh")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()