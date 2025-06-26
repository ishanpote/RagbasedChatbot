import React from 'react';
import { Brain, Sparkles } from 'lucide-react';
import { FileUpload } from './components/FileUpload';
import { ChatInterface } from './components/ChatInterface';
import { useChat } from './hooks/useChat';

function App() {
  const {
    chatState,
    uploadState,
    isConnecting,
    uploadDocument,
    connectToDatabase,
    sendMessage,
    clearChat,
    setVectorName,
  } = useChat();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/70 backdrop-blur-sm border-b border-white/20 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1">
                <Sparkles className="w-4 h-4 text-yellow-400 animate-pulse" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Resume AI Assistant
              </h1>
              <p className="text-sm text-gray-600">
                Connect to existing databases or upload new resumes
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <FileUpload
              onUpload={uploadDocument}
              onConnect={connectToDatabase}
              vectorName={chatState.vectorName}
              onVectorNameChange={setVectorName}
              uploadState={uploadState}
              isConnecting={isConnecting}
            />
            
            {/* Status Card */}
            <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-white/20 p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Status</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Vector Database</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    chatState.isVectorConfigured
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-500'
                  }`}>
                    {chatState.isVectorConfigured ? 'Connected' : 'Not Connected'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Messages</span>
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                    {chatState.messages.length}
                  </span>
                </div>
                {chatState.isVectorConfigured && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Database Name</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700 font-mono">
                      {chatState.vectorName}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chat Section */}
          <div>
            <ChatInterface
              messages={chatState.messages}
              onSendMessage={sendMessage}
              onClearChat={clearChat}
              isLoading={chatState.isLoading}
              isThinking={chatState.isThinking}
              vectorName={chatState.vectorName}
              isVectorConfigured={chatState.isVectorConfigured}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white/30 backdrop-blur-sm border-t border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Powered by AI • Connect to existing databases or upload new resumes
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;