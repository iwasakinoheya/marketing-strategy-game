import streamlit as st
import state
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.sidebar import show_sidebar
show_sidebar()


st.title("🏠 ホーム")
st.markdown("🧠 マーケティング戦略ゲームへようこそ！")
st.markdown("このゲームでは、チームで協力し、ある国の戦況を分析して戦略を立てます。")

team_name = st.text_input("👥 あなたたちのチーム名を入力してください")

if team_name:
    st.session_state["team_name"] = team_name
    st.success(f"チーム名「{team_name}」が登録されました！")
    st.markdown("左のサイドバーから、ページを切り替えてプレイしてください。")
