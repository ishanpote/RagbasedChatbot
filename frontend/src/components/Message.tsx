import React, { useState, useEffect } from 'react';
import { Avatar } from './Avatar';
import { Message as MessageType } from '../types';

interface MessageProps {
  message: MessageType;
  isLatest?: boolean;
}

export const Message: React.FC<MessageProps> = ({ message, isLatest = false }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!message.isUser && isLatest) {
      setIsTyping(true);
      setDisplayedText('');
      
      let currentIndex = 0;
      const typeText = () => {
        if (currentIndex < message.content.length) {
          setDisplayedText(message.content.slice(0, currentIndex + 1));
          currentIndex++;
          setTimeout(typeText, 30);
        } else {
          setIsTyping(false);
        }
      };
      
      setTimeout(typeText, 500);
    } else {
      setDisplayedText(message.content);
      setIsTyping(false);
    }
  }, [message.content, message.isUser, isLatest]);

  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div className={`flex max-w-[80%] ${message.isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <Avatar isUser={message.isUser} className={message.isUser ? 'ml-3' : 'mr-3'} />
        <div
          className={`px-4 py-3 rounded-2xl shadow-sm ${
            message.isUser
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-br-md'
              : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md'
          }`}
        >
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {displayedText}
            {isTyping && (
              <span className="inline-block w-2 h-4 bg-current ml-1 animate-pulse">|</span>
            )}
          </div>
          <div className={`text-xs mt-2 opacity-70 ${message.isUser ? 'text-blue-100' : 'text-gray-500'}`}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
};