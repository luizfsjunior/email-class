/**
 * App.tsx - Aplicação principal do Email Classifier
 * SPA React + TypeScript + Tailwind para classificação de emails
 */

import { useState, useEffect } from 'react';
import { EmailForm } from './components/EmailForm';
import { ResultDisplay } from './components/ResultDisplay';
import { History } from './components/History';
import { apiService, ProcessResponse, HealthResponse } from './services/api';
import { historyStorage, HistoryItem } from './lib/storage';

function App() {
  const [result, setResult] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [healthStatus, setHealthStatus] = useState<HealthResponse | null>(null);

  // Carrega histórico e health status na inicialização
  useEffect(() => {
    setHistory(historyStorage.getHistory());
    
    // Check health
    apiService.checkHealth()
      .then(setHealthStatus)
      .catch(() => setHealthStatus(null));
  }, []);

  const handleResult = (newResult: ProcessResponse) => {
    // DEBUG: Log da resposta da API
    console.log('📥 RESPOSTA DA API:', {
      categoria: newResult.category,
      confianca: newResult.confidence,
      razao: newResult.reason,
      model: newResult.model_used,
      id: newResult.id
    });
    
    setResult(newResult);
    setError('');

    // Adiciona ao histórico
    const historyItem: HistoryItem = {
      id: newResult.id,
      category: newResult.category,
      confidence: newResult.confidence,
      summary: newResult.summary,
      timestamp: newResult.timestamp,
    };

    historyStorage.addItem(historyItem);
    setHistory(historyStorage.getHistory());
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setResult(null);
  };

  const handleFeedback = async (feedback: { analysis_id: string; edited_reply?: string; rating?: number }) => {
    try {
      await apiService.submitFeedback(feedback);
      // Poderia mostrar toast de sucesso aqui
    } catch (err) {
      console.error('Erro ao enviar feedback:', err);
    }
  };

  const handleClearHistory = () => {
    historyStorage.clearHistory();
    setHistory([]);
  };

  const handleRemoveHistoryItem = (id: string) => {
    historyStorage.removeItem(id);
    setHistory(historyStorage.getHistory());
  };

  const handleNewAnalysis = () => {
    setResult(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 text-white w-10 h-10 rounded-lg flex items-center justify-center font-bold">
                📧
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Email Classifier
                </h1>
                <p className="text-sm text-gray-500">
                  Classifica emails e sugere respostas
                </p>
              </div>
            </div>

            {/* Health status indicator */}
            {healthStatus && (
              <div className="flex items-center gap-2 text-xs">
                <div className={`w-2 h-2 rounded-full ${
                  healthStatus.status === 'healthy' ? 'bg-green-500' :
                  healthStatus.status === 'degraded' ? 'bg-yellow-500' :
                  'bg-red-500'
                }`} />
                <span className="text-gray-600">
                  {healthStatus.openai_configured ? 'OpenAI ativo' : 'OpenAI não configurado'}
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Form and Result */}
          <div className="lg:col-span-2 space-y-6">
            {/* Form Card */}
            {!result && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Analisar Email
                </h2>
                <EmailForm onResult={handleResult} onError={handleError} />
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div className="ml-3">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Result Display */}
            {result && (
              <>
                <ResultDisplay result={result} onFeedback={handleFeedback} />
                
                <button
                  onClick={handleNewAnalysis}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg
                    hover:bg-blue-700 font-medium transition-colors"
                >
                  Nova Análise
                </button>
              </>
            )}
          </div>

          {/* Right Column - History */}
          <div className="lg:col-span-1">
            <History
              items={history}
              onClear={handleClearHistory}
              onRemove={handleRemoveHistoryItem}
            />

            {/* Info Card */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">
                ℹ️ Como funciona
              </h3>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• <strong>Produtivo:</strong> Email requer ação/resposta</li>
                <li>• <strong>Improdutivo:</strong> Email informativo/dispensável</li>
                <li>• Confiança indica certeza da classificação</li>
                <li>• Você pode editar a resposta antes de usar</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-sm text-gray-500">
        <p>Email Classifier MVP • Powered by FastAPI + React + OpenAI</p>
      </footer>
    </div>
  );
}

export default App;
