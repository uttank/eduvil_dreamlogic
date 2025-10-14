#!/usr/bin/env python3
"""
5단계 "수정하고 싶어요" 기능 테스트
새로운 추천이 실제로 생성되는지 확인
"""

import requests
import json
import time
from typing import Dict, Any, List

# 테스트 설정
BASE_URL = "http://localhost:8000"
TEST_STUDENT_NAME = "테스트학생"

def create_test_session() -> str:
    """테스트 세션 생성"""
    print("🎯 테스트 세션 생성 중...")
    
    response = requests.post(f"{BASE_URL}/career/start")
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data['data']['session_id']
        print(f"✅ 세션 생성 성공: {session_id}")
        return session_id
    else:
        raise Exception(f"세션 생성 실패: {response.status_code}")

def submit_student_info(session_id: str) -> bool:
    """학생 정보 제출"""
    print("📝 학생 정보 제출 중...")
    
    student_info = {
        "session_id": session_id,
        "student_info": {
            "name": TEST_STUDENT_NAME,
            "grade": 2,
            "school": "테스트중학교"
        }
    }
    
    response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=student_info)
    if response.status_code == 200:
        print("✅ 학생 정보 제출 성공")
        return True
    else:
        print(f"❌ 학생 정보 제출 실패: {response.status_code}")
        print(f"응답: {response.text}")
        return False

def complete_stages_1_to_4(session_id: str) -> bool:
    """1-4단계 완료"""
    print("🔄 1-4단계 진행 중...")
    
    # 테스트용 답변 데이터
    stages_data = {
        "STEP_1": {
            "choice_numbers": [1],  # 스토리 기획·세계관 만들기
            "custom_answer": ""
        },
        "STEP_2": {
            "choice_numbers": [2],  # 새로운 이야기나 캐릭터 만들기
            "custom_answer": ""
        },
        "STEP_3": {
            "choice_numbers": [3],  # 사람들에게 도움이 되는 일
            "custom_answer": ""
        },
        "STEP_4": {
            "choice_numbers": [4],  # 문화·예술·미디어
            "custom_answer": ""
        }
    }
    
    for stage, response_data in stages_data.items():
        print(f"  📋 {stage} 진행...")
        
        stage_request = {
            "session_id": session_id,
            "response": response_data
        }
        
        response = requests.post(f"{BASE_URL}/career/{session_id}/submit", json=stage_request)
        if response.status_code == 200:
            print(f"  ✅ {stage} 완료")
        else:
            print(f"  ❌ {stage} 실패: {response.status_code}")
            print(f"  응답: {response.text}")
            return False
    
    print("✅ 1-4단계 모두 완료")
    return True

def get_initial_recommendation(session_id: str) -> str:
    """첫 번째 추천 받기"""
    print("🤖 첫 번째 AI 추천 생성 중...")
    
    response = requests.post(
        f"{BASE_URL}/career/{session_id}/recommend",
        json={"regenerate": False}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success'] and 'career_recommendation' in data['data']:
            recommendation = data['data']['career_recommendation']
            print(f"✅ 첫 번째 추천: {recommendation}")
            return recommendation
        else:
            raise Exception("추천 데이터가 없습니다.")
    else:
        raise Exception(f"추천 생성 실패: {response.status_code} - {response.text}")

def get_modified_recommendation(session_id: str) -> str:
    """수정된 추천 받기 (regenerate=True)"""
    print("🔄 수정된 추천 생성 중...")
    
    response = requests.post(
        f"{BASE_URL}/career/{session_id}/recommend",
        json={"regenerate": True}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success'] and 'career_recommendation' in data['data']:
            recommendation = data['data']['career_recommendation']
            print(f"✅ 수정된 추천: {recommendation}")
            return recommendation
        else:
            raise Exception("수정된 추천 데이터가 없습니다.")
    else:
        raise Exception(f"수정된 추천 생성 실패: {response.status_code} - {response.text}")

def compare_recommendations(original: str, modified: str) -> Dict[str, Any]:
    """추천 비교 분석"""
    print("\n📊 추천 비교 분석:")
    print(f"원본 추천: {original}")
    print(f"수정 추천: {modified}")
    
    is_different = original.strip() != modified.strip()
    
    result = {
        "original": original,
        "modified": modified,
        "is_different": is_different,
        "original_length": len(original),
        "modified_length": len(modified)
    }
    
    if is_different:
        print("✅ 추천이 다릅니다! 수정 기능이 정상 작동합니다.")
    else:
        print("⚠️ 추천이 동일합니다. AI 설정을 확인해야 할 수 있습니다.")
    
    return result

def test_multiple_modifications(session_id: str, count: int = 3) -> List[str]:
    """여러 번 수정 테스트"""
    print(f"\n🔄 {count}번 연속 수정 테스트:")
    
    recommendations = []
    
    for i in range(count):
        print(f"\n--- {i+1}번째 수정 ---")
        try:
            recommendation = get_modified_recommendation(session_id)
            recommendations.append(recommendation)
            time.sleep(1)  # API 호출 간격
        except Exception as e:
            print(f"❌ {i+1}번째 수정 실패: {e}")
            break
    
    # 유니크한 추천 개수 확인
    unique_recommendations = list(set(recommendations))
    print(f"\n📈 결과 분석:")
    print(f"총 생성된 추천: {len(recommendations)}개")
    print(f"유니크한 추천: {len(unique_recommendations)}개")
    print(f"다양성 비율: {len(unique_recommendations)/len(recommendations)*100:.1f}%")
    
    return recommendations

def main():
    """메인 테스트 함수"""
    print("🎯 5단계 수정 기능 테스트 시작\n")
    
    try:
        # 1. 세션 생성
        session_id = create_test_session()
        
        # 2. 학생 정보 제출
        if not submit_student_info(session_id):
            return
        
        # 3. 1-4단계 완료
        if not complete_stages_1_to_4(session_id):
            return
        
        # 4. 첫 번째 추천 받기
        original_recommendation = get_initial_recommendation(session_id)
        
        # 5. 수정된 추천 받기
        time.sleep(2)  # 잠시 대기
        modified_recommendation = get_modified_recommendation(session_id)
        
        # 6. 추천 비교
        comparison = compare_recommendations(original_recommendation, modified_recommendation)
        
        # 7. 여러 번 수정 테스트
        multiple_recommendations = test_multiple_modifications(session_id, 3)
        
        # 8. 최종 결과
        print("\n🎉 테스트 완료!")
        print("=" * 60)
        
        if comparison['is_different']:
            print("✅ 5단계 수정 기능이 정상 작동합니다!")
        else:
            print("⚠️ 수정 기능에 문제가 있을 수 있습니다.")
        
        if len(set(multiple_recommendations)) > 1:
            print("✅ 연속 수정 시 다양한 추천 생성됩니다!")
        else:
            print("⚠️ 연속 수정 시 동일한 추천만 생성됩니다.")
            
    except Exception as e:
        print(f"\n💥 테스트 실패: {e}")

if __name__ == "__main__":
    main()