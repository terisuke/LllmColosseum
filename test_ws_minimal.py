#!/usr/bin/env python3
"""Minimal WebSocket test."""

import asyncio
import json
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/arena"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Send debate start message
            start_message = {
                "action": "start_debate",
                "topic": "Test topic",
                "roles": {
                    "combatant_a": "gemma3:latest",
                    "combatant_b": "qwen3:latest",
                    "judge": "llama3:latest"
                }
            }
            
            await websocket.send(json.dumps(start_message))
            print(f"Sent: {start_message}")
            
            # Receive just a few messages
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"Message {i+1}: {data.get('type', 'unknown')}")
                    
                    if data.get("type") == "error":
                        print(f"Error: {data.get('message')}")
                        break
                        
                except asyncio.TimeoutError:
                    print(f"Timeout after message {i}")
                    break
                    
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())