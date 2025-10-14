"""
한글 PDF 다운로드 생성 모듈
네이버 나눔고딕 폰트를 사용하여 한글이 깨지지 않는 PDF를 생성합니다.
"""

import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class KoreanPDFGenerator:
    """한글 PDF 생성기 클래스"""
    
    def __init__(self):
        """초기화 및 폰트 설정"""
        self.font_name = self._setup_korean_font()
        self.styles = self._create_styles()
    
    def _setup_korean_font(self):
        """한글 폰트 설정 (웹 호환성 우선)"""
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
    
    def _create_styles(self):
        """PDF 스타일 설정"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'KoreanTitle',
                parent=styles['Title'],
                fontName=self.font_name,
                fontSize=22,
                spaceAfter=30,
                alignment=1  # 중앙 정렬
            ),
            
            'heading': ParagraphStyle(
                'KoreanHeading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=15,
                spaceAfter=12,
                spaceBefore=18
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
            )
        }
        
        return custom_styles
    
    def _safe_text(self, text, default="정보 없음"):
        """텍스트 안전 처리"""
        if not text:
            return default
        if isinstance(text, list):
            return text if text else [default]
        return str(text).strip() if str(text).strip() else default
    
    def _clean_text_for_pdf(self, text):
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
    
    def create_simple_report(self, title="한글 PDF 테스트", content_dict=None):
        """간단한 한글 PDF 보고서 생성"""
        # 임시 파일 생성
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            temp_filename,
            pagesize=A4,
            leftMargin=inch*0.7,
            rightMargin=inch*0.7,
            topMargin=inch*0.8,
            bottomMargin=inch*0.8
        )
        
        story = []
        
        # 제목
        clean_title = self._clean_text_for_pdf(title)
        story.append(Paragraph(clean_title, self.styles['title']))
        story.append(Spacer(1, 20))
        
        # 생성 날짜
        current_date = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        story.append(Paragraph(f"생성일: {current_date}", self.styles['normal']))
        story.append(Spacer(1, 30))
        
        # 내용 추가
        if content_dict:
            for section_title, section_content in content_dict.items():
                # 섹션 제목
                clean_section_title = self._clean_text_for_pdf(section_title)
                story.append(Paragraph(clean_section_title, self.styles['heading']))
                
                # 섹션 내용
                if isinstance(section_content, list):
                    for item in section_content:
                        clean_item = self._clean_text_for_pdf(item)
                        story.append(Paragraph(f"• {clean_item}", self.styles['bullet']))
                else:
                    clean_content = self._clean_text_for_pdf(section_content)
                    story.append(Paragraph(clean_content, self.styles['normal']))
                
                story.append(Spacer(1, 15))
        
        # PDF 생성
        try:
            doc.build(story)
            print(f"✅ PDF 생성 완료: {temp_filename}")
            return temp_filename
        except Exception as e:
            print(f"❌ PDF 생성 오류: {e}")
            # 오류 발생 시 최소한의 내용으로 재시도
            simple_story = [
                Paragraph(clean_title, self.styles['title']),
                Spacer(1, 20),
                Paragraph(f"생성일: {current_date}", self.styles['normal'])
            ]
            doc.build(simple_story)
            return temp_filename
    
    def create_career_report(self, career_data):
        """진로 탐색 전용 PDF 보고서 생성"""
        # 임시 파일 생성
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            temp_filename,
            pagesize=A4,
            leftMargin=inch*0.7,
            rightMargin=inch*0.7,
            topMargin=inch*0.8,
            bottomMargin=inch*0.8
        )
        
        story = []
        
        # 제목
        story.append(Paragraph("⦿ 드림로직 진로 탐색 결과", self.styles['title']))
        story.append(Spacer(1, 20))
        
        # 생성 날짜
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        story.append(Paragraph(f"생성일: {current_date}", self.styles['normal']))
        story.append(Spacer(1, 25))
        
        # 진로 탐색 섹션들
        sections = [
            ("1️⃣ 선택한 직업", career_data.get('career', '정보 없음')),
            ("2️⃣ 직업 선택 이유", career_data.get('reasons', ['정보 없음'])),
            ("3️⃣ 관심 있는 이슈", career_data.get('issues_selected', ['정보 없음'])),
            ("4️⃣ 탐구 주제", career_data.get('topic', '정보 없음')),
            ("5️⃣ 진로 목표", career_data.get('goal', '정보 없음')),
            ("6️⃣ 중간 목표", career_data.get('midgoals', ['정보 없음'])),
        ]
        
        for section_title, section_content in sections:
            # 섹션 제목
            story.append(Paragraph(section_title, self.styles['heading']))
            
            # 섹션 내용
            content_safe = self._safe_text(section_content, "정보 없음")
            if isinstance(content_safe, list):
                for i, item in enumerate(content_safe, 1):
                    clean_item = self._clean_text_for_pdf(item)
                    if len(content_safe) > 1:
                        story.append(Paragraph(f"{i}. {clean_item}", self.styles['bullet']))
                    else:
                        story.append(Paragraph(f"• {clean_item}", self.styles['bullet']))
            else:
                clean_content = self._clean_text_for_pdf(content_safe)
                story.append(Paragraph(f"• {clean_content}", self.styles['bullet']))
            
            story.append(Spacer(1, 15))
        
        # 최종 요약
        final_summary = career_data.get('final_summary', '')
        if final_summary:
            story.append(Paragraph("7️⃣ 최종 종합 계획", self.styles['heading']))
            
            # 줄바꿈으로 분리하여 처리
            summary_lines = str(final_summary).split('\n')
            for line in summary_lines:
                line = line.strip()
                if line:
                    clean_line = self._clean_text_for_pdf(line)
                    story.append(Paragraph(clean_line, self.styles['normal']))
        
        # PDF 생성
        try:
            doc.build(story)
            print(f"✅ 진로 탐색 PDF 생성 완료: {temp_filename}")
            return temp_filename
        except Exception as e:
            print(f"❌ PDF 생성 오류: {e}")
            return None


def test_korean_pdf():
    """한글 PDF 생성 테스트"""
    print("🧪 한글 PDF 생성 테스트 시작...")
    
    # PDF 생성기 초기화
    pdf_generator = KoreanPDFGenerator()
    
    # 테스트 데이터
    test_content = {
        "📋 개요": "이것은 한글 PDF 생성 테스트입니다.",
        "🎯 목표": [
            "한글이 깨지지 않는 PDF 생성",
            "웹 서비스 호환성 확보",
            "다양한 운영체제 지원"
        ],
        "📝 상세 내용": "네이버 나눔고딕 폰트를 사용하여 안정적인 한글 표시를 보장합니다. 이모지도 적절히 변환됩니다. ✨🎉",
        "✅ 결론": [
            "성공적인 한글 PDF 생성",
            "웹 배포 준비 완료",
            "사용자 경험 향상"
        ]
    }
    
    # 간단한 보고서 생성
    pdf_file = pdf_generator.create_simple_report(
        title="🎯 한글 PDF 생성 테스트 보고서",
        content_dict=test_content
    )
    
    if pdf_file:
        print(f"✅ 테스트 완료! PDF 파일: {pdf_file}")
        return pdf_file
    else:
        print("❌ PDF 생성 실패")
        return None


def test_career_pdf():
    """진로 탐색 PDF 생성 테스트"""
    print("🎓 진로 탐색 PDF 생성 테스트 시작...")
    
    # PDF 생성기 초기화
    pdf_generator = KoreanPDFGenerator()
    
    # 테스트 진로 데이터
    career_data = {
        'career': '소프트웨어 개발자',
        'reasons': ['능력 발휘', '미래 비전', '창의성'],
        'issues_selected': ['AI 윤리 문제', '사이버 보안', '디지털 격차'],
        'topic': 'AI 기술의 윤리적 활용 방안',
        'goal': '사회에 도움이 되는 AI 소프트웨어를 개발하는 개발자가 되고 싶습니다.',
        'midgoals': [
            '프로그래밍 언어 숙달',
            'AI/ML 전문성 강화',
            '팀워크 및 소통 능력 향상'
        ],
        'final_summary': '''⦿ [최종 목표] 사회에 도움이 되는 AI 소프트웨어 개발자

📖 [중간목표1] 프로그래밍 기술 역량
• 실천활동1: Python, Java 마스터하기
• 실천활동2: 알고리즘 문제 해결 연습
• 실천활동3: 오픈소스 프로젝트 참여

🖼 [중간목표2] AI/ML 전문성 강화  
• 실천활동1: 머신러닝 기초 학습
• 실천활동2: 딥러닝 프레임워크 활용
• 실천활동3: AI 프로젝트 포트폴리오 구축

👥 [중간목표3] 소통 및 협업 능력
• 실천활동1: 팀 프로젝트 참여
• 실천활동2: 기술 블로그 운영
• 실천활동3: 개발자 커뮤니티 활동'''
    }
    
    # 진로 탐색 PDF 생성
    pdf_file = pdf_generator.create_career_report(career_data)
    
    if pdf_file:
        print(f"✅ 진로 탐색 PDF 테스트 완료! 파일: {pdf_file}")
        return pdf_file
    else:
        print("❌ 진로 탐색 PDF 생성 실패")
        return None


if __name__ == "__main__":
    print("🚀 한글 PDF 생성기 테스트 실행")
    print("=" * 50)
    
    # 기본 테스트
    test_pdf = test_korean_pdf()
    print()
    
    # 진로 탐색 테스트
    career_pdf = test_career_pdf()
    print()
    
    print("🎉 모든 테스트 완료!")
    if test_pdf:
        print(f"📄 기본 테스트 PDF: {test_pdf}")
    if career_pdf:
        print(f"🎓 진로 탐색 PDF: {career_pdf}")
