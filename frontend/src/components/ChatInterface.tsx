import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Trash2 } from 'lucide-react';
import { Message } from './Message';
import { TypingIndicator } from './TypingIndicator';
import { Message as MessageType } from '../types';

interface ChatInterfaceProps {
  messages: MessageType[];
  onSendMessage: (message: string) => void;
  onClearChat: () => void;
  isLoading: boolean;
  isThinking: boolean;
  vectorName: string;
  isVectorConfigured: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onClearChat,
  isLoading,
  isThinking,
  vectorName,
  isVectorConfigured
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showClearConfirmation, setShowClearConfirmation] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading && isVectorConfigured) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleClearChat = () => {
    if (showClearConfirmation) {
      onClearChat();
      setShowClearConfirmation(false);
    } else {
      setShowClearConfirmation(true);
      setTimeout(() => setShowClearConfirmation(false), 3000);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Resume Chat Assistant</h3>
          {isVectorConfigured && (
            <p className="text-sm text-gray-600">Connected to: {vectorName}</p>
          )}
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200 ${
              showClearConfirmation
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {showClearConfirmation ? 'Confirm Clear' : <Trash2 size={16} />}
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!isVectorConfigured ? (
          <div className="text-center text-gray-500 mt-20">
            <p className="text-lg font-medium">Welcome to Resume AI Assistant</p>
            <p className="text-sm mt-2">Please upload a resume to get started</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-20">
            <p className="text-lg font-medium">Ready to chat!</p>
            <p className="text-sm mt-2">Ask me anything about the uploaded resume</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <Message
              key={message.id}
              message={message}
              isLatest={index === messages.length - 1}
            />
          ))
        )}
        {isThinking && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={
                isVectorConfigured
                  ? "Ask a question about the resume..."
                  : "Upload a resume first to start chatting"
              }
              disabled={!isVectorConfigured || isLoading}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-colors pr-12"
            />
            <button
              type="button"
              onClick={toggleVoiceInput}
              disabled={!isVectorConfigured || isLoading}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full transition-colors ${
                isListening
                  ? 'text-red-500 hover:bg-red-50'
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isListening ? <MicOff size={16} /> : <Mic size={16} />}
            </button>
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || !isVectorConfigured || isLoading}
            className="px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow-md"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
};