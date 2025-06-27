# AIエージェントによるPython自動生成＆実行環境

### 概要

- AIエージェント（オーケストレーターAI＋コーディングAI）がユーザーの要求からPythonコードを自動生成し、実行・検証・修正までを自律的に繰り返す最小構成のサンプルです。  
- StreamlitによるWeb GUIを備え、OpenAI/Gemini/ローカルLLM（LM Studio等）に対応しています。

### 特徴

- AIエージェントが人の要求からPythonコードを自動生成・実行・検証・再生成
- StreamlitによるGUIで、やりたいことを入力するだけでOK
- OpenAI（GPT-4.0/4.1）、Gemini、ローカルLLM（LM Studio等）に対応
- プロンプト設計・ログ記録・リトライ制御など、実用的なAIエージェント設計例

### 使用ライブラリ

- [OpenAI](https://openai.com/)
- [Google Gemini](https://ai.google.dev/)
- [LM Studio](https://lmstudio.ai/)
- [Streamlit](https://streamlit.io/)

## セットアップ

- Python 3.8 以上
- 必要なパッケージ（requirements.txt参照）
- OpenAI APIキー、Google Gemini APIキー、またはローカルLLM（LM Studio等）のAPIエンドポイント

```bash
git clone https://github.com/manymids/AI_Agent.git
cd ai-agent-python
pip install -r requirements.txt
```

## 実行方法

1. **APIキーやエンドポイントを環境変数で設定**  
   - OpenAI: `OPENAI_API_KEY`
   - Gemini: `GOOGLE_API_KEY`
   - LM Studio: LM Studioを起動し、APIエンドポイントを指定
2. **Streamlitアプリを起動**
```bash
streamlit run ai_agent.py
```
3. **Web画面で「やりたいこと」を入力し、「AIエージェントに依頼」ボタンを押すだけ！**

## 拡張アイデア

- 実行環境のサンドボックス化（Docker等）
- ユーザーとの追加インタラクションによる要件明確化
- 外部入力・ファイルアップロード対応
- 生成コードのバージョン管理・履歴表示
- 自動テスト生成・実行
- セキュリティチェック・静的解析

## 注意事項

- 生成・実行されるコードの安全性は保証されません。自己責任でご利用ください。
- 本リポジトリは学習・研究・実験用途を主目的としています。

## ライセンス

- コード: MITライセンス
  
---
# おまけ

「このAIエージェントをOpenAI Agents SDKを使って書き換えてください。」とAIに依頼して
ai_agent.pyをOpenAIのAssistants API版に書き換えてみました。

## 実行方法
```bash
streamlit run ai_agent_openai_sdk.py
```

## オリジナルとの違い
- API版はコードがシンプルです
- API版は途中経過表示がシンプルです。
- API版はコード生成の割り切りが速いです。（元のはなんとか作ろうとする）
- API版のメッセージはフォーマルで固いです。（生成AIの意向？）
- API版は圧倒的に高速です。

## 結論

#### 実運用する場合は「OpenAIのAssistants API」を使いましょう！！ですね。