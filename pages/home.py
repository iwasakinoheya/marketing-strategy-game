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
st.markdown("あなた達のチームは、ミネラルウォーターを飲む習慣のない国に、ミネラルウォーターを売る戦略を考えます。")
st.markdown("以下の手順で進めていきます：")
st.markdown("1. 戦況分析：エージェントとチャットし、国の情報を集めます。")
st.markdown("2. 戦略設計：集めた情報をもとに、戦略を考えます。")
st.markdown("3. 戦略提出：考えた戦略をエージェントに提出します。")
st.markdown("4. リザルト：提出した戦略の採点結果を確認します。")

team_name = st.text_input("👥 あなたたちのチーム名を入力してください")

if team_name:
    st.session_state["team_name"] = team_name
    st.success(f"チーム名「{team_name}」が登録されました！")
    st.markdown("左のサイドバーから、ページを切り替えてプレイしてください。")
