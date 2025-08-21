from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import asyncio
import aiohttp
from datetime import datetime

from debate_manager import (
    DebateManager, DebateAgent, JudgeAgent, AgentRole,
    DebateMetrics, DebateTurn
)

app = FastAPI(title="LLLM Colosseum API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# アクティブなディベートセッションを管理
active_debates: Dict[str, DebateManager] = {}
active_connections: List[WebSocket] = []


class ModelInfo(BaseModel):
    name: str
    model_id: str
    description: Optional[str] = None
    size: Optional[str] = None


class StartDebateRequest(BaseModel):
    topic: str
    combatant_a: str
    combatant_b: str
    judge: str
    personas: Optional[Dict[str, str]] = None


class OllamaModelResponse(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str
    details: Optional[Dict] = None


@app.get("/")
async def root():
    return {
        "message": "Local LLM Arena API",
        "version": "1.0.0",
        "endpoints": {
            "models": "/api/models",
            "websocket": "/ws/arena",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    return {"status": "healthy", "ollama": "connected"}
                else:
                    return {"status": "unhealthy", "ollama": "unreachable"}
    except Exception as e:
        return {"status": "unhealthy", "ollama": "error", "message": str(e)}


@app.get("/api/models", response_model=List[ModelInfo])
async def get_available_models():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = []
                    for model in data.get("models", []):
                        # モデル名とサイズ情報を含めた表示名を作成
                        model_id = model["name"]
                        
                        # 特定のモデルに対してわかりやすい表示名を作成
                        if model_id == "gpt-oss:120b":
                            display_name = "GPT-OSS (120B)"
                        elif model_id == "qwen3:32B":
                            display_name = "Qwen3 (32B)"
                        elif model_id == "gemma3:27b":
                            display_name = "Gemma3 (27B)"
                        elif model_id == "gemma3:12b":
                            display_name = "Gemma3 (12B)"
                        elif model_id == "gemma3:latest":
                            display_name = "Gemma3 (Latest)"
                        elif model_id == "qwen3:latest":
                            display_name = "Qwen3 (Latest)"
                        elif model_id == "gpt-oss:latest":
                            display_name = "GPT-OSS (Latest)"
                        elif model_id == "llama3:latest":
                            display_name = "Llama3 (Latest)"
                        elif "Swallow-MS" in model_id:
                            display_name = "Swallow-MS (7B)"
                        else:
                            # デフォルトの処理
                            if ":" in model_id:
                                base_name, tag = model_id.split(":", 1)
                                display_name = f"{base_name.replace('-', ' ').title()} ({tag})"
                            else:
                                display_name = model_id.replace("-", " ").title()
                        
                        models.append(ModelInfo(
                            name=display_name,
                            model_id=model_id,
                            description=f"Model: {model_id}",
                            size=None
                        ))
                    
                    # 推奨モデルを追加（存在しない場合の仮想エントリ）
                    recommended_models = [
                        ModelInfo(
                            name="Qwen 3 (32B)",
                            model_id="qwen3:32B",
                            description="Creative strategist persona - Recommended",
                            size="32B"
                        ),
                        ModelInfo(
                            name="GPT-OSS (120B)",
                            model_id="gpt-oss:120b",
                            description="Analytical persona - Recommended",
                            size="120b"
                        ),
                        ModelInfo(
                            name="Gemma 3 (27B)",
                            model_id="gemma3:27b",
                            description="Scholarly persona - Recommended",
                            size="27b"
                        )
                    ]
                    
                    # 実際に存在するモデルかチェックして追加
                    existing_ids = {m.model_id for m in models}
                    for rec_model in recommended_models:
                        if rec_model.model_id not in existing_ids:
                            models.insert(0, rec_model)
                    
                    return models
                else:
                    raise HTTPException(status_code=500, detail="Failed to fetch models from Ollama")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")


@app.websocket("/ws/arena")
async def websocket_arena(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    debate_manager = None
    
    try:
        while True:
            # クライアントからのメッセージを受信
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["action"] == "start_debate":
                # ディベートの開始
                topic = message["topic"]
                roles = message["roles"]
                personas = message.get("personas", {})
                
                # エージェントの作成
                combatant_a = DebateAgent(
                    name="Agent A",
                    model_id=roles["combatant_a"],
                    persona=personas.get("combatant_a", "You are a logical and analytical debater.")
                )
                
                combatant_b = DebateAgent(
                    name="Agent B",
                    model_id=roles["combatant_b"],
                    persona=personas.get("combatant_b", "You are a creative and persuasive debater.")
                )
                
                judge = JudgeAgent(
                    name="Judge",
                    model_id=roles["judge"]
                )
                
                # ディベートマネージャーの作成
                debate_manager = DebateManager(
                    topic=topic,
                    combatant_a=combatant_a,
                    combatant_b=combatant_b,
                    judge=judge
                )
                
                await debate_manager.start_debate()
                
                # ディベート開始の通知
                await websocket.send_json({
                    "type": "debate_started",
                    "topic": topic,
                    "agents": {
                        "combatant_a": combatant_a.model_id,
                        "combatant_b": combatant_b.model_id,
                        "judge": judge.model_id
                    }
                })
                
                # ディベートフローの実行
                debate_order = [
                    AgentRole.COMBATANT_A,
                    AgentRole.COMBATANT_B,
                    AgentRole.COMBATANT_A,
                    AgentRole.COMBATANT_B,
                    AgentRole.COMBATANT_A,
                    AgentRole.COMBATANT_B,
                    AgentRole.JUDGE
                ]
                
                for agent_role in debate_order:
                    # ターン開始の通知
                    agent_name = "judge" if agent_role == AgentRole.JUDGE else (
                        "A" if agent_role == AgentRole.COMBATANT_A else "B"
                    )
                    
                    await websocket.send_json({
                        "type": "turn_start",
                        "agent": agent_name
                    })
                    
                    # ストリーミング応答の送信
                    async for chunk in debate_manager.process_turn_stream(agent_role):
                        await websocket.send_json(chunk)
                    
                    # ターン終了の通知
                    await websocket.send_json({
                        "type": "turn_end",
                        "agent": agent_name
                    })
                
                # ディベート終了の通知
                summary = debate_manager.get_debate_summary()
                await websocket.send_json({
                    "type": "debate_ended",
                    "summary": summary
                })
                
            elif message["action"] == "get_status":
                # 現在の状態を返す
                if debate_manager:
                    summary = debate_manager.get_debate_summary()
                    await websocket.send_json({
                        "type": "status",
                        "data": summary
                    })
                else:
                    await websocket.send_json({
                        "type": "status",
                        "data": {"state": "no_active_debate"}
                    })
            
            elif message["action"] == "stop_debate":
                # ディベートの停止
                if debate_manager:
                    await debate_manager.__aexit__(None, None, None)
                    debate_manager = None
                    await websocket.send_json({
                        "type": "debate_stopped"
                    })
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        if debate_manager:
            await debate_manager.__aexit__(None, None, None)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        if debate_manager:
            await debate_manager.__aexit__(None, None, None)


@app.post("/api/debate/start")
async def start_debate(request: StartDebateRequest):
    # HTTPエンドポイント版（オプション）
    debate_id = f"debate_{datetime.now().timestamp()}"
    
    combatant_a = DebateAgent(
        name="Agent A",
        model_id=request.combatant_a,
        persona=request.personas.get("combatant_a") if request.personas else None
    )
    
    combatant_b = DebateAgent(
        name="Agent B",
        model_id=request.combatant_b,
        persona=request.personas.get("combatant_b") if request.personas else None
    )
    
    judge = JudgeAgent(
        name="Judge",
        model_id=request.judge
    )
    
    debate_manager = DebateManager(
        topic=request.topic,
        combatant_a=combatant_a,
        combatant_b=combatant_b,
        judge=judge
    )
    
    active_debates[debate_id] = debate_manager
    
    return {
        "debate_id": debate_id,
        "status": "started",
        "topic": request.topic
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)