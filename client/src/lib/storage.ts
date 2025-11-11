/**
 * Local Storage utilities - Gerencia histórico de análises
 */

export interface HistoryItem {
  id: string;
  category: 'Produtivo' | 'Improdutivo';
  confidence: number;
  summary: string;
  timestamp: string;
}

const HISTORY_KEY = 'email-classifier-history';
const MAX_HISTORY_ITEMS = 10;

export const historyStorage = {
  /**
   * Adiciona item ao histórico
   */
  addItem(item: HistoryItem): void {
    const history = this.getHistory();
    
    // Adiciona no início
    history.unshift(item);
    
    // Mantém apenas últimos N itens
    const trimmed = history.slice(0, MAX_HISTORY_ITEMS);
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
  },

  /**
   * Retorna todo o histórico
   */
  getHistory(): HistoryItem[] {
    const stored = localStorage.getItem(HISTORY_KEY);
    
    if (!stored) {
      return [];
    }

    try {
      return JSON.parse(stored);
    } catch {
      return [];
    }
  },

  /**
   * Limpa histórico
   */
  clearHistory(): void {
    localStorage.removeItem(HISTORY_KEY);
  },

  /**
   * Remove item específico
   */
  removeItem(id: string): void {
    const history = this.getHistory();
    const filtered = history.filter(item => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
  }
};
