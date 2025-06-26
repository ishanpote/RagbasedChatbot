import { useState, useCallback } from 'react';
import { Message, ChatState, UploadState } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const useChat = () => {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    isThinking: false,
    vectorName: '',
    isVectorConfigured: false,
  });

  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    uploadProgress: 0,
    error: null,
  });

  const [isConnecting, setIsConnecting] = useState(false);

  const connectToDatabase = useCallback(async (vectorName: string) => {
    setIsConnecting(true);
    setUploadState(prev => ({ ...prev, error: null }));

    try {
      // Check if the vector database exists by making a test query
      const response = await fetch(`${API_BASE_URL}/chat?vector_name=${encodeURIComponent(vectorName)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: 'test connection' }),
      });

      if (response.ok) {
        setChatState(prev => ({
          ...prev,
          vectorName,
          isVectorConfigured: true,
          messages: [],
        }));
      } else if (response.status === 404) {
        setUploadState(prev => ({
          ...prev,
          error: 'Vector database not found. Please check the name or upload a new resume.',
        }));
      } else {
        throw new Error(`Connection failed: ${response.statusText}`);
      }
    } catch (error) {
      setUploadState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to connect to database',
      }));
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const uploadDocument = useCallback(async (file: File, vectorName: string) => {
    setUploadState({
      isUploading: true,
      uploadProgress: 0,
      error: null,
    });

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('vector_name', vectorName);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadState(prev => ({
          ...prev,
          uploadProgress: Math.min(prev.uploadProgress + 10, 90),
        }));
      }, 200);

      const response = await fetch(`${API_BASE_URL}/ingest`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      setUploadState({
        isUploading: false,
        uploadProgress: 100,
        error: null,
      });

      setChatState(prev => ({
        ...prev,
        vectorName,
        isVectorConfigured: true,
        messages: [],
      }));

      // Reset upload progress after a delay
      setTimeout(() => {
        setUploadState(prev => ({ ...prev, uploadProgress: 0 }));
      }, 2000);

    } catch (error) {
      setUploadState({
        isUploading: false,
        uploadProgress: 0,
        error: error instanceof Error ? error.message : 'Upload failed',
      });
    }
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!chatState.vectorName || chatState.isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date(),
    };

    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      isThinking: true,
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/chat?vector_name=${encodeURIComponent(chatState.vectorName)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: content }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || 'I apologize, but I could not process your request.',
        isUser: false,
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, botMessage],
        isLoading: false,
        isThinking: false,
      }));

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        isUser: false,
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false,
        isThinking: false,
      }));
    }
  }, [chatState.vectorName, chatState.isLoading]);

  const clearChat = useCallback(() => {
    setChatState(prev => ({
      ...prev,
      messages: [],
    }));
  }, []);

  const setVectorName = useCallback((name: string) => {
    setChatState(prev => ({
      ...prev,
      vectorName: name,
      isVectorConfigured: false,
    }));
    setUploadState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    chatState,
    uploadState,
    isConnecting,
    uploadDocument,
    connectToDatabase,
    sendMessage,
    clearChat,
    setVectorName,
  };
};