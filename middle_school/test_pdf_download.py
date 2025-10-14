#!/usr/bin/env python3
"""
중학교 진로탐색 PDF 다운로드 기능 테스트
"""

import requests
import json
import time
import os

# 서버 URL
BASE_URL = "http://localhost:8000"

def test_pdf_download():
    """PDF 다운로드 기능 전체 테스트"""
    print("🎯 중학교 진로탐색 PDF 다운로드 테스트 시작")
    
    # 1. 세션 생성
    print("\n1️⃣ 세션 생성")
    create_response = requests.post(f"{BASE_URL}/create-session")
    session_data = create_response.json()
    session_id = session_data["session_id"]
    print(f"✅ 세션 생성됨: {session_id}")
    
    # 2. 학생 정보 제출
    print("\n2️⃣ 학생 정보 제출")
    student_info = {
        "name": "테스트학생",
        "school": "테스트중학교",
        "grade": 2,
        "gender": "남",
        "region": "서울특별시"
    }
    
    info_response = requests.post(
        f"{BASE_URL}/submit-student-info/{session_id}",
        json=student_info
    )
    print(f"✅ 학생 정보 제출 완료")
    
    # 3. 1-4단계 빠르게 진행
    stages_data = {
        "STAGE_1": {
            "question_1": "게임 개발",
            "question_2": "새로운 기술 배우기",
            "question_3": "창의적인 문제 해결"
        },
        "STAGE_2": {
            "question_1": "논리적 사고력",
            "question_2": "집중력",
            "question_3": "창의성"
        },
        "STAGE_3": {
            "question_1": "창의성과 혁신",
            "question_2": "개인의 성장",
            "question_3": "사회적 기여"
        },
        "STAGE_4": {
            "question_1": "인공지능과 로봇",
            "question_2": "게임 및 엔터테인먼트",
            "question_3": "교육 기술"
        }
    }
    
    for stage, responses in stages_data.items():
        print(f"\n3️⃣ {stage} 진행")
        stage_response = requests.post(
            f"{BASE_URL}/submit-stage/{session_id}",
            json={
                "stage": stage,
                "responses": responses
            }
        )
        print(f"✅ {stage} 완료")
        time.sleep(0.5)
    
    # 4. 5단계 AI 추천 받기
    print("\n4️⃣ 5단계 AI 추천 생성")
    recommendation_response = requests.post(
        f"{BASE_URL}/get-recommendation/{session_id}",
        json={"regenerate": False}
    )
    recommendation_data = recommendation_response.json()
    print(f"✅ AI 추천 생성 완료")
    print(f"추천 직업: {recommendation_data['career_title']}")
    
    # 5. 5단계 꿈 확정
    print("\n5️⃣ 꿈 확정")
    confirm_response = requests.post(
        f"{BASE_URL}/dream-confirm/{session_id}",
        json={
            "action": "confirm",
            "dream_statement": f"나는 {recommendation_data['career_title']}가 되고 싶다"
        }
    )
    print(f"✅ 꿈 확정 완료")
    
    # 6. 6단계 진행
    print("\n6️⃣ 6단계 진행")
    next_stage_response = requests.post(
        f"{BASE_URL}/next-stage/{session_id}",
        json={"stage": "STAGE_6"}
    )
    stage6_data = next_stage_response.json()
    
    # 6단계 응답 제출
    stage6_responses = {
        "question_1": "매일 30분 프로그래밍 공부하기",
        "question_2": "학교 컴퓨터 동아리 활동하기", 
        "question_3": "월 1회 IT 전시회 관람하기"
    }
    
    stage6_submit = requests.post(
        f"{BASE_URL}/submit-stage/{session_id}",
        json={
            "stage": "STAGE_6",
            "responses": stage6_responses
        }
    )
    print(f"✅ 6단계 완료")
    
    # 7. PDF 다운로드 테스트
    print("\n7️⃣ PDF 다운로드 테스트")
    try:
        pdf_response = requests.post(
            f"{BASE_URL}/download-pdf",
            data={"session_id": session_id}
        )
        
        if pdf_response.status_code == 200:
            # PDF 파일 저장
            pdf_filename = f"test_career_report_{int(time.time())}.pdf"
            with open(pdf_filename, 'wb') as f:
                f.write(pdf_response.content)
            
            file_size = os.path.getsize(pdf_filename)
            print(f"✅ PDF 다운로드 성공!")
            print(f"📄 파일명: {pdf_filename}")
            print(f"📊 파일 크기: {file_size:,} bytes")
            
            # Content-Type 확인
            content_type = pdf_response.headers.get('content-type', '')
            print(f"📋 Content-Type: {content_type}")
            
            return True
        else:
            print(f"❌ PDF 다운로드 실패: {pdf_response.status_code}")
            print(f"응답: {pdf_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PDF 다운로드 예외 발생: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 중학교 진로탐색 PDF 다운로드 테스트")
    print("=" * 50)
    
    try:
        # 서버 연결 확인
        health_response = requests.get(f"{BASE_URL}/")
        if health_response.status_code != 200:
            print(f"❌ 서버 연결 실패: {BASE_URL}")
            return
        
        # PDF 다운로드 테스트 실행
        success = test_pdf_download()
        
        if success:
            print("\n🎉 모든 테스트 성공!")
        else:
            print("\n💥 테스트 실패")
            
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {str(e)}")

if __name__ == "__main__":
    main()