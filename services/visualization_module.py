# services/visualization_module.py
# 心理图谱可视化模块（兼容 DeepSeek 情绪分析结果）

import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict

def emotion_bar_chart(parsed_diaries: List[Dict]):
    if not parsed_diaries:
        return None

    df_list = []

    for i, diary in enumerate(parsed_diaries):
        try:
            emotion_json = diary.get("emotion_json", {})
            if not isinstance(emotion_json, dict):
                continue

            scores = emotion_json.get("scores", {})
            if not isinstance(scores, dict) or not scores:
                continue

            row = {}
            for k, v in scores.items():
                try:
                    row[k] = float(v)
                except Exception:
                    continue

            if row:
                row["index"] = i
                df_list.append(row)

        except Exception:
            continue

    if not df_list:
        return None

    df = pd.DataFrame(df_list)

    fig = px.bar(
        df,
        x="index",
        y=[col for col in df.columns if col != "index"],
        barmode="group",
        title="情绪分布柱状图"
    )
    return fig

def emotion_trend_line_chart(parsed_diaries: List[Dict]):
    if not parsed_diaries:
        return None

    df_list = []

    for i, diary in enumerate(parsed_diaries):
        try:
            emotion_json = diary.get("emotion_json", {})
            if not isinstance(emotion_json, dict):
                continue

            scores = emotion_json.get("scores", {})
            if not isinstance(scores, dict) or not scores:
                continue

            row = {}
            for k, v in scores.items():
                try:
                    row[k] = float(v)
                except Exception:
                    continue

            if row:
                row["index"] = i
                df_list.append(row)

        except Exception:
            continue

    if not df_list:
        return None

    df = pd.DataFrame(df_list)
    df_melt = df.melt(id_vars="index", var_name="emotion", value_name="score")

    chart = alt.Chart(df_melt).mark_line(point=True).encode(
        x="index:O",
        y="score:Q",
        color="emotion:N"
    ).properties(
        title="情绪趋势折线图"
    )

    return chart


def radar_chart(scores_dict: Dict):
    if not scores_dict or not isinstance(scores_dict, dict):
        return None

    categories = list(scores_dict.keys())
    values_raw = list(scores_dict.values())

    if not categories or not values_raw:
        return None

    try:
        values = [float(v) for v in values_raw]
    except Exception:
        return None

    values = values + [values[0]]

    fig = go.Figure(
        data=[go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself'
        )]
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=False,
        title="情绪雷达图"
    )
    return fig

def aggregate_emotion_scores(parsed_diaries: List[Dict], method: str = "avg") -> Dict:
    if not parsed_diaries:
        return {}

    all_scores = []
    for diary in parsed_diaries:
        emotion_json = diary.get("emotion_json", {})
        if not isinstance(emotion_json, dict):
            continue

        scores = emotion_json.get("scores", {})
        if not isinstance(scores, dict) or not scores:
            continue

        row = {}
        for k, v in scores.items():
            try:
                row[k] = float(v)
            except Exception:
                continue

        if row:
            all_scores.append(row)

    if not all_scores:
        return {}

    df = pd.DataFrame(all_scores).fillna(0)
    if method == "sum":
        return df.sum().to_dict()
    return df.mean().to_dict()


def build_inner_garden_state(parsed_diaries: List[Dict]) -> Dict:
    avg_scores = aggregate_emotion_scores(parsed_diaries, method="avg")
    if not avg_scores:
        return {}

    happy = float(avg_scores.get("快乐", 0))
    calm = float(avg_scores.get("平静", 0))
    sad = float(avg_scores.get("悲伤", 0))
    anxious = float(avg_scores.get("焦虑", 0))
    angry = float(avg_scores.get("愤怒", 0))

    dominant = max(avg_scores, key=avg_scores.get)

    brightness = min(1.0, 0.35 + happy * 0.35 + calm * 0.30 - sad * 0.08)
    brightness = max(0.2, brightness)

    stability = calm * 0.65 + happy * 0.18 - anxious * 0.20 - angry * 0.10
    stability = max(0.0, min(1.0, stability))

    wave_level = anxious * 0.55 + angry * 0.35 + sad * 0.12
    wave_level = max(0.05, min(1.0, wave_level))

    bloom_count = max(3, int(4 + (happy + calm - sad * 0.5) * 8))
    lotus_open_ratio = max(0.25, min(1.0, happy * 0.45 + calm * 0.35 + 0.25 - sad * 0.18))
    leaf_density = max(0.35, min(1.0, calm * 0.45 + happy * 0.20 + 0.35 - angry * 0.10))

    return {
        "avg_scores": avg_scores,
        "dominant": dominant,
        "brightness": brightness,
        "stability": stability,
        "wave_level": wave_level,
        "bloom_count": bloom_count,
        "lotus_open_ratio": lotus_open_ratio,
        "leaf_density": leaf_density,
    }


def _theme_by_dominant(dominant: str) -> Dict:
    theme_map = {
        "平静": {
            "title": "今日心境：静水微澜",
            "sky1": "#edf7f4",
            "sky2": "#dceee8",
            "water1": "#cde4de",
            "water2": "#b7d5cd",
            "mist": "rgba(255,255,255,0.18)",
            "lotus_outer": "#f7f1f6",
            "lotus_inner": "#efd5e4",
            "leaf": "#79b894",
            "leaf_dark": "#5d9475",
            "accent": "#8ec8ba",
            "rain": "rgba(255,255,255,0.00)",
        },
        "快乐": {
            "title": "今日心境：轻盈而明亮",
            "sky1": "#fff8ea",
            "sky2": "#eef8e9",
            "water1": "#d9eee5",
            "water2": "#c4e1d5",
            "mist": "rgba(255,255,255,0.20)",
            "lotus_outer": "#fff5fb",
            "lotus_inner": "#ffd4e7",
            "leaf": "#7fc889",
            "leaf_dark": "#60a86a",
            "accent": "#bfe49f",
            "rain": "rgba(255,255,255,0.00)",
        },
        "悲伤": {
            "title": "今日心境：微凉而低落",
            "sky1": "#eef2f6",
            "sky2": "#dfe6ec",
            "water1": "#ccdae6",
            "water2": "#b9cad7",
            "mist": "rgba(255,255,255,0.14)",
            "lotus_outer": "#f4f5f8",
            "lotus_inner": "#d9ddea",
            "leaf": "#8ba4ac",
            "leaf_dark": "#718891",
            "accent": "#9eb2c4",
            "rain": "rgba(255,255,255,0.16)",
        },
        "焦虑": {
            "title": "今日心境：风起未定",
            "sky1": "#f2f6f8",
            "sky2": "#dfe9ee",
            "water1": "#d2e2e8",
            "water2": "#bfd4dc",
            "mist": "rgba(255,255,255,0.13)",
            "lotus_outer": "#faf7fb",
            "lotus_inner": "#e6dceb",
            "leaf": "#86b3a0",
            "leaf_dark": "#6b8d7f",
            "accent": "#96bfd1",
            "rain": "rgba(255,255,255,0.05)",
        },
        "愤怒": {
            "title": "今日心境：炽热与翻涌",
            "sky1": "#f9f0ee",
            "sky2": "#efdfd9",
            "water1": "#e7d7d1",
            "water2": "#d7c2bb",
            "mist": "rgba(255,255,255,0.10)",
            "lotus_outer": "#fff3f2",
            "lotus_inner": "#f3c9c0",
            "leaf": "#a1b089",
            "leaf_dark": "#818d6e",
            "accent": "#d3a29a",
            "rain": "rgba(255,255,255,0.03)",
        },
    }
    return theme_map.get(dominant, theme_map["平静"])


def render_lotus_pond_html(garden_state: Dict) -> str:
    if not garden_state:
        return """
        <div style="
            padding:24px;
            border-radius:28px;
            background:#f5f7f8;
            color:#333;
            font-size:16px;
        ">
            暂无莲花池可视化数据
        </div>
        """

    dominant = garden_state.get("dominant", "平静")
    bloom_count = int(garden_state.get("bloom_count", 5))
    open_ratio = float(garden_state.get("lotus_open_ratio", 0.7))
    leaf_density = float(garden_state.get("leaf_density", 0.7))
    wave_level = float(garden_state.get("wave_level", 0.2))
    stability = float(garden_state.get("stability", 0.5))
    scores = garden_state.get("avg_scores", {})

    happy = int(scores.get("快乐", 0) * 100)
    calm = int(scores.get("平静", 0) * 100)
    sad = int(scores.get("悲伤", 0) * 100)
    anxious = int(scores.get("焦虑", 0) * 100)

    theme = _theme_by_dominant(dominant)

    # 情绪微调
    if dominant == "悲伤":
        bloom_count = max(3, bloom_count - 2)
        open_ratio *= 0.75
    elif dominant == "快乐":
        bloom_count += 1
        open_ratio *= 1.08
    elif dominant == "平静":
        open_ratio *= 0.96

    # ---------- 工具函数风格的片段拼接 ----------
    def lotus_flower(left, top, size, outer, inner, main=False, droop=False):
        main_shadow = "0 8px 24px rgba(255,255,255,0.22)" if main else "0 4px 14px rgba(255,255,255,0.14)"
        rotate = "-3deg" if droop else "0deg"
        return f"""
        <div style="
            position:absolute;
            left:{left}%;
            top:{top}%;
            width:{size}%;
            height:{size}%;
            transform:translate(-50%,-50%) rotate({rotate});
            filter:drop-shadow({main_shadow});
            z-index:{4 if main else 3};
        ">
            <div style="
                position:absolute; left:18%; top:42%;
                width:24%; height:30%;
                background:{outer};
                border-radius:50% 50% 46% 46%;
                transform:rotate(-28deg);
            "></div>

            <div style="
                position:absolute; left:31%; top:24%;
                width:24%; height:36%;
                background:{outer};
                border-radius:50% 50% 46% 46%;
            "></div>

            <div style="
                position:absolute; left:46%; top:18%;
                width:24%; height:40%;
                background:{outer};
                border-radius:50% 50% 46% 46%;
            "></div>

            <div style="
                position:absolute; left:60%; top:41%;
                width:24%; height:30%;
                background:{outer};
                border-radius:50% 50% 46% 46%;
                transform:rotate(28deg);
            "></div>

            <div style="
                position:absolute; left:31%; top:40%;
                width:16%; height:21%;
                background:{inner};
                border-radius:50%;
                opacity:0.95;
            "></div>

            <div style="
                position:absolute; left:43%; top:34%;
                width:16%; height:22%;
                background:{inner};
                border-radius:50%;
                opacity:0.95;
            "></div>

            <div style="
                position:absolute; left:55%; top:40%;
                width:16%; height:21%;
                background:{inner};
                border-radius:50%;
                opacity:0.95;
            "></div>

            <div style="
                position:absolute; left:46%; top:46%;
                width:10%; height:10%;
                background:#f3d6a2;
                border-radius:50%;
                z-index:5;
            "></div>
        </div>
        """

    def lotus_reflection(left, top, size):
        return f"""
        <div style="
            position:absolute;
            left:{left}%;
            top:{top}%;
            width:{size*0.9}%;
            height:{size*0.45}%;
            transform:translate(-50%,-50%);
            border-radius:50%;
            background:radial-gradient(
                ellipse at center,
                rgba(255,255,255,0.12) 0%,
                rgba(255,255,255,0.05) 45%,
                rgba(255,255,255,0.00) 75%
            );
            filter:blur(2px);
            z-index:1;
        "></div>
        """

    def leaf(left, top, width, height, rotate, opacity, z=2, vein=True):
        vein_html = ""
        if vein:
            vein_html = """
            <div style="
                position:absolute;
                left:50%;
                top:50%;
                width:42%;
                height:2px;
                background:rgba(255,255,255,0.14);
                transform:translate(-50%,-50%) rotate(-8deg);
                border-radius:999px;
            "></div>
            """
        return f"""
        <div style="
            position:absolute;
            left:{left}%;
            top:{top}%;
            width:{width}%;
            height:{height}%;
            transform:translate(-50%,-50%) rotate({rotate}deg);
            border-radius:50%;
            background:{theme['leaf']};
            opacity:{opacity};
            box-shadow:
                inset -12px -8px 0 0 {theme['leaf_dark']}44,
                0 6px 12px rgba(60,70,80,0.05);
            z-index:{z};
        ">
            {vein_html}
        </div>
        """

    def leaf_reflection(left, top, width, height, rotate):
        return f"""
        <div style="
            position:absolute;
            left:{left}%;
            top:{top}%;
            width:{width*0.95}%;
            height:{height*0.75}%;
            transform:translate(-50%,-50%) rotate({rotate}deg);
            border-radius:50%;
            background:rgba(255,255,255,0.07);
            filter:blur(1.5px);
            z-index:1;
        "></div>
        """

    # ---------- 分层叶片 ----------
    far_leaves = [
        (10, 55.0, 5.4, 2.8, -12, 0.42),
        (26, 57.0, 5.8, 3.0, -8, 0.40),
        (50, 56.2, 5.4, 2.8, 10, 0.42),
        (72, 55.5, 6.0, 3.1, -6, 0.40),
        (92, 57.2, 5.2, 2.6, 7, 0.42),
    ]

    mid_leaves = [
        (18, 53.2, 7.0, 3.6, -10, 0.54),
        (39, 55.2, 7.6, 3.9, 6, 0.52),
        (61, 54.0, 6.8, 3.4, -14, 0.54),
        (83, 54.1, 7.8, 4.0, 2, 0.52),
    ]

    front_leaves = [
        (28, 62.5, 9.5, 4.8, 4, 0.66),
        (52, 61.0, 10.0, 5.2, -7, 0.68),
        (76, 63.0, 9.8, 5.1, 5, 0.66),
    ]

    if dominant == "悲伤":
        far_leaves = [(x, y + 1.0, w, h, r, o) for x, y, w, h, r, o in far_leaves]
        mid_leaves = [(x, y + 1.4, w, h, r, o) for x, y, w, h, r, o in mid_leaves]
        front_leaves = [(x, y + 1.8, w, h, r, o) for x, y, w, h, r, o in front_leaves]

    leaf_html = ""
    reflection_html = ""

    for x, y, w, h, r, o in far_leaves:
        leaf_html += leaf(x, y, w, h, r, o, z=2, vein=False)
        reflection_html += leaf_reflection(x, y + 7.0, w, h, r)

    for x, y, w, h, r, o in mid_leaves:
        leaf_html += leaf(x, y, w, h, r, o, z=3, vein=True)
        reflection_html += leaf_reflection(x, y + 7.5, w, h, r)

    for x, y, w, h, r, o in front_leaves:
        leaf_html += leaf(x, y, w, h, r, o, z=4, vein=True)
        reflection_html += leaf_reflection(x, y + 8.0, w, h, r)

    # ---------- 花朵：一朵主花 + 陪衬花 ----------
    main_flower_left = 50 if dominant != "悲伤" else 52
    main_flower_top = 48.5 if dominant != "悲伤" else 50.2
    main_flower_size = 9.8 + open_ratio * 3.0

    lotus_html = ""
    lotus_html += lotus_reflection(main_flower_left, main_flower_top + 10.5, main_flower_size)
    lotus_html += lotus_flower(
        main_flower_left,
        main_flower_top,
        main_flower_size,
        theme["lotus_outer"],
        theme["lotus_inner"],
        main=True,
        droop=(dominant == "悲伤")
    )

    side_positions = [
        (12, 49.2, 5.8),
        (88, 49.0, 5.6),
        (24, 47.8, 5.0),
        (73, 48.4, 5.1),
    ]

    if dominant == "悲伤":
        side_positions = [
            (12, 50.6, 4.8),
            (88, 50.3, 4.6),
            (74, 49.8, 4.4),
        ]

    for idx, (left, top, size) in enumerate(side_positions):
        size = size + open_ratio * 1.1
        lotus_html += lotus_reflection(left, top + 9.0, size)
        lotus_html += lotus_flower(
            left,
            top,
            size,
            theme["lotus_outer"],
            theme["lotus_inner"],
            main=False,
            droop=(dominant == "悲伤")
        )

    # ---------- 波纹 ----------
    wave_opacity = 0.10 + wave_level * 0.10
    ripple_html = f"""
    <div style="
        position:absolute;
        left:-6%; right:-6%; top:61%;
        height:14%;
        border-top:2px solid rgba(255,255,255,{wave_opacity:.2f});
        border-radius:50%;
        z-index:1;
    "></div>

    <div style="
        position:absolute;
        left:-8%; right:-8%; top:67%;
        height:16%;
        border-top:2px solid rgba(255,255,255,{wave_opacity*0.75:.2f});
        border-radius:50%;
        z-index:1;
    "></div>

    <div style="
        position:absolute;
        left:-10%; right:-10%; top:72%;
        height:18%;
        border-top:1px solid rgba(255,255,255,{wave_opacity*0.45:.2f});
        border-radius:50%;
        z-index:1;
    "></div>
    """

    # ---------- 雨丝 / 雾 / 漂浮颗粒 ----------
    rain_html = ""
    if dominant == "悲伤":
        rain_positions = [11, 19, 31, 44, 58, 71, 84]
        for i, left in enumerate(rain_positions):
            height = 9 + (i % 3) * 2
            top = 12 + (i % 2) * 3
            rain_html += f"""
            <div style="
                position:absolute;
                left:{left}%;
                top:{top}%;
                width:1px;
                height:{height}%;
                background:linear-gradient(
                    to bottom,
                    rgba(255,255,255,0.00),
                    {theme['rain']}
                );
                transform:rotate(11deg);
                opacity:0.85;
                z-index:2;
            "></div>
            """

    particles_html = ""
    if dominant == "快乐":
        particle_positions = [(16, 22), (28, 18), (57, 20), (76, 19), (88, 23)]
        for x, y in particle_positions:
            particles_html += f"""
            <div style="
                position:absolute;
                left:{x}%;
                top:{y}%;
                width:6px;
                height:6px;
                border-radius:50%;
                background:rgba(255,244,210,0.45);
                box-shadow:0 0 12px rgba(255,244,210,0.35);
                z-index:2;
            "></div>
            """

    # ---------- 顶部信息区 ----------
    info_html = f"""
    <div style="
        position:absolute;
        left:4%;
        top:7%;
        z-index:10;
        color:#2f3340;
        max-width:70%;
    ">
        <div style="
            font-size:24px;
            font-weight:700;
            letter-spacing:0.3px;
            margin-bottom:12px;
        ">{theme['title']}</div>

        <div style="
            display:flex;
            gap:10px;
            flex-wrap:wrap;
        ">
            <span style="
                padding:7px 14px;
                border-radius:999px;
                background:rgba(255,255,255,0.40);
                backdrop-filter:blur(4px);
                font-size:12px;
                line-height:1;
            ">主情绪：{dominant}</span>

            <span style="
                padding:7px 14px;
                border-radius:999px;
                background:rgba(255,255,255,0.36);
                backdrop-filter:blur(4px);
                font-size:12px;
                line-height:1;
            ">稳定度：{int(stability * 100)}%</span>

            <span style="
                padding:7px 14px;
                border-radius:999px;
                background:rgba(255,255,255,0.34);
                backdrop-filter:blur(4px);
                font-size:12px;
                line-height:1;
            ">快乐 {happy} / 平静 {calm} / 悲伤 {sad} / 焦虑 {anxious}</span>
        </div>
    </div>
    """

    html = f"""
    <div style="
        position:relative;
        width:100%;
        height:460px;
        overflow:hidden;
        border-radius:30px;
        background:
            linear-gradient(to bottom,
                {theme['sky1']} 0%,
                {theme['sky2']} 33%,
                {theme['water1']} 33%,
                {theme['water2']} 100%);
        box-shadow:
            0 14px 34px rgba(40,50,70,0.10),
            inset 0 1px 0 rgba(255,255,255,0.55);
    ">
        <!-- 天空雾层 -->
        <div style="
            position:absolute;
            inset:0;
            background:
                radial-gradient(circle at 20% 12%, {theme['mist']}, transparent 18%),
                radial-gradient(circle at 50% 13%, {theme['mist']}, transparent 19%),
                radial-gradient(circle at 80% 12%, {theme['mist']}, transparent 18%);
            z-index:0;
        "></div>

        <!-- 远景天空留白 -->
        <div style="
            position:absolute;
            left:0; right:0; top:0;
            height:30%;
            background:linear-gradient(
                to bottom,
                rgba(255,255,255,0.06),
                rgba(255,255,255,0.00)
            );
            z-index:0;
        "></div>

        <!-- 水岸线 -->
        <div style="
            position:absolute;
            left:0; right:0; top:34%;
            height:2px;
            background:rgba(255,255,255,0.22);
            z-index:1;
        "></div>

        <!-- 水面高光 -->
        <div style="
            position:absolute;
            left:0; right:0; top:35%;
            height:12%;
            background:linear-gradient(
                to bottom,
                rgba(255,255,255,0.11),
                rgba(255,255,255,0.00)
            );
            z-index:1;
        "></div>

        <!-- 纵向柔光 -->
        <div style="
            position:absolute;
            left:50%;
            top:18%;
            width:38%;
            height:58%;
            transform:translateX(-50%);
            background:radial-gradient(
                ellipse at center,
                rgba(255,255,255,0.14) 0%,
                rgba(255,255,255,0.06) 34%,
                rgba(255,255,255,0.00) 72%
            );
            filter:blur(4px);
            z-index:1;
        "></div>

        {ripple_html}
        {reflection_html}
        {leaf_html}
        {lotus_html}
        {rain_html}
        {particles_html}
        {info_html}
    </div>
    """

    return html



