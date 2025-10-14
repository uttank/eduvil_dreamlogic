"""
초등학생 진로 탐색 결과 PDF 다운로드 생성 모듈
NanumGothic 폰트를 사용하여 한글이 깨지지 않는 PDF를 생성합니다.
"""

import os
import tempfile
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from typing import Dict, List
from models import CareerStage


class ElementaryCareerPDFGenerator:
    """초등학생 진로 탐색 결과 PDF 생성기"""
    
    def __init__(self):
        """초기화 및 폰트 설정"""
        self.font_name = self._setup_korean_font()
        self.styles = self._create_web_like_styles()
    
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        font_name = 'Helvetica'  # 기본값
        
        # NanumGothic 폰트 경로
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "NanumGothic.ttf")
        
        if os.path.exists(font_path):
            try:
                font_reg_name = 'NanumGothic'
                pdfmetrics.registerFont(TTFont(font_reg_name, font_path))
                font_name = font_reg_name
                print(f"✅ 폰트 등록 성공: {font_path} → {font_name}")
            except Exception as e:
                print(f"❌ 폰트 등록 실패 {font_path}: {e}")
        else:
            print(f"❌ 폰트 파일을 찾을 수 없음: {font_path}")
        
        print(f"🔤 최종 사용 폰트: {font_name}")
        return font_name
    
    def _create_web_like_styles(self):
        """웹페이지와 유사한 스타일 생성"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            # 기본 제목 (호환성을 위해)
            'title': ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName=self.font_name,
                fontSize=20,
                spaceAfter=20,
                spaceBefore=15,
                alignment=1,  # 중앙 정렬
                textColor=colors.HexColor('#1e40af'),  # 파란색
                borderWidth=1,
                borderColor=colors.HexColor('#3b82f6'),
                borderPadding=8,
                backColor=colors.HexColor('#eff6ff')  # 연한 파란 배경
            ),
            
            # 메인 제목 (웹의 h1과 유사)
            'main_title': ParagraphStyle(
                'MainTitle',
                parent=styles['Title'],
                fontName=self.font_name,
                fontSize=24,
                spaceAfter=30,
                spaceBefore=20,
                alignment=1,  # 중앙 정렬
                textColor=colors.HexColor('#1e40af'),  # 파란색
                borderWidth=2,
                borderColor=colors.HexColor('#3b82f6'),
                borderPadding=15,
                backColor=colors.HexColor('#eff6ff')  # 연한 파란 배경
            ),
            
            # 섹션 제목 (웹의 h2와 유사)
            'section_title': ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=18,
                spaceAfter=15,
                spaceBefore=25,
                textColor=colors.HexColor('#059669'),  # 초록색
                borderWidth=1,
                borderColor=colors.HexColor('#10b981'),
                borderPadding=10,
                backColor=colors.HexColor('#f0fdf4')  # 연한 초록 배경
            ),
            
            # 드림로직 제목 (웹의 특별한 스타일과 유사)
            'dream_title': ParagraphStyle(
                'DreamTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=20,
                spaceAfter=20,
                spaceBefore=20,
                textColor=colors.HexColor('#7c2d12'),  # 갈색
                alignment=1,  # 중앙 정렬
                borderWidth=2,
                borderColor=colors.HexColor('#ea580c'),
                borderPadding=12,
                backColor=colors.HexColor('#fff7ed')  # 연한 주황 배경
            ),
            
            # 최종꿈 스타일 (웹의 특별한 카드와 유사)
            'final_dream': ParagraphStyle(
                'FinalDream',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=16,
                spaceAfter=20,
                spaceBefore=15,
                textColor=colors.HexColor('#be185d'),  # 핑크색
                alignment=1,  # 중앙 정렬
                borderWidth=3,
                borderColor=colors.HexColor('#ec4899'),
                borderPadding=15,
                backColor=colors.HexColor('#fdf2f8')  # 연한 핑크 배경
            ),
            
            # 중간목표 스타일 (웹의 목표 카드와 유사)
            'middle_goal': ParagraphStyle(
                'MiddleGoal',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=15,
                textColor=colors.HexColor('#1e40af'),  # 파란색
                borderWidth=2,
                borderColor=colors.HexColor('#3b82f6'),
                borderPadding=8,
                backColor=colors.HexColor('#dbeafe')  # 연한 파란 배경
            ),
            
            # 실천활동 제목 (웹의 서브헤딩과 유사)
            'activity_title': ParagraphStyle(
                'ActivityTitle',
                parent=styles['Heading3'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=8,
                spaceBefore=10,
                textColor=colors.HexColor('#7c2d12'),  # 갈색
                borderWidth=1,
                borderColor=colors.HexColor('#f97316'),
                borderPadding=6,
                backColor=colors.HexColor('#fed7aa')  # 연한 주황 배경
            ),
            
            # 활동 아이템 (웹의 리스트 아이템과 유사)
            'activity_item': ParagraphStyle(
                'ActivityItem',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=6,
                spaceBefore=4,
                leftIndent=20,
                textColor=colors.HexColor('#374151'),  # 회색
                borderWidth=1,
                borderColor=colors.HexColor('#e5e7eb'),
                borderPadding=8,
                backColor=colors.HexColor('#f9fafb')  # 연한 회색 배경
            ),
            
            # 응원메시지 (웹의 특별한 황금 카드와 유사)
            'encouragement': ParagraphStyle(
                'Encouragement',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=13,
                spaceAfter=20,
                spaceBefore=15,
                textColor=colors.HexColor('#92400e'),  # 골드색
                alignment=1,  # 중앙 정렬
                borderWidth=3,
                borderColor=colors.HexColor('#f59e0b'),
                borderPadding=15,
                backColor=colors.HexColor('#fffbeb')  # 연한 골드 배경
            ),
            
            # 일반 텍스트 (웹의 본문과 유사)
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=8,
                leading=16,
                textColor=colors.HexColor('#374151')
            ),
            
            # 헤딩 스타일 (호환성을 위해)
            'heading': ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=10,
                spaceBefore=15,
                textColor=colors.HexColor('#059669'),  # 초록색
                borderWidth=1,
                borderColor=colors.HexColor('#10b981'),
                borderPadding=6,
                backColor=colors.HexColor('#d1fae5')  # 연한 초록 배경
            ),
            
            # 결과 스타일 (호환성을 위해)
            'result': ParagraphStyle(
                'Result',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=12,
                spaceBefore=8,
                textColor=colors.HexColor('#1f2937'),  # 어두운 회색
                borderWidth=1,
                borderColor=colors.HexColor('#6b7280'),
                borderPadding=8,
                backColor=colors.HexColor('#f9fafb')  # 연한 회색 배경
            ),
            
            # 드림로직 목표 스타일
            'dream_goal': ParagraphStyle(
                'DreamGoal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=15,
                spaceBefore=10,
                textColor=colors.HexColor('#be185d'),  # 핑크색
                alignment=1,  # 중앙 정렬
                borderWidth=3,
                borderColor=colors.HexColor('#ec4899'),
                borderPadding=15,
                backColor=colors.HexColor('#fdf2f8')  # 연한 핑크 배경
            ),
            
            # 드림로직 섹션 스타일
            'dream_section': ParagraphStyle(
                'DreamSection',
                parent=styles['Heading3'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.HexColor('#1e40af'),  # 파란색
                borderWidth=2,
                borderColor=colors.HexColor('#3b82f6'),
                borderPadding=8,
                backColor=colors.HexColor('#dbeafe')  # 연한 파란 배경
            ),
            
            # 드림로직 활동 스타일
            'dream_activity': ParagraphStyle(
                'DreamActivity',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=5,
                spaceBefore=5,
                leftIndent=20,
                textColor=colors.HexColor('#374151'),  # 회색
                borderWidth=1,
                borderColor=colors.HexColor('#e5e7eb'),
                borderPadding=8,
                backColor=colors.HexColor('#f9fafb')  # 연한 회색 배경
            ),
            
            # 드림로직 아이템 스타일
            'dream_item': ParagraphStyle(
                'DreamItem',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=3,
                spaceBefore=2,
                leftIndent=40,
                textColor=colors.HexColor('#6b7280')  # 연한 회색
            )
        }
        
        return custom_styles
    
    def generate_career_report(self, student_name: str, responses: Dict[CareerStage, Dict], final_recommendation: str, dream_logic_result: str = "", encouragement_message: str = "") -> bytes:
        """진로 탐색 PDF 보고서 생성 (드림로직 결과 및 응원메시지 포함)"""
        
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
            story.append(Spacer(1, 30))
            
            # 학생 정보
            story.append(Paragraph(f"학생 이름: {student_name}", self.styles['heading']))
            story.append(Spacer(1, 15))
            
            # 한국 시간(KST) 계산
            kst = timezone(timedelta(hours=9))  # UTC+9
            korea_time = datetime.now(kst)
            story.append(Paragraph(f"생성 일시: {korea_time.strftime('%Y년 %m월 %d일 %H시 %M분')} (한국시간)", self.styles['normal']))
            story.append(Spacer(1, 25))
            
            # 단계별 응답 내용
            stage_names = {
                CareerStage.STEP_1: "1단계: 흥미 탐색",
                CareerStage.STEP_2: "2단계: 장점 탐색", 
                CareerStage.STEP_3: "3단계: 가치관 탐색",
                CareerStage.STEP_4: "4단계: 미래 탐색"
            }
            
            stage_questions = {
                CareerStage.STEP_1: "무엇을 할 때 시간이 빨리 가나요?",
                CareerStage.STEP_2: "다른 사람에게 자랑할만한 나만의 장점이 무엇인가요?",
                CareerStage.STEP_3: "어떤 일을 할 때 행복함을 느끼나요?",
                CareerStage.STEP_4: "미래 사회에서 가장 걱정되는 것은 무엇인가요?"
            }
            
            # 각 단계별 응답 표시
            for stage, response_data in responses.items():
                if stage in stage_names:
                    story.append(Paragraph(stage_names[stage], self.styles['heading']))
                    story.append(Paragraph(f"질문: {stage_questions[stage]}", self.styles['normal']))
                    
                    # 답변 내용 처리
                    answer_text = self._format_answer(response_data, stage)
                    story.append(Paragraph(f"답변: {answer_text}", self.styles['normal']))
                    story.append(Spacer(1, 15))
            
            # 최종 추천 결과
            story.append(Paragraph("🎯 AI가 추천하는 맞춤 진로", self.styles['heading']))
            story.append(Paragraph(final_recommendation, self.styles['result']))
            story.append(Spacer(1, 20))
            """
            # 드림로직 결과 추가 (구조화된 형태)
            if dream_logic_result:
                story.append(Paragraph("🌈 드림로직 - 꿈 실현 계획", self.styles['heading']))
                story.append(Spacer(1, 10))
                
                # 드림로직 내용을 구조화하여 추가
                dream_elements = self._format_dream_logic(dream_logic_result)
                story.extend(dream_elements)
                story.append(Spacer(1, 20))
            
            # 응원메시지 별도 섹션 추가
            if encouragement_message:
                story.append(Paragraph("💝 AI가 보내는 특별한 응원 메시지", self.styles['heading']))
                story.append(Spacer(1, 10))
                
                # 응원메시지를 특별한 스타일로 표시
                story.append(Paragraph(encouragement_message, self.styles['result']))
                story.append(Spacer(1, 20))
            """
            # 마무리 메시지
            story.append(Paragraph("💡 진로 탐색 완료!", self.styles['heading']))
            if dream_logic_result:
                story.append(Paragraph(
                    f"{student_name} 학생의 관심사와 장점을 바탕으로 분석한 결과와 드림로직 분석이 완료되었습니다. "
                    "이 결과들을 종합하여 더 구체적인 진로 계획을 세워보세요!", 
                    self.styles['normal']
                ))
            else:
                story.append(Paragraph(
                    f"{student_name} 학생의 관심사와 장점을 바탕으로 분석한 결과입니다. "
                    "이 결과를 참고하여 더 구체적인 진로 계획을 세워보세요!", 
                    self.styles['normal']
                ))
            """
            # PDF 생성
            doc.build(story)
            
            # 파일 읽기
            with open(tmp_path, 'rb') as f:
                pdf_content = f.read()
            
            return pdf_content
            
        finally:
            # 임시 파일 정리
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _format_answer(self, response_data: Dict, current_stage: CareerStage) -> str:
        """응답 데이터를 텍스트로 포맷팅"""
        choice_numbers = response_data.get("choice_numbers", [])
        custom_answer = response_data.get("custom_answer", "")
        
        # 기타 선택지인 경우 커스텀 답변 반환
        if custom_answer:
            return f"기타: {custom_answer}"
        
        # 해당 단계의 선택지만 가져오기
        from models import STAGE_QUESTIONS
        
        if current_stage not in STAGE_QUESTIONS:
            return "선택된 답변 없음"
            
        stage_data = STAGE_QUESTIONS[current_stage]
        if "choices" not in stage_data:
            return "선택된 답변 없음"
            
        stage_choices = stage_data["choices"]
        answer_texts = []
        
        for choice_num in choice_numbers:
            if 1 <= choice_num <= len(stage_choices):
                answer_texts.append(stage_choices[choice_num - 1])
        
        return ", ".join(answer_texts) if answer_texts else "선택된 답변 없음"
    
    def _format_dream_logic(self, dream_logic_text: str) -> list:
        """드림로직 텍스트를 구조화된 PDF 요소로 변환"""
        story_elements = []
        
        if not dream_logic_text:
            return story_elements
            
        lines = dream_logic_text.split('\n')
        current_section = None
        current_activity = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 드림로직 제목 (대괄호로 둘러싸인)
            if line.startswith('[') and line.endswith(']'):
                if '드림 로직' in line:
                    story_elements.append(Paragraph(line, self.styles['dream_title']))
                else:
                    # 중간목표 섹션
                    story_elements.append(Paragraph(line, self.styles['dream_section']))
                    current_section = line
                    
            # 최종꿈
            elif line.startswith('최종꿈:'):
                goal_text = line.replace('최종꿈:', '').strip()
                story_elements.append(Paragraph(f"🎯 최종꿈: {goal_text}", self.styles['dream_goal']))
                story_elements.append(Spacer(1, 10))
                
            # 실천활동 (• 로 시작)
            elif line.startswith('•'):
                activity_text = line.replace('•', '').strip()
                story_elements.append(Paragraph(f"• {activity_text}", self.styles['dream_activity']))
                current_activity = activity_text
                
            # 구체적 활동 (숫자로 시작)
            elif line.strip() and (line.strip()[0].isdigit() and '.' in line):
                item_text = line.strip()
                story_elements.append(Paragraph(f"    {item_text}", self.styles['dream_item']))
                
            # 응원 메모 라인은 별도 섹션에서 처리되므로 건너뛰기
            elif '응원' in line and ('메모' in line or '메시지' in line):
                continue  # 응원메모는 별도 매개변수로 처리되므로 건너뛰기
                
            # 일반 텍스트 (응원 메모 내용 등)
            elif line and not line.startswith('작은 습관'):
                # 이모지가 포함된 텍스트이지만 응원메모가 아닌 경우
                if any(emoji in line for emoji in ['😊', '💚', '🎉', '✨', '💪', '🌟']):
                    # 응원메모 관련 키워드가 없으면 일반 텍스트로 처리
                    if not any(keyword in line for keyword in ['응원', '메모', '메시지', '힘내', '화이팅']):
                        story_elements.append(Paragraph(line, self.styles['dream_activity']))
                else:
                    story_elements.append(Paragraph(line, self.styles['dream_activity']))
                    
            # 작은 습관 체크리스트
            elif '작은 습관' in line:
                story_elements.append(Spacer(1, 10))
                story_elements.append(Paragraph("📋 작은 습관 체크리스트", self.styles['dream_section']))
                
        return story_elements