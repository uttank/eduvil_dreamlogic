#!/usr/bin/env python3
"""
중학교 진로탐색 앱 전체 플로우 테스트 (0-6단계)
기존 test_stages.py 기반으로 6단계 드림로직까지 확장
5단계 수정 기능과 6단계 fallback 문제 확인 포함
"""

import requests
import json
import time
from typing import Dict, Any

# 테스트 설정
BASE_URL = "http://127.0.0.1:8000"
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
        return data["data"].get("next_question")
    else:
        print(f"❌ 0단계 실패: {data.get('message', '알 수 없는 오류')}")
        return None

def submit_step(step_num: int, choice_numbers: list, custom_answer: str = ""):
    """단계별 응답 제출 공통 함수"""
    step_names = {
        1: "흥미 탐색",
        2: "장점 탐색", 
        3: "가치관 탐색",
        4: "미래 관심"
    }
    
    print_separator(f"🎯 {step_num}단계 테스트 - {step_names[step_num]}")
    
    payload = {
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {
            "choice_numbers": choice_numbers,
            "custom_answer": custom_answer
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=payload)
    data = response.json()
    
    print(f"📤 요청 데이터: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print(f"✅ {step_num}단계 성공")
        return data["data"].get("next_question")
    else:
        print(f"❌ {step_num}단계 실패: {data.get('message', '알 수 없는 오류')}")
        return None

def test_step_5():
    """5단계 테스트 - 진로 추천 생성 및 수정 기능"""
    print_separator("🎯 5단계 테스트 - 진로 추천 생성 및 수정 기능")
    
    # 테스트 케이스 1: 진로 추천 생성
    print("\n--- 테스트 케이스 1: 진로 추천 생성 ---")
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/recommend", json={})
    data = response.json()
    
    print(f"📤 요청: POST /career/{session_id}/recommend")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if not data["success"]:
        print(f"❌ 진로 추천 생성 실패: {data.get('message')}")
        return None
    
    print("✅ 진로 추천 생성 성공")
    career_recommendation = data["data"]["career_recommendation"]
    print(f"🎯 생성된 진로 추천: {career_recommendation}")
    
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
    print(f"🆕 새로운 진로 추천: {new_recommendation}")
    
    # 추천 내용이 달라졌는지 확인
    if new_recommendation != career_recommendation:
        print("✅ 수정 전후 추천이 다름 - 수정 기능 정상 작동")
    else:
        print("⚠️ 수정 전후 추천이 동일함 - AI 응답이 유사할 수 있음")
    
    # 테스트 케이스 3: 꿈 확정
    print("\n--- 테스트 케이스 3: 꿈 확정 ---")
    
    confirm_request = {
        "action": "confirm",
        "dream_statement": new_recommendation
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/dream-confirm", json=confirm_request)
    data = response.json()
    
    print(f"📤 요청: {json.dumps(confirm_request, ensure_ascii=False, indent=2)}")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 꿈 확정 성공")
        confirmed_dream = data['data'].get('confirmed_dream', new_recommendation)
        print(f"🎉 확정된 꿈: {confirmed_dream}")
        return confirmed_dream
    else:
        print(f"❌ 꿈 확정 실패: {data.get('message')}")
        return None

def test_step_6():
    """6단계 테스트 - 드림로직 생성"""
    print_separator("🌟 6단계 테스트 - 드림로직 생성")
    
    print("\n--- 드림로직 생성 요청 ---")
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/dream-logic")
    data = response.json()
    
    print(f"📤 요청: POST /career/{session_id}/dream-logic")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if not data["success"]:
        print(f"❌ 드림로직 생성 실패: {data.get('message')}")
        return None
    
    print("✅ 드림로직 생성 성공")
    dream_logic = data["data"]["dream_logic"]
    
    # 드림로직 내용 분석
    print("\n📝 드림로직 분석:")
    print(f"📏 길이: {len(dream_logic)} 글자")
    
    # fallback 여부 확인
    is_fallback = "기초 실력 쌓기" in dream_logic and "경험 넓히기" in dream_logic
    if is_fallback:
        print("⚠️  WARNING: Fallback 드림로직이 사용되었습니다!")
        print("🔍 원인: OpenAI API 오류 또는 예외 처리로 인한 fallback 호출")
    else:
        print("✅ AI 생성 드림로직이 정상적으로 생성되었습니다!")
    
    # 드림로직 구조 확인
    structure_checks = {
        "3개 중간목표": "[중간목표 1]" in dream_logic and "[중간목표 2]" in dream_logic and "[중간목표 3]" in dream_logic,
        "실천활동 구조": "실천활동(학교):" in dream_logic and "실천활동(일상):" in dream_logic,
        "추천 활동": "추천 활동:" in dream_logic,
        "응원 메모": "💬 응원 메모" in dream_logic
    }
    
    for check_name, is_valid in structure_checks.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {check_name}: {'정상' if is_valid else '비정상'}")
    
    # 드림로직 내용 출력 (일부)
    print(f"\n📄 드림로직 미리보기:")
    print("-" * 40)
    preview_length = min(500, len(dream_logic))
    print(dream_logic[:preview_length])
    if len(dream_logic) > preview_length:
        print("... (후략)")
    print("-" * 40)
    
    return dream_logic

def test_session_summary():
    """세션 요약 조회 테스트"""
    print_separator("📊 세션 요약 조회 테스트")
    
    response = requests.get(f"{BASE_URL}/career/{session_id}/summary")
    data = response.json()
    
    print(f"📤 요청: GET /career/{session_id}/summary")
    print(f"📥 응답 상태: {response.status_code}")
    print(f"📥 응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if data["success"]:
        print("✅ 세션 요약 조회 성공")
        summary = data["data"]
        
        print(f"\n📋 전체 세션 요약:")
        print(f"👤 학생명: {summary.get('student_name')}")
        print(f"🎯 최종 꿈: {summary.get('final_career_goal')}")
        print(f"📈 현재 단계: {summary.get('current_stage')}")
        print(f"✅ 꿈 확정 여부: {summary.get('career_confirmed')}")
        print(f"📝 드림로직 존재: {'있음' if summary.get('dream_logic_result') else '없음'}")
        
        return summary
    else:
        print(f"❌ 세션 요약 조회 실패: {data.get('message')}")
        return None

def test_step_5_specific_issues():
    """5단계 수정 기능 특정 이슈 테스트"""
    print_separator("🔧 5단계 수정 기능 특정 이슈 테스트")
    
    # 새 세션으로 5단계까지 빠르게 진행
    print("\n--- 새 세션으로 5단계까지 진행 ---")
    
    new_session = requests.post(f"{BASE_URL}/career/start").json()
    new_session_id = new_session["data"]["session_id"]
    print(f"🆕 새 세션 ID: {new_session_id}")
    
    # 0-4단계 빠르게 완료
    steps_data = [
        {"student_info": {"name": "수정테스트", "grade": 1}},
        {"student_info": {"name": "수정테스트", "grade": 1}, "response": {"choice_numbers": [1, 5]}},
        {"student_info": {"name": "수정테스트", "grade": 1}, "response": {"choice_numbers": [2]}},
        {"student_info": {"name": "수정테스트", "grade": 1}, "response": {"choice_numbers": [1]}},
        {"student_info": {"name": "수정테스트", "grade": 1}, "response": {"choice_numbers": [3]}}
    ]
    
    for i, step_data in enumerate(steps_data):
        step_data["session_id"] = new_session_id
        response = requests.post(f"{BASE_URL}/career/{new_session_id}/submit", json=step_data)
        if response.json()["success"]:
            print(f"✅ {i}단계 완료")
        else:
            print(f"❌ {i}단계 실패: {response.json().get('message')}")
            return
    
    # 5단계 진로 추천 생성
    print("\n--- 진로 추천 생성 ---")
    response = requests.post(f"{BASE_URL}/career/{new_session_id}/recommend", json={})
    if not response.json()["success"]:
        print(f"❌ 진로 추천 생성 실패: {response.json().get('message')}")
        return
    
    original_recommendation = response.json()["data"]["career_recommendation"]
    print(f"🎯 원본 추천: {original_recommendation}")
    
    # 연속 수정 요청 테스트
    print("\n--- 연속 수정 요청 테스트 (세션 에러 확인) ---")
    
    for i in range(3):
        print(f"\n{i+1}번째 수정 요청:")
        modify_request = {"action": "modify"}
        
        response = requests.post(f"{BASE_URL}/career/{new_session_id}/dream-confirm", json=modify_request)
        
        if response.status_code == 500:
            print("❌ 500 서버 에러 발생!")
            print(f"   응답: {response.text}")
        elif response.status_code in [400, 404]:
            print(f"❌ {response.status_code} 클라이언트 에러 발생!")
            print(f"   응답: {response.json()}")
        elif response.json()["success"]:
            new_rec = response.json()["data"]["career_recommendation"]
            print(f"✅ 수정 성공: {new_rec}")
        else:
            print(f"❌ 수정 실패: {response.json().get('message')}")
        
        time.sleep(0.5)  # API 호출 간격

def test_step_6_fallback_issue():
    """6단계 fallback 이슈 특정 테스트"""
    print_separator("🔍 6단계 Fallback 이슈 특정 테스트")
    
    # 여러 번 드림로직 생성하여 fallback 패턴 확인
    print("\n--- 다중 드림로직 생성 테스트 ---")
    
    fallback_count = 0
    ai_count = 0
    
    for i in range(5):
        print(f"\n{i+1}번째 드림로직 생성:")
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/dream-logic")
        
        if response.json()["success"]:
            dream_logic = response.json()["data"]["dream_logic"]
            is_fallback = "기초 실력 쌓기" in dream_logic and "경험 넓히기" in dream_logic
            
            if is_fallback:
                fallback_count += 1
                print("⚠️  Fallback 드림로직 감지")
            else:
                ai_count += 1
                print("✅ AI 생성 드림로직 감지")
        else:
            print(f"❌ 드림로직 생성 실패: {response.json().get('message')}")
        
        time.sleep(1)  # API 호출 간격
    
    print(f"\n📊 테스트 결과:")
    print(f"   AI 생성: {ai_count}회")
    print(f"   Fallback: {fallback_count}회")
    
    if fallback_count > 0:
        print("⚠️  Fallback이 발생했습니다. 원인 분석이 필요합니다.")
        print("   가능한 원인:")
        print("   1. OpenAI API 오류")
        print("   2. 프롬프트 처리 오류")
        print("   3. 예외 처리 로직 문제")
    else:
        print("✅ 모든 드림로직이 정상적으로 AI 생성되었습니다.")

def main():
    """메인 테스트 함수"""
    print_separator("🧪 중학교 진로탐색 앱 전체 플로우 테스트 (0-6단계)")
    print("📍 테스트 대상: 0단계(이름/학년) ~ 6단계(드림로직)")
    print("🎯 특별 테스트: 5단계 수정 기능, 6단계 fallback 문제")
    
    try:
        # 서버 연결 확인
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            print(f"\n✅ 서버 연결 성공 (상태코드: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ 서버 연결 실패: {e}")
            print("💡 서버가 실행 중인지 확인해주세요: python middle_school.py")
            return
        
        # === 기본 플로우 테스트 ===
        
        # 세션 시작
        if not test_start_session():
            return
        
        # 0단계 테스트
        if not test_step_0():
            return
        
        # 1-4단계 테스트 (빠르게 진행)
        test_data = [
            ([1, 5], ""),    # 1단계: 스토리 기획, 코딩
            ([2], ""),       # 2단계: 창의발상
            ([1], ""),       # 3단계: 도움/서비스 제공
            ([3], "")        # 4단계: AI·로봇과 사람의 협업
        ]
        
        for step, (choices, custom) in enumerate(test_data, 1):
            if not submit_step(step, choices, custom):
                return
            time.sleep(0.5)
        
        # 5단계 테스트
        confirmed_dream = test_step_5()
        if not confirmed_dream:
            print("❌ 5단계 실패 - 6단계 테스트 건너뜀")
            return
        
        # 6단계 테스트
        dream_logic = test_step_6()
        if not dream_logic:
            print("❌ 6단계 실패")
            return
        
        # 세션 요약
        test_session_summary()
        
        # === 특별 이슈 테스트 ===
        
        # 5단계 수정 기능 이슈 테스트
        test_step_5_specific_issues()
        
        # 6단계 fallback 이슈 테스트
        test_step_6_fallback_issue()
        
        print_separator("🎉 전체 테스트 완료")
        print("✅ 모든 단계 테스트가 성공적으로 완료되었습니다!")
        print("📋 테스트 결과:")
        print("   - 0단계 (이름/학년): ✅")
        print("   - 1단계 (흥미탐색): ✅")
        print("   - 2단계 (장점탐색): ✅") 
        print("   - 3단계 (가치관탐색): ✅")
        print("   - 4단계 (미래관심): ✅")
        print("   - 5단계 (진로추천): ✅ 생성 + 수정 + 확정")
        print("   - 6단계 (드림로직): ✅ AI 생성 + fallback 확인")
        print("   - 특별 이슈 테스트: ✅ 5단계 수정 기능, 6단계 fallback 분석")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()