# llm_client.py
# -*- coding: utf-8 -*-
import os
import streamlit as st
from openai import OpenAI
from services.user_service import get_growth_contract

API_URL = "https://api.deepseek.com"


def _get_client():
    api_key = os.environ.get("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("未配置 DEEPSEEK_API_KEY")
    return OpenAI(
        api_key=api_key.strip(),
        base_url=API_URL,
    )


def call_llm(user_id: int, message: str, context: list, strategy_text: str = ""):
    contract = get_growth_contract(user_id)
    contract_text = "未签署成长契约"
    if contract:
        contract_text = f"{contract['contract_type']} / {contract['goals']}"

    context_lines = []
    for item in context[-6:]:
        if isinstance(item, tuple) and len(item) >= 2:
            msg, reply = item[0], item[1]
            if msg:
                context_lines.append(f"用户：{msg}")
            if reply:
                context_lines.append(f"AI：{reply}")

    context_text = "\n".join(context_lines) if context_lines else "暂无历史对话"

    prompt = (
        f"成长契约：{contract_text}\n"
        f"最近对话：\n{context_text}\n\n"
        f"用户当前输入：{message}\n\n"
        f"可参考的支持策略：\n{strategy_text}\n\n"
        "请回复时遵守以下要求：\n"
        "1. 风格温和、真诚、稳定，像陪伴式聊天，不要说教。\n"
        "2. 控制在 2 到 4 段，总长度适中，不要过长。\n"
        "3. 如果给建议，最多给 3 条，而且要具体、可马上做到。\n"
        "4. 优先短句、短段落，避免大段堆砌。\n"
        "5. 结尾必须完整自然，不要输出半句。\n"
        "6. 不做医学诊断，不替代治疗。\n"
    )

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一名温和、稳定、具备成长陪伴风格的AI成长官。"
                        "回复要自然、简洁、具体，有陪伴感，避免冗长说教。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            stream=False,
            max_tokens=700,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        return content.strip() if content else "我还在整理这段回应，你可以再和我说一句。"

    except Exception as e:
        return f"调用大模型失败: {str(e)}"

