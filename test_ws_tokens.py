#!/usr/bin/env python3
"""Test to see actual tokens."""

import asyncio
import json
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/arena"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Send debate start message
        start_message = {
            "action": "start_debate",
            "topic": "Is water wet?",
            "roles": {
                "combatant_a": "gemma3:latest",
                "combatant_b": "gemma3:latest",
                "judge": "gemma3:latest"
            }
        }
        
        await websocket.send(json.dumps(start_message))
        print(f"Sent debate start\n")
        
        token_count = 0
        agent_tokens = {}
        
        for i in range(50):  # Receive first 50 messages
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                if data.get("type") == "token_stream":
                    agent = data.get("agent", "unknown")
                    token = data.get("token", "")
                    
                    if agent not in agent_tokens:
                        agent_tokens[agent] = ""
                    agent_tokens[agent] += token
                    
                    token_count += 1
                    
                    # Print first few tokens from each agent
                    if len(agent_tokens[agent]) <= 50:
                        print(f"[{agent}] {repr(token)}", end="")
                        if token_count % 10 == 0:
                            print()  # New line every 10 tokens
                            
                elif data.get("type") == "turn_start":
                    print(f"\n--- Turn start: {data.get('agent')} ---")
                    
                elif data.get("type") == "turn_end":
                    agent = data.get('agent')
                    if agent in agent_tokens:
                        print(f"\n--- Turn end: {agent} (said {len(agent_tokens[agent])} chars) ---\n")
                        
            except asyncio.TimeoutError:
                break
                
        print("\n\nSummary:")
        for agent, content in agent_tokens.items():
            print(f"{agent}: {content[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_ws())