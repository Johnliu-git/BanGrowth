DBT_TEMPLATES = {
    "validation_feedback": """
请先承接用户当前情绪，使用验证式反馈。
避免立刻讲道理，先表达理解，再帮助用户梳理感受。
""",
    "dear_man": """
请使用 DEAR MAN 结构帮助用户处理边界表达问题：
D 描述事实
E 表达感受
A 提出请求
R 强化结果
""",
    "mindfulness_grounding": """
请使用简短正念引导帮助用户回到当下，
例如呼吸、身体感受、注意力锚定等。
""",
}


def select_dbt_strategy(text: str):
    text = text or ""

    if any(k in text for k in ["焦虑", "崩溃", "委屈", "难受", "烦死了", "很累"]):
        return "validation_feedback", DBT_TEMPLATES["validation_feedback"]

    if any(k in text for k in ["拒绝", "开口", "边界", "室友", "朋友", "同事", "表达"]):
        return "dear_man", DBT_TEMPLATES["dear_man"]

    if any(k in text for k in ["睡不着", "停不下来", "一直想", "控制不住", "脑子很乱"]):
        return "mindfulness_grounding", DBT_TEMPLATES["mindfulness_grounding"]

    return "general_support", ""