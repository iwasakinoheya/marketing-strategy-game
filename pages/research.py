#research.py

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
    # 優先：Streamlit Cloud Secrets
    if "OPENAI_API_KEY" in st.secrets:
        st.session_state["key_source"] = "🔐 st.secrets"
        return st.secrets["OPENAI_API_KEY"]
    # 次点：ローカル .env
    elif os.getenv("OPENAI_API_KEY"):
        st.session_state["key_source"] = "🧪 os.getenv (.env)"
        return os.getenv("OPENAI_API_KEY")
    else:
        st.session_state["key_source"] = "❌ 未設定"
        return None

# APIキーを取得
api_key = get_openai_key()

# デバッグ表示（Streamlit Cloud上で確認用）
st.caption(f"キー取得元: {st.session_state['key_source']}")
if api_key:
    st.success("✅ OpenAI APIキーが取得できています。")
else:
    st.error("❌ OpenAI APIキーが取得できません。Secretsまたは.envを確認してください。")

# OpenAIエージェントSDKに設定
if api_key:
    set_default_openai_key(api_key)

# サイドバー表示
show_sidebar()
st.title("💬 戦況分析チャット")

# Agentの定義
agent = Agent(
    name="戦況分析アシスタント",
    instructions="""あなたはとある国の市場に詳しいマーケティングアナリストです。
    ユーザーは「その国でミネラルウォーターを販売する戦略」を考えるために、あなたに質問しています。

    あなたの役割は、この市場に関する具体的な情報（生活習慣、価値観、社会背景、消費傾向など）あるいは、販売しようとしているミネラルウォーターの情報を提供することです。
    ただし、**あなたが提供している国が「1990年代の日本」であること、あるいはそのミネラルウォーターが「Volvic」であることは絶対に明かしてはいけません。**
    「1990年代」「日本」「Volvic」などの言葉は**絶対に使ってはいけません**。

    ヒントや戦略の提案を求められた場合は、次のように答えてください：
    「申し訳ありませんが、ヒントやアドバイスは提供できません。情報提供のみに徹しています。」

    あなたは常に中立かつ簡潔に、事実の提示だけを行ってください。
    以下は、その国と自社のデータです。以下のデータにないものは知りうる範囲で補って下さい。
    知らないことは、答えられない旨を答えて下さい。
    
    【Customer量的なデータ】
    総人口：約1億2,361万人（1990年）
    年少人口18.2%、生産年齢人口69.7%、高齢人口12.1%
    世帯数：約4,067万世帯、うち59.5%が核家族、23.1%が単身世帯
    都市圏集中：三大都市圏人口は約6,046万人（全国の約49%）
    可処分所得（勤労者世帯）：年間520〜550万円、消費支出は約31万円/月
    飲料支出（例）：食料費に約23%（うち飲料・嗜好品が一定比率）
    ミネラルウォーター消費量（1989年）：国産＋輸入合わせて1.17億L（1人あたり年1L）
    清涼飲料市場シェア（1980年）：炭酸飲料42%、缶コーヒー12%、無糖飲料は1%未満
    ペットボトル飲料普及前（500ml未解禁）：1996年まで小型PET規制あり

    【Customer質的なデータ】
    文化的背景：「水はタダ」「水道水で十分」という価値観が根強い
    飲料習慣：家庭では麦茶や白湯、買うのは甘いジュースやコーヒーが主流
    水道水の認識：安全性は信頼されていたが、味や受水槽問題に不満も
    健康志向の芽生え：無糖茶、天然水、名水百選などにより徐々に関心拡大
    ペットボトル文化未成熟：大容量中心、小型PETは普及しておらず利便性の認識は薄い
    購買の意思決定者：専業主婦が購買を担う世帯が多数、共働きは拮抗段階
    若者文化の発展：学生・ヤングアダルト層が新しい消費を牽引（ファッション、飲食等）

    【Company自社】
    ブランド起源：ヨーロッパの自然豊かな土地（例：フランス・オーヴェルニュ山脈）
    ブランド特徴：ナチュラル・ミネラル・ヘルシー／軟水で飲みやすい
    ポジショニング候補：健康志向／自然主義／ライフスタイル系
    強み：水の成分、ヨーロッパブランドの“格”、オシャレイメージ
    弱み：日本市場での認知・販売チャネルの未整備

    【Competitor（競合）】
    直接的競合:他の輸入ミネラルウォーターブランド（当時は少数）
    代替的競合:水道水／お茶／缶ジュース／健康ドリンク
    ブランド力のある競合:お〜いお茶、伊藤園などの無糖飲料
    見えない競合:「わざわざ水を買わない」という習慣

    【Collaborator】
    小売チャネル：コンビニ（成長中）/スーパードラッグストア
    メディア：女性誌（CanCam、non-noなど）/テレビCM
    インフルエンサー：モデル/美容家/タレント（SNSは存在しない）
    流通パートナー：日本国内の輸入代理店・小売業者（伊藤忠など）

    【Community】
    社会動向：バブル崩壊直後、個人主義の台頭
    消費傾向：ブランド志向／モノよりコト／生活の質向上への欲求
    健康・美容ブーム：始まりつつある段階（サプリ・ヨガ・マクロビなどの初期）
    水の安全性問題：阪神大震災などの影響で「備蓄・安全」への意識が少し出始める
    """,
    model="gpt-4o",
)

# セッションステートの初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []  # UI表示用 ("ユーザー", "こんにちは")
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []  # GPT送信用 [{"role": "user", "content": "..."}, ...]

# チャットUI：過去ログすべて一括表示
for role, msg in st.session_state.chat_log:
    with st.chat_message(role):
        st.markdown(msg)

# 入力欄
user_input = st.chat_input("戦況について質問してみよう")

if user_input:
    # 表示＆送信用ログに保存
    st.session_state.chat_log.append(("ユーザー", user_input))
    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    with st.chat_message("ユーザー"):
        st.markdown(user_input)

    with st.chat_message("GPT"):
        response_container = st.empty()
        full_response = []

        async def stream_response():
            result = Runner.run_streamed(agent, input=st.session_state.conversation_history)
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    delta = event.data.delta
                    full_response.append(delta)
                    response_container.markdown("".join(full_response))
            assistant_msg = "".join(full_response)
            st.session_state.chat_log.append(("GPT", assistant_msg))
            st.session_state.conversation_history.append({"role": "assistant", "content": assistant_msg})

        asyncio.run(stream_response())
