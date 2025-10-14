#!/usr/bin/env python3
"""
간단한 PDF 생성 테스트 스크립트
"""
import os
from pdf_generator_elementary_style import MiddleSchoolCareerPDFGenerator


def main():
    print("PDF 생성기 테스트 시작")
    gen = MiddleSchoolCareerPDFGenerator()

    student_name = "테스트학생"
    responses = {}
    final_recommendation = "게임 개발자"
    dream_logic = "[중간목표 1]\n설명: 코딩 실력 향상 / 프로젝트 경험 쌓기\n실천활동(학교): 컴퓨터 동아리 활동 / 알고리즘 대회 참가\n실천활동(일상): 매일 코딩 30분 / 오픈소스 기여"
    encouragement = "너의 노력이 큰 변화를 만듭니다!"

    out_path = gen.generate_career_report(
        student_name=student_name,
        responses=responses,
        final_recommendation=final_recommendation,
        dream_logic_result=dream_logic,
        encouragement_message=encouragement
    )

    # out_path may be bytes (elementary style returns bytes), so handle both
    if isinstance(out_path, bytes):
        filename = 'test_output.pdf'
        with open(filename, 'wb') as f:
            f.write(out_path)
        print(f"PDF 바이트를 파일로 저장했습니다: {filename}")
    else:
        print(f"PDF 생성됨: {out_path}")


if __name__ == '__main__':
    main()
