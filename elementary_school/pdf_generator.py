"""
초등학생 진로 탐색 PDF 생성기 (웹 스타일 적용)
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

from .models import CareerStage


class ElementaryCareerPDFGenerator:
    """초등학생 진로 탐색 PDF 생성기"""
    
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
    
    def _create_web_like_styles(self) -> Dict:
        """웹페이지와 유사한 스타일 생성"""
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
            
            # 드림로직 스타일
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
                parent=styles['Heading3'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=6,
                spaceBefore=8,
                textColor=colors.HexColor('#1e40af'),
                borderWidth=1,
                borderColor=colors.HexColor('#3b82f6'),
                borderPadding=4,
                backColor=colors.HexColor('#dbeafe')
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
            ),
            
            'dream_item': ParagraphStyle(
                'DreamItem',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=8,
                spaceAfter=2,
                spaceBefore=1,
                leftIndent=30,
                textColor=colors.HexColor('#6b7280')
            )
        }
        
        return custom_styles
    
    def generate_career_report(self, student_name: str, responses: Dict[CareerStage, Dict], 
                             final_recommendation: str, dream_logic_result: str = "", 
                             encouragement_message: str = "") -> bytes:
        """진로 탐색 PDF 보고서 생성"""
        
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
            
            # 문서 내용 구성
            story = []
            
            # 제목
            story.append(Paragraph("🎓 초등학생 진로 탐색 결과", self.styles['title']))
            story.append(Spacer(1, 20))
            """
            # AI 추천 진로
            story.append(Paragraph("🎯 AI가 추천하는 맞춤 진로", self.styles['heading']))
            story.append(Paragraph(final_recommendation, self.styles['result']))
            story.append(Spacer(1, 15))
            """
            # 드림로직 결과
            if dream_logic_result:
                #story.append(Paragraph("🌈 드림로직 - 꿈 실현 계획", self.styles['heading']))
                story.append(Spacer(1, 8))
                
                dream_elements = self._format_dream_logic(dream_logic_result)
                story.extend(dream_elements)
                story.append(Spacer(1, 15))
            """
            # 응원 메시지
            if encouragement_message:
                story.append(Paragraph("💝 AI가 보내는 특별한 응원 메시지", self.styles['heading']))
                story.append(Spacer(1, 8))
                story.append(Paragraph(encouragement_message, self.styles['result']))
                story.append(Spacer(1, 15))
            """
            # PDF 빌드
            doc.build(story)
            
            # 생성된 PDF 파일 읽기
            with open(tmp_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            return pdf_content
            
        except Exception as e:
            raise Exception(f"PDF 생성 중 오류 발생: {str(e)}")
        finally:
            # 임시 파일 정리
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _format_answer(self, response_data: Dict, stage: CareerStage) -> str:
        """응답 데이터를 텍스트로 포맷팅"""
        choice_numbers = response_data.get("choice_numbers", [])
        custom_answer = response_data.get("custom_answer", "")
        
        # 기타 선택지인 경우 커스텀 답변 반환
        if custom_answer:
            return custom_answer
        
        # 선택지 번호가 있는 경우 해당 텍스트 반환
        if choice_numbers:
            return f"선택지 {', '.join(map(str, choice_numbers))}"
        
        # response 키로 직접 답변이 있는 경우
        if "response" in response_data:
            return response_data["response"]
        
        return "답변 없음"
    
    def _format_dream_logic(self, dream_logic_text: str) -> list:
        """드림로직 텍스트를 구조화된 PDF 요소로 변환"""
        story_elements = []
        
        if not dream_logic_text:
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
                story_elements.append(Spacer(1, 3))
            
            # 세부 항목 (들여쓰기된 것들)
            elif line.startswith(('  ', '\t')):
                story_elements.append(Paragraph(line, self.styles['dream_item']))
                story_elements.append(Spacer(1, 2))
            
            # 일반 텍스트
            else:
                story_elements.append(Paragraph(line, self.styles['dream_activity']))
                story_elements.append(Spacer(1, 4))
        
        return story_elements