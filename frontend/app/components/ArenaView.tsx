'use client';

import { useState, useEffect, useRef } from 'react';
import { AgentStream } from './AgentStream';
import { Trophy, MessageSquare, AlertCircle } from 'lucide-react';
import { WebSocketMessage } from '../hooks/useWebSocket';

interface ArenaViewProps {
  messages: WebSocketMessage[];
  currentRoles: {
    combatant_a: string;
    combatant_b: string;
    judge: string;
  };
  topic: string;
  isDebating: boolean;
}

interface DebateHistory {
  round: number;
  phase: string;
  combatantA: string;
  combatantB: string;
  judgeEvaluation?: string;
  winner?: string;
}

export const ArenaView = ({ messages, currentRoles, topic, isDebating }: ArenaViewProps) => {
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [currentPhase, setCurrentPhase] = useState('');
  const [debateHistory, setDebateHistory] = useState<DebateHistory[]>([]);
  
  const agentRefs = useRef<{ [key: string]: any }>({});

  useEffect(() => {
    // Process incoming WebSocket messages
    messages.forEach((msg) => {
      if (msg.action === 'debate_started') {
        // Clear all agent streams
        Object.keys(agentRefs.current).forEach((agentId) => {
          const agent = (window as any)[`agentStream_${agentId}`];
          if (agent?.clearContent) {
            agent.clearContent();
          }
        });
        setDebateHistory([]);
        setCurrentRound(1);
        setCurrentPhase('opening');
      }
      
      if (msg.agent_id) {
        setActiveAgent(msg.agent_id);
        
        // Handle token streaming
        if (msg.token) {
          const agent = (window as any)[`agentStream_${msg.agent_id}`];
          if (agent?.handleToken) {
            agent.handleToken(msg.token);
          }
        }
        
        // Handle metrics update
        if (msg.metrics) {
          const agent = (window as any)[`agentStream_${msg.agent_id}`];
          if (agent?.handleMetrics) {
            agent.handleMetrics({
              tokensPerSecond: msg.metrics.tokens_per_second || 0,
              totalTokens: msg.metrics.total_tokens || 0,
              timeElapsed: msg.metrics.time_elapsed || 0,
            });
          }
        }
      }
      
      // Update round and phase
      if (msg.round !== undefined) {
        setCurrentRound(msg.round);
      }
      if (msg.phase) {
        setCurrentPhase(msg.phase);
      }
      
      // Handle debate completion
      if (msg.action === 'debate_completed') {
        setActiveAgent(null);
      }
    });
  }, [messages]);

  const getPhaseLabel = (phase: string) => {
    const labels: { [key: string]: string } = {
      opening: 'Opening Statements',
      rebuttal: 'Rebuttals',
      closing: 'Closing Arguments',
      judging: 'Judge Evaluation',
    };
    return labels[phase] || phase;
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Header */}
      <div className="bg-gray-900 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Trophy className="w-6 h-6 text-yellow-400" />
            <span>Debate Arena</span>
          </h2>
          {isDebating && (
            <div className="flex items-center space-x-3 text-sm">
              <span className="text-gray-400">Round:</span>
              <span className="text-white font-semibold">{currentRound}</span>
              <span className="text-gray-400">|</span>
              <span className="text-gray-400">Phase:</span>
              <span className="text-white font-semibold">{getPhaseLabel(currentPhase)}</span>
            </div>
          )}
        </div>
        
        {topic && (
          <div className="bg-gray-800 rounded p-3 mt-3">
            <div className="flex items-start space-x-2">
              <MessageSquare className="w-5 h-5 text-blue-400 mt-0.5" />
              <div>
                <p className="text-xs text-gray-400 mb-1">Debate Topic:</p>
                <p className="text-white font-medium">{topic}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Three-Column Layout */}
      <div className="flex-1 grid grid-cols-3 gap-4">
        {/* Combatant A (Pro) */}
        <div className="flex flex-col">
          <AgentStream
            agentId="combatant_a"
            agentName={currentRoles.combatant_a || 'Combatant A'}
            role="pro"
            isActive={activeAgent === 'combatant_a'}
          />
        </div>

        {/* Judge */}
        <div className="flex flex-col">
          <AgentStream
            agentId="judge"
            agentName={currentRoles.judge || 'Judge'}
            role="judge"
            isActive={activeAgent === 'judge'}
          />
        </div>

        {/* Combatant B (Con) */}
        <div className="flex flex-col">
          <AgentStream
            agentId="combatant_b"
            agentName={currentRoles.combatant_b || 'Combatant B'}
            role="con"
            isActive={activeAgent === 'combatant_b'}
          />
        </div>
      </div>

      {/* Status Bar */}
      {!isDebating && !topic && (
        <div className="bg-gray-800 rounded-lg p-4 flex items-center justify-center space-x-2 text-gray-400">
          <AlertCircle className="w-5 h-5" />
          <span>Configure the debate settings and click "Start Debate" to begin</span>
        </div>
      )}
    </div>
  );
};