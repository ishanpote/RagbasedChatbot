import React, { useCallback, useState } from 'react';
import { Upload, File, CheckCircle2, AlertCircle, Database } from 'lucide-react';
import { UploadState } from '../types';

interface FileUploadProps {
  onUpload: (file: File, vectorName: string) => Promise<void>;
  onConnect: (vectorName: string) => Promise<void>;
  vectorName: string;
  onVectorNameChange: (name: string) => void;
  uploadState: UploadState;
  isConnecting: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  onConnect,
  vectorName,
  onVectorNameChange,
  uploadState,
  isConnecting
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        setSelectedFile(file);
      }
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  }, []);

  const handleUpload = useCallback(async () => {
    if (selectedFile && vectorName.trim()) {
      await onUpload(selectedFile, vectorName.trim());
      setSelectedFile(null);
    }
  }, [selectedFile, vectorName, onUpload]);

  const handleConnect = useCallback(async () => {
    if (vectorName.trim()) {
      await onConnect(vectorName.trim());
    }
  }, [vectorName, onConnect]);

  return (
    <div className="bg-white/60 backdrop-blur-sm rounded-xl border border-white/20 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Resume Database</h3>
      
      <div className="mb-4">
        <label htmlFor="vectorName" className="block text-sm font-medium text-gray-700 mb-2">
          Vector Database Name
        </label>
        <div className="flex space-x-2">
          <input
            type="text"
            id="vectorName"
            value={vectorName}
            onChange={(e) => onVectorNameChange(e.target.value)}
            placeholder="Enter database name"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          />
          <button
            onClick={handleConnect}
            disabled={!vectorName.trim() || isConnecting || uploadState.isUploading}
            className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-medium hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow-md flex items-center space-x-2"
          >
            <Database size={16} />
            <span>{isConnecting ? 'Connecting...' : 'Connect'}</span>
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Connect to an existing database or upload a new resume below
        </p>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">or upload new resume</span>
        </div>
      </div>

      <div
        className={`mt-4 relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : uploadState.error
            ? 'border-red-300 bg-red-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".txt"
          onChange={handleFileSelect}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploadState.isUploading || isConnecting}
        />
        
        <div className="flex flex-col items-center">
          {selectedFile ? (
            <>
              <File className="w-12 h-12 text-green-500 mb-2" />
              <p className="text-sm font-medium text-green-700">{selectedFile.name}</p>
              <p className="text-xs text-gray-500">Ready to upload</p>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400 mb-2" />
              <p className="text-sm font-medium text-gray-700">Drop your resume here or click to browse</p>
              <p className="text-xs text-gray-500">Supports .txt files only</p>
            </>
          )}
        </div>

        {uploadState.isUploading && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadState.uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-600 mt-1">Uploading... {uploadState.uploadProgress}%</p>
          </div>
        )}

        {uploadState.error && (
          <div className="mt-4 flex items-center justify-center text-red-600">
            <AlertCircle size={16} className="mr-1" />
            <span className="text-sm">{uploadState.error}</span>
          </div>
        )}
      </div>

      <button
        onClick={handleUpload}
        disabled={!selectedFile || !vectorName.trim() || uploadState.isUploading || isConnecting}
        className="w-full mt-4 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow-md"
      >
        {uploadState.isUploading ? 'Uploading...' : 'Upload New Resume'}
      </button>
    </div>
  );
};