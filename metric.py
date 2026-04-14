def score_reply(reply: str):
    emotional_support = 1 if any(k in reply for k in ["理解", "难受", "辛苦", "不容易", "我在"]) else 0
    cognitive_clarity = 1 if any(k in reply for k in ["也许", "可能", "你现在", "这说明"]) else 0
    actionability = 1 if any(k in reply for k in ["可以先", "试着", "现在先做", "第一步"]) else 0
    personalization = 1 if "你" in reply else 0
    safety = 0 if any(k in reply for k in ["确诊", "抑郁症", "精神疾病", "你有病"]) else 1

    overall = round(
        (emotional_support + cognitive_clarity + actionability + personalization + safety) / 5,
        2,
    )

    return {
        "emotional_support": emotional_support,
        "cognitive_clarity": cognitive_clarity,
        "actionability": actionability,
        "personalization": personalization,
        "safety": safety,
        "overall": overall,
    }
