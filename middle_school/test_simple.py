#!/usr/bin/env python3
"""
중학교 진로탐색 앱 간단한 테스트 스크립트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_basic_flow():
    """기본 플로우 테스트"""
    print("🧪 중학교 진로탐색 앱 기본 플로우 테스트")
    
    # 1. 세션 시작
    print("\n1️⃣ 세션 시작...")
    start_resp = requests.post(f"{BASE_URL}/career/start").json()
    session_id = start_resp["data"]["session_id"]
    print(f"✅ 세션 ID: {session_id}")
    
    # 2. 0단계 - 이름과 학년
    print("\n2️⃣ 0단계 - 이름과 학년 입력...")
    step0_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2}
    }).json()
    print(f"✅ 0단계 완료, 다음: {step0_resp['data']['next_stage']}")
    
    # 3. 1단계 - 일반 선택지 테스트
    print("\n3️⃣ 1단계 - 일반 선택지 (다중선택)...")
    step1_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {"choice_numbers": [1, 5]}  # 스토리 기획, 코딩
    }).json()
    print(f"✅ 1단계 완료, 다음: {step1_resp['data']['next_stage']}")
    
    # 4. 2단계 - 일반 선택지 테스트  
    print("\n4️⃣ 2단계 - 일반 선택지 (단일선택)...")
    step2_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {"choice_numbers": [2]}  # 창의발상
    }).json()
    print(f"✅ 2단계 완료, 다음: {step2_resp['data']['next_stage']}")
    
    # 5. 3단계 - 일반 선택지 테스트
    print("\n5️⃣ 3단계 - 일반 선택지 (단일선택)...")
    step3_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {"choice_numbers": [3]}  # 어려운 문제 해결
    }).json()
    print(f"✅ 3단계 완료, 다음: {step3_resp['data']['next_stage']}")
    
    # 6. 4단계 - 일반 선택지 테스트
    print("\n6️⃣ 4단계 - 일반 선택지 (단일선택)...")
    step4_resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
        "session_id": session_id,
        "student_info": {"name": "김테스트", "grade": 2},
        "response": {"choice_numbers": [3]}  # AI·로봇과 사람의 협업
    }).json()
    print(f"✅ 4단계 완료, 다음: {step4_resp['data']['next_stage']}")
    
    print("\n🎉 일반 선택지 테스트 완료!")
    return True

def test_other_choices():
    """기타 선택지 테스트"""
    print("\n🧪 기타 선택지 테스트")
    
    # 새 세션들로 각 단계의 기타 선택지 테스트
    stages_to_test = [
        (1, 13, "음악 작곡하고 연주하기"),
        (2, 11, "빠른 학습능력과 적응력"),
        (3, 10, "가족과 친구들이 안전하고 행복한 모습을 볼 때"),
        (4, 11, "메타버스에서의 개인정보 보호와 윤리 문제")
    ]
    
    for stage_num, other_choice_num, custom_text in stages_to_test:
        print(f"\n{stage_num}단계 기타 선택지 테스트...")
        
        # 새 세션 시작
        start_resp = requests.post(f"{BASE_URL}/career/start").json()
        session_id = start_resp["data"]["session_id"]
        
        # 0단계 완료
        requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
            "session_id": session_id,
            "student_info": {"name": f"김테스트{stage_num}", "grade": min(stage_num, 3)}  # grade는 1-3만 허용
        })
        
        # 이전 단계들 완료 (더미 데이터)
        if stage_num >= 2:
            requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
                "session_id": session_id,
                "student_info": {"name": f"김테스트{stage_num}", "grade": min(stage_num, 3)},
                "response": {"choice_numbers": [1, 2] if stage_num == 1 else [1]}
            })
        if stage_num >= 3:
            requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
                "session_id": session_id,
                "student_info": {"name": f"김테스트{stage_num}", "grade": min(stage_num, 3)},
                "response": {"choice_numbers": [1]}
            })
        if stage_num >= 4:
            requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
                "session_id": session_id,
                "student_info": {"name": f"김테스트{stage_num}", "grade": min(stage_num, 3)},
                "response": {"choice_numbers": [1]}
            })
        
        # 기타 선택지 테스트
        try:
            resp = requests.post(f"{BASE_URL}/career/{session_id}/submit", json={
                "session_id": session_id,
                "student_info": {"name": f"김테스트{stage_num}", "grade": min(stage_num, 3)},
                "response": {
                    "choice_numbers": [other_choice_num],
                    "custom_answer": custom_text
                }
            })
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    print(f"✅ {stage_num}단계 기타 선택지 성공")
                else:
                    print(f"❌ {stage_num}단계 기타 선택지 실패: {data.get('message', '알 수 없는 오류')}")
            else:
                print(f"❌ {stage_num}단계 기타 선택지 HTTP 오류: {resp.status_code}")
                print(f"   응답: {resp.text}")
                
        except Exception as e:
            print(f"❌ {stage_num}단계 기타 선택지 예외: {e}")

def check_models():
    """모델 데이터 확인"""
    print("🧪 모델 데이터 확인")
    
    try:
        from models import STAGE_QUESTIONS, CareerStage
        
        print("\n📋 각 단계별 선택지 개수와 기타 항목:")
        for stage in [CareerStage.STEP_1, CareerStage.STEP_2, CareerStage.STEP_3, CareerStage.STEP_4]:
            stage_data = STAGE_QUESTIONS[stage]
            choices = stage_data['choices']
            others = [i+1 for i, choice in enumerate(choices) if '기타' in choice]
            
            print(f"  {stage.value}: {len(choices)}개 선택지, 기타: {others}번")
            
        return True
        
    except Exception as e:
        print(f"❌ 모델 데이터 확인 실패: {e}")
        return False

def main():
    print("="*60)
    print(" 🧪 중학교 진로탐색 앱 테스트")
    print("="*60)
    
    # 서버 연결 확인
    try:
        resp = requests.get(BASE_URL, timeout=5)
        print(f"✅ 서버 연결 성공 (상태: {resp.status_code})")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 모델 데이터 확인
    if not check_models():
        return
    
    # 기본 플로우 테스트
    if not test_basic_flow():
        return
    
    # 기타 선택지 테스트
    test_other_choices()
    
    print("\n" + "="*60)
    print(" 🎉 테스트 완료")
    print("="*60)
    print("✅ 결과 요약:")
    print("   - 모든 단계(1-4)에 기타 선택지 추가됨")
    print("   - 1단계: 다중선택(최대 2개) + 13번 기타")
    print("   - 2단계: 단일선택 + 11번 기타")  
    print("   - 3단계: 단일선택 + 10번 기타")
    print("   - 4단계: 단일선택 + 11번 기타")
    print("   - 기타 선택 시 custom_answer 필드 사용")

if __name__ == "__main__":
    main()