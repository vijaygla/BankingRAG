import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatResponse, CitationItem } from '../../services/chat.service';

interface MessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: 'POLICY_DOC' | 'USER_SQL' | 'REFUSE_OOS';
  modelUsed?: string;
  citations?: CitationItem[];
  latencyMs?: number;
  cached?: boolean;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-widget" [class.minimized]="isMinimized()">
      <!-- Chat Header -->
      <div class="chat-header" (click)="toggleMinimize()">
        <div class="header-left">
          <span class="status-indicator"></span>
          <span class="header-title">🤖 Capgemini AI Banking Assistant</span>
        </div>
        <div class="header-actions">
          <button class="icon-btn" (click)="$event.stopPropagation(); toggleMinimize()">
            {{ isMinimized() ? '▲' : '▼' }}
          </button>
        </div>
      </div>

      <!-- Chat Body -->
      <div class="chat-body" *ngIf="!isMinimized()">
        <!-- Model Selector & Info Bar -->
        <div class="model-bar">
          <label>Active Engine:</label>
          <select [(ngModel)]="selectedModel" (change)="onModelChange()">
            <option *ngFor="let m of availableModels()" [value]="m">{{ m }}</option>
          </select>
        </div>

        <!-- Quick Prompts -->
        <div class="quick-prompts">
          <button (click)="sendQuickPrompt('What is the base interest rate and floating spread for a Home Loan?')">
            🏠 Home Loan Rates
          </button>
          <button (click)="sendQuickPrompt('What is my current account balance?')">
            💰 My Live Balance
          </button>
          <button (click)="sendQuickPrompt('What is the penalty for premature withdrawal of a 1-year FD?')">
            📑 1-Yr FD Rules
          </button>
        </div>

        <!-- Messages Area -->
        <div class="messages-container" #scrollArea>
          <div *ngIf="messages().length === 0" class="welcome-banner">
            <p>👋 Hello! I am your AI Banking Assistant.</p>
            <small>Ask me policy rules, FD/loan rates, or your secure account balance.</small>
          </div>

          <div *ngFor="let msg of messages()" [class]="'msg-row ' + msg.role">
            <div class="msg-bubble">
              <!-- Intent Badge -->
              <div *ngIf="msg.intent" class="intent-badge" [ngClass]="msg.intent">
                <span *ngIf="msg.intent === 'POLICY_DOC'">📚 Policy Document RAG</span>
                <span *ngIf="msg.intent === 'USER_SQL'">🔒 User-Scoped Database Query</span>
                <span *ngIf="msg.intent === 'REFUSE_OOS'">🛡️ Security Guardrail Triggered</span>
                <span *ngIf="msg.cached" class="cached-pill">⚡ Cached ({{ msg.latencyMs }}ms)</span>
              </div>

              <!-- Message Content -->
              <div class="msg-text">{{ msg.content }}</div>

              <!-- Citations Section -->
              <div *ngIf="msg.citations && msg.citations.length > 0" class="citations-box">
                <div class="citations-header">
                  <span>📎 Source Citations ({{ msg.citations.length }})</span>
                </div>
                <div *ngFor="let c of msg.citations" class="citation-item">
                  <strong>📄 {{ c.filename }}</strong> (Page/Chunk {{ c.chunk_index + 1 }}) - Match: {{ (c.score * 100).toFixed(1) }}%
                  <p class="snippet">"{{ c.snippet }}"</p>
                </div>
              </div>

              <!-- Feedback & Meta Footer -->
              <div class="msg-meta" *ngIf="msg.role === 'assistant'">
                <span class="meta-item">{{ msg.modelUsed }} | {{ msg.latencyMs }}ms</span>
                <div class="feedback-group">
                  <button (click)="sendFeedback(1)" title="Helpful answer">👍</button>
                  <button (click)="sendFeedback(-1)" title="Needs improvement">👎</button>
                </div>
              </div>
            </div>
          </div>

          <div *ngIf="loading()" class="msg-row assistant">
            <div class="msg-bubble loading-dots">
              <span>Thinking with {{ selectedModel }}</span>
              <div class="dot-flashing"></div>
            </div>
          </div>
        </div>

        <!-- Chat Input Bar -->
        <div class="chat-input-bar">
          <input
            type="text"
            [(ngModel)]="inputText"
            (keyup.enter)="sendMessage()"
            placeholder="Type your banking question..."
            [disabled]="loading()"
          />
          <button (click)="sendMessage()" [disabled]="!inputText.trim() || loading()" class="send-btn">
            ➤
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-widget {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 440px;
      height: 600px;
      background: #0f172a;
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 16px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      z-index: 1000;
      font-family: 'Segoe UI', system-ui, sans-serif;
      color: #e2e8f0;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .chat-widget.minimized {
      height: 52px;
      width: 320px;
    }
    .chat-header {
      background: linear-gradient(135deg, #0284c7, #0369a1);
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      color: #ffffff;
      font-weight: 600;
      font-size: 14px;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .status-indicator {
      width: 8px;
      height: 8px;
      background: #4ade80;
      border-radius: 50%;
      box-shadow: 0 0 8px #4ade80;
    }
    .icon-btn {
      background: transparent;
      border: none;
      color: #ffffff;
      cursor: pointer;
      font-size: 14px;
    }
    .chat-body {
      display: flex;
      flex-direction: column;
      flex: 1;
      height: calc(100% - 52px);
      background: #0b1120;
    }
    .model-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.03);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 11px;
      color: #94a3b8;
    }
    .model-bar select {
      background: #1e293b;
      border: 1px solid #334155;
      color: #38bdf8;
      font-size: 11px;
      padding: 3px 6px;
      border-radius: 6px;
      outline: none;
    }
    .quick-prompts {
      display: flex;
      gap: 6px;
      padding: 6px 12px;
      overflow-x: auto;
      background: rgba(0, 0, 0, 0.2);
    }
    .quick-prompts button {
      background: rgba(14, 165, 233, 0.12);
      border: 1px solid rgba(14, 165, 233, 0.25);
      color: #7dd3fc;
      border-radius: 12px;
      padding: 4px 10px;
      font-size: 11px;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s;
    }
    .quick-prompts button:hover {
      background: rgba(14, 165, 233, 0.25);
    }
    .messages-container {
      flex: 1;
      padding: 12px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .welcome-banner {
      text-align: center;
      padding: 24px 12px;
      color: #94a3b8;
    }
    .msg-row {
      display: flex;
      flex-direction: column;
    }
    .msg-row.user {
      align-items: flex-end;
    }
    .msg-row.assistant {
      align-items: flex-start;
    }
    .msg-bubble {
      max-width: 88%;
      padding: 10px 14px;
      border-radius: 12px;
      font-size: 13px;
      line-height: 1.5;
    }
    .msg-row.user .msg-bubble {
      background: #0284c7;
      color: #ffffff;
      border-bottom-right-radius: 2px;
    }
    .msg-row.assistant .msg-bubble {
      background: #1e293b;
      color: #f1f5f9;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-bottom-left-radius: 2px;
    }
    .intent-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 10px;
      margin-bottom: 6px;
    }
    .intent-badge.POLICY_DOC {
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .intent-badge.USER_SQL {
      background: rgba(52, 211, 153, 0.2);
      color: #34d399;
      border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .intent-badge.REFUSE_OOS {
      background: rgba(248, 113, 113, 0.2);
      color: #f87171;
      border: 1px solid rgba(248, 113, 113, 0.3);
    }
    .cached-pill {
      margin-left: 4px;
      color: #facc15;
    }
    .citations-box {
      margin-top: 8px;
      padding: 8px;
      background: rgba(0, 0, 0, 0.25);
      border-radius: 8px;
      border: 1px dashed rgba(56, 189, 248, 0.2);
      font-size: 11px;
    }
    .citations-header {
      color: #38bdf8;
      font-weight: 600;
      margin-bottom: 4px;
    }
    .citation-item {
      margin-bottom: 6px;
      color: #cbd5e1;
    }
    .snippet {
      margin: 2px 0 0 0;
      color: #94a3b8;
      font-style: italic;
    }
    .msg-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 6px;
      font-size: 10px;
      color: #64748b;
    }
    .feedback-group button {
      background: transparent;
      border: none;
      cursor: pointer;
      font-size: 12px;
      padding: 0 3px;
    }
    .chat-input-bar {
      padding: 10px 12px;
      background: #0f172a;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      gap: 8px;
    }
    .chat-input-bar input {
      flex: 1;
      padding: 10px 12px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #ffffff;
      font-size: 13px;
      outline: none;
    }
    .chat-input-bar input:focus {
      border-color: #0284c7;
    }
    .send-btn {
      padding: 0 16px;
      background: #0284c7;
      border: none;
      border-radius: 8px;
      color: #ffffff;
      cursor: pointer;
      font-size: 14px;
      transition: background 0.2s;
    }
    .send-btn:hover:not(:disabled) {
      background: #0369a1;
    }
  `]
})
export class ChatComponent implements OnInit {
  isMinimized = signal<boolean>(false);
  availableModels = signal<string[]>(['openai.gpt-5', 'openai.gpt-4o', 'anthropic.claude-opus-4-6-v1', 'grok-4']);
  selectedModel = 'openai.gpt-5';
  messages = signal<MessageItem[]>([]);
  inputText = '';
  loading = signal<boolean>(false);
  sessionId = 'sess-' + Math.random().toString(36).substring(2, 9);

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.chatService.getModels().subscribe({
      next: (res) => {
        if (res.available_models) {
          this.availableModels.set(res.available_models);
          this.selectedModel = res.default_model || res.available_models[0];
        }
      }
    });
  }

  toggleMinimize(): void {
    this.isMinimized.set(!this.isMinimized());
  }

  onModelChange(): void {}

  sendQuickPrompt(prompt: string): void {
    this.inputText = prompt;
    this.sendMessage();
  }

  sendMessage(): void {
    const text = this.inputText.trim();
    if (!text || this.loading()) return;

    this.messages.update((list) => [
      ...list,
      {
        id: 'usr-' + Date.now(),
        role: 'user',
        content: text,
        timestamp: new Date()
      }
    ]);

    this.inputText = '';
    this.loading.set(true);

    this.chatService.ask({
      message: text,
      session_id: this.sessionId,
      model: this.selectedModel
    }).subscribe({
      next: (res: ChatResponse) => {
        this.loading.set(false);
        this.messages.update((list) => [
          ...list,
          {
            id: 'ast-' + Date.now(),
            role: 'assistant',
            content: res.answer,
            intent: res.intent,
            modelUsed: res.model_used,
            citations: res.citations,
            latencyMs: res.latency_ms,
            cached: res.cached,
            timestamp: new Date()
          }
        ]);
      },
      error: (err) => {
        this.loading.set(false);
        this.messages.update((list) => [
          ...list,
          {
            id: 'err-' + Date.now(),
            role: 'assistant',
            content: err.error?.detail || 'Unable to connect to AI engine. Please verify connectivity.',
            timestamp: new Date()
          }
        ]);
      }
    });
  }

  sendFeedback(rating: number): void {
    this.chatService.submitFeedback(rating, 'User feedback via widget').subscribe();
    alert('Thank you for your feedback!');
  }
}
