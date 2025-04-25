# utils/sidebar.py

import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.caption(f"チーム名：{st.session_state.get('team_name', '未設定')}")
        st.header("📂 ナビゲーション")
        st.page_link("pages/home.py", label="🏠 ホーム")
        st.page_link("pages/research.py", label="💬 戦況分析")
        st.page_link("pages/submit.py", label="📝 戦略提出")
        st.page_link("pages/result.py", label="📊 リザルト")
