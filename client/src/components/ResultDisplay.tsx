/**
 * ResultDisplay Component - Exibe resultado da classificação
 * Permite editar resposta sugerida antes de copiar
 */

import React, { useState } from 'react';
import { ProcessResponse } from '../services/api';

interface ResultDisplayProps {
  result: ProcessResponse;
  onFeedback?: (feedback: { analysis_id: string; edited_reply?: string; rating?: number }) => void;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onFeedback }) => {
  const [editedReply, setEditedReply] = useState(result.suggested_reply);
  const [showFeedback, setShowFeedback] = useState(false);
  const [rating, setRating] = useState<number>(0);
  const [copied, setCopied] = useState(false);

  const categoryColor = result.category === 'Produtivo' 
    ? 'bg-green-100 text-green-800 border-green-200'
    : 'bg-gray-100 text-gray-800 border-gray-200';

  const confidenceColor = result.confidence >= 0.8
    ? 'text-green-600'
    : result.confidence >= 0.6
    ? 'text-yellow-600'
    : 'text-red-600';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editedReply);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  const handleSubmitFeedback = () => {
    if (onFeedback) {
      onFeedback({
        analysis_id: result.id,
        edited_reply: editedReply !== result.suggested_reply ? editedReply : undefined,
        rating: rating || undefined,
      });
    }
    setShowFeedback(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${categoryColor}`}>
              {result.category}
            </span>
            <span className={`text-sm font-medium ${confidenceColor}`}>
              {(result.confidence * 100).toFixed(0)}% confiança
            </span>
          </div>
          
          <p className="text-xs text-gray-500">
            Modelo: {result.model_used} • ID: {result.id.slice(0, 8)}...
          </p>
        </div>

        {/* Close button could go here */}
      </div>

      {/* Summary */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Resumo</h3>
        <p className="text-gray-600 bg-gray-50 p-3 rounded-md text-sm">
          {result.summary}
        </p>
      </div>

      {/* Reason (if available) */}
      {result.reason && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Justificativa</h3>
          <p className="text-gray-600 text-sm italic">
            {result.reason}
          </p>
        </div>
      )}

      {/* Suggested Reply */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-700">Resposta Sugerida</h3>
          <button
            onClick={handleCopy}
            className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            {copied ? (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                </svg>
                Copiado!
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copiar
              </>
            )}
          </button>
        </div>
        
        <textarea
          value={editedReply}
          onChange={(e) => setEditedReply(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm
            focus:ring-blue-500 focus:border-blue-500 text-sm"
        />
        
        {editedReply !== result.suggested_reply && (
          <p className="mt-1 text-xs text-amber-600">
            ✏️ Resposta editada (original será salva ao enviar feedback)
          </p>
        )}
      </div>

      {/* Feedback Section */}
      <div className="border-t pt-4">
        {!showFeedback ? (
          <button
            onClick={() => setShowFeedback(true)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            📝 Avaliar resultado
          </button>
        ) : (
          <div className="space-y-3">
            <p className="text-sm font-medium text-gray-700">Como foi o resultado?</p>
            
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className={`text-2xl ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
                >
                  ★
                </button>
              ))}
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleSubmitFeedback}
                disabled={rating === 0}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md
                  hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Enviar Avaliação
              </button>
              <button
                onClick={() => setShowFeedback(false)}
                className="px-4 py-2 border border-gray-300 text-sm rounded-md
                  hover:bg-gray-50"
              >
                Cancelar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
