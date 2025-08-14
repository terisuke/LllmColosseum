#!/usr/bin/env python3
"""Simple test to debug Ollama API integration."""

import asyncio
import aiohttp
import json

async def test_ollama_direct():
    """Test Ollama API directly."""
    url = "http://localhost:11434/api/chat"
    
    async with aiohttp.ClientSession() as session:
        print("Testing Ollama streaming API...")
        
        async with session.post(
            url,
            json={
                "model": "gemma3:latest",
                "messages": [{"role": "user", "content": "Count to 3"}],
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 10
                }
            }
        ) as response:
            print(f"Status: {response.status}")
            
            token_count = 0
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        try:
                            data = json.loads(line_str)
                            if 'message' in data and not data.get('done', False):
                                content = data['message'].get('content', '')
                                if content:
                                    token_count += 1
                                    print(f"Token {token_count}: {repr(content)}")
                                    if token_count >= 10:
                                        break
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            print(f"Line: {repr(line_str)}")

if __name__ == "__main__":
    asyncio.run(test_ollama_direct())