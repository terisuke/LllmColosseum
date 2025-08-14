'use client';

import { useEffect, useRef, useState } from 'react';
import { User, Zap, Clock, Hash } from 'lucide-react';

interface AgentStreamProps {
  agentId: string;
  agentName: string;
  role: 'pro' | 'con' | 'judge';
  isActive: boolean;
}

interface StreamContent {
  text: string;
  metrics: {
    tokensPerSecond: number;
    totalTokens: number;
    timeElapsed: number;
  };
}

export const AgentStream = ({ agentId, agentName, role, isActive }: AgentStreamProps) => {
  const [content, setContent] = useState<StreamContent>({
    text: '',
    metrics: {
      tokensPerSecond: 0,
      totalTokens: 0,
      timeElapsed: 0,
    },
  });
  const contentRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new content arrives
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [content.text]);

  // Handle incoming tokens from WebSocket
  const handleToken = (token: string) => {
    setContent((prev) => ({
      ...prev,
      text: prev.text + token,
    }));
  };

  // Handle metrics update
  const handleMetrics = (metrics: StreamContent['metrics']) => {
    setContent((prev) => ({
      ...prev,
      metrics,
    }));
  };

  // Clear content when debate starts
  const clearContent = () => {
    setContent({
      text: '',
      metrics: {
        tokensPerSecond: 0,
        totalTokens: 0,
        timeElapsed: 0,
      },
    });
  };

  // Expose methods for parent component
  useEffect(() => {
    // Store methods in window for parent component access
    const methods = {
      handleToken,
      handleMetrics,
      clearContent,
    };
    (window as any)[`agentStream_${agentId}`] = methods;

    return () => {
      delete (window as any)[`agentStream_${agentId}`];
    };
  }, [agentId]);

  const getRoleColor = () => {
    switch (role) {
      case 'pro':
        return 'border-green-500 bg-green-950/20';
      case 'con':
        return 'border-red-500 bg-red-950/20';
      case 'judge':
        return 'border-blue-500 bg-blue-950/20';
      default:
        return 'border-gray-500 bg-gray-950/20';
    }
  };

  const getRoleLabel = () => {
    switch (role) {
      case 'pro':
        return 'PRO';
      case 'con':
        return 'CON';
      case 'judge':
        return 'JUDGE';
      default:
        return '';
    }
  };

  return (
    <div className={`flex flex-col h-full border rounded-lg ${getRoleColor()} transition-all duration-300`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <User className="w-5 h-5 text-gray-400" />
          <div>
            <h3 className="font-semibold text-white">{agentName}</h3>
            <span className={`text-xs px-2 py-1 rounded ${
              role === 'pro' ? 'bg-green-500/20 text-green-400' :
              role === 'con' ? 'bg-red-500/20 text-red-400' :
              'bg-blue-500/20 text-blue-400'
            }`}>
              {getRoleLabel()}
            </span>
          </div>
        </div>
        {isActive && (
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs text-green-400">Active</span>
          </div>
        )}
      </div>

      {/* Content Area */}
      <div 
        ref={contentRef}
        className="flex-1 overflow-y-auto p-4 font-mono text-sm text-gray-300"
        style={{ minHeight: '200px', maxHeight: '400px' }}
      >
        {content.text ? (
          <div className="whitespace-pre-wrap">{content.text}</div>
        ) : (
          <div className="text-gray-500 italic">Waiting for response...</div>
        )}
      </div>

      {/* Metrics Footer */}
      <div className="p-3 border-t border-gray-700 bg-black/30">
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="flex items-center space-x-1">
            <Zap className="w-3 h-3 text-yellow-400" />
            <span className="text-gray-400">Speed:</span>
            <span className="text-white font-semibold">
              {content.metrics.tokensPerSecond.toFixed(1)} t/s
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <Hash className="w-3 h-3 text-cyan-400" />
            <span className="text-gray-400">Tokens:</span>
            <span className="text-white font-semibold">
              {content.metrics.totalTokens}
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-purple-400" />
            <span className="text-gray-400">Time:</span>
            <span className="text-white font-semibold">
              {content.metrics.timeElapsed.toFixed(1)}s
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};