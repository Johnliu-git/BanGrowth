from db import get_connection
import json


def save_diary(user_id, content, emotion_data=None):
    conn = get_connection()
    cursor = conn.cursor()
    emotion_json = json.dumps(emotion_data or {}, ensure_ascii=False)
    cursor.execute(
        "INSERT INTO diary(user_id, content, emotion_json) VALUES (?, ?, ?)",
        (user_id, content, emotion_json),
    )
    conn.commit()
    conn.close()



def get_recent_diaries(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT content, emotion_json, created_at FROM diary WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()

    diaries = []
    for content, emotion_json, created_at in rows:
        try:
            emotion_data = json.loads(emotion_json) if emotion_json else {}
        except Exception:
            emotion_data = {}

        diaries.append(
            {
                "content": content,
                "emotion": emotion_data,
                "created_at": created_at,
            }
        )
    return diaries

