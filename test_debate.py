#!/usr/bin/env python3
"""Test script to verify debate functionality."""

import asyncio
import json
import websockets

async def test_debate():
    uri = "ws://localhost:8000/ws/arena"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Send debate start message
        start_message = {
            "action": "start_debate",
            "topic": "Should AI replace human teachers?",
            "roles": {
                "combatant_a": "gemma3:latest",
                "combatant_b": "qwen3:latest",
                "judge": "llama3:latest"
            }
        }
        
        await websocket.send(json.dumps(start_message))
        print(f"Sent: {start_message}")
        
        # Receive messages
        message_count = 0
        token_count = {}
        
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(message)
                
                if data.get("type") == "token_stream":
                    agent = data.get("agent", "unknown")
                    token = data.get("token", "")
                    
                    if agent not in token_count:
                        token_count[agent] = 0
                    token_count[agent] += 1
                    
                    # Print first few tokens for each agent
                    if token_count[agent] <= 5:
                        print(f"[{agent}] Token {token_count[agent]}: {repr(token)}")
                
                elif data.get("type") == "debate_end":
                    print("\nDebate ended!")
                    print(f"Token counts: {token_count}")
                    break
                    
                elif data.get("type") == "error":
                    print(f"Error: {data.get('message')}")
                    break
                    
                else:
                    print(f"Received: {data.get('type', 'unknown')}")
                
                message_count += 1
                
            except asyncio.TimeoutError:
                print("\nTimeout waiting for messages")
                print(f"Total messages received: {message_count}")
                print(f"Token counts: {token_count}")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    print("Testing debate functionality...")
    asyncio.run(test_debate())