import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://127.0.0.1:8000/api/v1';

  constructor(private http: HttpClient, private auth: AuthService) {}

  private get headers() {
    return { headers: this.auth.getAuthHeaders() };
  }

  // --- HEALTH & METRICS ---
  getHealth(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/health`);
  }

  getMetrics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/metrics`, this.headers);
  }

  // --- CUSTOMER DASHBOARD ---
  getBalances(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/me/balance`, this.headers);
  }

  getCards(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/me/cards`, this.headers);
  }

  getLoans(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/me/loans`, this.headers);
  }

  getTransactions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/me/transactions`, this.headers);
  }

  submitKYC(payload: { document_type: string; document_number: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/me/kyc/submit`, payload, this.headers);
  }

  createTicket(payload: { subject: string; description: string; priority: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/me/tickets`, payload, this.headers);
  }

  // --- STAFF WORKSPACE ---
  getKYCQueue(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/staff/kyc-queue`, this.headers);
  }

  verifyKYC(docId: number, status: string, notes: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/staff/kyc-verify/${docId}`, {
      status,
      verification_notes: notes
    }, this.headers);
  }

  activateAccount(userId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/staff/activate-account/${userId}`, {}, this.headers);
  }

  getStaffTickets(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/staff/tickets`, this.headers);
  }

  actionTicket(ticketId: number, status: string, notes: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/staff/tickets/${ticketId}/action`, {
      status,
      action_notes: notes
    }, this.headers);
  }

  // --- ADMIN GOVERNANCE ---
  provisionEmployee(payload: { email: string; password: string; full_name: string; phone_number?: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/admin/employees`, payload, this.headers);
  }

  getUsers(role?: string, status?: string): Observable<any[]> {
    let url = `${this.apiUrl}/admin/users`;
    const params: string[] = [];
    if (role) params.push(`role=${role}`);
    if (status) params.push(`status=${status}`);
    if (params.length) url += `?${params.join('&')}`;
    return this.http.get<any[]>(url, this.headers);
  }

  getAuditLogs(limit: number = 30): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/audit-logs?limit=${limit}`, this.headers);
  }

  seedKnowledgeBase(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/ingest/seed`, {}, this.headers);
  }

  // --- KNOWLEDGE INGESTION & REAL-TIME VECTORIZATION ---
  uploadPolicyDocument(file: File, title?: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (title && title.trim()) {
      formData.append('title', title.trim());
    }
    return this.http.post<any>(`${this.apiUrl}/ingest`, formData, this.headers);
  }

  getDocuments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/ingest/documents`, this.headers);
  }

  deleteDocument(docId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/ingest/documents/${docId}`, this.headers);
  }
}
