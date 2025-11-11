/**
 * API Service - Cliente para comunicação com backend FastAPI
 * Centraliza todas as chamadas HTTP
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ProcessResponse {
  id: string;
  category: 'Produtivo' | 'Improdutivo';
  confidence: number;
  suggested_reply: string;
  summary: string;
  model_used: string;
  timestamp: string;
  reason?: string;
}

export interface FeedbackRequest {
  analysis_id: string;
  edited_reply?: string;
  user_category?: 'Produtivo' | 'Improdutivo';
  rating?: number;
  comments?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  openai_configured: boolean;
  database_connected: boolean;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Processa email enviando arquivo
   */
  async processFile(file: File): Promise<ProcessResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/process`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao processar arquivo');
    }

    return response.json();
  }

  /**
   * Processa email enviando texto direto
   */
  async processText(text: string): Promise<ProcessResponse> {
    const formData = new FormData();
    formData.append('text', text);

    const response = await fetch(`${this.baseUrl}/api/process`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao processar texto');
    }

    return response.json();
  }

  /**
   * Envia feedback sobre uma análise
   */
  async submitFeedback(feedback: FeedbackRequest): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao enviar feedback');
    }
  }

  /**
   * Busca status de uma análise
   */
  async getStatus(analysisId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/status/${analysisId}`);

    if (!response.ok) {
      throw new Error('Erro ao buscar status');
    }

    return response.json();
  }

  /**
   * Busca resposta mock (para desenvolvimento)
   */
  async getMockResponse(): Promise<ProcessResponse> {
    const response = await fetch(`${this.baseUrl}/api/mock`);
    
    if (!response.ok) {
      throw new Error('Erro ao buscar mock');
    }

    return response.json();
  }

  /**
   * Health check
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Health check falhou');
    }

    return response.json();
  }
}

export const apiService = new ApiService();
