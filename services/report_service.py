# services/report_service.py
from db import get_connection
from services.diary_service import get_recent_diaries
from services.emotion_service import analyze_emotion


def save_growth_report(user_id: int, report_text: str, report_type: str = "weekly"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO growth_reports(user_id, report_text, report_type) VALUES (?, ?, ?)",
        (user_id, report_text, report_type),
    )
    conn.commit()
    conn.close()



def generate_growth_report(user_id: int) -> str:
    diaries = get_recent_diaries(user_id, limit=20)
    if not diaries:
        return "暂无日记数据，无法生成成长报告"

    sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    dominant_emotions = {}
    summaries = []

    for diary in diaries:
        content = diary.get("content", "")
        emotion_json = diary.get("emotion", {})

        if not emotion_json:
            analysis = analyze_emotion(content)
        else:
            analysis = emotion_json

        sentiment = analysis.get("sentiment", "NEUTRAL")
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        dominant = analysis.get("dominant", "中性")
        dominant_emotions[dominant] = dominant_emotions.get(dominant, 0) + 1
        summaries.append(analysis.get("summary", ""))

    report = f"用户最近 {len(diaries)} 篇日记的成长报告：\n\n"
    report += "情绪分布:\n"
    for k, v in sentiment_counts.items():
        report += f"- {k}: {v}\n"

    report += "\n主要情绪:\n"
    sorted_dominant = sorted(dominant_emotions.items(), key=lambda x: x[1], reverse=True)
    for emotion, count in sorted_dominant:
        report += f"- {emotion}: {count}\n"

    report += "\n日记摘要:\n"
    for i, s in enumerate(summaries, start=1):
        report += f"{i}. {s}\n"

    save_growth_report(user_id, report, report_type="weekly")
    return report

