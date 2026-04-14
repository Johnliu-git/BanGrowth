import sqlite3

DB_NAME = "db.sqlite"


def get_connection():
    return sqlite3.connect(DB_NAME)


def _ensure_column(cursor, table_name: str, column_name: str, column_type: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")



def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            profile_json TEXT
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS growth_contracts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            contract_type TEXT,
            goals TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS diary(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT,
            emotion_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS chat_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            reply TEXT,
            strategy_tag TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS dbt_templates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT UNIQUE,
            scene_tag TEXT,
            template_text TEXT
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS growth_reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            report_text TEXT,
            report_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS evaluation_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario TEXT,
            emotional_support REAL,
            cognitive_clarity REAL,
            actionability REAL,
            personalization REAL,
            safety REAL,
            overall REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    # 兼容旧数据库
    _ensure_column(cursor, "chat_history", "strategy_tag", "TEXT")
    _ensure_column(cursor, "growth_contracts", "start_date", "TEXT")
    _ensure_column(cursor, "growth_contracts", "end_date", "TEXT")
    _ensure_column(cursor, "growth_contracts", "status", "TEXT")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("数据库初始化完成")
