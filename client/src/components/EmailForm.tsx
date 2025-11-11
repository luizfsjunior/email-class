/**
 * EmailForm Component - Formulário principal para upload/texto
 * Permite upload de arquivo .txt/.pdf ou colar texto direto
 */

import React, { useState, useRef } from 'react';
import { apiService } from '../services/api';

interface EmailFormProps {
  onResult: (result: any) => void;
  onError: (error: string) => void;
}

export const EmailForm: React.FC<EmailFormProps> = ({ onResult, onError }) => {
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    
    if (!selectedFile) return;

    // Valida extensão
    const validExtensions = ['.txt', '.pdf'];
    const fileExtension = selectedFile.name.toLowerCase().match(/\.[^.]+$/)?.[0];
    
    if (!fileExtension || !validExtensions.includes(fileExtension)) {
      onError('Apenas arquivos .txt ou .pdf são aceitos');
      return;
    }

    // Valida tamanho (1MB)
    if (selectedFile.size > 1048576) {
      onError('Arquivo muito grande (máximo 1MB)');
      return;
    }

    setFile(selectedFile);
    setText(''); // Limpa texto se arquivo foi selecionado
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file && !text.trim()) {
      onError('Envie um arquivo ou cole o texto do email');
      return;
    }

    if (text.trim() && text.length < 10) {
      onError('Texto muito curto (mínimo 10 caracteres)');
      return;
    }

    setIsProcessing(true);

    try {
      let result;
      
      if (file) {
        result = await apiService.processFile(file);
      } else {
        result = await apiService.processText(text);
      }

      onResult(result);
      
      // Limpa form após sucesso
      setText('');
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

    } catch (err) {
      onError(err instanceof Error ? err.message : 'Erro ao processar email');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClear = () => {
    setText('');
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload de arquivo (.txt ou .pdf)
        </label>
        <div className="flex items-center gap-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf"
            onChange={handleFileChange}
            disabled={isProcessing}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100
              disabled:opacity-50"
          />
          {file && (
            <span className="text-sm text-green-600 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
              </svg>
              {file.name}
            </span>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">OU</span>
        </div>
      </div>

      {/* Text Area */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cole o texto do email
        </label>
        <textarea
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            if (e.target.value) setFile(null); // Limpa arquivo se texto foi digitado
          }}
          disabled={isProcessing || !!file}
          placeholder="Cole aqui o conteúdo do email..."
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
            focus:ring-blue-500 focus:border-blue-500
            disabled:bg-gray-100 disabled:text-gray-500"
        />
        <p className="mt-1 text-sm text-gray-500">
          {text.length} caracteres
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isProcessing || (!file && !text.trim())}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md
            hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
            disabled:bg-gray-300 disabled:cursor-not-allowed
            font-medium transition-colors"
        >
          {isProcessing ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Processando...
            </span>
          ) : (
            'Processar Email'
          )}
        </button>
        
        <button
          type="button"
          onClick={handleClear}
          disabled={isProcessing}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700
            hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Limpar
        </button>
      </div>
    </form>
  );
};
