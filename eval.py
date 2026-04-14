import json
from llm_client import call_llm
from metric import score_reply
from db import get_connection, create_tables
from services.strategy_service import select_dbt_strategy

TEST_SCENARIOS = [
    {
        "scenario": "首次对话",
        "context": [],
        "message": "我最近总觉得很焦虑，不知道自己到底怎么了",
    },
    {
        "scenario": "日常情绪记录",
        "context": [],
        "message": "今天又很累，感觉做什么都提不起劲",
    },
    {
        "scenario": "周复盘",
        "context": [],
        "message": "这一周我总觉得状态反反复复，有点怀疑自己",
    },
    {
        "scenario": "长期跟进",
        "context": [],
        "message": "我这段时间一直不太敢表达需求，总怕别人不高兴",
    },
]


def save_eval_result(result: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO evaluation_results(
            scenario, emotional_support, cognitive_clarity,
            actionability, personalization, safety, overall
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            result["scenario"],
            result["scores"]["emotional_support"],
            result["scores"]["cognitive_clarity"],
            result["scores"]["actionability"],
            result["scores"]["personalization"],
            result["scores"]["safety"],
            result["scores"]["overall"],
        ),
    )
    conn.commit()
    conn.close()



def run_eval(save_to_db: bool = True):
    create_tables()
    results = []
    for item in TEST_SCENARIOS:
        strategy_tag, strategy_text = select_dbt_strategy(item["message"])
        reply = call_llm(
            user_id=0,
            message=item["message"],
            context=item["context"],
            strategy_text=strategy_text,
        )
        scores = score_reply(reply)
        result = {
            "scenario": item["scenario"],
            "message": item["message"],
            "strategy_tag": strategy_tag,
            "reply": reply,
            "scores": scores,
        }
        results.append(result)
        if save_to_db:
            save_eval_result(result)
    return results


if __name__ == "__main__":
    output = run_eval(save_to_db=True)
    print(json.dumps(output, ensure_ascii=False, indent=2))
