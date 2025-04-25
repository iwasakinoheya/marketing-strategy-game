# submit.py

import streamlit as st
import sys
import os
import asyncio
from openai.types.responses import ResponseTextDeltaEvent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.sidebar import show_sidebar
from agents import Agent, Runner
from dotenv import load_dotenv
from agents import set_default_openai_key

# .env 読み込み（ローカルのみ、Cloudでは無視される）
load_dotenv()

# 環境に応じてAPIキーを取得
def get_openai_key():
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return os.getenv("OPENAI_API_KEY")

# エージェントSDKにセット
api_key = get_openai_key()
if not api_key:
    st.error("❌ OpenAI APIキーが設定されていません。Secretsまたは.envに設定してください。")
else:
    set_default_openai_key(api_key)

# サイドバー
show_sidebar()
st.title("📝 戦略を設計・提出しよう")

# ----------------------------
# 戦況要約エージェントの定義
# ----------------------------
summary_agent = Agent(
    name="要約アシスタント",
    instructions="""
    あなたは戦略ゲームのファシリテーターです。
    ユーザーが過去にアシスタントと交わしたチャット履歴「全体」を要約してください。箇条書きでお願いします。
    ・ユーザーには「ある国でミネラルウォーターを売りたい」という目的があります
    ・チャット履歴から分かる戦況を箇条書きにして下さい。
    ・「1990年代」「日本」「Volvic」などの表現は使ってはいけません
    """,
    model="gpt-4o",
)

# 要約を生成する関数
async def summarize_chat(status=None):
    response_box = st.empty()
    result_text = []
    result = Runner.run_streamed(summary_agent, input=st.session_state["conversation_history"])
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            delta = event.data.delta
            result_text.append(delta)
            response_box.markdown("".join(result_text))
    st.session_state["summary"] = "".join(result_text)
    status.update(label="✅ 戦況分析の要約が完了しました！", state="complete")

# ----------------------------
# 要約セクション
# ----------------------------
st.subheader("🧠 戦況分析まとめ")

# 初回表示時に自動要約（履歴がある場合のみ）
if "summary" not in st.session_state and st.session_state.get("conversation_history"):
    st.session_state["summary"] = ""
    with st.status("戦況分析の要約を生成中...", expanded=False) as status:
        asyncio.run(summarize_chat(status))

# 要約表示（既存 or 空白）
st.markdown(st.session_state.get("summary", "_（まだ要約が生成されていません）_"))

# 🔁 要約再生成ボタン
if st.button("🔄 要約を再生成する"):
    with st.status("戦況分析の要約を再生成中...", expanded=False) as status:
        asyncio.run(summarize_chat(status))
        st.success("要約を更新しました。")

# ----------------------------
# 自由メモ欄（保持あり）
# ----------------------------
st.subheader("🗒 自分たちのメモ")
if "memo" not in st.session_state:
    st.session_state["memo"] = ""
# 入力欄（valueで値保持）
memo_input = st.text_area("戦況に対する自分たちの考察メモ", value=st.session_state["memo"])
st.session_state["memo"] = memo_input

# ----------------------------
# 戦略入力欄（保持あり）
# ----------------------------
st.subheader("📌 戦略を提出")

who = st.text_input("WHO（誰に向けて）", value=st.session_state.get("who", ""))
what = st.text_input("WHAT（何の価値を届ける？）", value=st.session_state.get("what", ""))
how = st.text_area("HOW（どうやって届ける？）", value=st.session_state.get("how", ""))

# 値の保持
st.session_state["who"] = who
st.session_state["what"] = what
st.session_state["how"] = how

# 提出処理
if st.button("🚀 提出する"):
    if not (who.strip() and what.strip() and how.strip()):
        st.warning("WHO・WHAT・HOWのすべてを入力してください。")
    else:
        st.session_state["submission"] = {
            "who": who,
            "what": what,
            "how": how,
            "memo": st.session_state["memo"],
            "summary": st.session_state["summary"]
        }
        st.success("提出が完了しました！結果ページに移動します。")
        st.switch_page("pages/result.py")
