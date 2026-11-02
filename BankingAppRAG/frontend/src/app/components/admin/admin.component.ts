import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { ChatComponent } from '../chat/chat.component';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, ChatComponent],
  template: `
    <div class="dashboard-layout">
      <!-- Navbar -->
      <header class="navbar">
        <div class="brand">
          <span class="icon">⚙️</span>
          <div>
            <strong>Capgemini Commercial Bank</strong>
            <div class="user-badge">Super-Admin System Control & Governance Portal</div>
          </div>
        </div>
        <div class="nav-right">
          <span class="admin-tag">ADMIN: {{ auth.currentUser()?.full_name }}</span>
          <button class="btn-logout" (click)="auth.logout()">Logout ⎋</button>
        </div>
      </header>

      <main class="content-container">
        <!-- Telemetry Metrics Strip -->
        <div class="metrics-row" *ngIf="metrics()">
          <div class="metric-card">
            <div class="card-label">Total AI Queries Processed</div>
            <div class="card-value">{{ metrics().total_queries }}</div>
            <div class="card-meta">All classification categories</div>
          </div>
          <div class="metric-card">
            <div class="card-label">Average Model Latency</div>
            <div class="card-value">{{ metrics().avg_latency_ms }} ms</div>
            <div class="card-meta">Benchmark across models</div>
          </div>
          <div class="metric-card">
            <div class="card-label">Total Tokens Consumed</div>
            <div class="card-value">{{ metrics().total_tokens_used | number }}</div>
            <div class="card-meta">Capgemini Generative Engine</div>
          </div>
          <div class="metric-card">
            <div class="card-label">Cache Memory Hit Rate</div>
            <div class="card-value">{{ metrics().cache_hit_rate_pct }}%</div>
            <div class="card-meta">{{ metrics().cache_hit_count }} instant hits</div>
          </div>
        </div>

        <div *ngIf="actionMsg()" class="alert alert-success">{{ actionMsg() }}</div>

        <!-- 2 Column Layout: Provision Employee & Knowledge Ingestion Studio -->
        <div class="grid-2col">
          <!-- Left: Provision Employee Profile -->
          <div class="section-card">
            <h3>👤 Employee Account Provisioning (Admin-Only)</h3>
            <p class="section-desc">Create bank staff profiles and grant operational verification privileges.</p>

            <form (ngSubmit)="onProvisionEmployee()">
              <div class="form-group">
                <label>Staff Full Name</label>
                <input type="text" [(ngModel)]="empName" name="empName" placeholder="e.g. Vikramaditya Singh" required />
              </div>
              <div class="form-group">
                <label>Corporate Staff Email</label>
                <input type="email" [(ngModel)]="empEmail" name="empEmail" placeholder="e.g. vikram.singh@capgemini-bank.com" required />
              </div>
              <div class="form-group">
                <label>Contact Number</label>
                <input type="tel" [(ngModel)]="empPhone" name="empPhone" placeholder="+91 98765 00002" />
              </div>
              <div class="form-group">
                <label>Temporary Password</label>
                <input type="password" [(ngModel)]="empPassword" name="empPassword" placeholder="Minimum 6 characters" required />
              </div>
              <button type="submit" [disabled]="!empEmail.trim() || !empPassword.trim()" class="btn-primary">
                Provision Bank Staff Profile ➜
              </button>
            </form>
          </div>

          <!-- Right: Knowledge Ingestion & PDF Real-Time Vector Studio -->
          <div class="section-card highlight-card">
            <div class="card-header-flex">
              <div>
                <h3>📄 Bank Policy & Knowledge Document Ingestion</h3>
                <p class="section-desc">
                  Upload banking rules, compliance policies, or rate manuals (PDF, JSON, TXT). 
                  Real-time pipeline extracts text, generates 800-token chunks with 120-token overlap, calculates vector embeddings, and stores in database.
                </p>
              </div>
              <span class="badge-role ADMIN">ADMIN-ONLY</span>
            </div>

            <!-- Upload Drop Zone -->
            <div 
              class="drop-zone" 
              [class.dragging]="isDragging"
              (dragover)="onDragOver($event)"
              (dragleave)="onDragLeave($event)"
              (drop)="onDrop($event)"
              (click)="fileInput.click()"
            >
              <input 
                #fileInput 
                type="file" 
                (change)="onFileSelected($event)" 
                accept=".pdf,.json,.txt,application/pdf,application/json,text/plain" 
                style="display: none" 
              />
              <div class="drop-zone-content" *ngIf="!selectedFile">
                <span class="upload-icon">📑 ⬆️</span>
                <strong>Click to browse or Drag & Drop PDF / Policy Document here</strong>
                <p class="drop-hint">Supports Banking Manuals (.pdf), Compliance Rules (.txt), and Policy JSON (.json)</p>
              </div>
              <div class="selected-file-info" *ngIf="selectedFile">
                <div class="file-badge">
                  <span class="format-tag" [ngClass]="getFileExtension(selectedFile.name)">{{ getFileExtension(selectedFile.name) }}</span>
                  <div class="file-details">
                    <span class="file-name">{{ selectedFile.name }}</span>
                    <span class="file-size">{{ (selectedFile.size / 1024).toFixed(1) }} KB</span>
                  </div>
                </div>
                <button type="button" class="btn-remove-file" (click)="$event.stopPropagation(); removeSelectedFile()">✕ Remove</button>
              </div>
            </div>

            <!-- Title & Ingest Action Form -->
            <div class="upload-controls" *ngIf="selectedFile">
              <div class="form-group">
                <label>Document Title / Policy Subject</label>
                <input 
                  type="text" 
                  [(ngModel)]="docTitle" 
                  placeholder="e.g. Capgemini Retail Banking & Home Loan Policy 2026" 
                />
              </div>

              <div class="btn-group-row">
                <button 
                  type="button" 
                  (click)="onUploadDocument()" 
                  [disabled]="uploading()" 
                  class="btn-ingest-realtime"
                >
                  <span *ngIf="!uploading()">⚡ Ingest, Embed & Vectorize Real-Time</span>
                  <span *ngIf="uploading()">⏳ Processing Real-Time Ingestion...</span>
                </button>
              </div>
            </div>

            <!-- Live Ingestion Status Stepper -->
            <div *ngIf="uploading()" class="ingestion-progress-box">
              <div class="progress-spinner-row">
                <div class="spinner"></div>
                <div>
                  <strong>Real-Time Pipeline Executing...</strong>
                  <div class="step-text">{{ uploadStatusStep() }}</div>
                </div>
              </div>
            </div>

            <!-- Ingestion Success Alert -->
            <div *ngIf="uploadResult()" class="alert alert-success ingestion-success">
              <div class="success-header">
                <span>✅ <strong>Document Successfully Vectorized & Ready for RAG AI!</strong></span>
                <button class="btn-close-alert" (click)="uploadResult.set(null)">✕</button>
              </div>
              <div class="success-details">
                <div><strong>File:</strong> {{ uploadResult().filename }} ({{ uploadResult().file_type }})</div>
                <div><strong>Document ID:</strong> #{{ uploadResult().document_id }}</div>
                <div><strong>Total Chunks Vectorized:</strong> {{ uploadResult().total_chunks }} Chunks</div>
                <div class="ready-badge">✨ RAG Assistant can now answer questions citing this document with page & chunk references!</div>
              </div>
            </div>

            <div *ngIf="uploadError()" class="alert alert-danger">
              ⚠️ {{ uploadError() }}
              <button class="btn-close-alert" (click)="uploadError.set('')">✕</button>
            </div>

            <!-- Baseline Assets Footer -->
            <div class="seed-action-strip">
              <span>Looking to reset baseline knowledge assets (JSON, TXT, PDF)?</span>
              <button (click)="onSeedKnowledge()" [disabled]="seeding()" class="btn-sm-secondary">
                <span *ngIf="seeding()">Vectorizing & Indexing...</span>
                <span *ngIf="!seeding()">Re-Seed Sample Knowledge Assets ⟳</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Ingested Knowledge Assets Directory Table -->
        <div class="section-card">
          <div class="card-header-flex">
            <div>
              <h3>📚 Ingested Policy Documents & Vector Store Assets</h3>
              <p class="section-desc">Active banking policy manuals indexed in MS SQL vector store for RAG AI retrieval.</p>
            </div>
            <div class="table-actions">
              <button class="btn-icon-refresh" (click)="loadDocuments()" title="Refresh Knowledge Assets">⟳ Refresh Documents</button>
            </div>
          </div>

          <table class="data-table" *ngIf="documents().length > 0">
            <thead>
              <tr>
                <th>Doc ID</th>
                <th>Title</th>
                <th>Filename</th>
                <th>Format</th>
                <th>Vector Chunks</th>
                <th>Indexed Date</th>
                <th>RAG Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let doc of documents()">
                <td>#{{ doc.id }}</td>
                <td><strong>{{ doc.title }}</strong></td>
                <td><code>{{ doc.filename }}</code></td>
                <td>
                  <span class="badge-format" [ngClass]="doc.file_type">{{ doc.file_type }}</span>
                </td>
                <td>
                  <span class="badge-chunks">{{ doc.total_chunks }} Chunks</span>
                </td>
                <td>{{ doc.created_at | date:'medium' }}</td>
                <td>
                  <span class="badge-rag-active">● Active in RAG</span>
                </td>
                <td>
                  <button 
                    class="btn-delete-doc" 
                    (click)="onDeleteDocument(doc.id, doc.title)"
                    title="Delete document and remove vectors"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div *ngIf="documents().length === 0" class="empty-state">
            <p>No policy documents loaded in the vector database.</p>
            <small>Use the Upload Studio above to ingest your first PDF policy manual.</small>
          </div>
        </div>

        <!-- Users Directory Table -->
        <div class="section-card">
          <div class="card-header-flex">
            <h3>👥 System Users & Role Directory</h3>
            <div class="filters">
              <select [(ngModel)]="selectedRole" (change)="loadUsers()">
                <option value="">All Roles</option>
                <option value="ADMIN">ADMIN</option>
                <option value="EMPLOYEE">EMPLOYEE</option>
                <option value="CUSTOMER">CUSTOMER</option>
              </select>
            </div>
          </div>

          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let u of users()">
                <td>#{{ u.id }}</td>
                <td><strong>{{ u.full_name }}</strong></td>
                <td>{{ u.email }}</td>
                <td>
                  <span class="badge-role" [ngClass]="u.role">{{ u.role }}</span>
                </td>
                <td>
                  <span [class]="u.status === 'ACTIVE' ? 'badge-active' : 'badge-pending'">
                    {{ u.status }}
                  </span>
                </td>
                <td>{{ u.created_at | date:'mediumDate' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Compliance Audit Logs Table -->
        <div class="section-card">
          <h3>🛡️ Immutable Compliance Audit Logs Archive</h3>
          <p class="section-desc">Real-time traces of transaction events, operational actions, and authentication attempts.</p>

          <table class="data-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Action</th>
                <th>User ID</th>
                <th>Status</th>
                <th>Details</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let l of auditLogs()">
                <td>#{{ l.id }}</td>
                <td><code>{{ l.action }}</code></td>
                <td>{{ l.user_id ? '#' + l.user_id : 'Anonymous' }}</td>
                <td>
                  <span [class]="l.status === 'SUCCESS' ? 'badge-active' : 'badge-danger'">
                    {{ l.status }}
                  </span>
                </td>
                <td class="log-details">{{ l.details }}</td>
                <td>{{ l.created_at | date:'short' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>

      <!-- Reusable AI Banking Chatbot Widget -->
      <app-chat></app-chat>
    </div>
  `,
  styles: [`
    .dashboard-layout {
      min-height: 100vh;
      background: #090d16;
      color: #e2e8f0;
      font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .navbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 32px;
      background: #0f172a;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .icon {
      font-size: 28px;
    }
    .user-badge {
      font-size: 12px;
      color: #38bdf8;
    }
    .nav-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .admin-tag {
      font-size: 13px;
      color: #fbbf24;
      font-weight: 600;
    }
    .btn-logout {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #cbd5e1;
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
    }
    .content-container {
      padding: 24px 32px 100px 32px;
      max-width: 1400px;
      margin: 0 auto;
    }
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }
    .metric-card {
      background: #131d31;
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 14px;
      padding: 20px;
    }
    .card-label {
      font-size: 13px;
      color: #94a3b8;
      margin-bottom: 8px;
    }
    .card-value {
      font-size: 26px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 6px;
    }
    .card-meta {
      font-size: 12px;
      color: #38bdf8;
    }
    .grid-2col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }
    @media (max-width: 900px) {
      .grid-2col {
        grid-template-columns: 1fr;
      }
    }
    .section-card {
      background: #131d31;
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 24px;
    }
    .highlight-card {
      border: 1px solid rgba(56, 189, 248, 0.25);
      background: linear-gradient(180deg, #131e36 0%, #10192d 100%);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    h3 {
      margin: 0 0 8px 0;
      font-size: 16px;
      color: #f1f5f9;
    }
    .section-desc {
      font-size: 12px;
      color: #94a3b8;
      margin-bottom: 16px;
      line-height: 1.5;
    }
    .form-group {
      margin-bottom: 12px;
    }
    .form-group label {
      display: block;
      font-size: 12px;
      color: #cbd5e1;
      margin-bottom: 4px;
    }
    input, select {
      width: 100%;
      padding: 10px 12px;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #ffffff;
      font-size: 13px;
      box-sizing: border-box;
      outline: none;
    }
    input:focus, select:focus {
      border-color: #38bdf8;
    }
    .btn-primary {
      width: 100%;
      padding: 12px;
      background: #0284c7;
      border: none;
      color: #fff;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      margin-top: 8px;
      transition: background 0.2s;
    }
    .btn-primary:hover:not(:disabled) {
      background: #0369a1;
    }
    .drop-zone {
      border: 2px dashed rgba(56, 189, 248, 0.35);
      border-radius: 12px;
      background: rgba(15, 23, 42, 0.6);
      padding: 24px 16px;
      text-align: center;
      cursor: pointer;
      transition: all 0.25s ease;
      margin-bottom: 16px;
    }
    .drop-zone:hover, .drop-zone.dragging {
      border-color: #38bdf8;
      background: rgba(56, 189, 248, 0.08);
      transform: scale(1.005);
    }
    .drop-zone-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }
    .upload-icon {
      font-size: 32px;
    }
    .drop-hint {
      font-size: 11px;
      color: #94a3b8;
      margin: 4px 0 0 0;
    }
    .selected-file-info {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.04);
      border-radius: 8px;
    }
    .file-badge {
      display: flex;
      align-items: center;
      gap: 12px;
      text-align: left;
    }
    .format-tag {
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      background: #ef4444;
      color: #ffffff;
    }
    .format-tag.PDF {
      background: #dc2626;
    }
    .format-tag.JSON {
      background: #d97706;
    }
    .format-tag.TXT {
      background: #2563eb;
    }
    .file-details {
      display: flex;
      flex-direction: column;
    }
    .file-name {
      font-weight: 600;
      font-size: 13px;
      color: #f1f5f9;
    }
    .file-size {
      font-size: 11px;
      color: #94a3b8;
    }
    .btn-remove-file {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #f87171;
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 11px;
    }
    .upload-controls {
      margin-top: 12px;
    }
    .btn-ingest-realtime {
      width: 100%;
      padding: 12px;
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: #ffffff;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
      transition: all 0.2s;
    }
    .btn-ingest-realtime:hover:not(:disabled) {
      filter: brightness(1.1);
      transform: translateY(-1px);
    }
    .btn-ingest-realtime:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .ingestion-progress-box {
      margin-top: 14px;
      padding: 14px;
      background: rgba(14, 165, 233, 0.1);
      border: 1px solid rgba(14, 165, 233, 0.3);
      border-radius: 8px;
    }
    .progress-spinner-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .spinner {
      width: 24px;
      height: 24px;
      border: 3px solid rgba(56, 189, 248, 0.2);
      border-top-color: #38bdf8;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .step-text {
      font-size: 12px;
      color: #38bdf8;
      margin-top: 2px;
    }
    .ingestion-success {
      margin-top: 14px;
    }
    .success-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .success-details {
      font-size: 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      color: #cbd5e1;
    }
    .ready-badge {
      margin-top: 6px;
      padding: 6px 10px;
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid rgba(34, 197, 94, 0.3);
      border-radius: 6px;
      color: #4ade80;
      font-size: 12px;
      font-weight: 500;
    }
    .btn-close-alert {
      background: transparent;
      border: none;
      color: #94a3b8;
      cursor: pointer;
      font-size: 13px;
    }
    .seed-action-strip {
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #94a3b8;
      flex-wrap: wrap;
      gap: 10px;
    }
    .btn-sm-secondary {
      padding: 6px 12px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #cbd5e1;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
    }
    .card-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }
    .btn-icon-refresh {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #38bdf8;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
    }
    .filters select {
      width: auto;
      padding: 6px 12px;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .data-table th {
      text-align: left;
      padding: 10px 12px;
      color: #94a3b8;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .data-table td {
      padding: 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .badge-role {
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
    }
    .badge-role.ADMIN {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
    }
    .badge-role.EMPLOYEE {
      background: rgba(168, 85, 247, 0.15);
      color: #c084fc;
    }
    .badge-role.CUSTOMER {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
    }
    .badge-format {
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
    }
    .badge-format.PDF {
      background: rgba(239, 68, 68, 0.18);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-format.JSON {
      background: rgba(245, 158, 11, 0.18);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-format.TXT {
      background: rgba(59, 130, 246, 0.18);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-chunks {
      background: rgba(99, 102, 241, 0.18);
      color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.3);
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
    }
    .badge-rag-active {
      color: #4ade80;
      font-size: 12px;
      font-weight: 600;
    }
    .btn-delete-doc {
      background: transparent;
      border: none;
      cursor: pointer;
      font-size: 14px;
      opacity: 0.7;
      transition: opacity 0.2s;
    }
    .btn-delete-doc:hover {
      opacity: 1;
    }
    .empty-state {
      text-align: center;
      padding: 32px 16px;
      color: #94a3b8;
    }
    .badge-active {
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
    }
    .badge-pending {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
    }
    .badge-danger {
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
    }
    .log-details {
      max-width: 400px;
      color: #94a3b8;
      font-size: 12px;
    }
    .alert-success {
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid #22c55e;
      color: #86efac;
      padding: 10px 14px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 13px;
    }
    .alert-danger {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      color: #fca5a5;
      padding: 10px 14px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 13px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  `]
})
export class AdminComponent implements OnInit {
  metrics = signal<any>(null);
  users = signal<any[]>([]);
  auditLogs = signal<any[]>([]);
  documents = signal<any[]>([]);
  selectedRole = '';

  empName = '';
  empEmail = '';
  empPhone = '';
  empPassword = '';
  actionMsg = signal<string>('');
  seeding = signal<boolean>(false);

  // File Upload State
  selectedFile: File | null = null;
  docTitle = '';
  isDragging = false;
  uploading = signal<boolean>(false);
  uploadStatusStep = signal<string>('');
  uploadResult = signal<any>(null);
  uploadError = signal<string>('');

  constructor(public auth: AuthService, private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.api.getMetrics().subscribe((res) => this.metrics.set(res));
    this.loadUsers();
    this.loadDocuments();
    this.api.getAuditLogs().subscribe((res) => this.auditLogs.set(res));
  }

  loadUsers(): void {
    this.api.getUsers(this.selectedRole || undefined).subscribe((res) => this.users.set(res));
  }

  loadDocuments(): void {
    this.api.getDocuments().subscribe({
      next: (res) => this.documents.set(res),
      error: () => this.documents.set([])
    });
  }

  getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toUpperCase() || 'FILE';
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      this.handleFileSelected(file);
    }
  }

  onFileSelected(event: any): void {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      this.handleFileSelected(file);
    }
  }

  handleFileSelected(file: File): void {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['pdf', 'json', 'txt'].includes(ext || '')) {
      this.uploadError.set('Unsupported file format. Please upload .pdf, .json, or .txt documents.');
      return;
    }
    this.selectedFile = file;
    this.uploadError.set('');
    this.uploadResult.set(null);
    // Auto-generate clean title from filename
    this.docTitle = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  removeSelectedFile(): void {
    this.selectedFile = null;
    this.docTitle = '';
    this.uploadError.set('');
  }

  onUploadDocument(): void {
    if (!this.selectedFile) return;

    this.uploading.set(true);
    this.uploadError.set('');
    this.uploadResult.set(null);
    this.uploadStatusStep.set('Extracting text & generating 800-token chunks with 120-token overlap...');

    setTimeout(() => {
      if (this.uploading()) {
        this.uploadStatusStep.set('Generating AI vector embeddings via Generative Engine & persisting to MS SQL...');
      }
    }, 1200);

    this.api.uploadPolicyDocument(this.selectedFile, this.docTitle).subscribe({
      next: (res) => {
        this.uploading.set(false);
        this.uploadResult.set(res);
        this.selectedFile = null;
        this.docTitle = '';
        this.loadDocuments();
        this.api.getMetrics().subscribe((m) => this.metrics.set(m));
        this.api.getAuditLogs().subscribe((l) => this.auditLogs.set(l));
      },
      error: (err) => {
        this.uploading.set(false);
        this.uploadError.set(err.error?.detail || 'Failed to upload and vectorize document. Please try again.');
      }
    });
  }

  onDeleteDocument(docId: number, title: string): void {
    if (!confirm(`Are you sure you want to delete "${title}" (#${docId}) from the vector database?`)) {
      return;
    }

    this.api.deleteDocument(docId).subscribe({
      next: () => {
        this.actionMsg.set(`Document "${title}" and all its vector embeddings were deleted successfully.`);
        this.loadDocuments();
        this.api.getMetrics().subscribe((m) => this.metrics.set(m));
      },
      error: (err) => {
        alert(err.error?.detail || 'Failed to delete document.');
      }
    });
  }

  onProvisionEmployee(): void {
    this.api.provisionEmployee({
      full_name: this.empName,
      email: this.empEmail,
      phone_number: this.empPhone,
      password: this.empPassword
    }).subscribe({
      next: (res) => {
        this.actionMsg.set(`Bank Staff ${res.full_name} (${res.email}) provisioned successfully!`);
        this.empName = '';
        this.empEmail = '';
        this.empPhone = '';
        this.empPassword = '';
        this.loadUsers();
      },
      error: (err) => {
        alert(err.error?.detail || 'Employee provisioning failed.');
      }
    });
  }

  onSeedKnowledge(): void {
    this.seeding.set(true);
    this.api.seedKnowledgeBase().subscribe({
      next: () => {
        this.seeding.set(false);
        this.actionMsg.set('Sample knowledge base (JSON, TXT, PDF) re-vectorized and indexed successfully.');
        this.loadDocuments();
      },
      error: () => {
        this.seeding.set(false);
      }
    });
  }
}
