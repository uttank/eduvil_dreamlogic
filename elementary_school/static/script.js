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

        // Step 4 AI 이슈 생성 버튼 (새로운 기능)
        const generateStep4Issues = document.getElementById('generateStep4Issues');
        if (generateStep4Issues) {
            generateStep4Issues.onclick = () => this.generateStep4Issues();
        }

        // Step 4 재생성 버튼 (새로운 기능)
        const regenerateStep4Issues = document.getElementById('regenerateStep4Issues');
        if (regenerateStep4Issues) {
            regenerateStep4Issues.onclick = () => this.regenerateStep4Issues();
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
        console.log('🔍 === showQuestionScreen 디버깅 === NEW VERSION');
        console.log('currentQuestion:', this.currentQuestion);
        
        if (!this.currentQuestion) return;

        const stage = this.currentQuestion.stage;
        const stageNumber = parseInt(stage.split('_')[1]);
        
        console.log('🔍 NEW - Stage:', stage, 'Number:', stageNumber);
        console.log('🔍 NEW - Stage type:', typeof stage);
        console.log('🔍 NEW - Stage === "step_4":', stage === 'step_4');
        console.log('🔍 NEW - Choices exist:', !!this.currentQuestion.choices);
        console.log('🔍 NEW - Choices:', this.currentQuestion.choices);
        console.log('🔍 NEW - Multiple:', stageNumber <= 2);
        
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

        console.log('🔍 Step 4 체크 전 - stage:', stage);
        console.log('🔍 Step 4 체크 전 - stage === "step_4":', stage === 'step_4');

        // 4단계인 경우 AI 이슈 생성 처리 (선택지 생성 전에 체크)
        if (stage === 'step_4') {
            console.log('🚀 Step 4 감지! handleStep4() 호출');
            this.handleStep4();
            return;
        }

        // 5단계인 경우 AI 추천 생성
        if (stage === 'step_5') {
            console.log('🚀 Step 5 감지! handleStep5() 호출');
            this.handleStep5();
            return;
        }

        console.log('🔍 일반 단계 처리 - createChoices() 호출');

        // 선택지 생성 (4, 5단계가 아닌 경우만)
        this.createChoices();

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

    // ============================================================================
    // Step 4 AI 이슈 생성 관련 메서드들 (새로운 기능)
    // ============================================================================
    
    async handleStep4() {
        console.log('🤖 Step 4: AI 이슈 생성 처리 시작');
        
        // Step 4 전용 화면 구성
        this.showStep4AIScreen();
        
        // 자동으로 이슈 생성 시도
        await this.generateStep4Issues();
    }
    
    showStep4AIScreen() {
        console.log('📱 Step 4 AI 화면 표시');
        
        // 기존 선택지 관련 요소들 모두 숨기기
        const choicesContainer = document.getElementById('choicesContainer');
        const customAnswerContainer = document.getElementById('customAnswerContainer');
        const submitAnswer = document.getElementById('submitAnswer');
        
        if (choicesContainer) {
            choicesContainer.style.display = 'none';
            choicesContainer.innerHTML = ''; // 내용도 비우기
        }
        
        if (customAnswerContainer) {
            customAnswerContainer.style.display = 'none';
        }
        
        if (submitAnswer) {
            submitAnswer.style.display = 'none';
        }
        
        // Step 4 AI 컨테이너 생성 또는 표시
        let step4Container = document.getElementById('step4AIContainer');
        if (!step4Container) {
            step4Container = this.createStep4AIContainer();
        }
        
        step4Container.style.display = 'block';
        this.showScreen('questionScreen');
    }
    
    createStep4AIContainer() {
        console.log('🏗️ Step 4 AI 컨테이너 생성');
        
        const container = document.createElement('div');
        container.id = 'step4AIContainer';
        container.className = 'step4-ai-container';
        
        container.innerHTML = `
            <div class="ai-loading" id="step4Loading">
                <div class="loading-spinner"></div>
                <p>AI가 맞춤형 이슈를 생성하고 있어요... 🤖✨</p>
            </div>
            
            <div class="ai-issues-section" id="step4Issues" style="display: none;">
                <h3>🌟 당신의 관심사와 관련된 사회/기술적 이슈들</h3>
                <p class="issue-description">1~3단계 응답을 바탕으로 AI가 맞춤 제안해드려요!</p>
                
                <div class="issues-container" id="issuesContainer">
                    <!-- AI 생성 이슈들이 여기에 표시됩니다 -->
                </div>
                
                <div class="regenerate-section">
                    <button type="button" id="regenerateStep4Issues" class="btn btn-secondary" style="display: none;">
                        🔄 다른 이슈로 다시 생성 (<span id="regenerateCount">0</span>/5)
                    </button>
                </div>
                
                <div class="step4-submit-section" style="display: none;" id="step4SubmitSection">
                    <button type="button" id="submitStep4Choice" class="btn btn-primary" disabled>
                        선택 완료
                    </button>
                </div>
            </div>
            
            <div class="ai-error-section" id="step4Error" style="display: none;">
                <p class="error-message">이슈 생성에 실패했습니다. 다시 시도해주세요.</p>
                <button type="button" id="retryStep4" class="btn btn-secondary">다시 시도</button>
            </div>
        `;
        
        // questionScreen에 추가
        const questionScreen = document.getElementById('questionScreen');
        if (questionScreen) {
            questionScreen.appendChild(container);
        }
        
        // 이벤트 리스너 등록
        this.setupStep4EventListeners();
        
        return container;
    }
    
    setupStep4EventListeners() {
        console.log('🔧 Step 4 이벤트 리스너 설정');
        
        // 재생성 버튼
        const regenerateBtn = document.getElementById('regenerateStep4Issues');
        if (regenerateBtn) {
            regenerateBtn.onclick = () => this.regenerateStep4Issues();
        }
        
        // 제출 버튼
        const submitBtn = document.getElementById('submitStep4Choice');
        if (submitBtn) {
            submitBtn.onclick = () => this.submitStep4Choice();
        }
        
        // 재시도 버튼
        const retryBtn = document.getElementById('retryStep4');
        if (retryBtn) {
            retryBtn.onclick = () => this.generateStep4Issues();
        }
    }
    
    async generateStep4Issues(regenerate = false) {
        console.log(`🤖 Step 4 이슈 생성 ${regenerate ? '재생성' : '첫 생성'}`);
        
        this.showStep4Loading();
        
        try {
            const response = await fetch(`${this.baseURL}/career/${this.sessionId}/step4-issues`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    regenerate: regenerate
                })
            });
            
            const data = await response.json();
            console.log('📊 Step 4 이슈 생성 응답:', data);
            
            if (!response.ok) {
                throw new Error(data.detail || '이슈 생성에 실패했습니다.');
            }
            
            if (data.success && data.data.issues) {
                this.displayStep4Issues(data.data.issues, data.data.regeneration_count, data.data.can_regenerate);
            } else {
                throw new Error('이슈 데이터가 없습니다.');
            }
            
        } catch (error) {
            console.error('❌ Step 4 이슈 생성 오류:', error);
            this.showStep4Error(error.message);
        }
    }
    
    async regenerateStep4Issues() {
        console.log('🔄 Step 4 이슈 재생성');
        await this.generateStep4Issues(true);
    }
    
    showStep4Loading() {
        console.log('⏳ Step 4 로딩 표시');
        
        const loading = document.getElementById('step4Loading');
        const issues = document.getElementById('step4Issues');
        const error = document.getElementById('step4Error');
        
        if (loading) loading.style.display = 'block';
        if (issues) issues.style.display = 'none';
        if (error) error.style.display = 'none';
    }
    
    displayStep4Issues(issues, regenerationCount, canRegenerate) {
        console.log('📋 Step 4 이슈 표시:', issues);
        
        const loading = document.getElementById('step4Loading');
        const issuesSection = document.getElementById('step4Issues');
        const issuesContainer = document.getElementById('issuesContainer');
        const regenerateBtn = document.getElementById('regenerateStep4Issues');
        const regenerateCountSpan = document.getElementById('regenerateCount');
        const submitSection = document.getElementById('step4SubmitSection');
        
        // 로딩 숨기기
        if (loading) loading.style.display = 'none';
        
        // 이슈 섹션 표시
        if (issuesSection) issuesSection.style.display = 'block';
        
        // 이슈 목록 생성
        if (issuesContainer) {
            issuesContainer.innerHTML = '';
            
            issues.forEach((issue, index) => {
                const issueElement = document.createElement('div');
                issueElement.className = 'issue-item';
                issueElement.innerHTML = `
                    <input type="radio" id="issue${index + 1}" name="step4Issue" value="${index + 1}">
                    <label for="issue${index + 1}">
                        <span class="issue-number">${index + 1}</span>
                        <span class="issue-text">${issue}</span>
                    </label>
                `;
                
                // 라디오 버튼 이벤트 리스너
                const radio = issueElement.querySelector('input[type="radio"]');
                if (radio) {
                    radio.onchange = () => this.onStep4IssueSelect();
                }
                
                issuesContainer.appendChild(issueElement);
            });
        }
        
        // 재생성 버튼 업데이트
        if (regenerateBtn && regenerateCountSpan) {
            regenerateCountSpan.textContent = regenerationCount;
            regenerateBtn.style.display = canRegenerate ? 'block' : 'none';
            regenerateBtn.disabled = !canRegenerate;
        }
        
        // 제출 섹션 표시
        if (submitSection) {
            submitSection.style.display = 'block';
        }
    }
    
    onStep4IssueSelect() {
        console.log('✅ Step 4 이슈 선택됨');
        
        const submitBtn = document.getElementById('submitStep4Choice');
        const selectedRadio = document.querySelector('input[name="step4Issue"]:checked');
        
        if (submitBtn) {
            submitBtn.disabled = !selectedRadio;
        }
        
        // 선택된 이슈 저장
        if (selectedRadio) {
            this.selectedStep4Issue = parseInt(selectedRadio.value);
            console.log('📌 선택된 이슈 번호:', this.selectedStep4Issue);
        }
    }
    
    async submitStep4Choice() {
        console.log('📤 Step 4 선택 제출');
        
        if (!this.selectedStep4Issue) {
            this.showError('이슈를 선택해주세요.');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseURL}/career/${this.sessionId}/step4-submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    student_info: this.studentInfo,
                    response: {
                        choice_numbers: [this.selectedStep4Issue]
                    }
                })
            });
            
            const data = await response.json();
            console.log('📊 Step 4 제출 응답:', data);
            
            if (!response.ok) {
                throw new Error(data.detail || 'Step 4 제출에 실패했습니다.');
            }
            
            if (data.success) {
                console.log('✅ Step 4 성공적으로 완료');
                
                // 다음 질문이 있으면 표시
                if (data.data.next_question) {
                    this.currentQuestion = data.data.next_question;
                    this.showQuestionScreen();
                } else {
                    // 모든 단계 완료
                    this.showCompletionScreen();
                }
            } else {
                throw new Error(data.message || 'Step 4 처리에 실패했습니다.');
            }
            
        } catch (error) {
            console.error('❌ Step 4 제출 오류:', error);
            this.showError(error.message);
        }
    }
    
    showStep4Error(message) {
        console.log('❌ Step 4 오류 표시:', message);
        
        const loading = document.getElementById('step4Loading');
        const issues = document.getElementById('step4Issues');
        const error = document.getElementById('step4Error');
        
        if (loading) loading.style.display = 'none';
        if (issues) issues.style.display = 'none';
        if (error) {
            error.style.display = 'block';
            const errorMessage = error.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.textContent = message;
            }
        }
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