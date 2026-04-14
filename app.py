import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

from db import create_tables
from services import user_service, report_service, ceremony_module
from services.diary_service import save_diary, get_recent_diaries
from services.chat_service import save_chat, get_recent_chats
from services.emotion_service import analyze_emotion
from services.strategy_service import select_dbt_strategy
from services.visualization_module import (
    emotion_bar_chart,
    emotion_trend_line_chart,
    radar_chart,
    aggregate_emotion_scores,
    build_inner_garden_state,
    render_lotus_pond_html,
)
import llm_client

create_tables()

st.set_page_config(page_title="伴成长 AI成长官", layout="wide")

st.markdown(
    """
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; }
h1, h2, h3 { color: #4B0082; }
.stButton button { background-color: #8A2BE2; color: white; border-radius:5px; padding:5px 15px; }
.chat-bubble { border-radius: 15px; padding: 10px; margin: 5px 0; display: inline-block; max-width: 80%; }
.user-msg { background-color: #E6E6FA; color: #4B0082; text-align:left; }
.ai-msg { background-color: #FFFACD; color: #8A2BE2; text-align:right; float: right; }
.clear { clear: both; }
</style>
""",
    unsafe_allow_html=True,
)

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

if st.session_state["user_id"] is None:
    page = "注册/登录"
else:
    st.sidebar.success(f"当前已登录用户：{st.session_state['username']}")
    if st.sidebar.button("退出登录"):
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        st.rerun()

    page = st.sidebar.radio(
        "导航",
        ["成长契约", "心流日记", "AI陪伴", "心理图谱", "成长报告", "仪式感"],
    )

if page == "注册/登录":
    st.title("欢迎使用伴成长 AI成长官")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("注册"):
            if not username or not password:
                st.warning("请输入用户名和密码")
            else:
                if user_service.register_user(username, password):
                    st.success("注册成功，请登录")
                else:
                    st.error("用户名已存在")

    with col2:
        if st.button("登录"):
            if not username or not password:
                st.warning("请输入用户名和密码")
            else:
                uid = user_service.authenticate(username, password)
                if uid:
                    st.session_state["user_id"] = uid
                    st.session_state["username"] = username
                    st.success("登录成功")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
    st.stop()

user_id = st.session_state["user_id"]

if page == "成长契约":
    st.header("成长契约")
    existing_contract = user_service.get_growth_contract(user_id)

    if existing_contract:
        st.success("你已签署成长契约，当前不可重复签署。")
        st.write(f"**契约类型：** {existing_contract['contract_type']}")
        st.write(f"**目标：** {existing_contract['goals']}")
        if existing_contract.get("start_date"):
            st.write(f"**开始日期：** {existing_contract['start_date']}")
        if existing_contract.get("end_date"):
            st.write(f"**结束日期：** {existing_contract['end_date']}")
    else:
        contract_type = st.selectbox("契约类型", ["情绪稳定", "压力应对", "自我探索"])
        goals = st.text_area("目标")
        duration_months = st.selectbox("成长周期（月）", [3, 6, 12])

        if st.button("签署契约"):
            if not goals.strip():
                st.warning("请输入契约目标")
            else:
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=30 * duration_months)
                ok = user_service.set_growth_contract(
                    user_id,
                    contract_type,
                    goals,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    status="active",
                )
                if ok:
                    st.success("契约签署成功！")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("你已签署过成长契约，不能重复签署")

if page == "心流日记":
    st.header("心流日记")
    diary_text = st.text_area("记录今天的心情")
    if st.button("保存日记"):
        if not diary_text.strip():
            st.warning("请输入日记内容")
        else:
            emotion_result = analyze_emotion(diary_text)
            save_diary(user_id, diary_text, emotion_result)
            st.success("日记保存完成")
            st.subheader("情绪分析结果")
            st.markdown(f"- **主导情绪**: {emotion_result['dominant']}")
            st.markdown(f"- **情绪类别**: {emotion_result['sentiment']}")
            st.markdown(f"- **情绪强度**: {emotion_result['intensity']}")
            st.markdown(f"- **摘要**: {emotion_result['summary']}")

if page == "AI陪伴":
    st.header("AI成长官陪伴")
    user_message = st.text_input("输入你的想法")
    if st.button("发送"):
        if not user_message.strip():
            st.warning("请输入内容")
        else:
            context = get_recent_chats(user_id, limit=10)
            strategy_tag, strategy_text = select_dbt_strategy(user_message)
            reply = llm_client.call_llm(
                user_id=user_id,
                message=user_message,
                context=context,
                strategy_text=strategy_text,
            )
            save_chat(user_id, user_message, reply, strategy_tag)
            st.success("回复生成完成")
            st.rerun()

    st.subheader("最近对话")
    chats = get_recent_chats(user_id, limit=10)
    if not chats:
        st.info("暂无对话记录")
    for msg, reply, created_at in chats[::-1]:
        st.markdown(f"<div class='chat-bubble user-msg'>{msg}</div><div class='clear'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble ai-msg'>{reply}</div><div class='clear'></div>", unsafe_allow_html=True)

if page == "心理图谱":
    st.header("心理图谱 - 内心世界可视化")
    diaries = get_recent_diaries(user_id, limit=10)

    if diaries:
        parsed_diaries = [
            {
                "content": d.get("content", ""),
                "emotion_json": d.get("emotion", {}),
                "created_at": d.get("created_at"),
            }
            for d in diaries
        ]

        bar_chart = emotion_bar_chart(parsed_diaries)
        if bar_chart is not None:
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.info("暂无柱状图数据")

        trend_chart = emotion_trend_line_chart(parsed_diaries)
        if trend_chart is not None:
            st.altair_chart(trend_chart, use_container_width=True)
        else:
            st.info("暂无折线图数据")

        st.subheader("综合情绪雷达图")
        overall_scores = aggregate_emotion_scores(parsed_diaries, method="avg")
        radar_fig = radar_chart(overall_scores)
        if radar_fig is not None:
            st.plotly_chart(radar_fig, use_container_width=True)
        else:
            st.info("暂无综合雷达图数据")

        st.subheader("内心莲花池")
        garden_state = build_inner_garden_state(parsed_diaries)
        lotus_html = render_lotus_pond_html(garden_state)
        components.html(lotus_html, height=450, scrolling=False)
    else:
        st.info("暂无日记数据，无法生成心理图谱")

if page == "成长报告":
    st.header("成长报告")
    if st.button("生成报告"):
        report = report_service.generate_growth_report(user_id)
        with st.expander("查看成长报告", expanded=True):
            st.write(report)

if page == "仪式感":
    st.header("仪式感体验")
    st.write(ceremony_module.start_growth_ceremony(user_id))
    if st.button("本周复盘仪式"):
        st.write(ceremony_module.weekly_review_ceremony(user_id))