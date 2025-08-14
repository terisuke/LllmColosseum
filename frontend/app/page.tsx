'use client';

import { useState, useRef } from 'react';
import { ControlPanel } from './components/ControlPanel';
import { ArenaView } from './components/ArenaView';
import { useWebSocket, WebSocketMessage } from './hooks/useWebSocket';
import { Swords } from 'lucide-react';

export default function Home() {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isDebating, setIsDebating] = useState(false);
  const [currentTopic, setCurrentTopic] = useState('');
  const [currentRoles, setCurrentRoles] = useState({
    combatant_a: '',
    combatant_b: '',
    judge: '',
  });
  const messagesRef = useRef<WebSocketMessage[]>([]);

  const { isConnected, sendMessage, error } = useWebSocket({
    url: 'ws://localhost:8000/ws/arena',
    onMessage: (message) => {
      console.log('Received message:', message);
      messagesRef.current = [...messagesRef.current, message];
      setMessages([...messagesRef.current]);

      // Handle debate status changes
      if (message.action === 'debate_started') {
        setIsDebating(true);
      } else if (message.action === 'debate_completed') {
        setIsDebating(false);
      }
    },
    onOpen: () => {
      console.log('WebSocket connected');
    },
    onClose: () => {
      console.log('WebSocket disconnected');
      setIsDebating(false);
    },
    onError: (err) => {
      console.error('WebSocket error:', err);
      setIsDebating(false);
    },
  });

  const handleStartDebate = (topic: string, roles: typeof currentRoles) => {
    // Clear previous messages
    messagesRef.current = [];
    setMessages([]);
    
    // Set current debate configuration
    setCurrentTopic(topic);
    setCurrentRoles(roles);
    
    // Send start message to WebSocket
    const startMessage: WebSocketMessage = {
      action: 'start_debate',
      topic,
      roles,
    };
    
    sendMessage(startMessage);
    setIsDebating(true);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <Swords className="w-8 h-8 text-purple-500" />
            <h1 className="text-2xl font-bold">LLM Debate Arena</h1>
            <span className="text-sm text-gray-400">v1.0.0</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Control Panel - Left Sidebar */}
          <div className="lg:col-span-1">
            <ControlPanel
              onStartDebate={handleStartDebate}
              isConnected={isConnected}
              isDebating={isDebating}
            />
            
            {/* Connection Error Display */}
            {error && (
              <div className="mt-4 bg-red-900/20 border border-red-500 rounded-lg p-3">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
          </div>

          {/* Arena View - Main Content */}
          <div className="lg:col-span-3">
            <ArenaView
              messages={messages}
              currentRoles={currentRoles}
              topic={currentTopic}
              isDebating={isDebating}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-auto border-t border-gray-800 bg-gray-900">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>© 2024 LLM Debate Arena</span>
            <div className="flex items-center space-x-4">
              <span>Powered by Ollama</span>
              <span>•</span>
              <span>Built with Next.js & FastAPI</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}