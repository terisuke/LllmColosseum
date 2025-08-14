import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime


class AgentRole(Enum):
    COMBATANT_A = "combatant_a"
    COMBATANT_B = "combatant_b"
    JUDGE = "judge"


@dataclass
class DebateMetrics:
    ttft: Optional[float] = None  # Time to first token
    tps: float = 0.0  # Tokens per second
    total_tokens: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class DebateTurn:
    agent: AgentRole
    content: str
    metrics: DebateMetrics
    timestamp: datetime


class DebateAgent:
    def __init__(self, name: str, model_id: str, endpoint: str = "http://localhost:11434/api/chat", 
                 api_key: Optional[str] = None, persona: Optional[str] = None):
        self.name = name
        self.model_id = model_id
        self.endpoint = endpoint
        self.api_key = api_key
        self.persona = persona
        self.elo_score = 1000
        self.conversation_history: List[Dict[str, str]] = []
        
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def build_prompt(self, topic: str, opponent_response: Optional[str] = None, is_opening: bool = False) -> str:
        if is_opening:
            prompt = f"""You are participating in a debate on the topic: "{topic}"
            
{self.persona if self.persona else ""}

Please provide your opening argument. Be clear, logical, and persuasive.
Make your argument in 2-3 paragraphs."""
        else:
            prompt = f"""You are continuing a debate on the topic: "{topic}"

{self.persona if self.persona else ""}

Your opponent just said:
{opponent_response}

Please provide your counter-argument or response. Address their points directly and present your own perspective.
Make your response in 2-3 paragraphs."""
        
        return prompt
    
    async def generate_response_stream(self, session: aiohttp.ClientSession, prompt: str, 
                                      role: str = "user") -> AsyncGenerator[Tuple[str, DebateMetrics], None]:
        metrics = DebateMetrics()
        metrics.start_time = time.perf_counter()
        first_token = True
        
        messages = self.conversation_history + [{"role": role, "content": prompt}]
        
        async with session.post(
            url=self.endpoint,
            headers=self.get_headers(),
            json={
                "model": self.model_id,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            }
        ) as response:
            full_content = ""
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    # Ollama streams JSON directly without "data: " prefix
                    try:
                        data = json.loads(line_str)
                        # Ollama API format - each message contains a single token
                        if 'message' in data and not data.get('done', False):
                            message = data['message']
                            if 'content' in message:
                                token = message['content']
                                
                                if token:
                                    if first_token:
                                        metrics.ttft = time.perf_counter() - metrics.start_time
                                        first_token = False
                                    full_content += token
                                    metrics.total_tokens += 1
                                    
                                    current_time = time.perf_counter()
                                    elapsed = current_time - metrics.start_time
                                    if elapsed > 0:
                                        metrics.tps = metrics.total_tokens / elapsed
                                    
                                    yield token, metrics
                    except json.JSONDecodeError:
                        continue
            
            metrics.end_time = time.perf_counter()
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": full_content})


class JudgeAgent:
    def __init__(self, name: str, model_id: str, endpoint: str = "http://localhost:11434/api/chat",
                 api_key: Optional[str] = None):
        self.name = name
        self.model_id = model_id
        self.endpoint = endpoint
        self.api_key = api_key
    
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def evaluate_debate_stream(self, session: aiohttp.ClientSession, topic: str, 
                                    debate_history: List[DebateTurn]) -> AsyncGenerator[Tuple[str, DebateMetrics], None]:
        metrics = DebateMetrics()
        metrics.start_time = time.perf_counter()
        first_token = True
        
        debate_text = f"Topic: {topic}\n\n"
        for turn in debate_history:
            agent_name = "Agent A" if turn.agent == AgentRole.COMBATANT_A else "Agent B"
            debate_text += f"{agent_name}:\n{turn.content}\n\n"
        
        evaluation_prompt = f"""You are an impartial judge evaluating a debate between two agents.

{debate_text}

Please provide a comprehensive evaluation including:

1. **Summary of Arguments**: Briefly summarize each agent's main points
2. **Strengths and Weaknesses**: Analyze the strengths and weaknesses of each argument
3. **Logical Coherence**: Evaluate the logical consistency and reasoning
4. **Evidence and Support**: Assess the quality of evidence and examples used
5. **Persuasiveness**: Judge which argument was more compelling

Finally, provide your verdict with scores:
- Agent A Score: [1-10]
- Agent B Score: [1-10]
- Winner: [Agent A/Agent B/Tie]

Format your response with clear sections and provide detailed reasoning for your scores."""
        
        async with session.post(
            url=self.endpoint,
            headers=self.get_headers(),
            json={
                "model": self.model_id,
                "messages": [{"role": "user", "content": evaluation_prompt}],
                "stream": True,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1000
                }
            }
        ) as response:
            full_content = ""
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    # Ollama streams JSON directly without "data: " prefix
                    try:
                        data = json.loads(line_str)
                        # Ollama API format - each message contains a single token
                        if 'message' in data and not data.get('done', False):
                            message = data['message']
                            if 'content' in message:
                                token = message['content']
                                
                                if token:
                                    if first_token:
                                        metrics.ttft = time.perf_counter() - metrics.start_time
                                        first_token = False
                                    full_content += token
                                    metrics.total_tokens += 1
                                    
                                    current_time = time.perf_counter()
                                    elapsed = current_time - metrics.start_time
                                    if elapsed > 0:
                                        metrics.tps = metrics.total_tokens / elapsed
                                    
                                    yield token, metrics
                    except json.JSONDecodeError:
                        continue
            
            metrics.end_time = time.perf_counter()
            
            # Parse scores from the evaluation
            self._parse_scores(full_content)
    
    def _parse_scores(self, evaluation: str) -> Dict[str, any]:
        scores = {}
        try:
            if "Agent A Score:" in evaluation:
                score_a_start = evaluation.index("Agent A Score:") + len("Agent A Score:")
                score_a = int(evaluation[score_a_start:score_a_start+5].strip().split()[0])
                scores["agent_a_score"] = score_a
            
            if "Agent B Score:" in evaluation:
                score_b_start = evaluation.index("Agent B Score:") + len("Agent B Score:")
                score_b = int(evaluation[score_b_start:score_b_start+5].strip().split()[0])
                scores["agent_b_score"] = score_b
            
            if "Winner:" in evaluation:
                winner_start = evaluation.index("Winner:") + len("Winner:")
                winner_text = evaluation[winner_start:winner_start+20].strip().lower()
                if "agent a" in winner_text:
                    scores["winner"] = "agent_a"
                elif "agent b" in winner_text:
                    scores["winner"] = "agent_b"
                else:
                    scores["winner"] = "tie"
        except:
            scores = {"agent_a_score": 5, "agent_b_score": 5, "winner": "tie"}
        
        return scores


class DebateManager:
    def __init__(self, topic: str, combatant_a: DebateAgent, combatant_b: DebateAgent, judge: JudgeAgent):
        self.topic = topic
        self.combatant_a = combatant_a
        self.combatant_b = combatant_b
        self.judge = judge
        self.debate_history: List[DebateTurn] = []
        self.current_turn = 0
        self.max_turns = 3  # Each agent speaks 3 times
        self.debate_state = "not_started"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def start_debate(self):
        self.debate_state = "in_progress"
        self.current_turn = 0
    
    async def process_turn_stream(self, agent_role: AgentRole) -> AsyncGenerator[Dict[str, any], None]:
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        if agent_role == AgentRole.JUDGE:
            async for token, metrics in self.judge.evaluate_debate_stream(self.session, self.topic, self.debate_history):
                yield {
                    "type": "token_stream",
                    "agent": "judge",
                    "token": token,
                    "metrics": {
                        "tps": metrics.tps,
                        "ttft": metrics.ttft,
                        "total_tokens": metrics.total_tokens
                    }
                }
        else:
            agent = self.combatant_a if agent_role == AgentRole.COMBATANT_A else self.combatant_b
            opponent_agent = self.combatant_b if agent_role == AgentRole.COMBATANT_A else self.combatant_a
            
            # Get the last response from opponent if exists
            opponent_responses = [turn for turn in self.debate_history if 
                                 turn.agent == (AgentRole.COMBATANT_B if agent_role == AgentRole.COMBATANT_A else AgentRole.COMBATANT_A)]
            
            is_opening = len(opponent_responses) == 0
            opponent_response = opponent_responses[-1].content if opponent_responses else None
            
            prompt = agent.build_prompt(self.topic, opponent_response, is_opening)
            full_content = ""
            turn_metrics = DebateMetrics()
            
            async for token, metrics in agent.generate_response_stream(self.session, prompt):
                full_content += token
                turn_metrics = metrics
                yield {
                    "type": "token_stream",
                    "agent": "A" if agent_role == AgentRole.COMBATANT_A else "B",
                    "token": token,
                    "metrics": {
                        "tps": metrics.tps,
                        "ttft": metrics.ttft,
                        "total_tokens": metrics.total_tokens
                    }
                }
            
            # Save the turn to history
            self.debate_history.append(DebateTurn(
                agent=agent_role,
                content=full_content,
                metrics=turn_metrics,
                timestamp=datetime.now()
            ))
            
            self.current_turn += 1
            
            # Check if debate is complete
            if self.current_turn >= self.max_turns * 2:
                self.debate_state = "awaiting_judgment"
    
    def calculate_elo_update(self, winner: str, k_factor: int = 32) -> Tuple[float, float]:
        score_a = 1.0 if winner == "agent_a" else 0.5 if winner == "tie" else 0.0
        score_b = 1.0 - score_a
        
        expected_a = 1 / (1 + 10 ** ((self.combatant_b.elo_score - self.combatant_a.elo_score) / 400))
        expected_b = 1 - expected_a
        
        new_elo_a = self.combatant_a.elo_score + k_factor * (score_a - expected_a)
        new_elo_b = self.combatant_b.elo_score + k_factor * (score_b - expected_b)
        
        return new_elo_a, new_elo_b
    
    def get_debate_summary(self) -> Dict[str, any]:
        return {
            "topic": self.topic,
            "combatant_a": {
                "name": self.combatant_a.name,
                "model": self.combatant_a.model_id,
                "elo_score": self.combatant_a.elo_score
            },
            "combatant_b": {
                "name": self.combatant_b.name,
                "model": self.combatant_b.model_id,
                "elo_score": self.combatant_b.elo_score
            },
            "turns": len(self.debate_history),
            "state": self.debate_state,
            "history": [
                {
                    "agent": turn.agent.value,
                    "content": turn.content,
                    "timestamp": turn.timestamp.isoformat(),
                    "metrics": {
                        "ttft": turn.metrics.ttft,
                        "tps": turn.metrics.tps,
                        "total_tokens": turn.metrics.total_tokens
                    }
                } for turn in self.debate_history
            ]
        }