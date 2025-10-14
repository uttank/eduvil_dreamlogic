"""
중학생 진로 탐색 PDF 생성기
웹페이지 스타일을 반영한 한글 PDF 생성
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
from reportlab.rl_config import defaultEncoding

from .models import CareerStage

# ReportLab 기본 인코딩을 UTF-8로 설정
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0


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
    
    def _create_web_like_styles(self) -> Dict:
        """웹페이지와 유사한 스타일 생성"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # 가운데 정렬
                textColor=colors.HexColor('#2c3e50'),
                leading=28
            ),
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=18,
                spaceAfter=20,
                alignment=1,
                textColor=colors.HexColor('#34495e'),
                leading=22
            ),
            'section_header': ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading3'],
                fontName=self.font_name,
                fontSize=16,
                spaceBefore=20,
                spaceAfter=15,
                textColor=colors.HexColor('#2980b9'),
                leading=20,
                borderWidth=1,
                borderColor=colors.HexColor('#bdc3c7'),
                borderPadding=5,
                backColor=colors.HexColor('#ecf0f1')
            ),
            'goal_header': ParagraphStyle(
                'GoalHeader',
                parent=styles['Heading4'],
                fontName=self.font_name,
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.HexColor('#8e44ad'),
                leading=18,
                leftIndent=10
            ),
            'activity_header': ParagraphStyle(
                'ActivityHeader',
                parent=styles['Heading5'],
                fontName=self.font_name,
                fontSize=12,
                spaceBefore=10,
                spaceAfter=8,
                textColor=colors.HexColor('#27ae60'),
                leading=16,
                leftIndent=20
            ),
            'dream': ParagraphStyle(
                'Dream',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=15,
                alignment=1,
                textColor=colors.HexColor('#e74c3c'),
                leading=18,
                borderWidth=2,
                borderColor=colors.HexColor('#e74c3c'),
                borderPadding=10,
                backColor=colors.HexColor('#fdf2f2')
            ),
            'explanation': ParagraphStyle(
                'Explanation',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=8,
                textColor=colors.HexColor('#7f8c8d'),
                leading=14,
                leftIndent=30,
                fontStyle='italic'
            ),
            'school_activity': ParagraphStyle(
                'SchoolActivity',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=5,
                textColor=colors.HexColor('#2c3e50'),
                leading=14,
                leftIndent=40,
                bulletFontName=self.font_name,
                bulletText='📚',
                bulletIndent=25
            ),
            'personal_activity': ParagraphStyle(
                'PersonalActivity',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=5,
                textColor=colors.HexColor('#2c3e50'),
                leading=14,
                leftIndent=40,
                bulletFontName=self.font_name,
                bulletText='🏠',
                bulletIndent=25
            ),
            'recommendation': ParagraphStyle(
                'Recommendation',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=8,
                textColor=colors.HexColor('#2c3e50'),
                leading=14,
                leftIndent=40
            ),
            'encouragement': ParagraphStyle(
                'Encouragement',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=15,
                alignment=1,
                textColor=colors.HexColor('#e67e22'),
                leading=16,
                borderWidth=1,
                borderColor=colors.HexColor('#f39c12'),
                borderPadding=15,
                backColor=colors.HexColor('#fef9e7')
            ),
            'info_text': ParagraphStyle(
                'InfoText',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=5,
                textColor=colors.HexColor('#95a5a6'),
                leading=12
            )
        }
        
        return custom_styles
    
    def generate_career_report(self, session_data, output_path=None):
        """진로 탐색 결과 PDF 생성"""
        try:
            print(f"🔄 PDF 생성 시작 - 세션 데이터: {type(session_data)}")
            
            # 임시 파일 생성 또는 지정된 경로 사용
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix='.pdf',
                    prefix='middle_school_career_'
                )
                output_path = temp_file.name
                temp_file.close()
            
            print(f"📄 PDF 경로: {output_path}")
            
            # PDF 문서 생성 - 한글 지원을 위한 설정
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # 스타일 생성
            styles = self._create_web_like_styles()
            
            # 콘텐츠 빌드
            story = []
            
            print("📝 헤더 추가 중...")
            self._add_header(story, styles, session_data)
            
            print("📋 요약 추가 중...")
            self._add_summary(story, styles, session_data)
            
            print("🎯 드림로직 추가 중...")
            self._add_dream_logic(story, styles, session_data)
            
            print("💝 응원 메시지 추가 중...")
            self._add_encouragement(story, styles, session_data)
            
            print("📄 푸터 추가 중...")
            self._add_footer(story, styles)
            
            print("🔨 PDF 빌드 중...")
            # PDF 빌드
            doc.build(story)
            
            print(f"✅ PDF 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ PDF 생성 실패: {str(e)}")
            import traceback
            print(f"스택 트레이스: {traceback.format_exc()}")
            raise
    
    def _add_header(self, story, styles, session_data):
        """헤더 추가"""
        student_name = session_data.get('student_name', '학생')
        
        # 한글 텍스트를 안전하게 처리
        title_text = "🌟 중학생 진로 탐색 결과"
        subtitle_text = f"{student_name}님의 개인 맞춤 진로 계획서"
        
        story.append(self._safe_paragraph(title_text, styles['title']))
        story.append(self._safe_paragraph(subtitle_text, styles['subtitle']))
        story.append(Spacer(1, 20))
        
        # 생성 일자
        kst = timezone(timedelta(hours=9))
        current_time = datetime.now(kst)
        date_str = current_time.strftime("%Y년 %m월 %d일 %H:%M 생성")
        story.append(self._safe_paragraph(f"생성일: {date_str}", styles['info_text']))
        story.append(Spacer(1, 30))
    
    def _safe_paragraph(self, text, style):
        """한글 텍스트를 안전하게 Paragraph로 변환"""
        try:
            # 텍스트가 None이거나 빈 문자열인 경우 처리
            if not text:
                return Paragraph("", style)
            
            # 한글 텍스트 정규화
            if isinstance(text, str):
                # 유니코드 정규화
                import unicodedata
                safe_text = unicodedata.normalize('NFC', text)
                
                # HTML 이스케이프 처리
                safe_text = safe_text.replace('&', '&amp;')
                safe_text = safe_text.replace('<', '&lt;')
                safe_text = safe_text.replace('>', '&gt;')
                
            else:
                safe_text = str(text)
            
            return Paragraph(safe_text, style)
            
        except Exception as e:
            print(f"⚠️ Paragraph 생성 실패: {e}")
            print(f"문제 텍스트: {repr(text)}")
            
            # 최후의 폴백: 영어와 숫자만 남기기
            try:
                fallback_text = ''.join(c for c in str(text) if ord(c) < 128)
                if not fallback_text:
                    fallback_text = "[텍스트 표시 오류]"
                return Paragraph(fallback_text, style)
            except:
                return Paragraph("[텍스트 표시 오류]", style)
    
    def _add_summary(self, story, styles, session_data):
        """학생 정보 및 응답 요약 추가"""
        story.append(self._safe_paragraph("📋 진로 탐색 요약", styles['section_header']))
        
        student_info = session_data.get('student_info', {})
        student_name = student_info.get('name', '학생')
        grade = student_info.get('grade', 2)
        
        story.append(self._safe_paragraph(f"• 이름: {student_name}", styles['info_text']))
        story.append(self._safe_paragraph(f"• 학년: 중학교 {grade}학년", styles['info_text']))
        story.append(Spacer(1, 10))
        
        # 4단계 응답 요약
        responses = session_data.get('responses_summary', {})
        stage_names = {
            'step_1': '흥미 탐색',
            'step_2': '장점 탐색',
            'step_3': '가치관 탐색',
            'step_4': '미래 관심'
        }
        
        for step_key, stage_name in stage_names.items():
            if step_key in responses:
                response_data = responses[step_key]
                answer = response_data.get('answer', '')
                if answer:
                    story.append(self._safe_paragraph(f"• {stage_name}: {answer}", styles['info_text']))
        
        story.append(Spacer(1, 20))
    
    def _add_dream_logic(self, story, styles, session_data):
        """드림로직 추가"""
        dream_logic = session_data.get('dream_logic_result', '')
        final_dream = session_data.get('final_career_goal', '')
        
        if not dream_logic:
            return
        
        story.append(self._safe_paragraph("🎯 나만의 드림로직", styles['section_header']))
        story.append(Spacer(1, 10))
        
        # 최종꿈 표시
        if final_dream:
            story.append(self._safe_paragraph(f"🌟 최종꿈: {final_dream}", styles['dream']))
            story.append(Spacer(1, 15))
        
        # 드림로직 파싱 및 표시
        self._parse_and_add_dream_logic(story, styles, dream_logic)
    
    def _parse_and_add_dream_logic(self, story, styles, dream_logic_text):
        """드림로직 텍스트를 파싱하여 PDF에 추가"""
        lines = dream_logic_text.split('\n')
        current_section = ''
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 중간목표
            if line.startswith('[중간목표'):
                story.append(self._safe_paragraph(line, styles['goal_header']))
                current_section = 'goal'
            
            # 설명
            elif line.startswith('설명:'):
                explanation = line.replace('설명:', '').strip()
                story.append(self._safe_paragraph(explanation, styles['explanation']))
            
            # 실천활동(학교)
            elif '실천활동(학교)' in line:
                story.append(self._safe_paragraph("📚 실천활동(학교)", styles['activity_header']))
                # 콜론 뒤 내용이 있으면 추가
                content = line.split(':', 1)[-1].strip() if ':' in line else ''
                if content:
                    # 슬래시로 구분된 활동들 처리
                    activities = [act.strip() for act in content.split('/') if act.strip()]
                    for activity in activities:
                        story.append(self._safe_paragraph(activity, styles['school_activity']))
                current_section = 'school'
            
            # 실천활동(일상)
            elif '실천활동(일상)' in line:
                story.append(self._safe_paragraph("🏠 실천활동(일상)", styles['activity_header']))
                # 콜론 뒤 내용이 있으면 추가
                content = line.split(':', 1)[-1].strip() if ':' in line else ''
                if content:
                    # 슬래시로 구분된 활동들 처리
                    activities = [act.strip() for act in content.split('/') if act.strip()]
                    for activity in activities:
                        story.append(self._safe_paragraph(activity, styles['personal_activity']))
                current_section = 'personal'
            
            # 추천 활동
            elif '추천 활동' in line:
                story.append(self._safe_paragraph("🎯 추천 활동", styles['activity_header']))
                content = line.split(':', 1)[-1].strip() if ':' in line else ''
                if content:
                    story.append(self._safe_paragraph(content, styles['recommendation']))
            
            # 응원메모 건너뛰기 (별도 처리)
            elif '응원' in line and ('메모' in line or '메시지' in line):
                continue
            
            # 기타 텍스트
            elif line and not line.startswith('[') and not line.startswith('최종꿈:'):
                if current_section == 'goal':
                    story.append(self._safe_paragraph(line, styles['explanation']))
        
        story.append(Spacer(1, 20))
    
    def _add_encouragement(self, story, styles, session_data):
        """응원 메시지 추가"""
        encouragement = session_data.get('encouragement_message', '')
        
        if encouragement:
            story.append(self._safe_paragraph("💝 AI의 특별한 응원 메시지", styles['section_header']))
            story.append(Spacer(1, 10))
            story.append(self._safe_paragraph(encouragement, styles['encouragement']))
            story.append(Spacer(1, 20))
    
    def _add_footer(self, story, styles):
        """푸터 추가"""
        story.append(Spacer(1, 30))
        story.append(self._safe_paragraph("🎓 꿈을 향한 첫걸음을 응원합니다!", styles['subtitle']))
        story.append(Spacer(1, 10))
        story.append(self._safe_paragraph("이 진로 계획서를 바탕으로 하루하루 성장해나가세요.", styles['info_text']))


# 전역 PDF 생성기 인스턴스
pdf_generator = MiddleSchoolCareerPDFGenerator()