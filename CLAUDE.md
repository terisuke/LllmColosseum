# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLLM Colosseum (Local Large Language Model Colosseum) is a real-time debate arena platform where multiple LLMs compete against each other through structured debates. Built on FastAPI + Next.js, it provides a visual interface for comparing model capabilities through live debates with WebSocket streaming.

## Development Commands

### Quick Start
```bash
# Run both backend and frontend
./run_dev.sh
```

### Backend Only
```bash
cd backend
python main.py
# or
uvicorn main:app --reload
```

### Frontend Only
```bash
cd frontend
npm run dev
```

### Testing
```bash
# Test WebSocket connection
python test_ws_minimal.py

# Test debate functionality
python test_debate.py
```

## Architecture

### Core Components

1. **Backend** (`backend/`)
   - `main.py`: FastAPI server with WebSocket endpoints
     - `/ws/arena`: WebSocket for real-time debate streaming
     - `/api/models`: Get available Ollama models
     - `/health`: Health check endpoint
   - `debate_manager.py`: Debate orchestration logic
     - `DebateAgent`: Handles individual model responses
     - `JudgeAgent`: Evaluates debate outcomes
     - `DebateManager`: Coordinates the debate flow

2. **Frontend** (`frontend/`)
   - `app/page.tsx`: Main application page
   - `components/`:
     - `ControlPanel.tsx`: Model selection and debate controls
     - `ArenaView.tsx`: 3-column debate visualization
     - `AgentStream.tsx`: Individual agent response display
   - `hooks/useWebSocket.ts`: WebSocket connection management
   - `stores/arenaStore.ts`: Zustand state management

### Key Features

- **Bilingual Support**: Automatic language detection (Japanese/English)
- **Token Limits**: 
  - Agents: 3000 tokens
  - Judge: 5000 tokens
- **Model Display**: Shows model sizes (120B, 32B, 27B, etc.)
- **WebSocket Streaming**: Real-time token-by-token display
- **Performance Metrics**: TPS, TTFT, total tokens tracking

### WebSocket Message Flow

1. Client sends `start_debate` with topic and model selections
2. Server responds with `debate_started`
3. For each turn:
   - Server sends `turn_start`
   - Server streams `token_stream` messages
   - Server sends `turn_end`
4. Server sends `debate_ended` with summary

### Language Detection

The system automatically detects Japanese characters in the topic and adjusts:
- Prompts are generated in the detected language
- Judge evaluations use appropriate language
- Score parsing handles both English and Japanese formats

## Configuration

### Ollama Models
The system works with any Ollama model. Recommended models:

**For Testing (lightweight):**
- llama3.2:3b
- gemma2:2b
- qwen2.5:3b

**For Production (high performance):**
- gpt-oss:120b
- qwen3:32B
- gemma3:27b

### Token Limits
Configured in `debate_manager.py`:
- `num_predict`: Controls max tokens per response
- Agent responses: 3000 tokens
- Judge evaluation: 5000 tokens

## Troubleshooting

### WebSocket Issues
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify frontend WebSocket URL in `page.tsx`

### Model Display Issues
- Model names are mapped in `main.py:get_available_models()`
- Size information is extracted from model IDs

### Language Issues
- Language detection uses Unicode range check (> 0x3000)
- Prompts are in `debate_manager.py:build_prompt()`
- Judge prompts in `evaluate_debate_stream()`

## Recent Updates

- Added Japanese language support with automatic detection
- Fixed WebSocket message routing for proper agent display
- Increased token limits for complete responses
- Added model size information to dropdown displays
- Improved error handling and reconnection logic