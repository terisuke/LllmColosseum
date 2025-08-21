# LLLM Colosseum (Local Large Language Model Colosseum)

最先端のローカルLLMバトルアリーナ - M4 MacBook Pro最適化版

## 🎯 概要

複数のLLMモデルがリアルタイムでディベートを行い、その能力を視覚的に比較できるプラットフォーム。
完全にローカル環境で動作し、プライバシーとパフォーマンスを両立。

## 🙏 Credits

本プロジェクトは [syv-ai/OpenArena](https://github.com/syv-ai/OpenArena) のコアロジックを基に構築されています。

### OpenArenaから活用している機能：
- ELOレーティングシステム
- ディベートオーケストレーション
- 非同期LLM処理ロジック

### 本プロジェクトの独自拡張：
- Next.js/React によるリアルタイムUI
- WebSocketストリーミング
- 3カラムディベート可視化
- M4 Mac向けメモリ最適化

## 🚀 クイックスタート

### 1. 事前準備

```bash
# Ollamaが起動していることを確認
ollama serve

# モデルがインストールされていることを確認（最低1つ必要）
ollama list

# 軽量モデルをインストール（まだの場合）
ollama pull llama3.2:3b
```

### 2. アプリケーション起動

```bash
# 初回実行時は実行権限を付与
chmod +x run_dev.sh

# 開発環境の起動（バックエンドとフロントエンドを同時起動）
./run_dev.sh
```

### 3. アクセス

アプリケーションが起動すると：
- **Frontend UI**: http://localhost:3000 - メインのディベートUI
- **Backend API**: http://localhost:8000 - APIサーバー
- **API Docs**: http://localhost:8000/docs - Swagger UI

### 4. 使い方

1. ブラウザで http://localhost:3000 にアクセス
2. 左側のControl Panelで：
   - ディベートトピックを入力
   - 3つのモデルを選択（Agent A、Agent B、Judge）
   - "Start Debate"ボタンをクリック
3. 右側のArenaでリアルタイムディベートを観戦

### トラブルシューティング

**WebSocket接続エラーが表示される場合：**
```bash
# サービスを再起動
pkill -f "uvicorn\|next"
./run_dev.sh
```

**モデル一覧が表示されない場合：**
```bash
# Ollamaが起動しているか確認
curl http://localhost:11434/api/tags

# Ollamaを再起動
pkill ollama
ollama serve
```

## 📋 必要要件

- macOS (M4 MacBook Pro推奨)
- Ollama インストール済み
- Python 3.10+
- Node.js 18+
- 128GB RAM (3モデル同時実行時推奨)

### Ollamaのインストール

```bash
# Ollamaをインストール
curl -fsSL https://ollama.com/install.sh | sh

# Ollamaを起動
ollama serve
```

### 推奨モデル

開発・テスト用（軽量）：
```bash
ollama pull llama3.2:3b
ollama pull gemma2:2b
ollama pull qwen2.5:3b
```

本番用（高性能）：
```bash
ollama pull qwen2.5:32b
ollama pull llama3.1:70b
ollama pull gemma-3:27b
```

## 🏗️ アーキテクチャ

```
local-llm-arena/
├── backend/           # FastAPI バックエンド
│   ├── main.py       # WebSocketエンドポイント
│   ├── debate_manager.py  # ディベート制御ロジック
│   └── requirements.txt
├── frontend/         # Next.js フロントエンド
│   ├── app/
│   │   ├── components/    # UIコンポーネント
│   │   ├── hooks/        # カスタムフック
│   │   └── page.tsx      # メインページ
│   └── package.json
└── run_dev.sh       # 開発環境起動スクリプト
```

### 技術スタック

- **Backend**: FastAPI + WebSocket
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS
- **LLM Engine**: Ollama
- **State Management**: Zustand
- **WebSocket**: react-use-websocket

## 📦 開発セットアップ

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🎮 使い方

1. **モデル選択**: Control Panelから3つのモデルを選択
   - Combatant A: 賛成側の論者
   - Combatant B: 反対側の論者
   - Judge: 審判役
   
   ※ モデル名にサイズ（120B, 32B等）が表示されます

2. **トピック入力**: ディベートのテーマを入力
   - 英語例: "AI will replace human jobs"
   - 日本語例: "きのこの山よりたけのこの里の方が美味しい"
   
   ※ 言語は自動検出されます

3. **ディベート開始**: "Start Debate"ボタンをクリック

4. **リアルタイム観戦**: 3カラムレイアウトでトークンストリーミングを観察
   - 各エージェントの回答が正しいカラムに表示
   - 完全な回答が表示されるまでストリーミング

## ⚡ パフォーマンス最適化

### M4 MacBook Pro向け設定

- **メモリ管理**: 各モデルに40GB割り当て
- **並列処理**: 3モデル同時実行対応
- **ストリーミング**: TTFT < 500ms
- **スループット**: TPS > 40 tokens/sec

### トラブルシューティング

Ollamaが応答しない場合：
```bash
# Ollamaの再起動
pkill ollama
ollama serve
```

メモリ不足の場合：
```bash
# 軽量モデルに切り替え
ollama pull llama3.2:1b
ollama pull gemma2:2b
```

## 🌟 Features

- ⚡ Real-time token streaming with WebSocket
- 🎯 ELO rating system for model comparison
- 🔒 100% local & private execution
- 🚀 Optimized for Apple Silicon (M4 Mac)
- 🎨 Modern UI with Next.js 15 & Tailwind CSS
- 📊 Performance metrics (TPS, TTFT, time tracking)
- 🤖 Support for multiple Ollama models
- 🌏 **日本語/英語 自動言語検出対応**
- 📝 **拡張トークン制限** (Agent: 3000, Judge: 5000)
- 🏷️ **モデルサイズ表示** (120B, 32B, 27B, etc.)
- 🔄 **改善されたWebSocket通信**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 🤝 謝辞

- [OpenArena](https://github.com/syv-ai/OpenArena) by syv-ai - コアロジックの基盤
- [Ollama](https://ollama.com) - ローカルLLM実行環境
- [FastAPI](https://fastapi.tiangolo.com) - 高性能WebSocketサーバー
- [Next.js](https://nextjs.org) - モダンReactフレームワーク

---

Based on [OpenArena](https://github.com/syv-ai/OpenArena) by syv-ai