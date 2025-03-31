# Deep Research MCP Server

Deep Research は Web での検索と高度な調査機能を提供するエージェントベースのツールです。HuggingFace の smolagents を活用し、MCP サーバーとして実装されています。

このプロジェクトは HuggingFace の open_deep_research 事例を基に作成されています。

## 機能

- Web 検索と情報収集
- PDF およびドキュメント分析
- 画像分析と説明
- YouTube の字幕取得
- アーカイブサイトの検索

## 必要要件

- Python 3.11 以上
- uv パッケージマネージャー
- 以下の API キー：
  - OpenAI API キー
  - HuggingFace トークン
  - SerpAPI キー

## インストール

リポジトリをクローン：

```bash
git clone https://github.com/Hajime-Y/deep-research-mcp.git
cd deep-research-mcp
```

仮想環境の作成と依存関係のインストール：

```bash
uv venv
source .venv/bin/activate # LinuxまたはMac用
# .venv\Scripts\activate # Windows用
uv sync
```

## 環境変数

プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の環境変数を設定してください：

```
OPENAI_API_KEY=your_openai_api_key
HF_TOKEN=your_huggingface_token
SERPER_API_KEY=your_serper_api_key
```

SERPER_API_KEY は[Serper.dev](https://serper.dev)でサインアップすることで取得できます。

## 使用方法

MCP サーバーの起動：

```bash
uv run deep_research.py
```

これにより deep_research エージェントが MCP サーバーとして起動します。

## 主要コンポーネント

- `deep_research.py`: MCP サーバーのエントリーポイント
- `create_agent.py`: エージェントの作成と設定
- `scripts/`: 各種ツールとユーティリティ
  - `text_web_browser.py`: テキストベースの Web ブラウザ
  - `text_inspector_tool.py`: ファイル検査ツール
  - `visual_qa.py`: 画像分析ツール
  - `mdconvert.py`: 各種ファイル形式を Markdown に変換

## ライセンス

このプロジェクトは[ライセンス名]の下で提供されています。

## 謝辞

このプロジェクトは HuggingFace の smolagents と Microsoft の autogen プロジェクトのコードを使用しています。
