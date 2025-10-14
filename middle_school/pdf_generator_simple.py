"""
중학생 진로 탐색 PDF 생성기 (단순화 버전)
elementary_school 버전을 기반으로 한 안정적인 구현
"""

import tempfile
import os
from typing import Dict
from datetime import datetime, timezone, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models import CareerStage


class MiddleSchoolCareerPDFGenerator:
    """중학생 진로 탐색 PDF 생성기"""
    
    def __init__(self):
        """PDF 생성기 초기화"""
        self.font_name = self._register_korean_font()
        print(f"🔤 최종 사용 폰트: {self.font_name}")
    
    def _register_korean_font(self) -> str:
        """한글 폰트 등록"""
        try:
            # 프로젝트 내 폰트 파일 경로
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf')
            
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
                print(f"✅ 폰트 등록 성공: {font_path} → NanumGothic")
                return 'NanumGothic'
            else:
                print(f"⚠️ 폰트 파일을 찾을 수 없음: {font_path}")
                return 'Helvetica'  # 기본 폰트로 폴백
                
        except Exception as e:
            print(f"❌ 폰트 등록 실패: {e}")
            return 'Helvetica'  # 기본 폰트로 폴백
    
    def _create_styles(self) -> Dict:
        """스타일 생성"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            # 기본 제목
            'title': ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName=self.font_name,
                fontSize=18,
                spaceAfter=15,
                spaceBefore=10,
                alignment=1,  # 중앙 정렬
                textColor=colors.HexColor('#1e40af')
            ),
            
            # 헤딩 스타일
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.HexColor('#059669')
            ),
            
            # 일반 텍스트
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=6,
                leading=14,
                textColor=colors.HexColor('#374151')
            ),
            
            # 결과 스타일
            'result': ParagraphStyle(
                'Result',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=8,
                spaceBefore=6,
                textColor=colors.HexColor('#6366f1'),
                leftIndent=15
            ),
            
            # 인포 텍스트
            'info': ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
                textColor=colors.HexColor('#6b7280'),
                alignment=1
            )
        }
        
        return custom_styles
    
    def generate_career_report(self, session_data, output_path=None):
        """진로 탐색 결과 PDF 생성"""
        try:
            print(f"🔄 PDF 생성 시작")
            
            # 임시 파일 생성
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix='.pdf',
                    prefix='middle_school_career_'
                )
                output_path = temp_file.name
                temp_file.close()
            
            print(f"📄 PDF 경로: {output_path}")
            
            # 간단한 PDF 문서 생성
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # 스타일 생성
            styles = self._create_styles()
            
            # 스토리 생성
            story = []
            
            # 제목
            story.append(Paragraph("중학생 진로 탐색 결과", styles['title']))
            story.append(Spacer(1, 20))
            
            # 학생 정보
            student_name = session_data.get('student_name', '학생')
            story.append(Paragraph(f"학생명: {student_name}", styles['normal']))
            story.append(Spacer(1, 10))
            
            # 생성 일자
            kst = timezone(timedelta(hours=9))
            current_time = datetime.now(kst)
            date_str = current_time.strftime("%Y년 %m월 %d일 %H:%M")
            story.append(Paragraph(f"생성일: {date_str}", styles['info']))
            story.append(Spacer(1, 20))
            
            # 진로 탐색 요약
            story.append(Paragraph("진로 탐색 요약", styles['heading']))
            story.append(Spacer(1, 10))
            
            # 최종 진로 목표
            final_career = session_data.get('final_career_goal', '')
            if final_career:
                story.append(Paragraph(f"최종 진로 목표: {final_career}", styles['result']))
                story.append(Spacer(1, 10))
            
            # 드림로직 결과
            dream_logic = session_data.get('dream_logic_result', '')
            if dream_logic:
                story.append(Paragraph("나만의 드림로직", styles['heading']))
                story.append(Spacer(1, 10))
                
                # 드림로직을 줄별로 분리하여 처리
                lines = dream_logic.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # 특수 문자 처리
                        clean_line = line.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        story.append(Paragraph(clean_line, styles['normal']))
                        story.append(Spacer(1, 4))
                
                story.append(Spacer(1, 15))
            
            # 응원 메시지
            encouragement = session_data.get('encouragement_message', '')
            if encouragement:
                story.append(Paragraph("AI의 응원 메시지", styles['heading']))
                story.append(Spacer(1, 10))
                
                # 응원 메시지 처리
                clean_encouragement = encouragement.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                story.append(Paragraph(clean_encouragement, styles['result']))
                story.append(Spacer(1, 20))
            
            # 푸터
            story.append(Spacer(1, 30))
            story.append(Paragraph("꿈을 향한 첫걸음을 응원합니다!", styles['info']))
            
            print("🔨 PDF 빌드 중...")
            doc.build(story)
            
            print(f"✅ PDF 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ PDF 생성 실패: {str(e)}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
            raise


# 전역 PDF 생성기 인스턴스
pdf_generator = MiddleSchoolCareerPDFGenerator()