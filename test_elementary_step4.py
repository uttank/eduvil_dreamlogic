"""
Elementary School Step 4 AI 이슈 생성 기능 테스트
"""

import asyncio
import sys
import os

# elementary_school 모듈을 import하기 위한 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'elementary_school'))

from elementary_school.career_service import career_service
from elementary_school.models import CareerStage, StudentInfo, StepResponse
from elementary_school.openai_service import ai_service

async def test_step4_ai_issues():
    """Step 4 AI 이슈 생성 기능 테스트"""
    
    print("=" * 80)
    print("🧪 Elementary School Step 4 AI 이슈 생성 테스트 시작")
    print("=" * 80)
    
    # 1. 세션 생성
    print("\n1️⃣ 세션 생성...")
    session_id = career_service.create_session()
    print(f"✅ 세션 ID: {session_id}")
    
    # 2. 학생 정보 설정
    print("\n2️⃣ 학생 정보 설정...")
    student_info = StudentInfo(
        name="김예진",
        grade=6,
        school="테스트초등학교"
    )
    
    # 3. 1~3단계 응답 생성 (예제 응답)
    print("\n3️⃣ 1~3단계 응답 생성...")
    
    # Step 1: 흥미 (만화 그리기, 캐릭터 만들기)
    step1_response = StepResponse(choice_numbers=[1, 3], custom_answer=None)  # 1: 그림, 3: 만들기
    career_service.submit_response(session_id, student_info, step1_response)
    
    # Step 2: 장점 (창의성)
    step2_response = StepResponse(choice_numbers=[7], custom_answer=None)  # 7: 아이디어가 톡톡
    success, message, next_stage = career_service.submit_response(session_id, None, step2_response)
    print(f"Step 2 결과: {success}, {message}, 다음 단계: {next_stage}")
    
    # Step 3: 가치관 (새로운 것 만들기)
    step3_response = StepResponse(choice_numbers=[2], custom_answer=None)  # 2: 새로운 것을 만들 때 행복
    success, message, next_stage = career_service.submit_response(session_id, None, step3_response)
    print(f"Step 3 결과: {success}, {message}, 다음 단계: {next_stage}")
    
    # 4. 세션 상태 확인
    print("\n4️⃣ 세션 상태 확인...")
    session = career_service.get_session(session_id)
    
    if not session:
        print("❌ 세션을 찾을 수 없습니다.")
        return False
        
    print(f"현재 단계: {session.current_stage}")
    print(f"완료된 단계: {session.completed_stages}")
    
    # 5. AI 이슈 생성 테스트
    if ai_service:
        print("\n5️⃣ AI 이슈 생성 테스트...")
        
        # 응답 데이터를 딕셔너리로 변환
        responses_dict = {
            stage: response.dict() 
            for stage, response in session.responses.items()
        }
        
        print("입력 데이터:")
        for stage, response in responses_dict.items():
            print(f"  {stage}: {response}")
        
        # 첫 번째 이슈 생성
        print("\n🤖 첫 번째 이슈 생성...")
        issues = ai_service.generate_step4_issues(
            student_name=student_info.name,
            responses=responses_dict,
            regenerate=False
        )
        
        print(f"✅ 생성된 이슈 개수: {len(issues)}")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        # 재생성 테스트
        print("\n🔄 이슈 재생성 테스트...")
        regenerated_issues = ai_service.generate_step4_issues(
            student_name=student_info.name,
            responses=responses_dict,
            regenerate=True
        )
        
        print(f"✅ 재생성된 이슈 개수: {len(regenerated_issues)}")
        for i, issue in enumerate(regenerated_issues, 1):
            print(f"  {i}. {issue}")
        
        # 세션에 이슈 저장
        session.step4_ai_issues = issues
        session.step4_regeneration_count = 1
        career_service.sessions[session_id] = session
        
        print("\n✅ 세션에 이슈 저장 완료")
        
    else:
        print("\n❌ AI 서비스가 사용 불가능합니다.")
        return False
    
    # 6. Step 4 선택 시뮬레이션
    print("\n6️⃣ Step 4 선택 시뮬레이션...")
    
    # 첫 번째 이슈 선택
    selected_issue_num = 1
    selected_issue = session.step4_ai_issues[selected_issue_num - 1]
    
    print(f"선택된 이슈: {selected_issue_num}번")
    print(f"내용: {selected_issue}")
    
    # Step 4 응답 생성 및 제출
    step4_response = StepResponse(
        choice_numbers=[selected_issue_num],
        custom_answer=selected_issue
    )
    
    success, message, next_stage = career_service.submit_response(
        session_id, None, step4_response
    )
    
    print(f"Step 4 제출 결과: {success}")
    print(f"메시지: {message}")
    print(f"다음 단계: {next_stage}")
    
    # 7. 최종 결과 확인
    print("\n7️⃣ 최종 세션 상태...")
    final_session = career_service.get_session(session_id)
    
    if not final_session:
        print("❌ 최종 세션을 찾을 수 없습니다.")
        return False
        
    print(f"현재 단계: {final_session.current_stage}")
    print(f"완료된 단계: {final_session.completed_stages}")
    print(f"저장된 이슈들: {len(final_session.step4_ai_issues) if final_session.step4_ai_issues else 0}개")
    print(f"재생성 횟수: {final_session.step4_regeneration_count}")
    
    # Step 4 응답 확인
    if CareerStage.STEP_4 in final_session.responses:
        step4_final_response = final_session.responses[CareerStage.STEP_4]
        print(f"Step 4 최종 응답: {step4_final_response.dict()}")
    
    print("\n" + "=" * 80)
    print("🎉 Step 4 AI 이슈 생성 테스트 완료!")
    print("=" * 80)
    
    return True

def test_fallback_scenario():
    """AI 서비스 없이 Fallback 시나리오 테스트"""
    
    print("\n" + "=" * 80)
    print("🧪 Fallback 시나리오 테스트 시작")
    print("=" * 80)
    
    if ai_service:
        # Fallback 메서드 직접 호출
        fallback_issues = ai_service._get_fallback_step4_issues("테스트학생")
        
        print("Fallback 이슈들:")
        for i, issue in enumerate(fallback_issues, 1):
            print(f"  {i}. {issue}")
        
        print(f"✅ Fallback 이슈 개수: {len(fallback_issues)}")
    else:
        print("❌ AI 서비스가 없어서 Fallback 테스트를 건너뜁니다.")

if __name__ == "__main__":
    print("🚀 Elementary School Step 4 AI 이슈 생성 테스트 프로그램")
    
    try:
        # 메인 테스트 실행
        success = asyncio.run(test_step4_ai_issues())
        
        # Fallback 테스트
        test_fallback_scenario()
        
        if success:
            print("\n🎊 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("\n⚠️ 일부 테스트에서 문제가 발생했습니다.")
            
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()