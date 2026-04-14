# services/user_service.py
from db import get_connection


def register_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True



def authenticate(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None



def set_growth_contract(
    user_id: int,
    contract_type: str,
    goals: str,
    start_date: str = "",
    end_date: str = "",
    status: str = "active",
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM growth_contracts WHERE user_id=?", (user_id,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False

    cursor.execute(
        '''
        INSERT INTO growth_contracts(user_id, contract_type, goals, start_date, end_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (user_id, contract_type, goals, start_date, end_date, status),
    )
    conn.commit()
    conn.close()
    return True



def get_growth_contract(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT contract_type, goals, start_date, end_date, status FROM growth_contracts WHERE user_id=?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "contract_type": row[0],
            "goals": row[1],
            "start_date": row[2],
            "end_date": row[3],
            "status": row[4],
        }
    return None


