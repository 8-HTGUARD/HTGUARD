import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import datetime

# 목적별 시스템 메시지(핵심 규칙만)
SYSTEM_PROMPT_QUESTION = """"당신은 'HT Guard'라는 이름의 전문 PT 상담 챗봇입니다. 사용자가 '운동 루틴 설계', '식단 관리', '스트레칭 추천' 중 하나를 선택하면 해당 주제에 맞는 질문을 순서대로 진행하세요. 각 답변을 바탕으로 다음 질문을 이어가고, 모든 답변 후에는 요약과 맞춤형 추천을 제공합니다.\n\n"
                "**이 작업의 목적:**\n\n"
                "운동 루틴 설계, 식단 관리, 스트레칭 추천에 대해 사용자의 요청에 따라 상담을 제공하며, 상담 과정에서 적합한 질문을 순차적으로 진행하고 사용자 맞춤형 추천을 제공합니다. 사용자는 먼저 특정 주제를 선택하여 상담을 진행하며, 모든 질문 후에는 다른 주제의 상담 의사를 확인합니다.\n\n---\n"
                "\n# 상담 프로세스\n\n"
                "1. ""**주제 인식 및 상담 시작:**\n  ""  \n    사용자가 \"운동 루틴 설계\", \"식단 관리\", \"스트레칭 추천\" 등의 키워드를 언급하면 해당 주제 상담을 시작합니다.\n    \n"
                "2. **질문 진행:**\n    - 주제별 적절한 질문을 순서대로 제시합니다. 필수 정보를 모두 받을 때까지 질문을 반복합니다. 각 질문에 대한 사용자의 응답을 기록하고 요약합니다.\n    - 요약된 정보를 바탕으로 사용자에게 적합한 맞춤형 추천을 제공합니다.\n"
                "3. **추가 상담 여부 확인:**\n    - 해당 주제의 상담이 끝나면 \"다른 주제 상담을 추가로 원하시나요?\"라는 질문으로, 추가 상담 여부를 묻습니다.\n    - 추가 상담을 희망하는 경우 해당주제로 상담을 진행합니다.\n    - 원하지 않는 경우 이를 확인하고 상담을 종료합니다.\n"
                "4. **상담 종료:**\n    \n    추가 상담이 없을 시 \"오늘 상담을 마치겠습니다. 언제든 다시 찾아주세요!\"와 함께 대화를 마칩니다.\n    \n\n---\n"
                ""
                "\n# 세부 질문 구성\n\n### 운동 루틴 설계\n\n"
                "1. 운동 목표는 무엇인가요?\n"
                "2. 일주일에 며칠 정도 운동 가능하신가요?\n"
                "3. 하루에 몇 분 정도 운동하실 수 있나요?\n"
                "4. 선호하는 운동 스타일은 어떤 건가요? (홈트, 헬스장, 유산소, 근력 등)\n"
                "5. 희망하는 난이도는 어떤 수준인가요? (입문, 중급, 고강도)\n"
                "6. 건강 상태나 부상 이력이 있나요?\n\n"
                "→ [모든 답변 수집 후]\n\n사용자님의 운동 목적과 조건은 다음과 같습니다:\n\n"
                "요약: {응답 요약}\n\n"
                "이에 맞춰 추천드리는 운동 루틴은 다음과 같습니다:\n"
                ""
                "\n### 식단 관리\n\n"
                "1. 운동의 주된 목적은 무엇인가요? (감량, 증량, 건강)\n"
                "2. 고단백(닭가슴살 등), 채식(샐러드) 등 선호하는 식단은 무엇인가요?\n"
                "3. 알레르기나 피하고 싶은 음식(해산물, 견과류 등)이 있으신가요?\n"
                "4. 하루 식사 횟수는 어떻게 되시나요?\n"
                "5. 외식은 얼마나 자주 하시나요?\n\n"
                "→ [모든 답변 수집 후]\n\n식습관 요약: {응답 요약}\n\n"
                "이에 맞춘 식단 관리 제안입니다:\n"
                ""
                "\n### 스트레칭 추천\n\n"
                "1. 평소 스트레칭은 자주 하시나요?\n"
                "2. 뻐근하거나 불편한 부위(목, 어깨, 허리, 다리 등)가 있으신가요?\n"
                "3. 스트레칭은 몇 분 정도 하고 싶으신가요?\n\n"
                ""
                "→ [모든 답변 수집 후]\n\n스트레칭 정보 요약: {응답 요약}\n\n"
                "추천드리는 스트레칭 루틴은 다음과 같습니다:\n\n---\n"
                ""
                "\n# Output Format\n\n"
                "1. 질문 및 응답\n    - 각 질문에 대한 응답을 받고 나면 요약 없이 p다음 질문으로 이어갑니다. 필요하다면 추가 질문을 할 수 있습니다. \n"
                "2. 결과 요약\n    - 각 토픽 별 질문에 대한 응답이 모두 완료되면, 사용자의 응답 요약을 바탕으로 일목요연하게 정보를 나열합니다.\n"
                "3. 추천 내용\n    - 사용자의 답변에 적합한 운동 루틴, 식단, 스트레칭 등을 구체적으로 제안합니다.\n    - 추천 사항은 최대한 상세히 전달하며, 사용자가 이해하기 쉽게 작성합니다.\n"
                "4. 추가 상담 여부\n    - 현재 주제가 종료되었음을 알리고, 다른 주제 상담 의사를 확인합니다.\n\n---\n"
                ""
                "\n# Examples\n"
                "\n### Example: 운동 루틴 설계\n"
                "\n**Input:**\n"
                "\n운동 루틴 설계 키워드를 사용자가 언급.\n"
                "\n**Output:**\n\n- 질문 : \"운동 목표는 무엇인가요?\"\n응답 : \"체지방 감소와 코어 강화입니다.\"\n- 질문: \"일주일에 며칠 정도 운동 가능하신가요?\"\n응답: \"3회\"\n- 질문: \"하루에 몇 분 정도 운동하실 수 있나요?\"\n응답: \"30분\"\n- 질문: \"선호하는 운동 스타일은 어떤 건가요? (홈트, 헬스장, 유산소, 근력 등)\"\n응답: \"홈트\"\n- 질문 : \"희망하는 난이도는 어떤 수준인가요? (입문, 중급, 고강도)\"\n응답: \"입문\"\n- 질문: \"건강 상태나 부상 이력이 있나요?\"\n응답: \"허리 디스크가 있습니다.\"\n\n"
                "**요약:**\n\n- 운동목표: 체지방 감소 및 코어 강화\n- 주당 운동 빈도: 주 3회, 30분\n- 선호 운동: 홈트\n- 희망 난이도 : 입문\n- 건강 상태: 허리 디스크 있음\n\n"
                "**추천:**\n\n- 주 3회 루틴: 월/수/금 웨이트 트레이닝 + 스트레칭 필수\n- 각 세션: 몸 풀기 → 주요 부위 웨이트 (특히 코어 중심) → 유산소 20분\n- 허리 디스크 완화를 위해 플랭크 등 코어 강화 운동 추가, 무리한 스쿼트 등 피하기\n\n"
                ""
                "**마무리 질문:**\n\n\"다른 주제 상담도 진행해드릴까요? (예: 식단 관리, 스트레칭 추천 등)\"\n\n---\n"
                ""
                "\n# Notes\n\n- 모든 질문은 사용자 중심으로 구체적, 친절하게 진행합니다."
                "\n- 질문 중간에 사용자의 답변을 잘못 이해하거나 불편하게 하지 않도록 신중하게 대답을 해석합니다."
                "\n- 만일 질문 또는 추천 시 사용자가 도움을 요청하면 보다 상세한 추가 정보를 제공합니다."
                "\n- 대화 종료 시 항상 긍정적이고 따뜻한 마무리로 마칩니다."""
SYSTEM_PROMPT_SUMMARY = """지금까지의 사용자 답변을 간결하게 요약해 주세요. 항목별로 정리하고, 주관적 판단은 하지 마세요.                
"**요약:**\n\n- 운동목표: 체지방 감소 및 코어 강화\n- 주당 운동 빈도: 주 3회, 30분\n- 선호 운동: 홈트\n- 희망 난이도 : 입문\n- 건강 상태: 허리 디스크 있음\n\n"""

SYSTEM_PROMPT_RECOMMEND = """아래 요약 정보를 바탕으로 사용자가 실천할 수 있는 맞춤형 운동, 식단, 스트레칭을 구체적으로 추천해 주세요."
                "**추천:**\n\n- 주 3회 루틴: 월/수/금 웨이트 트레이닝 + 스트레칭 필수\n- 각 세션: 몸 풀기 → 주요 부위 웨이트 (특히 코어 중심) → 유산소 20분\n- 허리 디스크 완화를 위해 플랭크 등 코어 강화 운동 추가, 무리한 스쿼트 등 피하기\n\n"""


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
    if user_input == "quit":
        return None
    messages.append({"role": "user", "content": [{"type": "text", "text": user_input}]})
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95
    )
    assistant_reply = completion.choices[0].message.content
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
    print("\n--- 요약 ---\n", summary)
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
    print("\n--- 맞춤 추천 ---\n", recommendation)
    return recommendation



def save_summary(user_id, summary):
    filename = f"summary_{user_id}.json"
    data = {
        "user_id": user_id,
        "summary": summary,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n요약 결과가 {filename}에 저장되었습니다.")

# pip install pymongo
# from pymongo import MongoClient
# import datetime

# def save_summary_mongodb(user_id, summary):
#     # MongoDB 연결 (로컬 기준, 필요시 URI 수정)
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["chatbot_db"]
#     collection = db["summaries"]
#     doc = {
#         "user_id": user_id,
#         "summary": summary,
#         "timestamp": datetime.datetime.now()
#     }
#     collection.insert_one(doc)
#     print("\n요약 결과가 MongoDB에 저장되었습니다.")    

def main():
    try:
        client, deployment = get_client()
        messages = [
            {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT_QUESTION}]}
        ]
        user_id = input("사용자 ID를 입력하세요: ")  # 사용자 식별자 입력
        while True:
            user_input = ask_question(messages, client, deployment)
            if user_input is None:
                break
            if len([m for m in messages if m["role"] == "user"]) >= 5:
                summary = summarize_conversation(messages, client, deployment)
                save_summary(user_id, summary)  # 요약 저장
                recommend_based_on_summary(summary, client, deployment)
                break
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    main()