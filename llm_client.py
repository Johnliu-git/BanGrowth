# llm_client.py
# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from services.user_service import get_growth_contract

API_URL = "https://api.deepseek.com"

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url=API_URL,
)


def call_llm(user_id: int, message: str, context: list, strategy_text: str = ""):
    contract = get_growth_contract(user_id)
    contract_text = "未签署成长契约"
    if contract:
        contract_text = f"{contract['contract_type']} / {contract['goals']}"

    context_lines = []
    for item in context:
        if isinstance(item, tuple) and len(item) >= 2:
            msg, reply = item[0], item[1]
            if msg:
                context_lines.append(f"用户：{msg}")
            if reply:
                context_lines.append(f"AI：{reply}")
    context_text = "\n".join(context_lines)

    prompt = (
        f"用户ID: {user_id}\n"
        f"成长契约: {contract_text}\n"
        f"最近对话上下文:\n{context_text}\n"
        f"当前输入: {message}\n"
        f"DBT策略模板:\n{strategy_text}\n"
        "请生成温暖、稳定、鼓励用户行动、符合非临床边界的回复。"
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名温和、稳定、具备成长陪伴风格的AI成长官，不做诊断，不替代治疗。",
                },
                {"role": "user", "content": prompt},
            ],
            stream=False,
            max_tokens=256,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用大模型失败: {str(e)}"

