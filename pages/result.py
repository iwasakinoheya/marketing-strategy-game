# result.py

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
st.title("📊 リザルトページ")

# Volvicの模範戦略（裏データ）
model_answer = {
    "who": "都市部の20〜30代の美容・健康志向の高い女性",
    "what": "美と健康のために“身体に優しい水”を選ぶという自己表現",
    "how": "パ女性誌で文脈設計／コンビニで手軽に／パリ発のブランドストーリー"
}

# 提出されたデータがない場合
if "submission" not in st.session_state:
    st.warning("まだ戦略が提出されていません。")
    st.stop()

submission = st.session_state["submission"]
team_name = st.session_state.get("team_name", "未登録チーム")

# 採点用エージェント定義
grader = Agent(
    name="戦略採点官",
    instructions=f"""
    あなたはマーケティング戦略を採点するAIです。
    
    ユーザーが考えた戦略（WHO/WHAT/HOW）と、模範戦略（Volvic成功事例）を見比べて、
    ・戦略の整合性（WHO/WHAT/HOWがつながっているか）
    ・模範との近さ（方向性や着眼点が一致しているか）
    をふまえて100点満点で採点してください。
    
    出力は次の形式で行ってください：
    1. 点数（整数）：xx点
    2. 簡単なコメント：どこが良かったか、どこが異なっていたか
    
    ただし「Volvic」や「日本」「1990年代」という単語は使わないでください。
    """,
    model="gpt-4o",
)

# 採点実行
with st.status("戦略を採点中...", expanded=True):
    response_box = st.empty()
    result_lines = []

    async def score_strategy():
        compare_prompt = f"""[提出された戦略]
WHO: {submission['who']}
WHAT: {submission['what']}
HOW: {submission['how']}

[模範戦略]
WHO: {model_answer['who']}
WHAT: {model_answer['what']}
HOW: {model_answer['how']}
"""
        result = Runner.run_streamed(grader, input=compare_prompt)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                delta = event.data.delta
                result_lines.append(delta)
                response_box.markdown("".join(result_lines))
        st.session_state["score_result"] = "".join(result_lines)

    asyncio.run(score_strategy())

# 提出戦略の表示
st.markdown("## ✅ 提出された戦略")

st.markdown(f"**チーム名**: {team_name}")
st.markdown(f"**WHO**: {submission['who']}")
st.markdown(f"**WHAT**: {submission['what']}")
st.markdown(f"**HOW**: {submission['how']}")
st.markdown("**🧠 メモ:**")
st.code(submission["memo"])
st.markdown("**🧠 戦況分析まとめ:**")
st.markdown(submission["summary"])

# 採点結果の再表示
st.markdown("## 🧮 採点結果")
st.markdown(st.session_state["score_result"])
