/**
 * History Component - Exibe histórico de análises recentes
 * Armazenado em localStorage
 */

import React from 'react';
import { HistoryItem } from '../lib/storage';

interface HistoryProps {
  items: HistoryItem[];
  onClear: () => void;
  onRemove: (id: string) => void;
}

export const History: React.FC<HistoryProps> = ({ items, onClear, onRemove }) => {
  if (items.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="mt-2 text-sm text-gray-500">Nenhuma análise recente</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Histórico Recente
        </h2>
        <button
          onClick={onClear}
          className="text-xs text-red-600 hover:text-red-700"
        >
          Limpar tudo
        </button>
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const categoryColor = item.category === 'Produtivo'
            ? 'bg-green-100 text-green-800'
            : 'bg-gray-100 text-gray-800';

          const date = new Date(item.timestamp);
          const timeString = date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          });

          return (
            <div
              key={item.id}
              className="flex items-start gap-3 p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${categoryColor}`}>
                    {item.category}
                  </span>
                  <span className="text-xs text-gray-500">
                    {(item.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-gray-400">
                    {timeString}
                  </span>
                </div>
                <p className="text-sm text-gray-600 truncate">
                  {item.summary}
                </p>
              </div>

              <button
                onClick={() => onRemove(item.id)}
                className="text-gray-400 hover:text-red-600 flex-shrink-0"
                title="Remover"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
