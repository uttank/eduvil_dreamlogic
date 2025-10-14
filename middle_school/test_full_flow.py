#!/usr/bin/env python3
"""
중학교 진로탐색 서비스 전체 플로우 테스트 (1-6단계)
5단계 수정 기능과 6단계 드림로직 생성까지 모든 기능을 테스트
"""

import requests
import json
import time
from typing import Dict, Any

class MiddleSchoolCareerTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session_id = None
        self.current_stage = None
        self.ai_recommendation = None
        self.final_dream = None
        self.dream_logic = None
        
    def print_step(self, step: str, message: str):
        """단계별 출력 포맷"""
        print(f"\n{'='*50}")
        print(f"🔍 {step}: {message}")
        print(f"{'='*50}")
    
    def print_result(self, success: bool, data: Any = None):
        """결과 출력"""
        if success:
            print("✅ 성공!")
            if data:
                print(f"📋 결과: {data}")
        else:
            print("❌ 실패!")
            if data:
                print(f"🚨 오류: {data}")
    
    def start_session(self, student_name: str = "김테스트") -> bool:
        """세션 시작 (0단계)"""
        self.print_step("0단계", "세션 시작")
        
        try:
            response = requests.post(
                f"{self.base_url}/career/start",
                json={"name": student_name}
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.session_id = data["data"]["session_id"]
                # stage 정보가 없을 수 있으므로 기본값 설정
                self.current_stage = data["data"].get("stage", "STEP_1")
                self.print_result(True, f"세션 ID: {self.session_id}")
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def submit_student_info(self, name: str = "김테스트", grade: int = 2) -> bool:
        """학생 정보 제출 (0단계)"""
        self.print_step("0단계", "학생 정보 입력")
        
        try:
            response = requests.post(
                f"{self.base_url}/career/{self.session_id}/submit",
                json={
                    "session_id": self.session_id,
                    "student_info": {
                        "name": name,
                        "grade": grade
                    }
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.print_result(True, f"학생 정보: {name}, {grade}학년")
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def submit_step_response(self, step: int, choice_numbers: list, custom_answer: str = "") -> bool:
        """단계별 답변 제출 (1-4단계)"""
        step_names = {
            1: "흥미 탐색",
            2: "장점 탐색", 
            3: "가치관 탐색",
            4: "미래 관심"
        }
        
        self.print_step(f"{step}단계", step_names[step])
        
        try:
            response = requests.post(
                f"{self.base_url}/career/{self.session_id}/submit",
                json={
                    "session_id": self.session_id,
                    "response": {
                        "choice_numbers": choice_numbers,
                        "custom_answer": custom_answer
                    }
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.current_stage = data["data"]["stage"]
                self.print_result(True, f"선택: {choice_numbers}, 다음 단계: {self.current_stage}")
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def generate_recommendation(self, regenerate: bool = False) -> bool:
        """진로 추천 생성 (5단계)"""
        action = "재생성" if regenerate else "생성"
        self.print_step("5단계", f"진로 추천 {action}")
        
        try:
            response = requests.post(
                f"{self.base_url}/career/{self.session_id}/recommend",
                json={"regenerate": regenerate}
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.ai_recommendation = data["data"]["career_recommendation"]
                self.print_result(True, f"추천: {self.ai_recommendation}")
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def modify_dream(self) -> bool:
        """꿈 수정 (5단계 수정 기능 테스트)"""
        self.print_step("5단계", "꿈 수정 요청")
        
        try:
            response = requests.post(
                f"{self.base_url}/career/{self.session_id}/dream-confirm",
                json={
                    "action": "modify"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.ai_recommendation = data["data"]["career_recommendation"]
                self.print_result(True, f"수정된 추천: {self.ai_recommendation}")
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def confirm_dream(self) -> bool:
        """꿈 확정 (5단계 완료)"""
        self.print_step("5단계", "꿈 확정")
        
        try:
            response = requests.post(
                f"{self.base_url}/career/{self.session_id}/dream-confirm",
                json={
                    "action": "confirm",
                    "dream_statement": self.ai_recommendation
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.final_dream = data["data"]["confirmed_dream"]
                self.print_result(True, f"확정된 꿈: {self.final_dream}")
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def generate_dream_logic(self) -> bool:
        """드림로직 생성 (6단계)"""
        self.print_step("6단계", "드림로직 생성")
        
        try:
            response = requests.post(
                f"{self.base_url}/career/{self.session_id}/dream-logic"
            )
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                self.dream_logic = data["data"]["dream_logic"]
                self.print_result(True, "드림로직 생성 완료")
                
                # 드림로직 내용 분석
                print("\n📝 드림로직 분석:")
                print(f"📏 길이: {len(self.dream_logic)} 글자")
                
                # fallback 여부 확인
                is_fallback = "기초 실력 쌓기" in self.dream_logic and "경험 넓히기" in self.dream_logic
                if is_fallback:
                    print("⚠️  WARNING: Fallback 드림로직이 사용되었습니다!")
                else:
                    print("✅ AI 생성 드림로직이 정상적으로 생성되었습니다!")
                
                # 드림로직 구조 확인
                if "[중간목표 1]" in self.dream_logic and "[중간목표 2]" in self.dream_logic and "[중간목표 3]" in self.dream_logic:
                    print("✅ 3개 중간목표 구조 정상")
                else:
                    print("❌ 중간목표 구조 비정상")
                
                if "실천활동(학교):" in self.dream_logic and "실천활동(일상):" in self.dream_logic:
                    print("✅ 실천활동 구조 정상")
                else:
                    print("❌ 실천활동 구조 비정상")
                
                if "💬 응원 메모" in self.dream_logic:
                    print("✅ 응원 메모 포함")
                else:
                    print("❌ 응원 메모 누락")
                
                # 일부 내용 출력
                print(f"\n📄 드림로직 미리보기:")
                print(self.dream_logic[:300] + "..." if len(self.dream_logic) > 300 else self.dream_logic)
                
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False
    
    def get_session_summary(self) -> bool:
        """세션 요약 조회"""
        self.print_step("요약", "세션 전체 요약")
        
        try:
            response = requests.get(f"{self.base_url}/career/{self.session_id}/summary")
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                summary = data["data"]
                self.print_result(True, "세션 요약 조회 완료")
                
                print(f"\n📊 전체 세션 요약:")
                print(f"👤 학생명: {summary.get('student_name')}")
                print(f"🎯 최종 꿈: {summary.get('final_career_goal')}")
                print(f"📈 현재 단계: {summary.get('current_stage')}")
                print(f"✅ 꿈 확정 여부: {summary.get('career_confirmed')}")
                print(f"📝 드림로직 존재: {'있음' if summary.get('dream_logic_result') else '없음'}")
                
                return True
            else:
                self.print_result(False, data.get("message"))
                return False
                
        except Exception as e:
            self.print_result(False, str(e))
            return False

def run_full_test():
    """전체 플로우 테스트 실행"""
    print("🚀 중학교 진로탐색 서비스 전체 플로우 테스트 시작")
    print("=" * 60)
    
    tester = MiddleSchoolCareerTester()
    
    # 0단계: 세션 시작
    if not tester.start_session("김테스트"):
        print("❌ 세션 시작 실패, 테스트 중단")
        return False
    
    # 0단계: 학생 정보 입력
    if not tester.submit_student_info("김테스트", 2):
        print("❌ 학생 정보 입력 실패, 테스트 중단")
        return False
    
    # 1-4단계: 답변 제출
    test_responses = [
        ([1, 5], ""),  # 1단계: 스토리 기획, 코딩/게임
        ([2, 7], ""),  # 2단계: 창의발상, 협업/리더십
        ([1, 3], ""),  # 3단계: 도움/서비스 제공, 문제 해결
        ([3], "")      # 4단계: AI·로봇과 사람의 협업
    ]
    
    for step, (choices, custom) in enumerate(test_responses, 1):
        if not tester.submit_step_response(step, choices, custom):
            print(f"❌ {step}단계 제출 실패, 테스트 중단")
            return False
        time.sleep(0.5)  # API 호출 간격
    
    # 5단계: 진로 추천 생성
    if not tester.generate_recommendation():
        print("❌ 진로 추천 생성 실패, 테스트 중단")
        return False
    
    # 5단계: 수정 기능 테스트
    print("\n🔄 5단계 수정 기능 테스트")
    if not tester.modify_dream():
        print("❌ 꿈 수정 실패")
        return False
    
    # 5단계: 꿈 확정
    if not tester.confirm_dream():
        print("❌ 꿈 확정 실패, 테스트 중단")
        return False
    
    # 6단계: 드림로직 생성
    if not tester.generate_dream_logic():
        print("❌ 드림로직 생성 실패, 테스트 중단")
        return False
    
    # 세션 요약
    if not tester.get_session_summary():
        print("❌ 세션 요약 조회 실패")
        return False
    
    print(f"\n🎉 전체 테스트 완료!")
    print(f"📋 세션 ID: {tester.session_id}")
    print(f"🎯 최종 꿈: {tester.final_dream}")
    print(f"📝 드림로직 생성: {'완료' if tester.dream_logic else '실패'}")
    
    return True

def run_specific_tests():
    """특정 기능 개별 테스트"""
    print("\n" + "="*60)
    print("🔧 특정 기능 개별 테스트")
    print("="*60)
    
    tester = MiddleSchoolCareerTester()
    
    # 세션 시작
    if not tester.start_session("테스트용"):
        return False
    
    # 빠른 1-4단계 완료
    quick_responses = [([1], ""), ([1], ""), ([1], ""), ([1], "")]
    for step, (choices, custom) in enumerate(quick_responses, 1):
        tester.submit_step_response(step, choices, custom)
    
    # 5단계 수정 기능 집중 테스트
    print("\n🎯 5단계 수정 기능 집중 테스트")
    
    # 첫 번째 추천
    tester.generate_recommendation()
    first_recommendation = tester.ai_recommendation
    
    # 수정 요청
    tester.modify_dream()
    second_recommendation = tester.ai_recommendation
    
    # 결과 비교
    if first_recommendation != second_recommendation:
        print("✅ 수정 기능 정상: 다른 추천이 생성됨")
        print(f"🔹 첫 번째: {first_recommendation}")
        print(f"🔹 두 번째: {second_recommendation}")
    else:
        print("⚠️  수정 기능 주의: 동일한 추천이 생성됨")
    
    # 꿈 확정 후 6단계 테스트
    tester.confirm_dream()
    
    # 6단계 드림로직 여러 번 테스트
    print("\n🎯 6단계 드림로직 안정성 테스트")
    for i in range(3):
        print(f"\n📝 {i+1}차 드림로직 생성 테스트")
        success = tester.generate_dream_logic()
        if success and tester.dream_logic:
            is_fallback = "기초 실력 쌓기" in tester.dream_logic
            print(f"결과: {'Fallback' if is_fallback else 'AI 생성'}")
        else:
            print("❌ 생성 실패")
        time.sleep(1)

if __name__ == "__main__":
    print("중학교 진로탐색 서비스 테스트 프로그램")
    print("서버가 http://127.0.0.1:8000 에서 실행 중인지 확인하세요.")
    
    choice = input("\n테스트 선택 (1: 전체 플로우, 2: 특정 기능, 3: 둘 다): ")
    
    if choice == "1":
        run_full_test()
    elif choice == "2":
        run_specific_tests()
    elif choice == "3":
        run_full_test()
        run_specific_tests()
    else:
        print("잘못된 선택입니다.")