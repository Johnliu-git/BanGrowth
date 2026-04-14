# services/emotion_service.py
import os
import json
import requests
from typing import Dict, List

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

_analyzer_instance = None


class EmotionAnalyzer:
    """使用 DeepSeek 对话接口做情绪分析"""

    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("请先设置 DEEPSEEK_API_KEY 环境变量")
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL

    def analyze_emotion(self, text: str) -> Dict:
        if not text or not text.strip():
            return {
                "scores": {"中性": 1.0},
                "dominant": "中性",
                "sentiment": "NEUTRAL",
                "intensity": 0.5,
                "topics": [],
                "summary": "无文本输入",
                "raw_sentiment": {"label": "NEUTRAL", "score": 0.5},
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        prompt = f"""
请你作为中文情绪分析助手，分析下面这段文字的情绪，并且只返回 JSON，不要返回任何解释。

文本：
{text}

返回格式必须严格如下：
{{
  "scores": {{
    "快乐": 0.0,
    "平静": 0.0,
    "悲伤": 0.0,
    "焦虑": 0.0,
    "愤怒": 0.0
  }},
  "dominant": "悲伤",
  "sentiment": "NEGATIVE",
  "intensity": 0.8,
  "topics": ["自我"],
  "summary": "今天整体偏悲伤，和自我感受有关",
  "raw_sentiment": {{
    "label": "NEGATIVE",
    "score": 0.8
  }}
}}
要求：
1. scores 里的值是 0 到 1 之间的小数
2. dominant 必须是 scores 中最高的情绪
3. sentiment 只能是 POSITIVE、NEGATIVE、NEUTRAL 之一
4. 只返回 JSON
"""

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个严谨的中文情绪分析助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "stream": False,
        }

        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30)

            if resp.status_code != 200:
                return {
                    "scores": {"中性": 1.0},
                    "dominant": "中性",
                    "sentiment": "NEUTRAL",
                    "intensity": 0.5,
                    "topics": [],
                    "summary": f"调用大模型失败: {resp.status_code}",
                    "raw_sentiment": {"label": "NEUTRAL", "score": 0.5},
                }

            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            # 去掉可能的 markdown 代码块
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)

            # 补齐字段，避免前端报错
            result.setdefault("scores", {"中性": 1.0})
            result.setdefault("dominant", "中性")
            result.setdefault("sentiment", "NEUTRAL")
            result.setdefault("intensity", 0.5)
            result.setdefault("topics", [])
            result.setdefault("summary", "分析完成")
            result.setdefault("raw_sentiment", {"label": result["sentiment"], "score": result["intensity"]})

            return result

        except Exception as e:
            return {
                "scores": {"中性": 1.0},
                "dominant": "中性",
                "sentiment": "NEUTRAL",
                "intensity": 0.5,
                "topics": [],
                "summary": f"调用大模型异常: {str(e)}",
                "raw_sentiment": {"label": "NEUTRAL", "score": 0.5},
            }


def get_analyzer() -> EmotionAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EmotionAnalyzer()
    return _analyzer_instance


def analyze_emotion(text: str) -> Dict:
    return get_analyzer().analyze_emotion(text)


def batch_analyze_emotions(texts: List[str]) -> List[Dict]:
    return [analyze_emotion(text) for text in texts]
