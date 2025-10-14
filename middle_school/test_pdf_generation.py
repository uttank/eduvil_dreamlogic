#!/usr/bin/env python3
"""
중학교 진로탐색 PDF 생성 테스트
elementary_school 방식 적용 후 테스트
"""

import requests
import json
import time
import os

# 서버 URL
BASE_URL = "http://localhost:8000"

def test_pdf_generation_elementary_style():
    """elementary_school 방식 PDF 생성 테스트"""
    print("🎯 중학교 진로탐색 PDF 생성 테스트 (elementary_school 방식)")
    print("=" * 60)
    
    # PDF 다운로드 요청 데이터 (elementary_school과 동일한 형식)
    pdf_request_data = {
        "student_name": "김민수",
        "responses": {
            "STAGE_1": {
                "question_1": "게임 개발",
                "question_2": "새로운 기술 배우기",
                "question_3": "창의적인 문제 해결"
            },
            "STAGE_2": {
                "question_1": "논리적 사고력",
                "question_2": "집중력",
                "question_3": "창의성"
            }
        },
        "final_recommendation": "게임 개발자가 되어 창의적인 게임을 만들고, 사람들에게 즐거움을 주는 것이 나의 꿈이다.",
        "dream_logic_result": """[중간목표 1] 프로그래밍 기초 다지기
설명: 게임 개발의 핵심인 프로그래밍 언어를 배워보자

실천활동(학교): 컴퓨터 동아리 참여 / 정보 시간 적극 참여
실천활동(일상): 매일 30분 코딩 연습 / 온라인 프로그래밍 강의 수강
추천 활동: 스크래치로 간단한 게임 만들기

[중간목표 2] 게임 기획 능력 키우기
설명: 재미있는 게임을 만들기 위한 기획 능력을 기르자

실천활동(학교): 미술 시간에 캐릭터 디자인하기 / 국어 시간에 스토리 구성 연습
실천활동(일상): 다양한 게임 플레이하며 분석하기 / 게임 아이디어 노트 작성
추천 활동: 보드게임 만들어보기""",
        "encouragement_message": "민수야, 게임 개발자의 꿈을 향해 한 걸음씩 나아가고 있구나! 🎮 매일 조금씩 코딩을 연습하고, 창의적인 아이디어를 기록하다 보면 분명 멋진 게임 개발자가 될 수 있을 거야. 포기하지 말고 꾸준히 도전해보자!"
    }
    
    try:
        print("📋 PDF 생성 요청 데이터:")
        print(f"  - 학생명: {pdf_request_data['student_name']}")
        print(f"  - 최종 추천: {pdf_request_data['final_recommendation'][:50]}...")
        print(f"  - 드림로직 길이: {len(pdf_request_data['dream_logic_result'])} 문자")
        print(f"  - 응원 메시지 길이: {len(pdf_request_data['encouragement_message'])} 문자")
        
        print("\n🔄 PDF 생성 요청 중...")
        
        # PDF 생성 요청
        response = requests.post(
            f"{BASE_URL}/career/download-pdf",
            json=pdf_request_data,
            timeout=30
        )
        
        print(f"📊 응답 상태: {response.status_code}")
        print(f"📋 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            # PDF 파일 저장
            timestamp = int(time.time())
            pdf_filename = f"test_middle_school_career_{timestamp}.pdf"
            
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            actual_file_size = os.path.getsize(pdf_filename)
            
            print(f"✅ PDF 생성 성공!")
            print(f"📄 파일명: {pdf_filename}")
            print(f"📊 콘텐츠 크기: {file_size:,} bytes")
            print(f"📊 파일 크기: {actual_file_size:,} bytes")
            
            # Content-Type 확인
            content_type = response.headers.get('content-type', '')
            print(f"📋 Content-Type: {content_type}")
            
            # 파일이 실제 PDF인지 확인
            with open(pdf_filename, 'rb') as f:
                header = f.read(8)
                if header.startswith(b'%PDF'):
                    print("✅ 유효한 PDF 파일입니다!")
                else:
                    print(f"⚠️ PDF 헤더가 아닙니다: {header}")
            
            return True
            
        else:
            print(f"❌ PDF 생성 실패: {response.status_code}")
            print(f"📋 응답 내용: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ 요청 시간 초과 (30초)")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 서버 연결 실패 - 서버가 실행 중인지 확인해주세요")
        return False
    except Exception as e:
        print(f"❌ 예외 발생: {type(e).__name__}: {str(e)}")
        return False

def test_direct_pdf_generator():
    """PDF 생성기 직접 테스트"""
    print("\n" + "=" * 60)
    print("🔧 PDF 생성기 직접 테스트")
    print("=" * 60)
    
    try:
        # 직접 import 테스트
        import sys
        sys.path.append('/Users/yhpark/work/openai/career_dev/middle_school')
        
        from pdf_generator_elementary_style import pdf_generator
        
        print("✅ PDF 생성기 import 성공")
        
        # 직접 PDF 생성 테스트
        test_data = {
            "student_name": "테스트학생",
            "final_recommendation": "테스트 직업",
            "dream_logic_result": "테스트 드림로직\n[중간목표 1] 테스트 목표",
            "encouragement_message": "테스트 응원 메시지"
        }
        
        print("🔄 PDF 생성 중...")
        pdf_content = pdf_generator.generate_career_report(
            student_name=test_data["student_name"],
            responses={},
            final_recommendation=test_data["final_recommendation"],
            dream_logic_result=test_data["dream_logic_result"],
            encouragement_message=test_data["encouragement_message"]
        )
        
        print(f"✅ PDF 생성 성공! 크기: {len(pdf_content):,} bytes")
        
        # 파일 저장
        timestamp = int(time.time())
        filename = f"direct_test_{timestamp}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_content)
        
        print(f"📄 파일 저장: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 직접 테스트 실패: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📋 스택 트레이스:\n{traceback.format_exc()}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 중학교 진로탐색 PDF 생성 테스트")
    print("=" * 60)
    
    # 1. 직접 PDF 생성기 테스트
    direct_success = test_direct_pdf_generator()
    
    if not direct_success:
        print("\n💥 PDF 생성기 직접 테스트 실패 - API 테스트 건너뛰기")
        return
    
    # 2. 서버 연결 확인
    try:
        health_response = requests.get(f"{BASE_URL}/", timeout=5)
        if health_response.status_code != 200:
            print(f"\n❌ 서버 연결 실패: {BASE_URL}")
            print("서버를 실행해주세요: python middle_school.py")
            return
    except:
        print(f"\n❌ 서버 연결 실패: {BASE_URL}")
        print("서버를 실행해주세요: python middle_school.py")
        return
    
    print(f"\n✅ 서버 연결 확인: {BASE_URL}")
    
    # 3. API를 통한 PDF 생성 테스트
    api_success = test_pdf_generation_elementary_style()
    
    # 결과 요약
    print(f"\n📊 테스트 결과 요약:")
    print(f"  - 직접 PDF 생성: {'✅ 성공' if direct_success else '❌ 실패'}")
    print(f"  - API PDF 생성: {'✅ 성공' if api_success else '❌ 실패'}")
    
    if direct_success and api_success:
        print("\n🎉 모든 테스트 성공!")
    elif direct_success:
        print("\n⚠️ 직접 생성은 성공했지만 API에 문제가 있습니다.")
    else:
        print("\n💥 PDF 생성에 문제가 있습니다.")

if __name__ == "__main__":
    main()