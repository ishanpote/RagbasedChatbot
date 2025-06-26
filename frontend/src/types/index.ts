export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  isThinking: boolean;
  vectorName: string;
  isVectorConfigured: boolean;
}

export interface UploadState {
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
}