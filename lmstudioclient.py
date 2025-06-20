import openai


class LmStudioClient:
    """
    LM Studioクライアント。

    Attributes:
        base_url (str): LM Studio APIのベースURL
        model_name (str): 使用するモデル名
        messages (list): チャット履歴を保持するリスト
        client (openai.OpenAI): OpenAI互換クライアントインスタンス
    """

    def __init__(self, base_url: str, model_name: str):
        """
        LmStudioClientのインスタンスを初期化する。

        Args:
            base_url (str): LM Studio APIのベースURL
            model_name (str): 使用するモデル名

        Raises:
            Exception: APIクライアントの初期化に失敗した場合
        """
        self.base_url = base_url
        self.model_name = model_name
        self.messages = []        
        try:
            self.client = openai.OpenAI(base_url=self.base_url)
        except Exception as e:
            print(f"API接続エラー: {e}")
            raise

    def set_system_prompt(self, filename: str):
        """
        システムプロンプト用のテキストファイルを読み込み、messagesにsystemロールで追加する。

        Args:
            filename (str): システムプロンプトが書かれたファイル名

        Raises:
            Exception: ファイルの読み込みやプロンプト追加に失敗した場合
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
            # 既存のsystemプロンプトを除去（複数回呼ばれた場合のため）
            self.messages = [m for m in self.messages if m.get("role") != "system"]
            self.messages.insert(0, {"role": "system", "content": system_prompt})
        except Exception as e:
            print(f"システムプロンプトの読み込みエラー: {e}")
            raise
 
    def get_response(self, text: str):
        """
        LM Studio APIを使って応答文を生成する。

        Args:
            text (str): ユーザーからの入力メッセージ

        Returns:
            str: LM Studioからの応答テキスト

        Raises:
            Exception: テキスト生成に失敗した場合
        """
        try:
            self.messages.append({"role": "user", "content": text})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages
            )
            response_text = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": response_text})
            return response_text
        except Exception as e:
            print(f"テキスト生成エラー: {e}")
            raise  # エラーを再発生させる
