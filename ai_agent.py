import os
import datetime
import subprocess
import re
import streamlit as st
import google.generativeai as genai
from geminiclient import GeminiClient
from openaiclient import OpenAiClient
from lmstudioclient import LmStudioClient

LLM = "OpenAI"
#LLM = "Gemini"
#LLM = "google/gemma-3-4b"


def extract_python_code(result: str) -> str:
    """
    result文字列からPythonコード部分（```python ... ```）を抽出する。

    Args:
        result (str): LLMからの出力文字列

    Returns:
        str: コード部分のみの文字列
    """
    match = re.search(r"```python(.*?)```", result, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # バッククォートがない場合はそのまま返す
        return result.strip()


def save_code_to_file(code: str, filename: str = "result.py"):
    """
    文字列のPythonコードを指定ファイルに保存する。

    Args:
        code (str): 保存するPythonコード
        filename (str, optional): 保存先ファイル名。デフォルトは'result.py'
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)


def run_python_file(filename: str = "result.py") -> str:
    """
    指定したPythonファイルをサブプロセスで実行し、標準出力・標準エラーを取得して返す。

    Args:
        filename (str, optional): 実行するPythonファイル名。デフォルトは'result.py'

    Returns:
        str: 実行結果（標準出力＋標準エラー）
    """
    result = subprocess.run(
        ["python", filename],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr


def append_log(log_text: str, log_file: str = "agent_execution.log"):
    """
    指定したログファイルにタイムスタンプ付きでログを書き込む。

    Args:
        log_text (str): ログに記録するテキスト
        log_file (str, optional): ログファイル名。デフォルトは'agent_execution.log'
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {log_text}\n")


def get_ai_clients(llm_type: str):
    """
    オーケストレーターとPythonエンジニアAIのクライアントを初期化して返す。

    Args:
        llm_type (str): 使用するLLMの種類。'OpenAI', 'Gemini', またはローカルモデル名

    Returns:
        tuple: (orchestrator, python_engineer_ai)
    """
    if llm_type == "OpenAI":
        api_key = os.getenv("OPENAI_API_KEY")
        orchestrator = OpenAiClient(api_key)
        python_engineer_ai = OpenAiClient(api_key)
    elif llm_type == "Gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        orchestrator = GeminiClient()
        python_engineer_ai = GeminiClient()
    else:
        base_url = "http://localhost:1234/v1"
        model_name = llm_type
        orchestrator = LmStudioClient(base_url, model_name)
        python_engineer_ai = LmStudioClient(base_url, model_name)
    orchestrator.set_system_prompt("./オーケストレーター.txt")
    python_engineer_ai.set_system_prompt("./PythonエンジニアAI.txt")
    return orchestrator, python_engineer_ai

def agent_loop(
    orchestrator,
    python_engineer_ai,
    user_input: str,
    max_retry: int = 5
) -> bool:
    """
    AIエージェントのメインループ。Streamlitへの出力とログ記録も行う。

    Args:
        orchestrator: オーケストレーターAIクライアント
        python_engineer_ai: PythonエンジニアAIクライアント
        user_input (str): ユーザーからの要求
        max_retry (int, optional): 最大リトライ回数。デフォルトは5

    Returns:
        bool: 成功時はTrue、リトライオーバー時はFalse
    """
    human_instruction = user_input
    st.write("■人")
    st.write(human_instruction)
    append_log("■人\n" + human_instruction)

    for retry in range(max_retry):

        # オーケストレーターに指示を出す
        instructions = orchestrator.get_response(human_instruction)
        st.write("■オーケストレーター")
        st.write(instructions)
        append_log("■オーケストレーター\n" + instructions)

        if "#STATUS:NG" in instructions:
            st.stop()  # ユーザーの入力を待つ

        # PythonエンジニアAIがコード生成
        result = python_engineer_ai.get_response(instructions)
        st.write("■PythonエンジニアAI")
        st.code(result)
        append_log("■PythonエンジニアAI\n" + result)

        # コード抽出・保存・実行
        code = extract_python_code(result)
        save_code_to_file(code, "result.py")
        exec_result = run_python_file("result.py")
        st.write("■実行環境")
        st.code(exec_result)
        append_log("■実行環境\n" + exec_result)

        # 実行結果をオーケストレーターに判定させる
        result2 = orchestrator.get_response(
            "実行結果です。\n問題なければ人に完了を通知してください。\n"
            "問題があればコーディングAIに指示を出してください。\n"
            "あなたのすべての応答の最後に、以下のどちらかのタグを必ず出力してください：\n"
            "完了した場合: #STATUS:SUCCESS\n"
            "問題があった場合: #STATUS:RETRY\n"
            "実行結果です。\n" + exec_result
        )
        st.write("■オーケストレーター")
        st.write(result2)
        append_log("■オーケストレーター\n" + result2)

        if "#STATUS:SUCCESS" in result2:
            st.success("Pythonスクリプトは正常に動作しました。AIエージェントによるPythonスクリプト作成は完了です。")
            return True

        st.warning("作成したpythonスクリプトに問題があるので修正を依頼します。")
        # 次のループ用の指示を準備
        human_instruction = (
            "以下のPythonコードを実行したところ、不備やエラーが発生しました。\n"
            "コードと実行結果を確認し、問題点を特定して修正した新しいPythonコードを提案してください。\n"
            "【生成されたPythonコード】\n" + code +
            "\n【実行結果・エラーメッセージ】\n" + exec_result
        )
    # リトライオーバー
    st.write("リトライオーバー")
    st.write("試行回数を超えた為、作成したpythonスクリプトに問題があるまま終了しました。")
    return False

def main():
    """
    Streamlitアプリのエントリーポイント。
    ユーザー入力を受け取り、AIエージェントによるPythonコード生成・実行を行う。
    """    
    st.title("AIエージェントによる")
    st.title("Python自動生成＆実行環境")
    #st.image("ai_agent.png")

    user_input = st.text_area("作りたいものをAIに伝えて。", "〇〇をするpythonコードを作って")
    run_button = st.button("作成を依頼する")

    if run_button and user_input:
        orchestrator, python_engineer_ai = get_ai_clients(LLM)
        agent_loop(orchestrator, python_engineer_ai, user_input, max_retry=5)

if __name__ == "__main__":
    main()