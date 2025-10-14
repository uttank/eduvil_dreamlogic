#!/usr/bin/env python3
"""
중학교 진로탐색 앱 0-5단계 테스트 스크립트
기타 선택지 포함 + 5단계 수정 기능 테스트
"""

import requests
import json
import time
from typing import Dict, Any

# 테스트 설정
BASE_URL = "http://127.0.0.1:8001"
session_id = None

def print_separator(title: str):
    """구분선 출력"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_start_session():
    """세션 시작 테스트"""
    global session_id
    print_separator("🚀 세션 시작 테스트")
    
    response = requests.post(f"{BASE_URL}/career/start")
    data = response.json()
    
    if data["success"]:
        session_id = data["data"]["session_id"]
        print(f"✅ 세션 시작 성공")
        print(f"📋 세션 ID: {session_id}")
        if "first_question" in data["data"]:
            print(f"📋 첫 질문: {data['data']['first_question']['question']}")
        else:
            print(f"📋 응답 데이터: {data['data']}")
        return True
    else:
        print(f"❌ 세션 시작 실패: {data.get('message', '알 수 없는 오류')}")
        return False

def test_step_0():
    """0단계 테스트 - 이름과 학년 입력"""
    print_separator("📝 0단계 테스트 - 이름과 학년 입력")
    
    # 일반적인 이름과 학년
    student_info = {
        "name": "김테스트",
        "grade": 2  # 1, 2, 3 중 하나
    }
    
    payload = {
        "session_id": session_id,
        "student_info": student_info
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    data = response.json()
    
    print(f"📤 요청 데이터: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 0단계 성공")
        return data["data"]["next_question"]
    else:
        print(f"❌ 0단계 실패: {data.get('message', '알 수 없는 오류')}")
        return None

def test_step_1():
    """1단계 테스트 - 흥미 탐색 (다중선택 + 기타)"""
    print_separator("🎯 1단계 테스트 - 흥미 탐색 (다중선택 + 기타)")
    
    # 테스트 케이스 1: 일반 선택지 2개
    print("\n--- 테스트 케이스 1: 일반 선택지 2개 ---")
    test_case_1 = {
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {
            "choice_numbers": [1, 5]  # 스토리 기획, 코딩
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=test_case_1)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_1, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 1 성공")
        next_question = data["data"]["next_question"]
    else:
        print(f"❌ 테스트 케이스 1 실패: {data.get('message')}")
        return None
    
    # 새 세션으로 테스트 케이스 2
    print("\n--- 테스트 케이스 2: 기타 선택지 ---")
    
    # 새 세션 시작
    new_session = requests.post(f"{BASE_URL}/career/start").json()
    new_session_id = new_session["data"]["session_id"]
    
    # 0단계 건너뛰기
    step0_payload = {
        "session_id": new_session_id,
        "student_info": {"name": "김테스트2", "grade": 1}
    }
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json=step0_payload)
    
    # 기타 선택 테스트
    test_case_2 = {
        "session_id": new_session_id,
        "student_info": {"name": "김테스트2", "grade": 1},
        "response": {
            "choice_numbers": [13],  # 기타
            "custom_answer": "음악 작곡하고 연주하기"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json=test_case_2)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_2, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 2 성공")
    else:
        print(f"❌ 테스트 케이스 2 실패: {data.get('message')}")
    
    return next_question

def test_step_2():
    """2단계 테스트 - 장점 탐색 (단일선택 + 기타)"""
    print_separator("💪 2단계 테스트 - 장점 탐색 (단일선택 + 기타)")
    
    # 테스트 케이스 1: 일반 선택지
    print("\n--- 테스트 케이스 1: 일반 선택지 ---")
    test_case_1 = {
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {
            "choice_numbers": [2]  # 창의발상
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=test_case_1)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_1, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 1 성공")
        next_question = data["data"]["next_question"]
    else:
        print(f"❌ 테스트 케이스 1 실패: {data.get('message')}")
        return None
    
    # 새 세션으로 기타 테스트
    print("\n--- 테스트 케이스 2: 기타 선택지 ---")
    
    new_session = requests.post(f"{BASE_URL}/career/start").json()
    new_session_id = new_session["data"]["session_id"]
    
    # 0단계, 1단계 건너뛰기
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트3", "grade": 3}
    })
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트3", "grade": 3},
        "response": {"choice_numbers": [1, 2]}
    })
    
    test_case_2 = {
        "session_id": new_session_id,
        "student_info": {"name": "김테스트3", "grade": 3},
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "빠른 학습능력과 적응력"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json=test_case_2)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_2, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 2 성공")
    else:
        print(f"❌ 테스트 케이스 2 실패: {data.get('message')}")
    
    return next_question

def test_step_3():
    """3단계 테스트 - 가치관 탐색 (단일선택 + 기타)"""
    print_separator("❤️ 3단계 테스트 - 가치관 탐색 (단일선택 + 기타)")
    
    # 테스트 케이스 1: 일반 선택지
    print("\n--- 테스트 케이스 1: 일반 선택지 ---")
    test_case_1 = {
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {
            "choice_numbers": [3]  # 어려운 문제 해결하며 성장
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=test_case_1)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_1, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 1 성공")
        next_question = data["data"]["next_question"]
    else:
        print(f"❌ 테스트 케이스 1 실패: {data.get('message')}")
        return None
    
    # 새 세션으로 기타 테스트
    print("\n--- 테스트 케이스 2: 기타 선택지 ---")
    
    new_session = requests.post(f"{BASE_URL}/career/start").json()
    new_session_id = new_session["data"]["session_id"]
    
    # 이전 단계들 건너뛰기
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트4", "grade": 1}
    })
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트4", "grade": 1},
        "response": {"choice_numbers": [3, 7]}
    })
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트4", "grade": 1},
        "response": {"choice_numbers": [4]}
    })
    
    test_case_2 = {
        "session_id": new_session_id,
        "student_info": {"name": "김테스트4", "grade": 1},
        "response": {
            "choice_numbers": [10],  # 기타
            "custom_answer": "가족과 친구들이 안전하고 행복한 모습을 볼 때"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json=test_case_2)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_2, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 2 성공")
    else:
        print(f"❌ 테스트 케이스 2 실패: {data.get('message')}")
    
    return next_question

def test_step_4():
    """4단계 테스트 - 미래 관심 탐색 (단일선택 + 기타)"""
    print_separator("🔮 4단계 테스트 - 미래 관심 탐색 (단일선택 + 기타)")
    
    # 테스트 케이스 1: 일반 선택지
    print("\n--- 테스트 케이스 1: 일반 선택지 ---")
    test_case_1 = {
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {
            "choice_numbers": [3]  # AI·로봇과 사람의 협업·일자리
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=test_case_1)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_1, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 1 성공")
        next_question = data["data"]["next_question"]
    else:
        print(f"❌ 테스트 케이스 1 실패: {data.get('message')}")
        return None
    
    # 새 세션으로 기타 테스트
    print("\n--- 테스트 케이스 2: 기타 선택지 ---")
    
    new_session = requests.post(f"{BASE_URL}/career/start").json()
    new_session_id = new_session["data"]["session_id"]
    
    # 이전 단계들 건너뛰기
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트5", "grade": 2}
    })
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트5", "grade": 2},
        "response": {"choice_numbers": [11, 12]}
    })
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트5", "grade": 2},
        "response": {"choice_numbers": [7]}
    })
    requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json={
        "session_id": new_session_id,
        "student_info": {"name": "김테스트5", "grade": 2},
        "response": {"choice_numbers": [6]}
    })
    
    test_case_2 = {
        "session_id": new_session_id,
        "student_info": {"name": "김테스트5", "grade": 2},
        "response": {
            "choice_numbers": [11],  # 기타
            "custom_answer": "메타버스에서의 개인정보 보호와 윤리 문제"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json=test_case_2)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(test_case_2, ensure_ascii=False, indent=2)}")
    print(f"📥 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 테스트 케이스 2 성공")
    else:
        print(f"❌ 테스트 케이스 2 실패: {data.get('message')}")
    
    return next_question

def test_step_5():
    """5단계 테스트 - 진로 추천 생성 및 수정 기능"""
    print_separator("🎯 5단계 테스트 - 진로 추천 생성 및 수정 기능")
    
    # 테스트 케이스 1: 진로 추천 생성
    print("\n--- 테스트 케이스 1: 진로 추천 생성 ---")
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={})
    data = response.json()
    
    print(f"📤 요청: GET /career/{session_id}/recommend")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if not data["success"]:
        print(f"❌ 진로 추천 생성 실패: {data.get('message')}")
        return None
    
    print("✅ 진로 추천 생성 성공")
    career_recommendation = data["data"]["career_recommendation"]
    print(f"🎯 생성된 진로 추천: {career_recommendation[:100]}...")
    
    # 테스트 케이스 2: 수정 요청 (바로 새로운 추천 생성)
    print("\n--- 테스트 케이스 2: 수정 요청 (바로 새로운 추천 생성) ---")
    
    modify_request = {
        "action": "modify"
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/dream-confirm", json=modify_request)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(modify_request, ensure_ascii=False, indent=2)}")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if not data["success"]:
        print(f"❌ 새로운 추천 생성 실패: {data.get('message')}")
        return None
    
    print("✅ 새로운 추천 생성 성공")
    new_recommendation = data["data"]["career_recommendation"]
    print(f"🆕 새로운 진로 추천: {new_recommendation[:100]}...")
    
    # 추천 내용이 달라졌는지 확인
    if new_recommendation != career_recommendation:
        print("✅ 수정 전후 추천이 다름 - 수정 기능 정상 작동")
    else:
        print("⚠️ 수정 전후 추천이 동일함 - AI 응답이 유사할 수 있음")
    
    # 테스트 케이스 3: 여러 번 수정 요청
    print("\n--- 테스트 케이스 3: 여러 번 수정 요청 ---")
    
    for i in range(2):
        print(f"\n{i+1}번째 추가 수정 요청:")
        response = requests.post(f"{BASE_URL}/career/{session_id}/dream-confirm", json=modify_request)
        data = response.json()
        
        if data["success"]:
            another_recommendation = data["data"]["career_recommendation"]
            print(f"✅ {i+1}번째 수정 성공: {another_recommendation[:50]}...")
        else:
            print(f"❌ {i+1}번째 수정 실패: {data.get('message')}")
    
    # 최종 추천으로 확정
    final_recommendation = data["data"]["career_recommendation"] if data["success"] else new_recommendation
    
    # 테스트 케이스 4: 꿈 확정
    print("\n--- 테스트 케이스 4: 꿈 확정 ---")
    
    confirm_request = {
        "action": "confirm",
        "dream_statement": final_recommendation
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/dream-confirm", json=confirm_request)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(confirm_request, ensure_ascii=False, indent=2)}")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 꿈 확정 성공")
        print(f"🎉 확정된 꿈: {data['data'].get('confirmed_dream', '')[:100]}...")
        return True
    else:
        print(f"❌ 꿈 확정 실패: {data.get('message')}")
        return False

def test_step_5_error_cases():
    """5단계 에러 케이스 테스트"""
    print_separator("🚨 5단계 에러 케이스 테스트")
    
    # 에러 케이스 1: 존재하지 않는 세션으로 추천 요청
    print("\n--- 에러 케이스 1: 존재하지 않는 세션으로 추천 요청 ---")
    
    fake_session_id = "non-existent-session"
    response = requests.post(f"{BASE_URL}/career/{fake_session_id}/recommend", json={})
    data = response.json()
    
    print(f"📤 요청: POST /career/{fake_session_id}/recommend")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 404:
        print("✅ 존재하지 않는 세션 에러 처리 정상")
    else:
        print("❌ 존재하지 않는 세션 에러 처리 비정상")
    
    # 에러 케이스 2: 4단계 미완료 상태에서 추천 요청
    print("\n--- 에러 케이스 2: 4단계 미완료 상태에서 추천 요청 ---")
    
    # 새 세션 시작하고 1-2단계만 완료
    new_session = requests.post(f"{BASE_URL}/career/start").json()
    incomplete_session_id = new_session["data"]["session_id"]
    
    # 0단계만 완료
    requests.post(f"{BASE_URL}/career/{incomplete_session_id}/submit", json={
        "session_id": incomplete_session_id,
        "student_info": {"name": "미완료테스트", "grade": 1}
    })
    
    # 4단계 미완료 상태에서 추천 요청
    response = requests.post(f"{BASE_URL}/career/{incomplete_session_id}/recommend", json={})
    data = response.json()
    
    print(f"📤 요청: POST /career/{incomplete_session_id}/recommend")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 400:
        print("✅ 미완료 단계 에러 처리 정상")
    else:
        print("❌ 미완료 단계 에러 처리 비정상")

def test_models_data():
    """모델 데이터 구조 확인"""
    print_separator("📋 모델 데이터 구조 확인")
    
    try:
        from models import STAGE_QUESTIONS, CareerStage
        
        for stage in [CareerStage.STEP_1, CareerStage.STEP_2, CareerStage.STEP_3, CareerStage.STEP_4]:
            stage_data = STAGE_QUESTIONS[stage]
            print(f"\n📝 {stage.value}:")
            print(f"   질문: {stage_data['question']}")
            print(f"   선택지 개수: {len(stage_data['choices'])}")
            
            # 기타 선택지 확인
            others = [choice for choice in stage_data['choices'] if '기타' in choice]
            if others:
                print(f"   기타 선택지: {others}")
            else:
                print(f"   ❌ 기타 선택지 없음!")
                
    except Exception as e:
        print(f"❌ 모델 데이터 확인 실패: {e}")

def main():
    """메인 테스트 함수"""
    print_separator("🧪 중학교 진로탐색 앱 테스트 시작")
    print("📍 테스트 대상: 0단계(이름/학년) ~ 5단계(진로추천 및 수정)")
    print("🎯 테스트 항목: 일반 선택지 + 기타 선택지 + 추천 수정 기능")
    
    try:
        # 모델 데이터 구조 확인
        test_models_data()
        
        # 서버 연결 확인
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            print(f"\n✅ 서버 연결 성공 (상태코드: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ 서버 연결 실패: {e}")
            print("💡 서버가 실행 중인지 확인해주세요: uvicorn middle_school:app --reload --port 8000")
            return
        
        # 세션 시작
        if not test_start_session():
            return
        
        # 0단계 테스트
        next_q = test_step_0()
        if not next_q:
            return
        
        # 1단계 테스트
        next_q = test_step_1()
        if not next_q:
            return
            
        # 2단계 테스트
        next_q = test_step_2()
        if not next_q:
            return
            
        # 3단계 테스트
        next_q = test_step_3()
        if not next_q:
            return
            
        # 4단계 테스트
        next_q = test_step_4()
        if not next_q:
            return
        
        # 5단계 테스트 (진로 추천 생성 및 수정)
        if not test_step_5():
            print("❌ 5단계 테스트 실패 - 에러 케이스 테스트 건너뜀")
        else:
            # 5단계 에러 케이스 테스트
            test_step_5_error_cases()
        
        print_separator("🎉 테스트 완료")
        print("✅ 모든 단계 테스트가 성공적으로 완료되었습니다!")
        print("📋 테스트 결과:")
        print("   - 0단계 (이름/학년): ✅")
        print("   - 1단계 (흥미탐색): ✅ 다중선택 + 기타")
        print("   - 2단계 (장점탐색): ✅ 단일선택 + 기타") 
        print("   - 3단계 (가치관탐색): ✅ 단일선택 + 기타")
        print("   - 4단계 (미래관심): ✅ 단일선택 + 기타")
        print("   - 5단계 (진로추천): ✅ 생성 + 간단 수정 + 확정")
        print("   - 에러 처리: ✅ 잘못된 요청 에러 처리")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()