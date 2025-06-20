import google.generativeai as genai


class GeminiClient:
    """
    Gemini APIクライアント。

    Attributes:
        messages (list): チャット履歴を保持するリスト
        model (GenerativeModel): Geminiの生成モデルインスタンス
        chat (ChatSession): Geminiのチャットセッション
    """

    def __init__(self):
        """
        GeminiClientのインスタンスを初期化する。
        Geminiモデルとチャットセッションを開始する。

        Raises:
            Exception: モデルやチャットセッションの初期化に失敗した場合
        """
        try:
            self.messages = []
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            print(f"API接続エラー: {e}")
            raise

    def set_system_prompt(self, filename: str):
        """
        システムプロンプト用のテキストファイルを読み込み、チャットセッションにsystemプロンプトとして送信する。

        Args:
            filename (str): システムプロンプトが書かれたファイル名

        Raises:
            Exception: ファイルの読み込みやAPI送信に失敗した場合
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
            _ = self.chat.send_message(system_prompt)
        except Exception as e:
            print(f"システムプロンプトの読み込みエラー: {e}")
            raise

    def get_response(self, text: str):
        """
        Gemini APIを使って応答文を生成する。

        Args:
            text (str): ユーザーからの入力メッセージ

        Returns:
            str: Geminiからの応答テキスト

        Raises:
            Exception: テキスト生成に失敗した場合
        """
        #print(f"質問: {text}")
        try:
            response = self.chat.send_message(text)
            return response.text
        except Exception as e:
            print(f"テキスト生成エラー: {e}")
            raise  # エラーを再発生させる
