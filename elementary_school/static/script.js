// 초등학생 진로 탐색 JavaScript - 작동하는 버전
console.log('🌟 JavaScript 파일 로드됨');

class CareerExplorer {
    constructor() {
        console.log('🔧 CareerExplorer 생성자 시작');
        // 동적 베이스 URL 설정
        this.baseURL = `${window.location.protocol}//${window.location.host}/elementary_school`;
        console.log('🔗 동적 베이스 URL:', this.baseURL);
        this.sessionId = null;
        this.studentInfo = null;
        this.selectedChoices = [];
        this.maxChoices = 2;
        this.currentQuestion = null;
        
        console.log('✅ CareerExplorer 속성 초기화 완료');
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        console.log('🔧 이벤트 리스너 초기화 시작');
        
        // 시작 버튼 이벤트 - 간단한 방식으로 등록
        setTimeout(() => {
            const startBtn = document.getElementById('startBtn');
            if (startBtn) {
                console.log('✅ 시작 버튼 발견');
                startBtn.onclick = () => {
                    console.log('🖱️ 시작 버튼 클릭됨!');
                    this.startCareerExploration();
                };
                // 버튼에 시각적 표시 추가
                startBtn.style.border = '2px solid #4CAF50';
            } else {
                console.error('❌ 시작 버튼을 찾을 수 없습니다');
            }

            // 다른 버튼들도 등록
            this.setupOtherButtons();
        }, 100);

        this.setupInputValidation();
    }

    setupOtherButtons() {
        // 학생 정보 제출 버튼
        const submitStudentInfo = document.getElementById('submitStudentInfo');
        if (submitStudentInfo) {
            submitStudentInfo.onclick = () => this.submitStudentInfo();
        }

        // 답변 제출 버튼
        const submitAnswer = document.getElementById('submitAnswer');
        if (submitAnswer) {
            submitAnswer.onclick = () => this.submitAnswer();
        }

        // AI 추천 수락 버튼
        const acceptRecommendation = document.getElementById('acceptRecommendation');
        if (acceptRecommendation) {
            acceptRecommendation.onclick = () => this.acceptRecommendation();
        }

        // AI 추천 수정 버튼
        const modifyRecommendation = document.getElementById('modifyRecommendation');
        if (modifyRecommendation) {
            modifyRecommendation.onclick = () => this.modifyRecommendation();
        }

        // 드림로직 생성 버튼
        const generateDreamLogic = document.getElementById('generateDreamLogic');
        if (generateDreamLogic) {
            generateDreamLogic.onclick = () => this.generateDreamLogic();
        }

        // 여정 완료 버튼
        const finishJourney = document.getElementById('finishJourney');
        if (finishJourney) {
            finishJourney.onclick = () => this.finishJourney();
        }

        // 다시 시작 버튼
        const restartJourney = document.getElementById('restartJourney');
        if (restartJourney) {
            restartJourney.onclick = () => this.restart();
        }

        console.log('✅ 모든 이벤트 리스너 등록 완료');
    }

    setupInputValidation() {
        const inputs = ['studentName', 'studentAge', 'studentGrade', 'studentSchool'];
        
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.oninput = () => this.validateStudentInfo();
                input.onchange = () => this.validateStudentInfo();
            }
        });
    }

    validateStudentInfo() {
        const name = document.getElementById('studentName')?.value.trim();
        const age = document.getElementById('studentAge')?.value;
        const grade = document.getElementById('studentGrade')?.value;
        const school = document.getElementById('studentSchool')?.value.trim();
        const submitBtn = document.getElementById('submitStudentInfo');

        const isValid = name && age && grade && school;
        if (submitBtn) {
            submitBtn.disabled = !isValid;
        }
    }

    async startCareerExploration() {
        console.log('🚀 진로탐색 시작!');
        
        try {
            this.showLoading(true);
            console.log('📡 API 호출:', `${this.baseURL}/career/start`);
            
            const response = await fetch(`${this.baseURL}/career/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log('📡 응답 상태:', response.status);
            const data = await response.json();
            console.log('📡 응답 데이터:', data);
            
            if (data.success) {
                this.sessionId = data.data.session_id;
                console.log('✅ 세션 ID:', this.sessionId);
                this.showScreen('studentInfoScreen');
                this.updateProgress(0);
            } else {
                console.error('❌ API 실패:', data);
                this.showError('세션 시작에 실패했습니다.');
            }
        } catch (error) {
            console.error('❌ 오류 발생:', error);
            this.showError('서버 연결에 실패했습니다.');
        } finally {
            this.showLoading(false);
        }
    }

    showScreen(screenId) {
        console.log('🖼️ 화면 전환:', screenId);
        
        // 모든 화면 숨기기
        const screens = [
            'startScreen', 'studentInfoScreen', 'questionScreen', 
            'recommendationScreen', 'completionScreen', 'dreamLogicScreen'
        ];
        
        screens.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });

        // 선택된 화면 보이기
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.style.display = 'block';
        }
        
        // 진행 상황 표시 여부
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = screenId !== 'startScreen' ? 'block' : 'none';
        }
    }

    updateProgress(stage, completed = false) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (!progressFill || !progressText) return;
        
        let percentage;
        let text;
        
        if (completed) {
            percentage = 100;
            text = '완료! 🎉';
        } else {
            percentage = (stage / 5) * 100;
            text = `${stage}단계 / 5단계`;
        }
        
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = text;
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    showError(message) {
        console.error('❌ 오류:', message);
        alert(`❌ ${message}`);
    }

    async submitStudentInfo() {
        console.log('📝 학생 정보 제출 시작');
        
        const name = document.getElementById('studentName')?.value.trim();
        const age = parseInt(document.getElementById('studentAge')?.value);
        const grade = parseInt(document.getElementById('studentGrade')?.value);
        const school = document.getElementById('studentSchool')?.value.trim();

        if (!name || !age || !grade || !school) {
            this.showError('모든 정보를 입력해주세요.');
            return;
        }

        this.studentInfo = { name, age, grade, school };
        console.log('📝 학생 정보:', this.studentInfo);

        try {
            this.showLoading(true);

            const response = await fetch(`${this.baseURL}/career/${this.sessionId}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    student_info: this.studentInfo,
                    response: {
                        choice_numbers: [],
                        custom_answer: `안녕하세요! 저는 ${name}이고 ${age}살이에요.`
                    }
                })
            });

            const data = await response.json();
            console.log('📡 학생정보 제출 응답:', data);
            
            if (data.success && data.data.next_question) {
                this.currentQuestion = data.data.next_question;
                this.showQuestionScreen();
                this.updateProgress(1);
            } else {
                this.showError('학생 정보 저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('❌ 학생정보 제출 오류:', error);
            this.showError('서버 연결에 실패했습니다.');
        } finally {
            this.showLoading(false);
        }
    }

    async submitAnswer() {
        console.log('📝 답변 제출 (구현 예정)');
        this.showError('기능 구현 중입니다.');
    }

    async acceptRecommendation() {
        console.log('👍 추천 수락 (구현 예정)');
        this.showError('기능 구현 중입니다.');
    }

    async modifyRecommendation() {
        console.log('🔄 추천 수정 (구현 예정)');
        this.showError('기능 구현 중입니다.');
    }

    async generateDreamLogic() {
        console.log('🌈 드림로직 생성 (구현 예정)');
        this.showError('기능 구현 중입니다.');
    }

    finishJourney() {
        console.log('🏆 여정 완료 (구현 예정)');
        this.showError('기능 구현 중입니다.');
    }

    showQuestionScreen() {
        if (!this.currentQuestion) return;

        const stage = this.currentQuestion.stage;
        const stageNumber = parseInt(stage.split('_')[1]);
        
        // 진행률 업데이트
        this.updateProgress(stageNumber);

        // 질문 표시
        const questionTitle = document.getElementById('questionTitle');
        const questionDescription = document.getElementById('questionDescription');
        const encouragement = document.getElementById('encouragement');
        const questionEmoji = document.getElementById('questionEmoji');

        if (questionTitle) questionTitle.textContent = this.currentQuestion.question;
        if (questionDescription) questionDescription.textContent = this.getStageDescription(stage);
        if (encouragement) encouragement.textContent = this.currentQuestion.encouragement || '정말 특별한 생각이에요! 🌟';
        if (questionEmoji) questionEmoji.textContent = this.getStageEmoji(stage);

        // 선택 개수 제한 설정
        this.maxChoices = (stageNumber <= 2) ? 2 : 1;

        // 선택지 생성
        this.createChoices();

        // 5단계인 경우 AI 추천 생성
        if (stage === 'step_5') {
            this.handleStep5();
            return;
        }

        this.showScreen('questionScreen');
    }

    createChoices() {
        const container = document.getElementById('choicesContainer');
        const customContainer = document.getElementById('customAnswerContainer');
        
        if (!container) return;
        
        container.innerHTML = '';
        this.selectedChoices = [];

        if (!this.currentQuestion.choices) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        if (customContainer) customContainer.style.display = 'none';

        this.currentQuestion.choices.forEach((choice, index) => {
            const button = document.createElement('button');
            button.className = 'choice-item';
            button.textContent = choice;
            button.dataset.choiceNumber = index + 1;

            button.onclick = () => {
                this.selectChoice(button, index + 1);
            };

            // "기타" 선택지 처리
            if (choice.includes('기타') && customContainer) {
                button.onclick = () => {
                    this.selectChoice(button, index + 1);
                    customContainer.style.display = 'block';
                    const customAnswer = document.getElementById('customAnswer');
                    if (customAnswer) customAnswer.focus();
                };
            }

            container.appendChild(button);
        });

        this.updateSubmitButton();
    }

    selectChoice(button, choiceNumber) {
        const isSelected = button.classList.contains('selected');

        if (isSelected) {
            // 선택 해제
            button.classList.remove('selected');
            this.selectedChoices = this.selectedChoices.filter(num => num !== choiceNumber);
        } else {
            // 선택 개수 제한 확인
            if (this.selectedChoices.length >= this.maxChoices) {
                if (this.maxChoices === 1) {
                    // 기존 선택 해제
                    document.querySelectorAll('.choice-item.selected').forEach(item => {
                        item.classList.remove('selected');
                    });
                    this.selectedChoices = [];
                } else {
                    this.showError(`최대 ${this.maxChoices}개까지만 선택할 수 있어요!`);
                    return;
                }
            }

            // 새로운 선택
            button.classList.add('selected');
            this.selectedChoices.push(choiceNumber);
        }

        this.updateSubmitButton();
    }

    updateSubmitButton() {
        const submitBtn = document.getElementById('submitAnswer');
        if (!submitBtn) return;
        
        const hasSelection = this.selectedChoices.length > 0;
        const customAnswer = document.getElementById('customAnswer')?.value.trim();
        const hasCustomAnswer = customAnswer && customAnswer.length > 0;

        // "기타" 선택시 커스텀 답변 필요
        const hasOtherChoice = this.selectedChoices.includes(11);
        const isValid = hasSelection && (!hasOtherChoice || hasCustomAnswer);

        submitBtn.disabled = !isValid;
    }

    getStageDescription(stage) {
        const descriptions = {
            'step_1': '시간이 빨리 가는 활동을 최대 2개까지 선택해주세요!',
            'step_2': '자랑할 만한 장점을 최대 2개까지 선택해주세요!',
            'step_3': '행복을 느끼는 순간을 1개만 선택해주세요!',
            'step_4': '미래에 걱정되는 것을 1개만 선택해주세요!',
            'step_5': 'AI가 분석한 결과를 확인해주세요!'
        };
        return descriptions[stage] || '';
    }

    getStageEmoji(stage) {
        const emojis = {
            'step_1': '⏰',
            'step_2': '✨',
            'step_3': '😊',
            'step_4': '🤔',
            'step_5': '🎯'
        };
        return emojis[stage] || '🤔';
    }

    restart() {
        console.log('🔄 다시 시작');
        location.reload();
    }
}

// DOM 로드 완료 후 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌟 DOM 로드 완료, 앱 초기화 시작');
    
    try {
        window.careerExplorer = new CareerExplorer();
        console.log('✅ CareerExplorer 초기화 성공');
    } catch (error) {
        console.error('❌ CareerExplorer 초기화 실패:', error);
    }
});

console.log('🚀 JavaScript 파일 로드 완료!');