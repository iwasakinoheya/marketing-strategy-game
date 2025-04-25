# hello_agents.py

import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key
from openai.types.responses import ResponseTextDeltaEvent

# .env ファイルから API キーを読み込む
load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# エージェントの定義
agent = Agent(
    name="戦況分析アシスタント",
    instructions="""あなたは1990年代の日本市場に詳しいマーケティングアナリストです。ユーザーの質問に簡潔に答えてください。
    ユーザーはあなたの回答をもとに、戦略を考えるゲームをしています。
    ユーザーには「ある国にミネラルウォーターを販売したい。その国の戦況を分析して、戦略を考える」というシナリオが与えられています。
    ある国とは1990年代の日本を想定しており、Volvicの成功事例を基にしたゲームとなっています。
    ですから、あなたは1990年代の日本市場の情報をユーザーに提供してユーザーが戦略を立てることが出来るようにして下さい。
    ただし、「1990年代の日本市場」という情報や「Volvicの成功事例」という情報はユーザーには与えないでください。
    あくまで、あなたはユーザーに情報を提供する役割で、戦略を考えるのはユーザーです。
    くれぐれも、「1990年代」「日本市場」「Volvic」という言葉は使わないでください。
    情報提供に徹し、ヒントやアドバイスは避けてください。
    ヒントやアドバイスを求められた場合は、ユーザーに「ヒントやアドバイスを与えることは禁止されています」と答えて下さい。"""
)

async def main():
    # 初回の質問
    user_input = "健康意識はありますか？"
    print(f"ユーザー: {user_input}")
    result = Runner.run_streamed(agent, input=user_input)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print("\n")  # 改行

    # 会話履歴を取得し、次の質問を追加
    new_input = result.to_input_list() + [{"role": "user", "content": "その市場でミネラルウォーターを売るヒントはなんですか？"}]
    print("ユーザー: その市場でミネラルウォーターを売るヒントはなんですか？")
    result = Runner.run_streamed(agent, input=new_input)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print("\n")  # 改行

asyncio.run(main())
