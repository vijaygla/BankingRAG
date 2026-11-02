import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { ChatComponent } from '../chat/chat.component';

@Component({
  selector: 'app-customer',
  standalone: true,
  imports: [CommonModule, FormsModule, ChatComponent],
  template: `
    <div class="dashboard-layout">
      <!-- Navbar -->
      <header class="navbar">
        <div class="brand">
          <span class="icon">🏛️</span>
          <div>
            <strong>Capgemini Commercial Bank</strong>
            <div class="user-badge">Customer Portal ({{ auth.currentUser()?.full_name }})</div>
          </div>
        </div>
        <div class="nav-right">
          <span class="status-pill" [class.active]="auth.currentUser()?.status === 'ACTIVE'">
            ● {{ auth.currentUser()?.status }}
          </span>
          <button class="btn-logout" (click)="auth.logout()">Logout ⎋</button>
        </div>
      </header>

      <!-- Main Content -->
      <main class="content-container">
        <!-- KYC Alert if not active -->
        <div *ngIf="auth.currentUser()?.status !== 'ACTIVE'" class="kyc-banner">
          <div class="banner-text">
            ⚠️ <strong>Verification Action Required:</strong> Your account status is <code>{{ auth.currentUser()?.status }}</code>.
            Please submit your identity documents below to activate core banking features and debit/credit services.
          </div>
        </div>

        <!-- Metric Grid -->
        <div class="metrics-row">
          <!-- Primary Account Balance Card -->
          <div class="metric-card balance-card">
            <div class="card-label">Primary Account Balance</div>
            <div class="card-value">
              <span *ngIf="balances().length > 0">₹{{ balances()[0].balance | number:'1.2-2' }}</span>
              <span *ngIf="balances().length === 0" class="muted">Awaiting Activation</span>
            </div>
            <div class="card-meta">
              <span *ngIf="balances().length > 0">Account: {{ balances()[0].account_number }}</span>
              <span *ngIf="balances().length === 0">No active account linked yet</span>
            </div>
          </div>

          <!-- Credit Line Card -->
          <div class="metric-card">
            <div class="card-label">Credit Card Available Limit</div>
            <div class="card-value">
              <span *ngIf="cards().length > 0">₹{{ cards()[0].available_limit | number:'1.2-2' }}</span>
              <span *ngIf="cards().length === 0" class="muted">No Card Issued</span>
            </div>
            <div class="card-meta">
              <span *ngIf="cards().length > 0">Card: {{ cards()[0].card_number }} ({{ cards()[0].card_variant }})</span>
              <span *ngIf="cards().length === 0">Provided automatically post-KYC</span>
            </div>
          </div>

          <!-- Active Loans Card -->
          <div class="metric-card">
            <div class="card-label">Active Loan Portfolio</div>
            <div class="card-value">
              <span>{{ loans().length }} Active</span>
            </div>
            <div class="card-meta">Check lending terms & EMIs below</div>
          </div>
        </div>

        <!-- Two Column Content Grid -->
        <div class="grid-2col">
          <!-- Left Column: Transactions & KYC -->
          <div class="col">
            <!-- Account Details Table -->
            <div class="section-card">
              <h3>🏦 Accounts & Live Balances</h3>
              <div *ngIf="balances().length === 0" class="empty-state">
                No active accounts found. Once Bank Staff verifies your KYC, your 10-digit core account will appear here.
              </div>
              <table *ngIf="balances().length > 0" class="data-table">
                <thead>
                  <tr>
                    <th>Account No</th>
                    <th>Type</th>
                    <th>Balance</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let acc of balances()">
                    <td><code>{{ acc.account_number }}</code></td>
                    <td>{{ acc.account_type }}</td>
                    <td><strong>₹{{ acc.balance | number:'1.2-2' }}</strong></td>
                    <td><span class="badge-success">{{ acc.status }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- KYC Submission Section -->
            <div class="section-card">
              <h3>📄 KYC Document Submission</h3>
              <p class="section-desc">Submit your government identity proof for operational staff audit.</p>

              <div *ngIf="kycMsg()" class="alert alert-success">{{ kycMsg() }}</div>

              <div class="form-row">
                <div class="field">
                  <label>Document Type</label>
                  <select [(ngModel)]="kycDocType">
                    <option value="PAN">PAN Card</option>
                    <option value="AADHAAR">Aadhaar Card</option>
                    <option value="PASSPORT">Passport</option>
                  </select>
                </div>
                <div class="field">
                  <label>Document Number / ID</label>
                  <input type="text" [(ngModel)]="kycDocNumber" placeholder="e.g. ABCDE1234F" />
                </div>
                <button (click)="onSubmitKYC()" [disabled]="!kycDocNumber.trim()" class="btn-submit">
                  Upload & Verify
                </button>
              </div>
            </div>

            <!-- Support Ticket Submission -->
            <div class="section-card">
              <h3>🎫 Open Bank Support Ticket</h3>
              <div *ngIf="ticketMsg()" class="alert alert-success">{{ ticketMsg() }}</div>

              <div class="form-group">
                <label>Subject</label>
                <input type="text" [(ngModel)]="ticketSubject" placeholder="e.g. Card PIN reset or account statement request" />
              </div>
              <div class="form-group">
                <label>Description</label>
                <textarea rows="2" [(ngModel)]="ticketDesc" placeholder="Describe the inquiry..."></textarea>
              </div>
              <button (click)="onSubmitTicket()" [disabled]="!ticketSubject.trim()" class="btn-secondary">
                Submit Support Request
              </button>
            </div>
          </div>

          <!-- Right Column: Cards, Loans & Transactions -->
          <div class="col">
            <!-- Credit Cards Section -->
            <div class="section-card">
              <h3>💳 Credit Card Monitoring</h3>
              <div *ngIf="cards().length === 0" class="empty-state">No credit card assigned.</div>
              <div *ngFor="let card of cards()" class="card-detail-item">
                <div class="card-visual">
                  <div class="card-chip"></div>
                  <div class="card-no">{{ card.card_number }}</div>
                  <div class="card-holder">{{ auth.currentUser()?.full_name }}</div>
                  <div class="card-type">{{ card.card_variant }}</div>
                </div>
                <div class="card-stats">
                  <div>Available: <strong>₹{{ card.available_limit | number:'1.2-2' }}</strong></div>
                  <div>Total Limit: ₹{{ card.total_limit | number:'1.2-2' }}</div>
                  <div>Outstanding: ₹{{ card.outstanding_balance | number:'1.2-2' }}</div>
                  <div>Status: <span class="badge-success">{{ card.status }}</span></div>
                </div>
              </div>
            </div>

            <!-- Active Loans Section -->
            <div class="section-card">
              <h3>📊 Loan Portfolio Monitoring</h3>
              <div *ngIf="loans().length === 0" class="empty-state">No active lending facilities found.</div>
              <div *ngFor="let loan of loans()" class="loan-item">
                <div class="loan-header">
                  <strong>{{ loan.loan_type }}</strong>
                  <span class="badge-success">{{ loan.status }}</span>
                </div>
                <div class="loan-body">
                  <div>Remaining Principal: <strong>₹{{ loan.remaining_balance | number:'1.2-2' }}</strong></div>
                  <div>Monthly EMI: ₹{{ loan.monthly_emi | number:'1.2-2' }}</div>
                  <div>Interest Rate: {{ loan.interest_rate }}%</div>
                  <div>Tenure: {{ loan.tenure_months }} Months</div>
                </div>
              </div>
            </div>

            <!-- Recent Transactions Section -->
            <div class="section-card">
              <h3>📜 Recent Transaction Traces</h3>
              <div *ngIf="transactions().length === 0" class="empty-state">No recent transactions recorded.</div>
              <table *ngIf="transactions().length > 0" class="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let tx of transactions()">
                    <td>{{ tx.timestamp | date:'short' }}</td>
                    <td>
                      <span [class]="tx.transaction_type === 'CREDIT' ? 'badge-success' : 'badge-danger'">
                        {{ tx.transaction_type }}
                      </span>
                    </td>
                    <td>
                      <strong [style.color]="tx.transaction_type === 'CREDIT' ? '#34d399' : '#f87171'">
                        {{ tx.transaction_type === 'CREDIT' ? '+' : '-' }}₹{{ tx.amount | number:'1.2-2' }}
                      </strong>
                    </td>
                    <td>{{ tx.description }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
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
    .status-pill {
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 20px;
      background: rgba(239, 68, 68, 0.15);
      color: #fca5a5;
    }
    .status-pill.active {
      background: rgba(34, 197, 94, 0.15);
      color: #86efac;
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
    .kyc-banner {
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fde68a;
      padding: 12px 18px;
      border-radius: 10px;
      margin-bottom: 24px;
    }
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }
    .metric-card {
      background: #131d31;
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 14px;
      padding: 20px;
    }
    .balance-card {
      background: linear-gradient(135deg, #0369a1 0%, #0f172a 100%);
      border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .card-label {
      font-size: 13px;
      color: #94a3b8;
      margin-bottom: 8px;
    }
    .card-value {
      font-size: 28px;
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
    h3 {
      margin: 0 0 14px 0;
      font-size: 16px;
      color: #f1f5f9;
    }
    .section-desc {
      font-size: 12px;
      color: #94a3b8;
      margin-bottom: 12px;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .data-table th {
      text-align: left;
      padding: 8px 10px;
      color: #94a3b8;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .data-table td {
      padding: 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .badge-success {
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
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
    .form-row {
      display: flex;
      gap: 12px;
      align-items: flex-end;
    }
    .field {
      flex: 1;
    }
    .field label, .form-group label {
      display: block;
      font-size: 12px;
      color: #94a3b8;
      margin-bottom: 4px;
    }
    select, input, textarea {
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
    .form-group {
      margin-bottom: 12px;
    }
    .btn-submit {
      padding: 10px 16px;
      background: #0284c7;
      border: none;
      color: #fff;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
    }
    .btn-secondary {
      padding: 10px 16px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
    }
    .card-visual {
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 12px;
      padding: 18px;
      position: relative;
      margin-bottom: 12px;
    }
    .card-chip {
      width: 36px;
      height: 26px;
      background: #eab308;
      border-radius: 4px;
      margin-bottom: 14px;
    }
    .card-no {
      font-size: 18px;
      letter-spacing: 2px;
      font-family: monospace;
      margin-bottom: 10px;
    }
    .card-holder {
      font-size: 12px;
      color: #cbd5e1;
    }
    .card-type {
      position: absolute;
      bottom: 18px;
      right: 18px;
      font-size: 12px;
      color: #38bdf8;
      font-weight: 600;
    }
    .card-stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      font-size: 12px;
    }
    .loan-item {
      background: #0f172a;
      padding: 14px;
      border-radius: 10px;
      margin-bottom: 10px;
    }
    .loan-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .loan-body {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      font-size: 12px;
      color: #cbd5e1;
    }
    .empty-state {
      padding: 24px;
      text-align: center;
      color: #64748b;
      font-size: 13px;
    }
    .alert-success {
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid #22c55e;
      color: #86efac;
      padding: 8px 12px;
      border-radius: 6px;
      margin-bottom: 12px;
      font-size: 12px;
    }
  `]
})
export class CustomerComponent implements OnInit {
  balances = signal<any[]>([]);
  cards = signal<any[]>([]);
  loans = signal<any[]>([]);
  transactions = signal<any[]>([]);

  kycDocType = 'PAN';
  kycDocNumber = '';
  kycMsg = signal<string>('');

  ticketSubject = '';
  ticketDesc = '';
  ticketMsg = signal<string>('');

  constructor(public auth: AuthService, private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.api.getBalances().subscribe((res) => this.balances.set(res));
    this.api.getCards().subscribe((res) => this.cards.set(res));
    this.api.getLoans().subscribe((res) => this.loans.set(res));
    this.api.getTransactions().subscribe((res) => this.transactions.set(res));
  }

  onSubmitKYC(): void {
    if (!this.kycDocNumber.trim()) return;
    this.api.submitKYC({ document_type: this.kycDocType, document_number: this.kycDocNumber }).subscribe({
      next: () => {
        this.kycMsg.set('KYC Document uploaded successfully! Bank staff has received it in the Pending Queue.');
        this.kycDocNumber = '';
      }
    });
  }

  onSubmitTicket(): void {
    if (!this.ticketSubject.trim()) return;
    this.api.createTicket({
      subject: this.ticketSubject,
      description: this.ticketDesc,
      priority: 'MEDIUM'
    }).subscribe({
      next: () => {
        this.ticketMsg.set('Support ticket created. Bank staff will review your inquiry.');
        this.ticketSubject = '';
        this.ticketDesc = '';
      }
    });
  }
}
