import os
import time
import streamlit as st
from openai import OpenAI

# --- 定数 ---
ASSISTANT_NAME = "Python Code Assistant"
ASSISTANT_INSTRUCTIONS = """
あなたは、ユーザーの要求に応じてPythonコードを生成、実行、デバッグする専門のAIアシスタントです。

# あなたの役割
1.  ユーザーの要求を正確に理解し、それを満たすためのPythonコードを生成します。
2.  生成したコードは、あなた自身のCode Interpreter環境で即座に実行し、動作を検証します。
3.  実行結果にエラーが含まれていたり、要求を満たしていない場合は、問題点を自己分析し、コードを修正して再度実行します。
4.  この「生成→実行→検証→修正」のサイクルを、要求されたタスクが正常に完了するまで自律的に繰り返します。
5.  最終的に、完成したコードとその実行結果、そして結論をまとめてユーザーに提示してください。
6.  すべての応答は日本語で行ってください。
"""

def setup_assistant(client: OpenAI) -> str:
    """
    Assistantをセットアップし、そのIDを返す。
    指定した名前のAssistantが存在すればそれを使い、なければ新規作成する。
    """
    # 既存のAssistantを検索
    assistants = client.beta.assistants.list(limit=100)
    for assistant in assistants.data:
        if assistant.name == ASSISTANT_NAME:
            st.session_state.assistant_id = assistant.id
            return assistant.id

    # Assistantが存在しない場合は新規作成
    with st.spinner("初回起動のため、AIアシスタントをセットアップしています..."):
        assistant = client.beta.assistants.create(
            name=ASSISTANT_NAME,
            instructions=ASSISTANT_INSTRUCTIONS,
            tools=[{"type": "code_interpreter"}],
            model="gpt-4o", # または "gpt-4-turbo"
        )
        st.session_state.assistant_id = assistant.id
        return assistant.id

def run_agent(client: OpenAI, user_input: str):
    """
    AIエージェントのメイン処理。Assistantとの対話を実行し、結果をStreamlitに表示する。

    Args:
        client (OpenAI): OpenAIクライアント
        user_input (str): ユーザーからの要求
    """
    if "assistant_id" not in st.session_state:
        setup_assistant(client)

    assistant_id = st.session_state.assistant_id

    # 1. Threadを作成
    thread = client.beta.threads.create()
    thread_id = thread.id

    # 2. ユーザーメッセージをThreadに追加
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    # 3. Runを作成し、処理を開始
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    run_id = run.id

    # 4. Runの完了を待つ
    with st.spinner("AIエージェントがあなたの要求を処理中です...しばらくお待ちください。"):
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run_status.status in ['completed', 'failed', 'cancelled']:
                break
            time.sleep(1) # 1秒待機

    if run_status.status == 'completed':
        st.success("処理が完了しました。")
        display_results(client, thread_id, run_id)
    else:
        st.error(f"処理が失敗しました。ステータス: {run_status.status}")
        st.error(run_status.last_error)


def display_results(client: OpenAI, thread_id: str, run_id: str):
    """
    実行結果とAIの応答をStreamlitに表示する。

    Args:
        client (OpenAI): OpenAIクライアント
        thread_id (str): スレッドID
        run_id (str): 実行ID
    """
    # 実行ステップを取得して表示
    st.subheader("AIエージェントの実行ステップ")
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread_id,
        run_id=run_id,
        limit=100
    )

    for step in reversed(run_steps.data):
        if step.step_details.type == "tool_calls":
            for tool_call in step.step_details.tool_calls:
                if tool_call.type == "code_interpreter":
                    with st.expander(f"ステップ: Code Interpreterの実行", expanded=False):
                        st.write("▼ 実行したコード")
                        st.code(tool_call.code_interpreter.input, language="python")
                        st.write("▼ 実行結果（出力）")
                        for output in tool_call.code_interpreter.outputs:
                            if output.type == "logs":
                                st.code(output.logs, language="text")

    # スレッドのメッセージを取得して表示
    st.subheader("最終的なAIからの応答")
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for message in reversed(messages.data):
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    st.markdown(content.text.value)
                elif content.type == "image_file":
                    # 画像が表示される場合
                    image_data = client.files.content(content.image_file.file_id).read()
                    st.image(image_data)


def main():
    """
    Streamlitアプリのエントリーポイント。
    """
    st.set_page_config(page_title="AI Agent with Assistants API", layout="wide")
    st.title("🤖 Assistants API版 Python自動生成＆実行環境")

    st.info(
        "このアプリはOpenAI Assistants APIの`Code Interpreter`機能を利用しています。\n"
        "実行したい処理を自然言語で指示すると、AIエージェントが自律的にPythonコードを生成・実行・修正し、最終的な結果を出力します。"
    )

    # OpenAI APIキーの設定
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("OpenAI APIキーを入力してください:", type="password")
    
    if not api_key:
        st.warning("OpenAI APIキーが設定されていません。")
        st.stop()
        
    client = OpenAI(api_key=api_key)

    user_input = st.text_area(
        "作りたいものをAIに伝えてください。", 
        "カレントディレクトリにあるファイルの一覧を表示するPythonコードを書いて実行してください。",
        height=150
    )
    
    run_button = st.button("作成を依頼する", type="primary")

    if run_button and user_input:
        with st.container(border=True):
            st.subheader("ユーザーからの要求")
            st.write(user_input)
            run_agent(client, user_input)

if __name__ == "__main__":
    main()
