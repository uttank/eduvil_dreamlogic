"""
중학생 진로 탐색 PDF 생성기 (elementary_school 방식 적용)
"""

import tempfile
import os
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import CareerStage


class MiddleSchoolCareerPDFGenerator:
    """중학생 진로 탐색 PDF 생성기 (elementary_school 방식)"""
    
    def __init__(self):
        """PDF 생성기 초기화"""
        self.font_name = self._register_korean_font()
        self.styles: Optional[Dict] = None
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
    
    def _create_web_like_styles(self) -> Dict:
        """웹페이지와 유사한 스타일 생성 (elementary_school 완전 적용)"""
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
                textColor=colors.HexColor('#1e40af'),
                borderWidth=1,
                borderColor=colors.HexColor('#3b82f6'),
                borderPadding=6,
                backColor=colors.HexColor('#eff6ff')
            ),
            
            # 헤딩 스타일
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.HexColor('#059669'),
                borderWidth=1,
                borderColor=colors.HexColor('#10b981'),
                borderPadding=4,
                backColor=colors.HexColor('#d1fae5')
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
                textColor=colors.HexColor('#1f2937'),
                borderWidth=1,
                borderColor=colors.HexColor('#6b7280'),
                borderPadding=6,
                backColor=colors.HexColor('#f9fafb')
            ),
            
            # 인포 텍스트
            'info': ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
                textColor=colors.HexColor('#6b7280'),
                alignment=1
            ),
            
            # 드림로직 관련 스타일들 (elementary_school 완전 적용)
            'dream_title': ParagraphStyle(
                'DreamTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=10,
                spaceBefore=12,
                textColor=colors.HexColor('#7c2d12'),
                alignment=1,
                borderWidth=1,
                borderColor=colors.HexColor('#ea580c'),
                borderPadding=6,
                backColor=colors.HexColor('#fff7ed')
            ),
            
            'dream_goal': ParagraphStyle(
                'DreamGoal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=8,
                spaceBefore=6,
                textColor=colors.HexColor('#be185d'),
                alignment=1,
                borderWidth=2,
                borderColor=colors.HexColor('#ec4899'),
                borderPadding=8,
                backColor=colors.HexColor('#fdf2f8')
            ),
            
            'dream_section': ParagraphStyle(
                'DreamSection',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=6,
                spaceBefore=4,
                textColor=colors.HexColor('#065f46'),
                borderWidth=1,
                borderColor=colors.HexColor('#059669'),
                borderPadding=4,
                backColor=colors.HexColor('#d1fae5')
            ),
            
            'dream_activity': ParagraphStyle(
                'DreamActivity',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
                spaceAfter=4,
                spaceBefore=3,
                leftIndent=15,
                textColor=colors.HexColor('#374151'),
                borderWidth=1,
                borderColor=colors.HexColor('#e5e7eb'),
                borderPadding=4,
                backColor=colors.HexColor('#f9fafb')
            )
        }
        
        return custom_styles
    
    def generate_career_report(self, student_name: str, responses: Optional[Dict] = None, 
                             final_recommendation: str = "", dream_logic_result: str = "", 
                             encouragement_message: str = "") -> bytes:
        """진로 탐색 PDF 보고서 생성 (elementary_school 방식과 동일한 시그니처)"""
        
        # 웹 스타일 초기화
        self.styles = self._create_web_like_styles()
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # PDF 문서 생성
            doc = SimpleDocTemplate(
                tmp_path,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # 스토리 생성
            story = []
            
            # 제목
            story.append(Paragraph("중학생 진로 탐색 결과", self.styles['title']))
            story.append(Spacer(1, 20))
            
            # 학생 정보
            story.append(Paragraph(f"학생명: {student_name}", self.styles['normal']))
            story.append(Spacer(1, 10))
            
            # 생성 일자
            kst = timezone(timedelta(hours=9))
            current_time = datetime.now(kst)
            date_str = current_time.strftime("%Y년 %m월 %d일 %H:%M")
            story.append(Paragraph(f"생성일: {date_str}", self.styles['info']))
            story.append(Spacer(1, 20))
            
            # 최종 추천 결과
            """
            if final_recommendation:
                story.append(Paragraph("AI 추천 진로", self.styles['heading']))
                story.append(Spacer(1, 10))
                story.append(Paragraph(final_recommendation, self.styles['result']))
                story.append(Spacer(1, 15))
            """
            # 드림로직 결과
            if dream_logic_result:
                #story.append(Paragraph("나만의 드림로직", self.styles['heading']))
                #story.append(Spacer(1, 10))
                
                # 드림로직 포맷팅
                dream_elements = self._format_dream_logic(dream_logic_result)
                story.extend(dream_elements)
                story.append(Spacer(1, 15))
            
            # 응원 메시지
            """
            if encouragement_message:
                story.append(Paragraph("AI의 응원 메시지", self.styles['heading']))
                story.append(Spacer(1, 10))
                story.append(Paragraph(encouragement_message, self.styles['result']))
                story.append(Spacer(1, 20))
            """
            # 푸터
            story.append(Spacer(1, 30))
            story.append(Paragraph("꿈을 향한 첫걸음을 응원합니다!", self.styles['info']))
            
            # PDF 빌드
            doc.build(story)
            
            # 파일 읽기
            with open(tmp_path, 'rb') as f:
                pdf_content = f.read()
            
            print(f"✅ PDF 생성 완료: {len(pdf_content)} bytes")
            return pdf_content
            
        except Exception as e:
            print(f"❌ PDF 생성 실패: {str(e)}")
            raise
        finally:
            # 임시 파일 삭제
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def _format_dream_logic(self, dream_logic_text: str) -> list:
        """드림로직 텍스트를 구조화된 PDF 요소로 변환 (elementary_school 방식)"""
        story_elements = []
        
        if not dream_logic_text or not self.styles:
            return story_elements
            
        lines = dream_logic_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 제목이나 헤더 (대괄호로 둘러싸인 부분)
            if line.startswith('[') and line.endswith(']'):
                story_elements.append(Paragraph(line, self.styles['dream_title']))
                story_elements.append(Spacer(1, 6))
            
            # 최종꿈 (꿈: 또는 최종꿈: 으로 시작)
            elif line.startswith(('최종꿈:', '꿈:')):
                story_elements.append(Paragraph(line, self.styles['dream_goal']))
                story_elements.append(Spacer(1, 8))
            
            # 중간목표
            elif '중간목표' in line or '[중간목표' in line:
                story_elements.append(Paragraph(line, self.styles['dream_section']))
                story_elements.append(Spacer(1, 6))
            
            # 실천활동 (• 또는 - 로 시작)
            elif line.startswith(('•', '-', '・')):
                story_elements.append(Paragraph(line, self.styles['dream_activity']))
                story_elements.append(Spacer(1, 4))
            
            # 기타 일반 텍스트
            else:
                story_elements.append(Paragraph(line, self.styles['normal']))
                story_elements.append(Spacer(1, 4))
        
        return story_elements


# 전역 PDF 생성기 인스턴스
pdf_generator = MiddleSchoolCareerPDFGenerator()