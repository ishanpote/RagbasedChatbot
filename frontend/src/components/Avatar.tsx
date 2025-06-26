import React from 'react';
import { Bot, User } from 'lucide-react';

interface AvatarProps {
  isUser: boolean;
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({ isUser, className = '' }) => {
  return (
    <div className={`flex-shrink-0 ${className}`}>
      {isUser ? (
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
          <User size={16} className="text-white" />
        </div>
      ) : (
        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg">
          <Bot size={16} className="text-white" />
        </div>
      )}
    </div>
  );
};