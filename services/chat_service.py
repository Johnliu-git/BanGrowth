from db import get_connection


def save_chat(user_id, message, reply, strategy_tag=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO chat_history(user_id, message, reply, strategy_tag)
        VALUES (?, ?, ?, ?)
        ''',
        (user_id, message, reply, strategy_tag),
    )
    conn.commit()
    conn.close()



def get_recent_chats(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT message, reply, created_at
        FROM chat_history
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
