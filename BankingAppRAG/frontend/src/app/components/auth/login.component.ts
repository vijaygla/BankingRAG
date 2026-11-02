import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-header">
          <div class="brand-badge">
            <span class="bank-icon">🏛️</span> Capgemini Apex Commercial Bank
          </div>
          <h2>Enterprise Digital Banking Portal</h2>
          <p class="subtitle">Secure AI-Powered Multi-Role Banking Gateway</p>
        </div>

        <div class="tabs">
          <button [class.active]="activeTab() === 'login'" (click)="activeTab.set('login')">
            🔑 Secure Login
          </button>
          <button [class.active]="activeTab() === 'register'" (click)="activeTab.set('register')">
            👤 Customer Self-Registration
          </button>
        </div>

        <!-- Notification Banner -->
        <div *ngIf="message()" [class]="'alert alert-' + messageType()">
          {{ message() }}
        </div>

        <!-- LOGIN FORM -->
        <form *ngIf="activeTab() === 'login'" (ngSubmit)="onLogin()" class="form-container">
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" [(ngModel)]="loginEmail" name="email" placeholder="e.g. customer@domain.com" required />
          </div>

          <div class="form-group">
            <label>Secure Password</label>
            <input type="password" [(ngModel)]="loginPassword" name="password" placeholder="••••••••••••" required />
          </div>

          <button type="submit" [disabled]="loading()" class="btn-primary">
            <span *ngIf="loading()">Authenticating...</span>
            <span *ngIf="!loading()">Login➜</span>
          </button>
        </form>

        <!-- REGISTER FORM (CUSTOMER ONLY) -->
        <form *ngIf="activeTab() === 'register'" (ngSubmit)="onRegister()" class="form-container">
          <div class="form-group">
            <label>Full Legal Name</label>
            <input type="text" [(ngModel)]="regFullName" name="fullName" placeholder="e.g. Aarav Sharma" required />
          </div>

          <div class="form-group">
            <label>Email Address</label>
            <input type="email" [(ngModel)]="regEmail" name="regEmail" placeholder="e.g. aarav.sharma@example.com" required />
          </div>

          <div class="form-group">
            <label>Mobile Number</label>
            <input type="tel" [(ngModel)]="regPhone" name="regPhone" placeholder="+91 98765 43210" />
          </div>

          <div class="form-group">
            <label>Create Password</label>
            <input type="password" [(ngModel)]="regPassword" name="regPassword" placeholder="Minimum 6 characters" required />
          </div>

          <button type="submit" [disabled]="loading()" class="btn-primary">
            <span *ngIf="loading()">Registering Account...</span>
            <span *ngIf="!loading()">Complete Customer Registration ➜</span>
          </button>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .auth-wrapper {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: radial-gradient(circle at 10% 20%, #0d1b2a 0%, #1b263b 90%);
      padding: 24px;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .auth-card {
      width: 100%;
      max-width: 520px;
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      padding: 36px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
      color: #f1f5f9;
    }
    .auth-header {
      text-align: center;
      margin-bottom: 24px;
    }
    .brand-badge {
      display: inline-block;
      padding: 6px 14px;
      background: rgba(14, 165, 233, 0.15);
      border: 1px solid rgba(14, 165, 233, 0.3);
      color: #38bdf8;
      border-radius: 30px;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 12px;
    }
    h2 {
      font-size: 24px;
      margin: 0 0 8px 0;
      color: #ffffff;
    }
    .subtitle {
      font-size: 14px;
      color: #94a3b8;
      margin: 0;
    }
    .tabs {
      display: flex;
      background: rgba(0, 0, 0, 0.25);
      padding: 4px;
      border-radius: 12px;
      margin-bottom: 24px;
    }
    .tabs button {
      flex: 1;
      padding: 10px 16px;
      border: none;
      background: transparent;
      color: #94a3b8;
      font-size: 14px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .tabs button.active {
      background: #0284c7;
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    .form-group {
      margin-bottom: 16px;
      text-align: left;
    }
    .form-group label {
      display: block;
      font-size: 13px;
      color: #cbd5e1;
      margin-bottom: 6px;
      font-weight: 500;
    }
    input {
      width: 100%;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 10px;
      color: #ffffff;
      font-size: 14px;
      box-sizing: border-box;
      outline: none;
      transition: border-color 0.2s;
    }
    input:focus {
      border-color: #38bdf8;
      background: rgba(255, 255, 255, 0.1);
    }
    .btn-primary {
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, #0284c7, #0369a1);
      border: none;
      border-radius: 10px;
      color: #ffffff;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      margin-top: 10px;
    }
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(2, 132, 199, 0.4);
    }
    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .alert {
      padding: 12px;
      border-radius: 8px;
      font-size: 13px;
      margin-bottom: 16px;
      text-align: center;
    }
    .alert-success {
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid #22c55e;
      color: #86efac;
    }
    .alert-danger {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      color: #fca5a5;
    }
    .info-box {
      background: rgba(14, 165, 233, 0.1);
      border-left: 4px solid #0284c7;
      padding: 10px 14px;
      font-size: 12px;
      color: #bae6fd;
      border-radius: 4px;
      margin-bottom: 16px;
      line-height: 1.5;
    }
    .demo-hints {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 12px;
      color: #94a3b8;
    }
    code {
      background: rgba(0, 0, 0, 0.3);
      padding: 3px 6px;
      border-radius: 4px;
      color: #38bdf8;
    }
  `]
})
export class LoginComponent {
  activeTab = signal<'login' | 'register'>('login');
  loading = signal<boolean>(false);
  message = signal<string>('');
  messageType = signal<'success' | 'danger'>('success');

  loginEmail = '';
  loginPassword = '';

  regFullName = '';
  regEmail = '';
  regPhone = '';
  regPassword = '';

  constructor(private auth: AuthService) {}

  onLogin() {
    this.loading.set(true);
    this.message.set('');
    this.auth.login({ email: this.loginEmail, password: this.loginPassword }).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.messageType.set('success');
        this.message.set(`Welcome back, ${res.full_name}! Redirecting to ${res.role} portal...`);
        setTimeout(() => this.auth.navigateByRole(), 700);
      },
      error: (err) => {
        this.loading.set(false);
        this.messageType.set('danger');
        this.message.set(err.error?.detail || 'Authentication failed. Please verify credentials.');
      }
    });
  }

  onRegister() {
    this.loading.set(true);
    this.message.set('');
    this.auth.registerCustomer({
      email: this.regEmail,
      password: this.regPassword,
      full_name: this.regFullName,
      phone_number: this.regPhone
    }).subscribe({
      next: () => {
        this.loading.set(false);
        this.messageType.set('success');
        this.message.set('Registration successful! Your account is set to KYC_PENDING. Please login to complete KYC verification.');
        this.activeTab.set('login');
        this.loginEmail = this.regEmail;
      },
      error: (err) => {
        this.loading.set(false);
        this.messageType.set('danger');
        this.message.set(err.error?.detail || 'Registration failed. Please check your details.');
      }
    });
  }
}
