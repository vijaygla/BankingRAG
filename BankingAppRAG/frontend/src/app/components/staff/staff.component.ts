import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { ChatComponent } from '../chat/chat.component';

@Component({
  selector: 'app-staff',
  standalone: true,
  imports: [CommonModule, FormsModule, ChatComponent],
  template: `
    <div class="dashboard-layout">
      <!-- Navbar -->
      <header class="navbar">
        <div class="brand">
          <span class="icon">💼</span>
          <div>
            <strong>Capgemini Apex Commercial Bank</strong>
            <div class="user-badge">Bank Staff Operations & Verification Workspace</div>
          </div>
        </div>
        <div class="nav-right">
          <span class="staff-tag">STAFF: {{ auth.currentUser()?.full_name }}</span>
          <button class="btn-logout" (click)="auth.logout()">Logout ⎋</button>
        </div>
      </header>

      <main class="content-container">
        <!-- Section Header -->
        <div class="workspace-header">
          <h2>Identity Verification & Account Activation Queue</h2>
          <p class="subtitle">Audit submitted customer credentials,Pass validation checks, and execute 10-digit core account activation.</p>
        </div>

        <!-- Alert Notification -->
        <div *ngIf="actionMsg()" class="alert alert-success">{{ actionMsg() }}</div>

        <!-- Pending KYC Queue Table -->
        <div class="section-card">
          <div class="card-header-flex">
            <h3>📑 Pending Customer KYC Verification Queue</h3>
            <button class="btn-refresh" (click)="loadData()">Refresh Queue ⟳</button>
          </div>

          <div *ngIf="kycQueue().length === 0" class="empty-state">
            ✅ All KYC applications processed! No pending verification tasks in queue.
          </div>

          <table *ngIf="kycQueue().length > 0" class="data-table">
            <thead>
              <tr>
                <th>Doc ID</th>
                <th>Customer Name & Email</th>
                <th>Doc Type</th>
                <th>Doc Number</th>
                <th>Status</th>
                <th>Audit Actions</th>
                <th>Core Activation</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let item of kycQueue()">
                <td>#{{ item.id }}</td>
                <td>
                  <strong>{{ item.user_name }}</strong>
                  <div class="sub-email">{{ item.user_email }} (User ID: {{ item.user_id }})</div>
                </td>
                <td><span class="badge-type">{{ item.document_type }}</span></td>
                <td><code>{{ item.document_number }}</code></td>
                <td>
                  <span [class]="item.status === 'VERIFIED' ? 'badge-success' : 'badge-pending'">
                    {{ item.status }}
                  </span>
                </td>
                <td>
                  <div class="action-btns">
                    <button class="btn-verify" (click)="onVerifyKYC(item.id, 'VERIFIED')">
                      Approve & Verify ✓
                    </button>
                    <button class="btn-reject" (click)="onVerifyKYC(item.id, 'REJECTED')">
                      Reject ✕
                    </button>
                  </div>
                </td>
                <td>
                  <button
                    class="btn-activate"
                    [disabled]="item.status !== 'VERIFIED'"
                    (click)="onActivateAccount(item.user_id)"
                  >
                    Generate 10-Digit Account & Activate ⚡
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Operational Support Tickets -->
        <div class="section-card">
          <h3>🎫 Operational Support & Process Tickets</h3>
          <div *ngIf="tickets().length === 0" class="empty-state">No open support tickets.</div>

          <table *ngIf="tickets().length > 0" class="data-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Customer</th>
                <th>Subject</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Resolve Action</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let t of tickets()">
                <td><code>{{ t.ticket_code }}</code></td>
                <td>{{ t.user_name }}</td>
                <td>
                  <strong>{{ t.subject }}</strong>
                  <div class="sub-email">{{ t.description }}</div>
                </td>
                <td><span class="badge-priority">{{ t.priority }}</span></td>
                <td>
                  <span [class]="t.status === 'RESOLVED' ? 'badge-success' : 'badge-pending'">
                    {{ t.status }}
                  </span>
                </td>
                <td>
                  <button
                    *ngIf="t.status !== 'RESOLVED'"
                    class="btn-resolve"
                    (click)="onResolveTicket(t.id)"
                  >
                    Mark Resolved ✓
                  </button>
                  <span *ngIf="t.status === 'RESOLVED'" class="text-muted">Completed</span>
                </td>
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
    .staff-tag {
      font-size: 13px;
      color: #94a3b8;
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
    .workspace-header {
      margin-bottom: 24px;
    }
    h2 {
      margin: 0 0 6px 0;
      font-size: 22px;
      color: #ffffff;
    }
    .subtitle {
      margin: 0;
      font-size: 13px;
      color: #94a3b8;
    }
    .section-card {
      background: #131d31;
      border: 1px solid rgba(255, 255, 255, 0.07);
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 24px;
    }
    .card-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    h3 {
      margin: 0;
      font-size: 16px;
      color: #f1f5f9;
    }
    .btn-refresh {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
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
      vertical-align: middle;
    }
    .sub-email {
      font-size: 11px;
      color: #64748b;
      margin-top: 2px;
    }
    .badge-type {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
    }
    .badge-success {
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
    }
    .badge-pending {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
    }
    .badge-priority {
      background: rgba(168, 85, 247, 0.15);
      color: #c084fc;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
    }
    .action-btns {
      display: flex;
      gap: 6px;
    }
    .btn-verify {
      background: #16a34a;
      border: none;
      color: #fff;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
    }
    .btn-reject {
      background: #dc2626;
      border: none;
      color: #fff;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
    }
    .btn-activate {
      background: linear-gradient(135deg, #0284c7, #0369a1);
      border: none;
      color: #fff;
      padding: 8px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
    }
    .btn-activate:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    .btn-resolve {
      background: #0284c7;
      border: none;
      color: #fff;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
    }
    .empty-state {
      padding: 36px;
      text-align: center;
      color: #64748b;
      font-size: 14px;
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
    .text-muted {
      color: #64748b;
      font-size: 12px;
    }
  `]
})
export class StaffComponent implements OnInit {
  kycQueue = signal<any[]>([]);
  tickets = signal<any[]>([]);
  actionMsg = signal<string>('');

  constructor(public auth: AuthService, private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.api.getKYCQueue().subscribe((res) => this.kycQueue.set(res));
    this.api.getStaffTickets().subscribe((res) => this.tickets.set(res));
  }

  onVerifyKYC(docId: number, status: string): void {
    const notes = status === 'VERIFIED'
      ? 'Identity authenticated against government tax database'
      : 'Document image unreadable or mismatched';

    this.api.verifyKYC(docId, status, notes).subscribe({
      next: () => {
        this.actionMsg.set(`KYC Document #${docId} successfully marked as ${status}.`);
        this.loadData();
      }
    });
  }

  onActivateAccount(userId: number): void {
    this.api.activateAccount(userId).subscribe({
      next: (res) => {
        this.actionMsg.set(`Customer #${userId} successfully activated! Core 10-digit Account #${res.account_number} created with ₹${res.initial_balance} deposit.`);
        this.loadData();
      },
      error: (err) => {
        alert(err.error?.detail || 'Account activation failed.');
      }
    });
  }

  onResolveTicket(ticketId: number): void {
    this.api.actionTicket(ticketId, 'RESOLVED', 'Issue resolved by bank staff').subscribe({
      next: () => {
        this.actionMsg.set(`Ticket #${ticketId} marked as RESOLVED.`);
        this.loadData();
      }
    });
  }
}
