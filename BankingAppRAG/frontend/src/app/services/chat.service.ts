import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface CitationItem {
  filename: string;
  title: string;
  chunk_index: number;
  score: number;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  intent: 'POLICY_DOC' | 'USER_SQL' | 'REFUSE_OOS';
  citations: CitationItem[];
  model_used: string;
  latency_ms: number;
  tokens_used: number;
  session_id: string;
  cached: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://127.0.0.1:8000/api/v1';

  constructor(private http: HttpClient, private auth: AuthService) {}

  private get headers() {
    return { headers: this.auth.getAuthHeaders() };
  }

  ask(payload: { message: string; session_id?: string; model?: string }): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat/ask`, payload, this.headers);
  }

  getModels(): Observable<{ default_model: string; available_models: string[] }> {
    return this.http.get<{ default_model: string; available_models: string[] }>(`${this.apiUrl}/chat/models`);
  }

  submitFeedback(rating: number, comment?: string, messageId?: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/chat/feedback`, {
      rating,
      comment,
      message_id: messageId
    }, this.headers);
  }
}
