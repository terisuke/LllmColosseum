'use client';

import { useEffect } from 'react';
import { ControlPanel } from './components/ControlPanel';
import { ArenaView } from './components/ArenaView';
import { useWebSocket } from './hooks/useWebSocket';
import { useArenaStore } from './stores/arenaStore';
import { Swords } from 'lucide-react';

export default function Home() {
  const {
    setConnected,
    startDebate,
    endDebate,
    appendAgentOutput,
    setCurrentSpeaker,
    updateAgentMetrics,
    clearAgentOutput,
  } = useArenaStore();

  const { isConnected, sendMessage, error } = useWebSocket({
    url: 'ws://localhost:8000/ws/arena',
    onMessage: (message: any) => {
      console.log('Received message:', message);
      
      // token_stream メッセージの処理
      if (message.type === 'token_stream') {
        const agentMap: any = {
          'combatant_a': 'A',
          'combatant_b': 'B', 
          'judge': 'judge'
        };
        const mappedAgent = agentMap[message.agent] || message.agent;
        appendAgentOutput(mappedAgent, message.token);
        
        if (message.metrics) {
          updateAgentMetrics(mappedAgent, {
            tps: message.metrics.tps || 0,
            ttft: message.metrics.ttft,
            totalTokens: message.metrics.total_tokens || 0
          });
        }
      }
      
      // turn_start メッセージの処理
      else if (message.type === 'turn_start') {
        const agentMap: any = {
          'combatant_a': 'A',
          'combatant_b': 'B',
          'judge': 'judge'
        };
        const mappedAgent = agentMap[message.agent] || message.agent;
        setCurrentSpeaker(mappedAgent);
        clearAgentOutput(mappedAgent);
      }
      
      // debate_started メッセージの処理
      else if (message.type === 'debate_started') {
        startDebate();
      }
      
      // debate_end メッセージの処理
      else if (message.type === 'debate_end') {
        endDebate();
      }
    },
    onOpen: () => {
      console.log('WebSocket connected');
      setConnected(true);
    },
    onClose: () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      endDebate();
    },
    onError: (err) => {
      console.error('WebSocket error:', err);
      setConnected(false);
      endDebate();
    },
  });

  const handleStartDebate = (topic: string, roles: any) => {
    const startMessage = {
      action: 'start_debate',
      topic,
      roles,
    };
    
    sendMessage(startMessage);
    startDebate();
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="bg-gray-900 border-b border-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <Swords className="w-8 h-8 text-purple-500" />
            <h1 className="text-2xl font-bold">LLM Debate Arena</h1>
            <span className="text-sm text-gray-400">v1.0.0</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <ControlPanel onStartDebate={handleStartDebate} />
            {error && (
              <div className="mt-4 bg-red-900/20 border border-red-500 rounded-lg p-3">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
          </div>
          <div className="lg:col-span-3">
            <ArenaView />
          </div>
        </div>
      </div>
    </div>
  );
}