/**
 * 중학생 진로 탐색 앱 JavaScript
 * 흥미·강점·가치·미래 관심을 연결하여 "현실적인 진로 목표 + 실행 가능한 실천 계획"을 도출
 */

console.log('🌟 중학생 진로탐색 JavaScript 시작');

// API 기본 URL 설정
const API_BASE_URL = `${window.location.protocol}//${window.location.host}/middle_school`;
console.log('🔗 API 기본 URL:', API_BASE_URL);

// 전역 변수
let sessionId = null;
let studentInfo = null;
let currentQuestionData = null;
let selectedChoices = [];
let encouragementMessage = null;
let finalDream = null;

// DOM 로드 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM 로드 완료');
    
    // 시작 버튼 이벤트 등록
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        console.log('✅ 시작 버튼 발견');
        startBtn.onclick = function() {
            console.log('🖱️ 시작 버튼 클릭됨!');
            startCareerExploration();
        };
    }
    
    // 학생 정보 제출 버튼
    const submitStudentInfoBtn = document.getElementById('submitStudentInfo');
    if (submitStudentInfoBtn) {
        submitStudentInfoBtn.onclick = function() {
            console.log('📝 학생 정보 제출 버튼 클릭');
            submitStudentInfoData();
        };
    }

    // 학년 선택 이벤트 처리
    setupGradeSelection();
    
    // 꿈 확정/수정 버튼 이벤트
    setupDreamConfirmationButtons();
    
    // 드림로직 관련 버튼 이벤트
    setupDreamLogicButtons();
});

// 학년 선택 관련 함수들
function setupGradeSelection() {
    console.log('🎓 학년 선택 이벤트 설정');
    
    const gradeInputs = document.querySelectorAll('input[name="studentGrade"]');
    console.log('📋 학년 체크박스 개수:', gradeInputs.length);
    
    gradeInputs.forEach(input => {
        input.addEventListener('change', function() {
            console.log('🎓 학년 체크박스 클릭:', this.value, '체크됨:', this.checked);
            
            if (this.checked) {
                // 다른 체크박스 해제 (단일 선택)
                gradeInputs.forEach(otherInput => {
                    if (otherInput !== this) {
                        otherInput.checked = false;
                        otherInput.closest('.grade-option').classList.remove('selected');
                    }
                });
                this.closest('.grade-option').classList.add('selected');
                console.log('✅ 학년 선택:', this.value + '학년');
            } else {
                this.closest('.grade-option').classList.remove('selected');
                console.log('❌ 학년 선택 해제');
            }
        });
        
        // div 클릭으로도 선택 가능하게 하기
        const gradeOption = input.closest('.grade-option');
        gradeOption.addEventListener('click', function(e) {
            console.log('🖱️ 학년 옵션 div 클릭');
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'LABEL') {
                input.click();
            }
        });
    });
}
// 추천 결과를 5단계 화면에 표시하는 함수 (ReferenceError 방지)
function displayCareerRecommendation(recommendation) {
    const careerRecommendation = document.getElementById('careerRecommendation');
    if (careerRecommendation) {
        careerRecommendation.innerHTML = recommendation;
    }
}

// 꿈 확정/수정 버튼 이벤트 설정
function setupDreamConfirmationButtons() {
    const confirmBtn = document.getElementById('confirmDream');
    const modifyBtn = document.getElementById('modifyDream');
    const submitModificationBtn = document.getElementById('submitModification');
    const cancelModificationBtn = document.getElementById('cancelModification');
    
    if (confirmBtn) {
        confirmBtn.onclick = () => confirmDream();
    }
    
    if (modifyBtn) {
        modifyBtn.onclick = () => modifyDream();
    }
    
    if (submitModificationBtn) {
        submitModificationBtn.onclick = () => submitDreamModification();
    }
    
    if (cancelModificationBtn) {
        cancelModificationBtn.onclick = () => hideModificationInput();
    }
}

// 드림로직 관련 버튼 이벤트 설정
function setupDreamLogicButtons() {
    const finishBtn = document.getElementById('finishJourney');
    const downloadBtn = document.getElementById('downloadDreamLogicPDF');
    const restartBtn = document.getElementById('restartJourney');
    
    if (finishBtn) {
        finishBtn.onclick = () => finishJourney();
    }
    
    if (downloadBtn) {
        downloadBtn.onclick = () => downloadDreamLogicPDF();
    }
    
    if (restartBtn) {
        restartBtn.onclick = () => restartCareerJourney();
    }
}

// 진로 탐색 시작 함수
async function startCareerExploration() {
    console.log('🚀 진로 탐색 시작');
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/career/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        console.log('📡 API 응답:', data);
        
        if (data.success) {
            sessionId = data.data.session_id;
            console.log('✅ 세션 ID 저장:', sessionId);
            showScreen('studentInfoScreen');
            updateProgress(0);
        } else {
            showError('세션 시작에 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 오류:', error);
        showError('서버 연결에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 학생 정보 제출 함수
async function submitStudentInfoData() {
    console.log('📝 학생 정보 제출 시작');
    
    // 이름 가져오기
    const name = document.getElementById('studentName')?.value.trim();
    console.log('📝 입력된 이름:', name);
    
    // 선택된 학년 가져오기
    const selectedGrade = document.querySelector('input[name="studentGrade"]:checked');
    const grade = selectedGrade ? parseInt(selectedGrade.value) : null;
    console.log('📝 선택된 학년:', grade);

    if (!name || !grade) {
        console.error('❌ 필수 정보 누락 - 이름:', name, '학년:', grade);
        showError('이름과 학년을 입력해주세요.');
        return;
    }

    // 학생 정보 객체 생성
    studentInfo = { name, grade };
    console.log('📝 최종 학생 정보:', studentInfo);

    try {
        showLoading(true);

        const requestBody = {
            session_id: sessionId,
            student_info: studentInfo,
            response: {
                choice_numbers: [],
                custom_answer: `안녕하세요! 저는 ${name}이고 ${grade}학년이에요.`
            }
        };

        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`서버 응답 오류: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('📡 학생정보 제출 응답:', data);
        
        if (data.success) {
            console.log('🎉 학생 정보 서버 저장 성공!');
            
            if (data.data && data.data.next_question) {
                console.log('📝 다음 질문 데이터 수신:', data.data.next_question);
                showQuestionScreen(data.data.next_question);
            } else {
                showError('다음 단계 정보를 불러올 수 없습니다.');
            }
        } else {
            showError('학생 정보 저장에 실패했습니다: ' + (data.message || ''));
        }
    } catch (error) {
        console.error('❌ 네트워크 오류:', error);
        showError('서버 연결에 실패했습니다: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// 화면 전환 함수
function showScreen(screenId) {
    console.log('🖼️ 화면 전환:', screenId);
    
    const screens = [
        'startScreen', 'studentInfoScreen', 'questionScreen', 
        'recommendationScreen', 'dreamLogicScreen', 'completionScreen'
    ];
    
    screens.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });

    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.style.display = 'block';
    }
    
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = screenId !== 'startScreen' ? 'block' : 'none';
    }
}

// 진행률 업데이트 함수 (중학교는 6단계)
function updateProgress(stage, completed = false) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (!progressFill || !progressText) return;
    
    let percentage;
    let text;
    
    if (completed) {
        percentage = 100;
        text = '완료! 🎉';
    } else {
        percentage = (stage / 6) * 100; // 중학교는 6단계
        text = `${stage}단계 / 6단계`;
    }
    
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = text;
}

// 현재 단계 번호 가져오기 함수
function getCurrentStage() {
    if (currentQuestionData && currentQuestionData.stage) {
        return parseInt(currentQuestionData.stage.replace('step_', ''));
    }
    return 1;
}

// 단계별 제목 매핑
function getStageTitle(stageNumber) {
    const stageTitles = {
        0: "안녕하세요! 진로 탐색을 시작해볼까요? 이름과 학년을 알려주세요!",
        1: "무엇을 할 때 시간이 빠르게 지나가나요? (2개까지 가능해요)",
        2: "팀이나 프로젝트에서 특히 잘하는 부분은 무엇인가요? (1개만 선택)",
        3: "어떤 순간에 가장 보람이나 행복을 느끼나요? (1개만 선택)",
        4: "미래 사회에서 특히 걱정되는 주제를 골라 주세요. (1개만 선택)",
        5: "AI가 분석한 맞춤 꿈을 확인해주세요!",
        6: "꿈을 이루는 구체적인 실천 계획을 만들어보아요!"
    };
    return stageTitles[stageNumber] || "질문";
}

// 질문 화면 표시 함수
function showQuestionScreen(questionData) {
    console.log('📋 질문 화면 표시:', questionData);
    console.log('🔍 동적 선택지 확인:', questionData.dynamic_choices);
    console.log('🔍 기본 선택지 확인:', questionData.choices);
    currentQuestionData = questionData;
    selectedChoices = [];
    
    // 질문 화면으로 전환
    showScreen('questionScreen');
    
    // 진행률 업데이트
    const stageNumber = questionData.stage ? parseInt(questionData.stage.replace('step_', '')) : 1;
    updateProgress(stageNumber);
    
    // 질문 내용 업데이트
    const questionTitle = document.getElementById('questionTitle');
    const questionContent = document.getElementById('questionDescription');
    const choicesContainer = document.getElementById('choicesContainer');
    
    const stageQuestion = getStageTitle(stageNumber);
    
    if (questionTitle) {
        questionTitle.textContent = `${stageNumber}단계`;
    }
    
    if (questionContent) {
        const finalQuestion = stageQuestion || questionData.question || '';
        questionContent.textContent = finalQuestion;
    }
    
    // 선택지 렌더링
    if (choicesContainer) {
        choicesContainer.innerHTML = '';
        const isMultipleChoice = stageNumber === 1; // 1단계만 다중선택
        
        // 4단계 동적 선택지 확인
        const choicesToRender = questionData.dynamic_choices || questionData.choices;
        const isDynamicChoices = stageNumber === 4 && questionData.dynamic_choices;
        
        console.log('🔍 단계 번호:', stageNumber);
        console.log('🔍 렌더링할 선택지:', choicesToRender);
        console.log('🔍 동적 선택지 여부:', isDynamicChoices);
        
        if (choicesToRender) {
            choicesToRender.forEach((choice, index) => {
                const choiceDiv = document.createElement('div');
                choiceDiv.className = 'choice-item';
                choiceDiv.style.cursor = 'pointer';
                
                const input = document.createElement('input');
                input.type = isMultipleChoice ? 'checkbox' : 'radio';
                input.name = 'choice';
                input.value = index + 1;
                input.id = `choice${index + 1}`;
                
                const label = document.createElement('label');
                label.htmlFor = `choice${index + 1}`;
                label.textContent = choice;
                label.style.cursor = 'pointer';
                
                // "기타" 항목인지 확인 (동적 선택지가 아닌 경우에만)
                const isOtherOption = !isDynamicChoices && (choice.includes('기타') || choice === '기타');
            
            // 입력 변경 이벤트 핸들러
            const handleInputChange = () => {
                console.log('🔥 선택지 변경:', choice, 'checked:', input.checked);
                
                if (isOtherOption) {
                    // 기타 항목 처리
                    if (input.checked) {
                        // 기타 선택 시 다른 모든 선택 해제
                        document.querySelectorAll('input[name="choice"]').forEach(inp => {
                            if (inp !== input) {
                                inp.checked = false;
                            }
                        });
                        handleOtherSelection(input, stageNumber);
                    } else {
                        handleOtherSelection(input, stageNumber);
                    }
                } else {
                    // 일반 항목 처리
                    if (input.checked) {
                        if (isMultipleChoice) {
                            // 다중 선택에서 2개 제한 체크
                            const checkedInputs = document.querySelectorAll('input[name="choice"]:checked');
                            const nonOtherChecked = Array.from(checkedInputs).filter(inp => {
                                const label = document.querySelector(`label[for="${inp.id}"]`);
                                return label && !(label.textContent.includes('기타') || label.textContent === '기타');
                            });
                            if (nonOtherChecked.length > 2) {
                                input.checked = false;
                                showError('최대 2개까지만 선택할 수 있습니다.');
                                return;
                            }
                        }
                        
                        // 일반 항목 선택 시 기타 항목 해제 (입력값은 유지)
                        document.querySelectorAll('input[name="choice"]').forEach(inp => {
                            const label = document.querySelector(`label[for="${inp.id}"]`);
                            const isOther = label && (label.textContent.includes('기타') || label.textContent === '기타');
                            if (isOther && inp.checked) {
                                inp.checked = false;
                                // 입력값 유지를 위해 clearInput = false로 호출
                                handleOtherSelection(inp, stageNumber, false);
                            }
                        });
                    }
                }
                
                // 모든 경우에 선택 상태 업데이트
                updateSelectedChoices();
            };
            
            // 전체 div 클릭으로도 선택 가능하도록
            const handleDivClick = (e) => {
                // input이나 label을 직접 클릭한 경우는 제외
                if (e.target === input || e.target === label) {
                    return;
                }
                
                // div 클릭 시 input 상태 토글
                if (isMultipleChoice) {
                    // 체크박스 모드
                    input.checked = !input.checked;
                } else {
                    // 라디오 버튼 모드
                    if (!input.checked) {
                        input.checked = true;
                    }
                }
                
                // 변경 이벤트 발생
                handleInputChange();
            };
            
            // 이벤트 리스너 등록
            choiceDiv.addEventListener('click', handleDivClick);
            input.addEventListener('change', handleInputChange);
            
                choiceDiv.appendChild(input);
                choiceDiv.appendChild(label);
                choicesContainer.appendChild(choiceDiv);
            });
            
            // 4단계 동적 선택지인 경우 재생성 버튼 추가
            if (isDynamicChoices) {
                const regenerateCount = questionData.regenerate_count || 0;
                const maxRegenerate = questionData.max_regenerate || 5;
                
                if (regenerateCount < maxRegenerate) {
                    const regenerateDiv = document.createElement('div');
                    regenerateDiv.className = 'regenerate-container';
                    regenerateDiv.style.marginTop = '15px';
                    regenerateDiv.style.textAlign = 'center';
                    
                    const regenerateBtn = document.createElement('button');
                    regenerateBtn.className = 'btn btn-secondary';
                    regenerateBtn.textContent = `🔄 다른 선택지 보기 (${regenerateCount}/${maxRegenerate})`;
                    regenerateBtn.onclick = () => regenerateStep4Choices();
                    
                    regenerateDiv.appendChild(regenerateBtn);
                    choicesContainer.appendChild(regenerateDiv);
                }
            }
        }
    }    // 커스텀 입력창 초기화
    const customAnswerContainer = document.getElementById('customAnswerContainer');
    const customAnswerInput = document.getElementById('customAnswer');
    if (customAnswerContainer) {
        customAnswerContainer.style.display = 'none';
    }
    if (customAnswerInput) {
        customAnswerInput.value = '';
    }
    
    // 제출 버튼 업데이트
    const submitButton = document.getElementById('submitAnswer');
    if (submitButton) {
        submitButton.textContent = '🚀 다음 단계로';
        submitButton.disabled = true;
        submitButton.onclick = () => submitCurrentAnswer();
    }
}

// "기타" 선택 처리 함수
function handleOtherSelection(clickedInput, stageNumber, clearInput = true) {
    console.log('📝 기타 선택 처리:', clickedInput.value, 'Stage:', stageNumber, 'Checked:', clickedInput.checked);
    
    const customAnswerContainer = document.getElementById('customAnswerContainer');
    const customAnswerInput = document.getElementById('customAnswer');
    
    if (clickedInput.checked) {
        // 기타 선택 시
        if (customAnswerContainer) {
            customAnswerContainer.style.display = 'block';
        }
        if (customAnswerInput) {
            customAnswerInput.focus();
            customAnswerInput.oninput = () => updateSubmitButton();
        }
    } else {
        // 기타 선택 해제 시
        if (customAnswerContainer) {
            customAnswerContainer.style.display = 'none';
        }
        // clearInput가 true일 때만 입력값 지우기 (직접 기타를 클릭해서 해제할 때)
        // false일 때는 입력값 유지 (일반 선택지를 클릭해서 기타가 해제될 때)
        if (customAnswerInput && clearInput) {
            customAnswerInput.value = '';
        }
    }
    
    updateSelectedChoices();
}

// 선택된 선택지 업데이트
function updateSelectedChoices() {
    console.log('🔄 updateSelectedChoices 호출됨');
    
    const checkedInputs = document.querySelectorAll('input[name="choice"]:checked');
    selectedChoices = Array.from(checkedInputs).map(input => parseInt(input.value));
    console.log('📋 선택된 선택지 번호들:', selectedChoices);
    
    // 모든 choice-item에 대해 선택 상태 시각적 표시 업데이트
    document.querySelectorAll('.choice-item').forEach((choiceDiv, index) => {
        const input = choiceDiv.querySelector('input');
        if (input && input.checked) {
            choiceDiv.classList.add('selected');
        } else {
            choiceDiv.classList.remove('selected');
        }
    });
    
    // 기타가 선택되어 있는지 확인
    const otherInputChecked = Array.from(checkedInputs).some(input => {
        const label = document.querySelector(`label[for="${input.id}"]`);
        return label && (label.textContent.includes('기타') || label.textContent === '기타');
    });
    
    const customAnswerContainer = document.getElementById('customAnswerContainer');
    const customAnswerInput = document.getElementById('customAnswer');
    
    if (customAnswerContainer) {
        if (otherInputChecked) {
            customAnswerContainer.style.display = 'block';
        } else {
            customAnswerContainer.style.display = 'none';
            if (customAnswerInput) {
                customAnswerInput.value = '';
            }
        }
    }
    
    updateSubmitButton();
}

// 제출 버튼 상태 업데이트
function updateSubmitButton() {
    const submitButton = document.getElementById('submitAnswer');
    const customAnswerInput = document.getElementById('customAnswer');
    const customAnswerContainer = document.getElementById('customAnswerContainer');
    
    if (submitButton) {
        let canSubmit = false;
        
        if (customAnswerContainer && customAnswerContainer.style.display !== 'none') {
            // 커스텀 입력이 활성화된 경우
            const customValue = customAnswerInput ? customAnswerInput.value.trim() : '';
            canSubmit = customValue.length > 0;
        } else {
            // 일반 선택지의 경우
            canSubmit = selectedChoices.length > 0;
        }
        
        submitButton.disabled = !canSubmit;
    }
}

// 4단계 선택지 재생성 함수
async function regenerateStep4Choices() {
    console.log('🔄 4단계 선택지 재생성 요청');
    
    if (!sessionId) {
        showError('세션이 유효하지 않습니다.');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/regenerate-step4`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 4단계 재생성 성공:', data);
            
            // 새로운 선택지로 업데이트
            if (data.data && data.data.choices) {
                // 현재 질문 데이터에 새로운 동적 선택지 업데이트
                currentQuestionData.dynamic_choices = data.data.choices;
                currentQuestionData.regenerate_count = data.data.regenerate_count;
                
                // 화면 다시 렌더링
                showQuestionScreen(currentQuestionData);
                
                console.log('✅ 새로운 선택지가 생성되었습니다! 🎯');
                // showSuccess('새로운 선택지가 생성되었습니다! 🎯');
            } else {
                console.error('❌ 응답 데이터가 올바르지 않습니다:', data);
                showError('선택지 업데이트에 실패했습니다.');
            }
        } else {
            console.error('❌ 4단계 재생성 실패:', response.status, response.statusText);
            try {
                const errorData = await response.json();
                console.error('❌ 에러 상세:', errorData);
                showError(errorData.detail || '선택지 재생성에 실패했습니다.');
            } catch (parseError) {
                console.error('❌ 응답 파싱 오류:', parseError);
                showError(`서버 오류 (${response.status}): 선택지 재생성에 실패했습니다.`);
            }
        }
    } catch (error) {
        console.error('❌ 4단계 재생성 오류:', error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showError('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
        } else {
            showError(`오류가 발생했습니다: ${error.message}`);
        }
    } finally {
        showLoading(false);
    }
}

// 현재 답변 제출 함수
async function submitCurrentAnswer() {
    if (selectedChoices.length === 0) {
        showError('선택지를 하나 이상 선택해주세요.');
        return;
    }
    
    // 기타 항목이 선택되어 있는지 확인
    const checkedInputs = document.querySelectorAll('input[name="choice"]:checked');
    const otherInputSelected = Array.from(checkedInputs).some(input => {
        const label = document.querySelector(`label[for="${input.id}"]`);
        return label && (label.textContent.includes('기타') || label.textContent === '기타');
    });
    
    // 커스텀 입력 처리
    const customAnswerContainer = document.getElementById('customAnswerContainer');
    const customAnswerInput = document.getElementById('customAnswer');
    let customAnswer = "";
    
    if (otherInputSelected && customAnswerContainer && customAnswerContainer.style.display !== 'none' && customAnswerInput) {
        customAnswer = customAnswerInput.value.trim();
        if (!customAnswer) {
            showError('기타를 선택하셨습니다. 내용을 입력해주세요.');
            return;
        }
    }
    
    console.log('✅ 선택 제출:', selectedChoices);
    console.log('✅ 커스텀 답변:', customAnswer);
    console.log('✅ 기타 선택 여부:', otherInputSelected);
    
    try {
        showLoading(true);
        
        // 요청 본문 구성 - 기타가 선택되지 않았으면 custom_answer 필드 제외
        const requestBody = {
            session_id: sessionId,
            student_info: studentInfo,
            response: {
                choice_numbers: selectedChoices
            }
        };
        
        // 기타가 선택되고 입력값이 있을 때만 custom_answer 추가
        if (otherInputSelected && customAnswer) {
            requestBody.response.custom_answer = customAnswer;
        }
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        console.log('📡 선택 응답:', data);
        
        if (data.success) {
            if (data.data.next_question) {
                // 5단계인 경우 AI 추천 요청
                const nextStage = data.data.next_question.stage;
                if (nextStage === 'step_5') {
                    await requestAIRecommendation();
                } else {
                    // 다음 질문으로 이동
                    showQuestionScreen(data.data.next_question);
                }
            } else {
                // 완료 화면
                showScreen('completionScreen');
                updateProgress(6, true);
            }
        } else {
            showError('응답 처리에 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 오류:', error);
        showError('서버 연결에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// AI 추천 요청 함수 (5단계)
async function requestAIRecommendation() {
    console.log('🤖 AI 진로 추천 요청');
    
    try {
        // 추천 화면 표시
        showScreen('recommendationScreen');
        updateProgress(5);
        
        // 학생 이름 표시
        const studentNameDisplay = document.getElementById('studentNameDisplay');
        if (studentNameDisplay && studentInfo) {
            studentNameDisplay.textContent = `${studentInfo.name}님`;
        }
        
        // 로딩 표시
        const recommendationLoading = document.getElementById('recommendationLoading');
        const recommendationResult = document.getElementById('recommendationResult');
        
        if (recommendationLoading) {
            recommendationLoading.style.display = 'block';
        }
        if (recommendationResult) {
            recommendationResult.style.display = 'none';
        }
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        console.log('🤖 AI 추천 응답:', data);
        
        if (data.success && data.data.career_recommendation) {
            // 2초 후 결과 표시
            setTimeout(() => {
                if (recommendationLoading) {
                    recommendationLoading.style.display = 'none';
                }
                if (recommendationResult) {
                    recommendationResult.style.display = 'block';
                }
                
                const careerRecommendation = document.getElementById('careerRecommendation');
                if (careerRecommendation) {
                    careerRecommendation.innerHTML = data.data.career_recommendation;
                }
            }, 2000);
        } else {
            showError('AI 진로 추천을 받아오는데 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ AI 추천 오류:', error);
        showError('AI 진로 추천 서비스에 연결할 수 없습니다.');
    }
}

// 꿈 확정 함수
async function confirmDream() {
    console.log('👍 꿈 확정');
    
    const careerRecommendation = document.getElementById('careerRecommendation');
    if (!careerRecommendation) {
        showError('추천된 꿈을 찾을 수 없습니다.');
        return;
    }
    
    const dreamStatement = careerRecommendation.textContent || careerRecommendation.innerText;
    finalDream = dreamStatement.trim();
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/dream-confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: "confirm",
                dream_statement: finalDream
            })
        });
        
        const data = await response.json();
        console.log('👍 꿈 확정 응답:', data);
        
        if (data.success) {
            // 드림로직 생성으로 이동
            await generateDreamLogic();
        } else {
            showError('꿈 확정에 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 꿈 확정 오류:', error);
        showError('서버 연결에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 수정 요청 - 바로 새로운 추천 생성
async function modifyDream() {
    console.log('✏️ 꿈 수정 요청 - 새로운 추천 생성');
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/dream-confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: "modify"
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✏️ 새로운 추천 응답:', data);
        
        if (data.success && data.data && data.data.career_recommendation) {
            // 새로운 추천 표시
            displayCareerRecommendation(data.data.career_recommendation);
            console.log('✅ 새로운 진로 추천이 생성되었습니다! 🎯');
        } else {
            showError('새로운 추천 생성에 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 수정 요청 오류:', error);
        showError('서버 연결에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 수정 옵션 화면 표시
function showModificationOptions(data) {
    console.log('📝 수정 옵션 표시:', data);
    
    const container = document.getElementById('stage5Content');
    if (!container) return;
    
    container.innerHTML = `
        <div class="modification-options">
            <h3>🔧 수정할 부분을 선택해주세요</h3>
            <p>기존 답변을 수정하고 새로운 진로 추천을 받아보세요!</p>
            
            <div class="options-grid">
                ${data.modification_options.map(option => `
                    <div class="modification-option" onclick="selectModificationStep('${option.id}', '${option.title}')">
                        <h4>${option.title}</h4>
                        <p>${option.description}</p>
                        <div class="current-answer">
                            <strong>현재 답변:</strong>
                            ${formatCurrentAnswer(option.id, data.current_answers)}
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="action-buttons">
                <button onclick="goBackToRecommendation()" class="btn btn-secondary">
                    ↩️ 돌아가기
                </button>
            </div>
        </div>
    `;
}

// 현재 답변 포맷팅
function formatCurrentAnswer(stepId, currentAnswers) {
    const answer = currentAnswers[stepId];
    if (!answer) return '없음';
    
    let result = '';
    if (answer.choice_numbers && answer.choice_numbers.length > 0) {
        result += `선택: ${answer.choice_numbers.join(', ')}번`;
    }
    if (answer.custom_answer) {
        result += result ? ` (기타: ${answer.custom_answer})` : `기타: ${answer.custom_answer}`;
    }
    
    return result || '없음';
}

// 수정할 단계 선택
async function selectModificationStep(stepId, stepTitle) {
    console.log('📝 수정 단계 선택:', stepId, stepTitle);
    
    // 해당 단계로 이동하여 새로운 답변 받기
    const stageNumber = parseInt(stepId.replace('step', ''));
    
    // 임시로 currentStage 변경
    const originalStage = currentStage;
    currentStage = stageNumber;
    
    // 해당 단계 질문 표시
    await loadStageQuestion(stageNumber);
    
    // 수정 모드임을 표시
    const container = document.getElementById(`stage${stageNumber}Content`);
    if (container) {
        const modificationNotice = document.createElement('div');
        modificationNotice.className = 'modification-notice';
        modificationNotice.innerHTML = `
            <div class="alert alert-info">
                <strong>🔧 수정 모드</strong><br>
                ${stepTitle}의 답변을 수정하고 있습니다. 새로운 답변을 선택한 후 "새로운 추천 받기"를 클릭하세요.
            </div>
        `;
        container.insertBefore(modificationNotice, container.firstChild);
        
        // 제출 버튼 텍스트 변경
        const submitButton = document.getElementById('submitAnswer');
        if (submitButton) {
            submitButton.textContent = '🔄 새로운 추천 받기';
            submitButton.onclick = () => submitModifiedAnswer(stepId);
        }
    }
    
    // 5단계 화면 숨기고 해당 단계 화면 표시
    showScreen(`stage${stageNumber}Screen`);
}

// 수정된 답변 제출
async function submitModifiedAnswer(stepId) {
    console.log('🔄 수정된 답변 제출:', stepId);
    
    const stageNumber = parseInt(stepId.replace('step', ''));
    
    // 현재 선택된 답변 수집
    const checkedInputs = document.querySelectorAll('input[name="choice"]:checked');
    const choiceNumbers = Array.from(checkedInputs).map(input => parseInt(input.value));
    const customAnswer = document.getElementById('customAnswer')?.value || '';
    
    if (choiceNumbers.length === 0) {
        showError('답변을 선택해주세요.');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/regenerate-with-changes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                step_to_modify: stepId,
                new_answer: {
                    choice_numbers: choiceNumbers,
                    custom_answer: customAnswer
                }
            })
        });
        
        const data = await response.json();
        console.log('🔄 수정된 추천 응답:', data);
        
        if (data.success) {
            // 새로운 추천 표시
            showScreen('stage5Screen');
            displayCareerRecommendation(data.data.career_recommendation);
            
            // 성공 메시지
            showSuccess('새로운 진로 추천이 생성되었습니다!');
        } else {
            showError('새로운 추천 생성에 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 수정된 답변 제출 오류:', error);
        showError('서버 연결에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 추천 화면으로 돌아가기
function goBackToRecommendation() {
    console.log('↩️ 추천 화면으로 돌아가기');
    showScreen('stage5Screen');
}

// 수정 요청 입력창 표시
function showModificationInput() {
    const modificationContainer = document.getElementById('modificationContainer');
    if (modificationContainer) {
        modificationContainer.style.display = 'block';
        const textarea = document.getElementById('modificationRequest');
        if (textarea) {
            textarea.focus();
        }
    }
}

// 수정 요청 입력창 숨기기
function hideModificationInput() {
    const modificationContainer = document.getElementById('modificationContainer');
    if (modificationContainer) {
        modificationContainer.style.display = 'none';
        const textarea = document.getElementById('modificationRequest');
        if (textarea) {
            textarea.value = '';
        }
    }
}

// 꿈 수정 요청 제출
async function submitDreamModification() {
    const modificationInput = document.getElementById('modificationRequest');
    if (!modificationInput) {
        showError('수정 요청을 입력할 수 없습니다.');
        return;
    }
    
    const modificationRequest = modificationInput.value.trim();
    if (!modificationRequest) {
        showError('수정하고 싶은 내용을 입력해주세요.');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/dream-confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: "modify",
                modification_request: modificationRequest
            })
        });
        
        const data = await response.json();
        console.log('🔄 꿈 수정 응답:', data);
        
        if (data.success && data.data.modified_dream) {
            // 수정된 꿈으로 업데이트
            const careerRecommendation = document.getElementById('careerRecommendation');
            if (careerRecommendation) {
                careerRecommendation.innerHTML = data.data.modified_dream;
            }
            
            // 수정 입력창 숨기기
            hideModificationInput();
        } else {
            showError('꿈 수정에 실패했습니다.');
        }
    } catch (error) {
        console.error('❌ 꿈 수정 오류:', error);
        showError('서버 연결에 실패했습니다.');
    } finally {
        showLoading(false);
    }
}

// 드림로직 생성 함수 (6단계)
async function generateDreamLogic() {
    console.log('🌈 드림로직 생성 요청 시작');
    
    try {
        // 드림로직 화면으로 전환
        showScreen('dreamLogicScreen');
        updateProgress(6);
        
        // 로딩 표시
        const dreamLogicLoading = document.getElementById('dreamLogicLoading');
        const dreamLogicResult = document.getElementById('dreamLogicResult');
        
        if (dreamLogicLoading) {
            dreamLogicLoading.style.display = 'block';
        }
        if (dreamLogicResult) {
            dreamLogicResult.style.display = 'none';
        }
        
        // API 호출
        const response = await fetch(`${API_BASE_URL}/career/${sessionId}/dream-logic`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        console.log('🌈 드림로직 응답:', data);
        
        if (data.success && data.data && data.data.dream_logic) {
            // 3초 후 드림로직 결과 표시
            setTimeout(() => {
                if (dreamLogicLoading) {
                    dreamLogicLoading.style.display = 'none';
                }
                if (dreamLogicResult) {
                    dreamLogicResult.style.display = 'block';
                }
                
                const dreamSteps = document.getElementById('dreamSteps');
                if (dreamSteps) {
                    const formattedContent = formatDreamLogic(data.data.dream_logic);
                    dreamSteps.innerHTML = formattedContent;
                }
                
                // 액션 버튼 표시
                const dreamLogicActions = document.getElementById('dreamLogicActions');
                if (dreamLogicActions) {
                    dreamLogicActions.style.display = 'block';
                }
            }, 3000);
        } else {
            showError('드림로직 생성에 실패했습니다.');
            showScreen('recommendationScreen');
        }
    } catch (error) {
        console.error('❌ 드림로직 생성 오류:', error);
        showError('드림로직 생성 서비스에 연결할 수 없습니다.');
        showScreen('recommendationScreen');
    }
}

// 드림로직 텍스트를 HTML로 포맷팅
function formatDreamLogic(dreamLogicText) {
    console.log('🎨 드림로직 포맷팅 시작:', dreamLogicText);
    
    let formatted = '<div class="dream-logic-content">';
    const lines = dreamLogicText.split('\n');
    let currentSection = '';
    let inSchoolActivity = false;
    let inPersonalActivity = false;
    let foundEncouragement = false;
    let collectingEncouragement = false;
    let encouragementLines = [];
    
    for (let line of lines) {
        line = line.trim();
        if (!line) continue;
        
        console.log('처리 중인 라인:', line);
        
        // 응원 메모 시작 감지 (💬 응원 메모 또는 응원메모, 응원메시지 등)
        if ((line.includes('💬') && line.includes('응원')) || 
            (line.includes('응원') && (line.includes('메모') || line.includes('메시지')))) {
            console.log('🎯 응원메모 시작 라인 발견:', line);
            
            if (inSchoolActivity || inPersonalActivity) {
                formatted += '</ul></div>';
                inSchoolActivity = false;
                inPersonalActivity = false;
            }
            
            collectingEncouragement = true;
            foundEncouragement = true;
            
            // 응원메모 텍스트 추출
            const patterns = [
                /💬\s*응원\s*메모\s*/i,
                /응원\s*메모\s*[:：]\s*/i,
                /응원메모\s*[:：]\s*/i,
                /응원\s*메시지\s*[:：]\s*/i
            ];
            
            let encouragementText = line;
            for (const pattern of patterns) {
                if (pattern.test(line)) {
                    encouragementText = line.replace(pattern, '').trim();
                    break;
                }
            }
            
            if (encouragementText) {
                encouragementLines.push(encouragementText);
            }
            continue;
        }
        
        // 응원메모 수집 중이면 다음 라인들도 수집
        if (collectingEncouragement) {
            // 새로운 섹션이 시작되면 응원메모 수집 종료
            if (line.match(/^\[.+\]$/) || line.startsWith('최종꿈:')) {
                collectingEncouragement = false;
                console.log('🔚 응원메모 수집 종료 - 새 섹션 시작');
            } else {
                encouragementLines.push(line);
                console.log('📝 응원메모 라인 수집:', line);
                continue;
            }
        }
        
        // 드림로직 제목 (대괄호)
        if (line.match(/^\[.+의 드림 로직\]$/)) {
            formatted += `<h3>${line}</h3>`;
        }
        // 최종꿈
        else if (line.startsWith('최종꿈:')) {
            const dream = line.replace('최종꿈:', '').trim();
            formatted += `<div class="final-dream"><strong>🌟 최종꿈:</strong> ${dream}</div>`;
        }
        // 중간목표 (중학교 형식: [중간목표 1] 핵심 역량 A)
        else if (line.match(/^\[중간목표\s*\d+\]/)) {
            if (inSchoolActivity || inPersonalActivity) {
                formatted += '</ul></div>';
                inSchoolActivity = false;
                inPersonalActivity = false;
            }
            formatted += `<h4>${line}</h4>`;
            currentSection = 'goal';
        }
        // 설명
        else if (line.startsWith('설명:')) {
            const content = line.replace('설명:', '').trim();
            formatted += `<p style="margin-left: 15px; color: #666; font-style: italic;">${content}</p>`;
        }
        // 실천활동(학교)
        else if (line.includes('실천활동(학교)')) {
            if (inPersonalActivity) {
                formatted += '</ul></div>';
                inPersonalActivity = false;
            }
            formatted += `<h5>📚 실천활동(학교)</h5>`;
            formatted += '<div class="activity-container"><ul>';
            inSchoolActivity = true;
            
            // 같은 줄에 내용이 있으면 추가 (콜론 뒤 내용)
            const content = line.replace(/실천활동\(학교\)\s*[:：]\s*/i, '').trim();
            if (content) {
                // 슬래시로 구분된 여러 활동 처리
                const activities = content.split('/').map(act => act.trim()).filter(act => act);
                activities.forEach(activity => {
                    formatted += `<li class="school-activity">${activity}</li>`;
                });
            }
        }
        // 실천활동(일상)
        else if (line.includes('실천활동(일상)')) {
            if (inSchoolActivity) {
                formatted += '</ul></div>';
                inSchoolActivity = false;
            }
            formatted += `<h5>🏠 실천활동(일상)</h5>`;
            formatted += '<div class="activity-container"><ul>';
            inPersonalActivity = true;
            
            // 같은 줄에 내용이 있으면 추가 (콜론 뒤 내용)
            const content = line.replace(/실천활동\(일상\)\s*[:：]\s*/i, '').trim();
            if (content) {
                // 슬래시로 구분된 여러 활동 처리
                const activities = content.split('/').map(act => act.trim()).filter(act => act);
                activities.forEach(activity => {
                    formatted += `<li class="personal-activity">${activity}</li>`;
                });
            }
        }
        // 추천 활동
        else if (line.includes('추천 활동')) {
            if (inSchoolActivity || inPersonalActivity) {
                formatted += '</ul></div>';
                inSchoolActivity = false;
                inPersonalActivity = false;
            }
            formatted += `<h5>🎯 추천 활동</h5>`;
            const content = line.replace(/추천\s*활동\s*[:：]\s*/i, '').trim();
            if (content) {
                formatted += `<p style="margin-left: 15px; color: #666;">${content}</p>`;
            }
        }
        // 활동 리스트 항목 (점, 대시, 별표로 시작)
        else if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
            const content = line.replace(/^[•\-*]\s*/, '');
            if (inSchoolActivity) {
                formatted += `<li class="school-activity">${content}</li>`;
            } else if (inPersonalActivity) {
                formatted += `<li class="personal-activity">${content}</li>`;
            } else {
                formatted += `<li>${content}</li>`;
            }
        }
        // 기타 텍스트
        else if (line.length > 0 && !collectingEncouragement) {
            if (currentSection === 'goal' && !line.includes('실천활동') && !line.includes('추천 활동')) {
                formatted += `<p style="margin-left: 15px; color: #666; font-style: italic;">${line}</p>`;
            }
        }
    }
    
    // 마지막에 열린 컨테이너들 닫기
    if (inSchoolActivity || inPersonalActivity) {
        formatted += '</ul></div>';
    }
    
    formatted += '</div>';
    
    // 수집된 응원메모 저장
    if (foundEncouragement && encouragementLines.length > 0) {
        encouragementMessage = encouragementLines.join(' ').trim();
        console.log('💝 최종 응원메모:', encouragementMessage);
        
        // 응원메모 표시
        setTimeout(() => {
            showEncouragementInDreamLogic();
        }, 100);
    }
    
    return formatted;
}

// 드림로직 화면에 응원메모 표시
function showEncouragementInDreamLogic() {
    console.log('💝 응원메모 표시:', encouragementMessage);
    
    const encouragementDiv = document.getElementById('encouragementMessage');
    
    if (encouragementDiv && encouragementMessage && encouragementMessage.trim() !== '') {
        encouragementDiv.innerHTML = `
            <div class="encouragement-card">
                <h3>💝 AI가 보내는 특별한 응원 메시지</h3>
                <p>${encouragementMessage}</p>
            </div>
        `;
        encouragementDiv.style.display = 'block';
        console.log('✅ 응원메모 표시 완료!');
    }
}

// 진로 탐색 완료 후 홈페이지로 이동하는 함수
function finishJourney() {
    console.log('🏆 진로 탐색 완료 - 홈페이지로 이동');
    window.location.href = '/';
}

// 최종 완료 화면 표시
function showFinalCompletion() {
    console.log('🎉 최종 완료 화면 표시');
    
    showScreen('completionScreen');
    updateProgress(6, true);
    
    const completionTitle = document.getElementById('completionTitle');
    const completionMessage = document.getElementById('completionMessage');
    const finalDreamDiv = document.getElementById('finalDream');
    
    if (completionTitle && studentInfo) {
        completionTitle.textContent = `수고했어요, ${studentInfo.name}님! 🎉`;
    }
    
    if (completionMessage) {
        completionMessage.textContent = '드림로직이 완성되었습니다! 꿈을 향한 첫걸음을 시작해보세요!';
    }
    
    if (finalDreamDiv && finalDream) {
        finalDreamDiv.innerHTML = `
            <div class="final-career-card">
                <h3>🎯 확정된 꿈</h3>
                <p>${finalDream}</p>
            </div>
        `;
    }
    
    // 응원메모 표시
    const finalEncouragement = document.getElementById('finalEncouragement');
    const finalEncouragementText = document.getElementById('finalEncouragementText');
    
    if (finalEncouragement && finalEncouragementText) {
        let messageToShow = encouragementMessage;
        
        if (!messageToShow || messageToShow.trim() === '') {
            messageToShow = `${studentInfo?.name || '여러분'}의 열정과 노력이 있다면 분명 멋진 꿈을 이룰 수 있을 거예요! 😊💪`;
        }
        
        finalEncouragementText.textContent = messageToShow;
        finalEncouragement.style.display = 'block';
    }
}

// 드림로직 PDF 다운로드
async function downloadDreamLogicPDF() {
    console.log('📄 드림로직 PDF 다운로드');
    
    if (!studentInfo || !sessionId) {
        showError('학생 정보가 없습니다. 다시 시작해주세요.');
        return;
    }
    
    try {
        showLoading(true);
        
        // 세션 데이터 조회
        const sessionResponse = await fetch(`${API_BASE_URL}/career/${sessionId}/data`);
        const sessionData = await sessionResponse.json();
        
        if (!sessionData.success) {
            throw new Error('세션 데이터를 가져올 수 없습니다.');
        }
        
        const responses = sessionData.data.responses;
        const finalRecommendation = sessionData.data.final_dream || finalDream || '진로 추천 정보 없음';
        
        // 드림로직 결과 가져오기
        const dreamLogicElement = document.getElementById('dreamSteps');
        const dreamLogicResult = dreamLogicElement ? dreamLogicElement.innerText : '';
        
        // PDF 다운로드 요청
        const pdfResponse = await fetch(`${API_BASE_URL}/career/download-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_name: studentInfo.name,
                responses: responses,
                final_recommendation: finalRecommendation,
                dream_logic_result: dreamLogicResult,
                encouragement_message: encouragementMessage || ''
            })
        });
        
        if (!pdfResponse.ok) {
            throw new Error('PDF 생성에 실패했습니다.');
        }
        
        // PDF 파일 다운로드
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
        a.download = `${studentInfo.name}_중학교진로탐색_드림로직_${timestamp}.pdf`;
        
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ 드림로직 PDF 다운로드 완료');
        
    } catch (error) {
        console.error('❌ PDF 다운로드 오류:', error);
        showError(`PDF 다운로드에 실패했습니다: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// 여정 재시작
function restartCareerJourney() {
    console.log('🔄 진로 탐색 재시작 - 메인 페이지로 이동');
    
    // 메인 페이지로 이동
    window.location.href = '/';
}

// 로딩 표시 함수
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// 오류 표시 함수
function showError(message) {
    console.error('❌ 오류:', message);
    alert(`❌ ${message}`);
}

// 성공 메시지 표시 함수
function showSuccess(message) {
    console.log('✅ 성공:', message);
    alert(`✅ ${message}`);
}

console.log('🚀 중학생 진로탐색 JavaScript 로드 완료');