"""
초등학생 진로 탐색 시스템 자동화 테스트
4명의 가상 사용자로 전체 프로세스 테스트
"""

import asyncio
import aiohttp
import json
import random
from typing import Dict, List, Any
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8000"
TEST_USERS = [
    {
        "name": "김민수",
        "age": 10,
        "profile": "창의적이고 만들기를 좋아하는 학생"
    },
    {
        "name": "이수진",
        "age": 9,
        "profile": "활발하고 운동을 좋아하는 학생"
    },
    {
        "name": "박지훈",
        "age": 11,
        "profile": "조용하고 책 읽기를 좋아하는 학생"
    },
    {
        "name": "최하영",
        "age": 10,
        "profile": "사교적이고 도움을 주기 좋아하는 학생"
    }
]

# 각 단계별 선택 패턴 (3가지씩)
CHOICE_PATTERNS = {
    "step_1": [
        [1, 3],  # 만화 그리기 + 과학 실험
        [4, 9],  # 운동 + 영상 편집
        [7, 10], # 책 읽기 + 퍼즐
        [2, 5]   # 레고 + 동물 돌보기
    ],
    "step_2": [
        [2, 5],  # 손재주 + 창의성
        [4, 6],  # 팀워크 + 발표력
        [8, 9],  # 관찰력 + 공감
        [1, 10]  # 설명력 + 자기관리
    ],
    "step_3": [
        [2],  # 새로운 것 만들기
        [4],  # 몸 움직이며 활동
        [8],  # 새 지식 배우기
        [1]   # 누군가 도와주기
    ],
    "step_4": [
        [1],  # 기후변화 문제
        [8],  # 건강 문제
        [3],  # AI·로봇 문제
        [6]   # 멸종위기 동물
    ]
}

class CareerTestAutomation:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def create_session(self) -> aiohttp.ClientSession:
        """HTTP 세션 생성"""
        return aiohttp.ClientSession()
    
    async def start_career_exploration(self, session: aiohttp.ClientSession) -> str:
        """진로 탐색 세션 시작"""
        async with session.post(f"{BASE_URL}/career/start") as response:
            data = await response.json()
            if data["success"]:
                return data["data"]["session_id"]
            raise Exception("세션 시작 실패")
    
    async def submit_student_info(self, session: aiohttp.ClientSession, session_id: str, user: Dict) -> Dict:
        """학생 정보 제출"""
        payload = {
            "session_id": session_id,
            "student_info": {
                "name": user["name"],
                "age": user["age"]
            },
            "response": {
                "choice_numbers": [],
                "custom_answer": f"안녕하세요! 저는 {user['name']}이고 {user['age']}살이에요."
            }
        }
        
        async with session.post(f"{BASE_URL}/career/{session_id}/submit", json=payload) as response:
            return await response.json()
    
    async def submit_stage_response(self, session: aiohttp.ClientSession, session_id: str, 
                                  choices: List[int], custom_answer: str = "") -> Dict:
        """단계별 응답 제출"""
        payload = {
            "session_id": session_id,
            "response": {
                "choice_numbers": choices,
                "custom_answer": custom_answer
            }
        }
        
        async with session.post(f"{BASE_URL}/career/{session_id}/submit", json=payload) as response:
            return await response.json()
    
    async def get_ai_recommendation(self, session: aiohttp.ClientSession, session_id: str, 
                                  regenerate: bool = False) -> Dict:
        """AI 진로 추천 받기"""
        payload = {"regenerate": regenerate}
        
        print(f"\n🤖 OpenAI API 호출 중... (regenerate={regenerate})")
        print("=" * 60)
        
        async with session.post(f"{BASE_URL}/career/{session_id}/recommend", json=payload) as response:
            data = await response.json()
            
            print(f"🔍 API 응답 구조: {data}")
            
            if data.get("success", False):
                recommendation = data["data"]["career_recommendation"]
                print(f"📝 GPT 5단계 추천 결과:")
                print(f"   {recommendation}")
                print("=" * 60)
            else:
                print(f"❌ 추천 생성 실패: {data.get('message', '알 수 없는 오류')}")
            
            return data
    
    async def accept_recommendation(self, session: aiohttp.ClientSession, session_id: str) -> Dict:
        """진로 추천 수락"""
        async with session.post(f"{BASE_URL}/career/{session_id}/accept-recommendation") as response:
            return await response.json()
    
    async def generate_dream_logic(self, session: aiohttp.ClientSession, session_id: str) -> Dict:
        """드림로직 생성"""
        print(f"\n🌈 OpenAI API 드림로직 생성 호출 중...")
        print("=" * 60)
        
        async with session.post(f"{BASE_URL}/career/{session_id}/dream-logic") as response:
            data = await response.json()
            
            print(f"🔍 드림로직 API 응답 구조: {data}")
            
            if data.get("success", False):
                dream_logic = data["data"]["dream_logic"]
                print(f"📝 GPT 6단계 드림로직 결과:")
                print(dream_logic)
                print("=" * 60)
            else:
                print(f"❌ 드림로직 생성 실패: {data.get('message', '알 수 없는 오류')}")
            
            return data
    
    async def run_single_user_test(self, user: Dict, user_index: int) -> Dict:
        """단일 사용자 테스트 실행"""
        print(f"\n🚀 {user['name']} ({user['profile']}) 테스트 시작")
        print("=" * 80)
        
        session = await self.create_session()
        test_result = {
            "user": user,
            "session_id": None,
            "stages_completed": [],
            "recommendations": [],
            "dream_logic": None,
            "success": False,
            "error": None
        }
        
        try:
            # 1. 세션 시작
            session_id = await self.start_career_exploration(session)
            test_result["session_id"] = session_id
            print(f"✅ 세션 시작: {session_id}")
            
            # 2. 학생 정보 제출 (0단계)
            response = await self.submit_student_info(session, session_id, user)
            if response.get("success", False):
                print(f"✅ 0단계 완료: 학생 정보 제출")
                test_result["stages_completed"].append(0)
            else:
                print(f"🔍 0단계 응답: {response}")
                raise Exception(f"0단계 실패: {response.get('message', '알 수 없는 오류')}")
            
            # 3. 1-4단계 진행
            for stage in range(1, 5):
                stage_key = f"step_{stage}"
                choices = CHOICE_PATTERNS[stage_key][user_index % len(CHOICE_PATTERNS[stage_key])]
                
                # 가끔 기타 선택 테스트
                if random.random() < 0.2:  # 20% 확률
                    choices = [11]  # 기타 선택
                    custom_answer = f"{user['name']}의 특별한 답변 - {stage}단계"
                    response = await self.submit_stage_response(session, session_id, choices, custom_answer)
                    print(f"✅ {stage}단계 완료: 기타 선택 - '{custom_answer}'")
                else:
                    response = await self.submit_stage_response(session, session_id, choices)
                    print(f"✅ {stage}단계 완료: 선택지 {choices}")
                
                if response.get("success", False):
                    test_result["stages_completed"].append(stage)
                else:
                    print(f"🔍 {stage}단계 응답: {response}")
                    raise Exception(f"{stage}단계 실패: {response.get('message', '알 수 없는 오류')}")
            
            # 4. AI 진로 추천 (5단계) - 첫 번째 시도
            recommendation1 = await self.get_ai_recommendation(session, session_id, False)
            if recommendation1.get("success", False):
                test_result["recommendations"].append(recommendation1["data"]["career_recommendation"])
                print(f"✅ 5단계 첫 번째 추천 완료")
            else:
                print(f"❌ 5단계 첫 번째 추천 실패: {recommendation1}")
            
            # 5. AI 진로 추천 재시도 (다른 추천)
            await asyncio.sleep(1)  # API 호출 간격
            recommendation2 = await self.get_ai_recommendation(session, session_id, True)
            if recommendation2.get("success", False):
                test_result["recommendations"].append(recommendation2["data"]["career_recommendation"])
                print(f"✅ 5단계 두 번째 추천 완료")
            else:
                print(f"❌ 5단계 두 번째 추천 실패: {recommendation2}")
            
            # 6. 진로 추천 수락
            accept_response = await self.accept_recommendation(session, session_id)
            if accept_response.get("success", False):
                print(f"✅ 진로 추천 수락 완료")
            else:
                print(f"❌ 진로 추천 수락 실패: {accept_response}")
            
            # 7. 드림로직 생성 (6단계)
            await asyncio.sleep(1)  # API 호출 간격
            dream_response = await self.generate_dream_logic(session, session_id)
            if dream_response.get("success", False):
                test_result["dream_logic"] = dream_response["data"]["dream_logic"]
                test_result["stages_completed"].append(6)
                print(f"✅ 6단계 드림로직 생성 완료")
            else:
                print(f"❌ 6단계 드림로직 생성 실패: {dream_response}")
            
            test_result["success"] = True
            print(f"🎉 {user['name']} 테스트 완료!")
            
        except Exception as e:
            test_result["error"] = str(e)
            print(f"❌ {user['name']} 테스트 실패: {e}")
        
        finally:
            await session.close()
        
        return test_result
    
    async def run_all_tests(self):
        """모든 사용자 테스트 실행"""
        print("🎯 초등학생 진로 탐색 시스템 자동화 테스트 시작")
        print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        tasks = []
        for i, user in enumerate(TEST_USERS):
            task = self.run_single_user_test(user, i)
            tasks.append(task)
        
        # 모든 테스트 동시 실행
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 요약
        await self.print_summary()
    
    async def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📊 테스트 결과 요약")
        print("=" * 80)
        
        success_count = 0
        total_recommendations = 0
        total_dream_logic = 0
        
        for i, result in enumerate(self.results):
            if isinstance(result, Exception):
                print(f"❌ 사용자 {i+1}: 예외 발생 - {result}")
                continue
            
            # result가 정상적인 딕셔너리인 경우만 처리
            if not isinstance(result, dict):
                print(f"❌ 사용자 {i+1}: 잘못된 결과 형식")
                continue
                
            user_name = result["user"]["name"]
            stages = len(result["stages_completed"])
            recommendations = len(result["recommendations"])
            has_dream_logic = bool(result["dream_logic"])
            
            status = "✅ 성공" if result["success"] else f"❌ 실패: {result['error']}"
            print(f"👤 {user_name}: {status}")
            print(f"   📈 완료 단계: {stages}/6 (단계: {result['stages_completed']})")
            print(f"   🤖 AI 추천: {recommendations}개")
            print(f"   🌈 드림로직: {'생성됨' if has_dream_logic else '생성 안됨'}")
            
            if result["success"]:
                success_count += 1
            total_recommendations += recommendations
            if has_dream_logic:
                total_dream_logic += 1
            
            print()
        
        print("=" * 80)
        print(f"📈 전체 통계:")
        print(f"   👥 총 사용자: {len(TEST_USERS)}명")
        print(f"   ✅ 성공: {success_count}명 ({success_count/len(TEST_USERS)*100:.1f}%)")
        print(f"   🤖 총 AI 추천: {total_recommendations}개")
        print(f"   🌈 드림로직 생성: {total_dream_logic}개")
        print(f"   📅 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

async def main():
    """메인 실행 함수"""
    automation = CareerTestAutomation()
    await automation.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())