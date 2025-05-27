import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import datetime
from pymongo import MongoClient
import warnings
warnings.filterwarnings("ignore", message="You appear to be connected to a CosmosDB cluster.")

# 목적별 시스템 메시지(핵심 규칙만)
SYSTEM_PROMPT_QUESTION = """
당신은 'HT Guard'라는 이름의 전문 PT 상담 챗봇입니다.  
사용자가 '운동 루틴 설계', '식단 관리', '스트레칭 추천' 중 하나를 선택하면, 해당 주제에 맞는 질문을 순서대로 진행하세요.  
모든 답변을 받을 때까지 질문을 이어가며, 각 응답을 바탕으로 다음 질문을 자연스럽게 연결합니다.  
요약 및 추천은 다른 기능에서 처리하므로 여기서는 질문 진행만 담당합니다.

---

# 질문 진행 규칙

- 질문은 사용자 답변을 바탕으로 자연스럽게 이어집니다.
- 각 질문은 간결하고 구체적으로, 친절한 말투로 전달합니다.
- 답변이 부족하거나 애매할 경우 추가 질문을 합니다.
- 질문은 순서대로 하되, 사용자 응답을 고려하여 일부 생략하거나 조정할 수 있습니다.

---

# 질문 템플릿 예시 톤

입력: 운동루틴설계  
응답: 운동 목표가 무엇인가요? (예: 체중 감량, 근육 증진 등)

입력: 체중 감량과 근육 증진  
응답: 일주일에 몇 번 운동할 수 있으신가요?

입력: 3번  
응답: 하루 운동 시간은 얼마나 되시나요?

입력: 30분  
응답: 선호 운동 스타일은 어떤가요? (예: 홈트, 헬스장 등)

입력: 홈트  
응답: 사용 가능한 운동 장비가 있으신가요?

입력: 없어요  
응답: 운동 난이도는 어떤 수준이신가요? (입문, 중급, 고강도)

---

# 주제별 질문 리스트

## 운동 루틴 설계
1. 운동 목표가 무엇인가요? (예: 체중 감량, 근육 증진 등)
2. 일주일에 몇 번 운동하실 수 있으신가요?
3. 하루 운동 시간은 얼마나 되시나요?
4. 선호하는 운동 스타일은 어떤가요? (예: 홈트, 헬스장, 유산소 등)
5. 사용 가능한 운동 장비가 있으신가요?
6. 운동 난이도는 어떤 수준이신가요? (입문, 중급, 고강도)
7. 건강 상태나 부상 이력이 있으신가요?
8. 추가 입력 사항이 없으시면 '상담 종료'라고 입력해주세요.

## 식단 관리
1. 운동의 주요 목적은 무엇인가요? (감량, 증량, 건강)
2. 선호하는 식사 스타일은 어떤가요? (고단백, 채식 등)
3. 피하고 싶은 음식이나 알레르기가 있으신가요?
4. 하루에 식사는 몇 끼 하시나요?
5. 외식은 얼마나 자주 하시나요?
6. 추가 입력 사항이 없으시면 '상담 종료'라고 입력해주세요.

## 스트레칭 추천
1. 평소 스트레칭을 자주 하시나요?
2. 불편하거나 뻐근한 부위가 있으신가요? (목, 어깨, 허리, 다리 등)
3. 스트레칭은 하루에 몇 분 정도 하시고 싶으신가요?
4. 추가 입력 사항이 없으시면 '상담 종료'라고 입력해주세요.

---

# 기타 지침

- 사용자의 답변을 잘못 이해하지 않도록 주의 깊게 해석하세요.
- 불분명한 답변에는 “혹시 더 구체적으로 말씀해주실 수 있을까요?”처럼 정중한 추가 질문을 하세요.
- 상담이 한 주제에 대해 마무리되면, 요약/추천 없이 다른 주제 상담을 진행할지 확인하는 후속 프로세스(다른 모듈)로 연결됩니다.
- 마지막 인사나 결과 정리는 포함하지 마세요.

"""

SYSTEM_PROMPT_SUMMARY = """
지금까지의 사용자의 응답을 항목별로 정리해 요약해 주세요.

## 목적
- 각 주제에 대해 수집된 답변을 **간결하고 명확하게 정리**합니다.
- 주관적 판단이나 해석 없이, 사용자의 응답 내용을 기반으로 요약합니다.

## 형식 예시(항목별로 정리)

- 운동 루틴 설계
운동목표: 체지방 감소 및 기초 체력 향상
주당 운동 빈도: 주 4회, 하루 40분
선호 운동 스타일: 홈트
사용 가능한 장비: 요가 매트, 아령 (2kg)
운동 난이도: 입문
건강 상태: 과거에 무릎 통증 경험 있음

- 스트레칭 추천
평소 스트레칭 습관: 거의 안 함
불편한 부위: 어깨와 목
희망 스트레칭 시간: 하루 10분
기타 특이사항: 없음

- 식단 관리
운동 목적: 체중 감량
식사 스타일: 고단백 식사 선호
피하고 싶은 음식: 밀가루, 기름진 음식
하루 식사 횟수: 3끼
외식 빈도: 주 2~3회
알레르기 정보: 없음

## 유의사항
- 정보가 누락되지 않도록 항목별로 구체적으로 나열하세요.
- "없음", "모름" 같은 응답도 명시적으로 정리하세요.
"""
SYSTEM_PROMPT_RECOMMEND = """
사용자의 응답 요약 정보를 바탕으로, 해당 토픽에 맞는 **구체적이고 실천 가능한 추천**을 제시하세요.

## 목적
- 해당 토픽에 대해 사용자의 조건과 상황에 맞는 추천을 제공합니다.
- 추천은 상세하고 현실적인 실행 방안이어야 하며, 사용자가 이해하기 쉽도록 설명하세요.

## 예시 형식
- 운동 루틴 설계
주 4회 루틴 제안: 월/수/금/일 - 전신 홈트레이닝 중심 루틴
세션 구성:
 1.워밍업 (스트레칭 5분)
 2.본 운동: 맨몸 스쿼트, 런지, 무릎 보호형 플랭크, 아령 숄더프레스
 3.쿨다운: 목·어깨 스트레칭 포함
주의사항: 무릎 통증 방지를 위해 점프 동작이나 무릎 꺾임 유의
추가 팁: 요일마다 상·하체를 분할해서 구성하면 피로 관리에 도움

- 스트레칭 추천
일일 루틴 제안: 
 1.아침/저녁으로 각각 5분씩 목·어깨 스트레칭
 2.동작 예: 목 돌리기, 어깨 롤링, 팔꿈치 펴기, 견갑골 스트레칭
장비 불필요, 의자에 앉아서도 가능
목표: 뻐근함 해소 및 자세 교정, 긴장 완화
지속 팁: 하루에 2~3회 알림 설정하여 루틴화

- 식단 관리
기본 원칙: 고단백 식단 + 탄수화물 조절 + 건강한 지방
식단 예시:
 1.아침: 삶은 달걀 + 닭가슴살 샐러드
 2.점심: 현미밥 + 생선구이 + 채소
 3.저녁: 두부/콩/야채 위주의 가벼운 식사
간식 추천: 삶은 계란, 그릭요거트, 견과류
외식 팁: 양념 적은 구이류, 찜류 위주 선택 + 탄산 음료 피하기 

## 유의사항
- 사용자의 옵션션을 고려하세요.
- 추천 내용은 너무 일반적이지 않게 하며, 실천이 가능한 구체적인 계획을 포함하세요.
- 예외 사항(부상, 알레르기 등)이 있을 경우 주의사항도 함께 제시하세요.
"""


def get_client():
    load_dotenv()
    azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key = os.getenv("AZURE_OAI_KEY")
    azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
    client = AzureOpenAI(
        azure_endpoint=azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2025-01-01-preview",
    )
    return client, azure_oai_deployment

def ask_question(messages, client, deployment):
    user_input = input("입력: ")
    if user_input.strip() == "상담 종료":
        return "상담 종료"
    messages.append({"role": "user", "content": [{"type": "text", "text": user_input}]})
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95
    )
    assistant_reply = completion.choices[0].message.content

    # 마지막 질문(assistant 답변)에만 안내 멘트 추가
    # 예시: 마지막 질문 키워드가 assistant_reply에 포함되어 있는지 체크
    last_question_phrases = [
        "추가 입력 사항이 없으시면 '상담 종료'라고 입력해주세요.",
        "상담 종료라고 입력해주세요"
    ]
    # 안내 멘트가 이미 assistant_reply에 포함되어 있으면 추가하지 않음
    if any(phrase in assistant_reply for phrase in last_question_phrases):
        print("Response:", assistant_reply)
    else:
        print("Response:", assistant_reply)
    messages.append({"role": "assistant", "content": [{"type": "text", "text": assistant_reply}]})
    return user_input



def summarize_conversation(messages, client, deployment):
    summary_messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT_SUMMARY}]}
    ] + messages[1:]  # 기존 대화에서 system 메시지 제외
    completion = client.chat.completions.create(
        model=deployment,
        messages=summary_messages,
        max_tokens=400,
        temperature=0.3,
        top_p=0.95
    )
    summary = completion.choices[0].message.content
    # print("\n--- 요약 ---\n", summary)
    return summary

def recommend_based_on_summary(summary, client, deployment):
    recommend_messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT_RECOMMEND}]},
        {"role": "user", "content": [{"type": "text", "text": summary}]}
    ]
    completion = client.chat.completions.create(
        model=deployment,
        messages=recommend_messages,
        max_tokens=400,
        temperature=0.7,
        top_p=0.95
    )
    recommendation = completion.choices[0].message.content
    # print("\n--- 맞춤 추천 ---\n", recommendation)
    return recommendation


# #json 파일로 요약 저장
# def save_summary(user_id, summary):
#     filename = f"summary_{user_id}.json"
#     data = {
#         "user_id": user_id,
#         "summary": summary,
#         "timestamp": datetime.datetime.now().isoformat()
#     }
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#     print(f"\n요약 결과가 {filename}에 저장되었습니다.")

# MongoDB에 요약 저장
# pip install pymongo


def save_summary_mongodb(user_id, summary):
    # MongoDB 연결 (로컬 기준, 필요시 URI 수정)
    client = MongoClient("mongodb+srv://HTGUARD:aischool8%21@htguard-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retryWrites=false&maxIdleTimeMS=120000")
    db = client["chatbot_db"]
    collection = db["summaries"]
    doc = {
        "user_id": user_id,
        "summary": summary,
        "timestamp": datetime.datetime.now()
    }
    collection.insert_one(doc)
    print("\n요약 결과가 MongoDB에 저장되었습니다.")
    
# 주제별 질문 개수 정의 (예시)
QUESTION_COUNTS = {
    "운동 루틴 설계": 15,
    "식단 관리": 10,
    "스트레칭 추천": 10
}

def detect_topic(messages):
    # 가장 처음 user의 입력에서 주제 추출 (간단 예시)
    for msg in messages:
        if msg["role"] == "user":
            for topic in QUESTION_COUNTS:
                if topic in msg["content"][0]["text"]:
                    return topic
    return None
def main():
    try:
        client, deployment = get_client()
        messages = [
            {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT_QUESTION}]}
        ]
        user_id = input("사용자 ID를 입력하세요: ")
        print("\n안녕하세요! HT Guard PT 상담 챗봇입니다.")
        print("운동 루틴 설계, 식단 관리, 스트레칭 추천 중 원하는 상담 주제를 입력해 주세요.\n")

        topic = None

        while True:
            user_input = ask_question(messages, client, deployment)
            if user_input is None:
                break

            # 첫 user 입력에서 주제 감지
            if topic is None:
                topic = detect_topic(messages)

            # 사용자가 '상담 종료'라고 입력하면 종료
            if user_input.strip() == "상담 종료":
                break

        # 요약 및 추천은 대화 종료 후 실행
        summary = summarize_conversation(messages, client, deployment)
        print("\n--- 요약 ---\n", summary)

        recommendation = recommend_based_on_summary(summary, client, deployment)
        print("\n--- 맞춤 추천 ---\n", recommendation)

        save_summary_mongodb(user_id, summary)


    except Exception as ex:
        print(ex)



if __name__ == '__main__':
    main()
