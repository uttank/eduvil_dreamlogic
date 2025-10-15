"""
고등학생 진로 탐색 PDF 생성기
웹페이지 스타일을 반영한 한글 PDF 생성
"""

import tempfile
import os
import re
import urllib.parse
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.rl_config import defaultEncoding

from openai import OpenAI
from dotenv import load_dotenv

# OpenAI 클라이언트 설정
load_dotenv()
_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_key)

# ReportLab 기본 인코딩을 UTF-8로 설정
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0

# 기본 GPT 모델 설정
DEFAULT_GPT_MODEL = "gpt-4.1-mini"


class HighSchoolCareerPDFGenerator:
    """고등학생 진로 탐색 PDF 생성기"""
    
    def __init__(self):
        """PDF 생성기 초기화"""
        self.font_name = self._register_korean_font()
        print(f"🔤 최종 사용 폰트: {self.font_name}")
    
    def _register_korean_font(self) -> str:
        """한글 폰트 등록 (웹 호환성 우선)"""
        font_name = 'Helvetica'  # 기본값
        
        # 웹 호환 한글 폰트 경로 (우선순위)
        font_paths = [
            # 1순위: 네이버 나눔고딕 (웹 서비스 호환성 최우선)
            os.path.join(os.path.dirname(__file__), "fonts", "NanumGothic.ttf"),
            # 2순위: macOS 시스템 폰트 (개발 환경용)
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            # 3순위: Linux 환경의 나눔고딕
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Ubuntu/Debian
            '/usr/share/fonts/nanum-gothic/NanumGothic.ttf',    # CentOS/RHEL
            # 4순위: Windows 환경
            'C:/Windows/Fonts/malgun.ttf',  # 맑은 고딕
        ]
        
        for i, font_path in enumerate(font_paths):
            if os.path.exists(font_path):
                try:
                    font_reg_name = f'NanumGothic{i}'
                    
                    if font_path.endswith('.ttc'):
                        # TTC 파일의 경우 서브폰트 지정
                        pdfmetrics.registerFont(TTFont(font_reg_name, font_path, subfontIndex=0))
                    else:
                        # TTF 파일
                        pdfmetrics.registerFont(TTFont(font_reg_name, font_path))
                    
                    font_name = font_reg_name
                    print(f"✅ 폰트 등록 성공: {font_path} → {font_name}")
                    break
                except Exception as e:
                    print(f"❌ 폰트 등록 실패 {font_path}: {e}")
                    continue
        
        print(f"🔤 최종 사용 폰트: {font_name}")
        return font_name
    
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
            'normal': ParagraphStyle(
                'KoreanNormal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=10,
                leading=16
            ),
            'bullet': ParagraphStyle(
                'KoreanBullet',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=11,
                spaceAfter=8,
                leading=16,
                leftIndent=20
            ),
            'heading': ParagraphStyle(
                'KoreanHeading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=15,
                spaceAfter=12,
                spaceBefore=18
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
    
    def translate_career_to_english(self, career_korean: str) -> str:
        """한글 직업명을 영어로 번역"""
        try:
            # 한글이 포함되어 있는지 확인
            has_korean = any('\uac00' <= char <= '\ud7af' for char in career_korean)
            
            if not has_korean:
                # 한글이 없으면 영어로 간주하고 정리만
                english_career = ''.join(c for c in career_korean if c.isalnum() or c.isspace())
                result = english_career.lower().replace(' ', '_')
                return result
            
            # 한글이 있는 경우 OpenAI로 번역
            chat_completion = client.chat.completions.create(
                model=DEFAULT_GPT_MODEL,
                messages=[
                    {"role": "system", "content": "당신은 한국어 직업명을 영어로 번역하는 전문가입니다. 직업명만 간단하게 영어로 번역해주세요. 부가 설명은 하지 말고 직업명만 답변하세요."},
                    {"role": "user", "content": f"다음 한국어 직업명을 영어로 번역해주세요: {career_korean}"},
                ],
                max_completion_tokens=200
            )
            
            english_career = chat_completion.choices[0].message.content
            if not english_career or not english_career.strip():
                english_career = "unknown_job"
            else:
                english_career = english_career.strip()
            
            # 특수문자 제거하고 소문자로 변환, 공백을 언더스코어로
            english_career = ''.join(c for c in english_career if c.isalnum() or c.isspace())
            english_career = english_career.lower().replace(' ', '_')
            
            # 빈 문자열 체크
            if not english_career or english_career == '_':
                english_career = "unknown_job"
            
            return english_career
            
        except Exception as e:
            # 번역 실패 시 한글을 안전한 형태로 변환
            safe_career = re.sub(r'[^\w\s가-힣]', '', career_korean)
            safe_career = re.sub(r'\s+', '_', safe_career.strip())
            result = f"korean_job_{safe_career}" if safe_career else "unknown_job"
            return result
    
    def _clean_text_for_pdf(self, text) -> str:
        """PDF 호환성을 위한 텍스트 정리"""
        if not text:
            return ""
        
        text = str(text)
        
        # 이모지를 텍스트로 변환
        emoji_map = {
            '🎯': '⦿',  '📚': '📖',  '🎨': '🖼',  '🤝': '👥',  '🔬': '•',
            '✨': '★',  '🏠': '🏘',  '💼': '👔',  '📝': '✍',  '🌟': '⭐',
            '📅': '[날짜]', '🎓': '[교육]', '💡': '[아이디어]', '🚀': '[시작]',
            '❤️': '♥', '👍': '[좋음]', '🔥': '[인기]', '💪': '[힘]'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        
        # HTML 특수문자 처리
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        return text
    
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
                
                # PDF 호환성을 위한 텍스트 정리
                safe_text = self._clean_text_for_pdf(safe_text)
                
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
    
    def generate_career_report(self, career_data: Dict, output_path: Optional[str] = None) -> str:
        """진로 탐색 결과 PDF 생성"""
        try:
            print(f"🔄 PDF 생성 시작 - 진로 데이터: {type(career_data)}")
            
            # 임시 파일 생성 또는 지정된 경로 사용
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix='.pdf',
                    prefix='high_school_career_'
                )
                output_path = temp_file.name
                temp_file.close()
            
            print(f"📄 PDF 경로: {output_path}")
            
            # PDF 문서 생성
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=inch*0.7,
                rightMargin=inch*0.7,
                topMargin=inch*0.8,
                bottomMargin=inch*0.8
            )
            
            # 스타일 생성
            styles = self._create_web_like_styles()
            
            # 콘텐츠 빌드
            story = []
            
            print("📝 헤더 추가 중...")
            self._add_header(story, styles, career_data)
            
            print("📋 요약 추가 중...")
            self._add_summary(story, styles, career_data)
            
            print("🎯 드림로직 추가 중...")
            self._add_dream_logic(story, styles, career_data)
            
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
    
    def _add_header(self, story, styles, career_data):
        """헤더 추가"""
        career = career_data.get('career', '진로탐색')
        
        # 한글 텍스트를 안전하게 처리
        title_text = "⦿ 드림로직 진로 탐색 결과"
        subtitle_text = f"{career} 분야 맞춤 진로 계획서"
        
        story.append(self._safe_paragraph(title_text, styles['title']))
        story.append(self._safe_paragraph(subtitle_text, styles['subtitle']))
        story.append(Spacer(1, 20))
        
        # 생성 일자
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        story.append(self._safe_paragraph(f"생성일: {current_date}", styles['info_text']))
        story.append(Spacer(1, 30))
    
    def _add_summary(self, story, styles, career_data):
        """진로 탐색 요약 추가"""
        story.append(self._safe_paragraph("📋 진로 탐색 요약", styles['section_header']))
        
        # 진로 탐색 섹션들 (주석 처리된 부분 복원)
        sections = [
            ("선택한 직업", career_data.get('career', '정보 없음')),
            ("직업 선택 이유", career_data.get('reasons', ['정보 없음'])),
            ("관심 있는 이슈", career_data.get('issues_selected', ['정보 없음'])),
            ("탐구 주제", career_data.get('topic', '정보 없음')),
            ("진로 목표", career_data.get('goal', '정보 없음')),
            ("중간 목표", career_data.get('midgoals', ['정보 없음'])),
        ]
        
        for section_title, section_content in sections:
            # 섹션 제목
            clean_title = self._clean_text_for_pdf(f"• {section_title}")
            story.append(self._safe_paragraph(clean_title, styles['heading']))
            
            # 섹션 내용
            if isinstance(section_content, list):
                for i, item in enumerate(section_content, 1):
                    clean_item = self._clean_text_for_pdf(item)
                    if len(section_content) > 1:
                        story.append(self._safe_paragraph(f"  {i}. {clean_item}", styles['bullet']))
                    else:
                        story.append(self._safe_paragraph(f"  {clean_item}", styles['bullet']))
            else:
                clean_content = self._clean_text_for_pdf(section_content)
                story.append(self._safe_paragraph(f"  {clean_content}", styles['bullet']))
            
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 20))
    
    def _add_dream_logic(self, story, styles, career_data):
        """드림로직 추가"""
        final_summary = career_data.get('final_summary', '')
        
        if not final_summary:
            return
        
        story.append(self._safe_paragraph("🎯 나만의 드림로직", styles['section_header']))
        story.append(Spacer(1, 10))
        
        # 최종 요약을 줄바꿈으로 분리하여 처리
        summary_lines = str(final_summary).split('\n')
        for line in summary_lines:
            line = line.strip()
            if line:
                clean_line = self._clean_text_for_pdf(line)
                story.append(self._safe_paragraph(clean_line, styles['normal']))
        
        story.append(Spacer(1, 20))
    
    def _add_footer(self, story, styles):
        """푸터 추가"""
        story.append(Spacer(1, 30))
        story.append(self._safe_paragraph("🎓 꿈을 향한 도전을 응원합니다!", styles['subtitle']))
        story.append(Spacer(1, 10))
        story.append(self._safe_paragraph("이 진로 계획서를 바탕으로 체계적으로 준비해나가세요.", styles['info_text']))
    
    def generate_download_filename(self, career: str) -> tuple:
        """다운로드용 파일명 생성 (영문, 한글)"""
        # 한글 직업명을 영어로 번역
        english_career = self.translate_career_to_english(career)
        
        # 파일명을 영문으로 생성 (날짜만 포함, 시간 제외)
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 번역된 직업명이 있으면 추가, 없으면 기본 파일명
        if english_career and english_career.strip():
            filename = f"dreamlogic_career_report_{timestamp}_{english_career}.pdf"
        else:
            filename = f"dreamlogic_career_report_{timestamp}_unknown_job.pdf"
        
        # 한글 파일명도 생성 (UTF-8 인코딩)
        safe_career = re.sub(r'[^\w\s가-힣]', '', career)
        safe_career = re.sub(r'\s+', '_', safe_career.strip())
        korean_filename = f"드림로직_진로탐색결과_{safe_career}_{timestamp}.pdf"
        encoded_korean_filename = urllib.parse.quote(korean_filename)
        
        return filename, encoded_korean_filename


# 전역 PDF 생성기 인스턴스
pdf_generator = HighSchoolCareerPDFGenerator()