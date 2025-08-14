# Local LLM Arena

M4 MacBook Pro（128GB）向けに最適化されたローカルLLMディベートシステム

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

```bash
# 開発環境の起動
chmod +x run_dev.sh
./run_dev.sh
```

アプリケーションが起動すると：
- Frontend UI: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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

2. **トピック入力**: ディベートのテーマを入力

3. **ディベート開始**: "Start Debate"ボタンをクリック

4. **リアルタイム観戦**: 3カラムレイアウトでトークンストリーミングを観察

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

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 🤝 謝辞

- [OpenArena](https://github.com/syv-ai/OpenArena) by syv-ai - コアロジックの基盤
- [Ollama](https://ollama.com) - ローカルLLM実行環境
- [FastAPI](https://fastapi.tiangolo.com) - 高性能WebSocketサーバー
- [Next.js](https://nextjs.org) - モダンReactフレームワーク

---

Based on [OpenArena](https://github.com/syv-ai/OpenArena) by syv-ai