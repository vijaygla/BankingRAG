# Capgemini Apex Commercial Bank - Enterprise AI Banking & RAG Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQL Server](https://img.shields.io/badge/Database-MS%20SQL%20Server%202022-CC292B?logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/sql-server)
[![Capgemini Generative Engine](https://img.shields.io/badge/AI%20Engine-Capgemini%20Generative%20Engine-0070AD)](https://openai.generative.engine.capgemini.com/v1)
[![Angular](https://img.shields.io/badge/Frontend-Angular%2021-DD0031?logo=angular&logoColor=white)](https://angular.dev)
[![Python](https://img.shields.io/badge/Python-3.12.10-blue?logo=python&logoColor=white)](https://python.org)

An enterprise-grade, secure, multi-role financial banking portal and intelligent conversational assistant powered by **FastAPI**, **Microsoft SQL Server 2022**, the **Capgemini Generative Engine Platform**, and **Angular 21**.

---

## 🏛️ Project Highlights & 5 Core Use Cases

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             5 CORE SYSTEM USE CASES                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. Foundation & Core Retrieval: Multi-format chunking (800/120) & MS SQL vectors  │
│ 2. End-to-End RAG Assistant: Policy guidelines with precise source citations     │
│ 3. Secure Banking Data Integration: User-scoped Text-to-SQL with PII masking     │
│ 4. Intelligence Maturity: Query caching (0-token response) & telemetry metrics    │
│ 5. Unified Integration: Smart Intent Classifier Router with strict RBAC          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

1. **Foundation & Core Retrieval for Banking Policies:** Background pipeline supporting multi-format document parsing (**PDF**, **JSON**, and **TXT**). Chunks documents at 800-token boundaries with 120-token window overlap (`cl100k_base` BPE tokenization) and converts text into 1536-dimensional vector embeddings using Capgemini Generative Engine (`text-embedding-3-small`), indexed inside MS SQL Server.
2. **End-to-End RAG Banking Assistant:** Answers compliance, loan guidelines, and interest rate inquiries accurately. Attaches a **Source Citations Engine** linking every response back to its exact filename, document title, and page/chunk index with cosine similarity scores.
3. **Secure Banking Data Integration (User-Scoped Text-to-SQL):** Customers query their live balance, credit cards, loans, and transaction history using natural language. Strictly filtered by `WHERE user_id = :current_user_id` with automated PII masking (`AC*******1023`, `4111********1234`).
4. **Intelligence Maturity & Optimization:** Built-in **Conversational Query Caching** in MS SQL Server. Duplicate queries resolve in **~5ms with 0 token consumption**. Real-time computational telemetry (`/metrics`) tracks latency benchmarks, token usage, and cache hit ratios.
5. **Final Integrated Banking RAG System:** Centralized **Smart Intent Classifier Router** at the API gateway that routes incoming traffic to `POLICY_DOC` (Vector RAG), `USER_SQL` (Personal Database), or `REFUSE_OOS` (Security Refusal).

---

## 👥 3-Role Authorization & Workflows

### 👤 Customer (Retail Banking User)
- **Self-Registration:** Public registration (`POST /api/v1/auth/register`) automatically assigns `CUSTOMER` role and `KYC_PENDING` status. No role selection dropdown is exposed.
- **Personal Banking Dashboard:** Live balances, credit card limits, loan repayment schedules, and transaction ledger.
- **Identity Verification:** Submits PAN, Aadhaar, or Passport proof for staff review.
- **AI Assistant:** Interacts with the AI Assistant for policy guidance and personal financial data queries.
- **Access Control:** Blocked from staff KYC queues and admin management with `403 Forbidden`.

### 💼 Employee (Bank Staff Operations)
- **Provisioning:** Exclusively created through the Admin portal (`POST /api/v1/admin/employees`). No public registration.
- **Pending KYC Workspace:** Audits customer identity documents (`GET /api/v1/staff/kyc-queue`, `POST /api/v1/staff/kyc-verify/{id}`).
- **Account Core Activation:** Generates a unique 10-digit account string code (e.g. `4633179749`), sets up a Primary Savings account with initial credit, provisions a Platinum Rewards credit card, and activates user status to `ACTIVE`.
- **Support Operations:** Reviews and resolves customer support tickets.
- **Access Control:** Blocked from admin functions (employee provisioning, document ingestion) with `403 Forbidden`.

### ⚙️ Admin (System Super-User)
- **Super-User Auto-Seeding:** Master administrator account (`admin@capgemini-bank.com`) is auto-seeded in MS SQL on initial startup.
- **Employee Provisioning:** Creates and authorizes bank staff profiles.
- **Knowledge Ingestion:** Drag-and-drop ingestion of PDF, JSON, and TXT policy rulebooks (`POST /api/v1/ingest`).
- **Telemetry & Governance:** Monitors latency benchmarks, token consumption, cache hit ratios (`/metrics`), and inspects immutable compliance audit logs (`/admin/audit-logs`).

---

## 🏗️ Architecture Diagram

```mermaid
graph TD
    Client[Angular 21 Single Page App / HTTP Client] --> APIGateway[FastAPI Gateway /api/v1]

    subgraph Security & Access Control
        APIGateway --> AuthGuard[24-Hour JWT Token Validator & RBAC Guard]
        APIGateway --> Guardrails[Prompt Injection & SQL Scanner]
        APIGateway --> MaskingEngine[PII Data Masking Engine]
    end

    subgraph 3-Role Segregation
        AuthGuard -->|Role: CUSTOMER| CustomerRouter[Customer Dashboard & KYC Upload]
        AuthGuard -->|Role: EMPLOYEE| StaffRouter[KYC Queue & 10-Digit Account Activation]
        AuthGuard -->|Role: ADMIN| AdminRouter[Staff Provisioning, Ingest & Metrics]
    end

    subgraph AI Intelligence Pipeline
        APIGateway --> Router[Smart Intent Classifier Router]
        Router -->|POLICY_DOC| CacheEngine[Query Cache Engine]
        CacheEngine -->|Cache Miss| RAGRetrieval[Vector Retrieval & Citations Engine]
        Router -->|USER_SQL| SafeSQL[User-Scoped Text-to-SQL Executor]
        Router -->|REFUSE_OOS| Refusal[Security Guardrail Interceptor]
    end

    subgraph External LLM Gateway
        RAGRetrieval --> CapgeminiAI[Capgemini Generative Engine]
        CapgeminiAI --> GPT5[openai.gpt-5]
        CapgeminiAI --> GPT4o[openai.gpt-4o]
        CapgeminiAI --> Claude[anthropic.claude-opus-4-6-v1]
        CapgeminiAI --> Grok[grok-4]
        RAGRetrieval --> Embeddings[text-embedding-3-small]
    end

    subgraph Persistence Layer
        SafeSQL --> MSSQL[(Microsoft SQL Server 2022: BankingAppRAG)]
        RAGRetrieval --> MSSQL
        CustomerRouter --> MSSQL
        StaffRouter --> MSSQL
        AdminRouter --> MSSQL
    end
```

---

## 🛠️ Technology Stack

| Layer | Component | Specification |
|---|---|---|
| **Backend** | FastAPI / Python 3.12 | Asynchronous REST API, Pydantic v2 schemas |
| **Database** | Microsoft SQL Server 2022 | 13 relational tables with foreign keys and indexes |
| **ODBC Driver**| ODBC Driver 18 for SQL Server | `pyodbc` connection pooling with TLS encryption |
| **ORM** | SQLAlchemy 2.0 | Parameterized queries, schema migrations |
| **AI Platform**| Capgemini Generative Engine | US Hosted OpenAI-compatible endpoint |
| **AI Models** | GPT-5, GPT-4o, Claude, Grok-4 | Multi-model runtime selection |
| **Embeddings** | `text-embedding-3-small` | 1536-dimensional vector representations |
| **Frontend** | Angular 21 | Standalone components, reactive signals, client routing |
| **Security** | BCrypt / PyJWT | 24-hr cryptographically signed JWT tokens |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+** installed
- **Node.js (v20+ or v25)** and **npm** installed
- **ODBC Driver 18 for SQL Server** installed
- **Microsoft SQL Server 2022** instance accessible

---

### Step 1: Backend Setup

1. Open PowerShell and navigate to `backend`:
   ```powershell
   cd "c:\Users\vkuma141\OneDrive - Capgemini\Desktop\capg\L2\BankingAppRAG\backend"
   ```
2. Verify environment configuration in `.env`:
   ```env
   API_V1_STR="/api/v1"
   DATABASE_URL="mssql+pyodbc://sa:Capgemini%4012345@LIN-5CD6268KRS/BankingAppRAG?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes"
   JWT_SECRET="c6b547285627f12e8b2b6c164a6d36e890c0a34b21e8b4e78a2e1d7f6c5b4a39"
   JWT_ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=1440

   CAPGEMINI_AI_API_KEY="sk-x3FOSdELzRNhQ1fpzloftA"
   CAPGEMINI_AI_ENDPOINT="https://openai.generative.engine.capgemini.com/v1"
   DEFAULT_AI_MODEL="openai.gpt-5"
   EMBEDDING_MODEL="text-embedding-3-small"

   ADMIN_EMAIL="admin@capgemini-bank.com"
   ADMIN_PASSWORD="Admin@Capgemini123"
   ADMIN_NAME="System Super Admin"
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Start the FastAPI backend server:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - **Backend API:** `http://127.0.0.1:8000`
   - **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
   - **Health Monitor:** `http://127.0.0.1:8000/api/v1/health`

---

### Step 2: Frontend Setup

1. Open a second PowerShell window and navigate to `frontend`:
   ```powershell
   cd "c:\Users\vkuma141\OneDrive - Capgemini\Desktop\capg\L2\BankingAppRAG\frontend"
   ```
2. Install dependencies:
   ```powershell
   npm install
   ```
3. Start the Angular development server:
   ```powershell
   npm start
   ```
   - **Angular Web Application:** [http://localhost:4200](http://localhost:4200)

---

### Step 3: Run Automated Test Suite

To verify all 23 end-to-end integration test scenarios against MS SQL Server and Capgemini Generative Engine:
```powershell
cd "c:\Users\vkuma141\OneDrive - Capgemini\Desktop\capg\L2\BankingAppRAG\backend"
python tests/test_api_suite.py
```

---

## 🔑 Pre-Configured Demo Credentials

| Role | Email | Password | Allowed Access |
|---|---|---|---|
| **System Super-Admin** | `admin@capgemini-bank.com` | `Admin@Capgemini123` | Full administrative control, staff provisioning, RAG ingestion, telemetry |
| **Bank Staff (Employee)** | `priya.verma@capgemini-bank.com` | `Staff@Priya2026` | KYC queue workspace, document audit, 10-digit account core activation |
| **Retail Customer** | `sneha.kulkarni@gmail.com` | `Customer@Sneha123` | Personal balances, credit cards, loans, KYC submit, AI chatbot |

---

## 📄 Knowledge Assets Included for RAG Ingestion

The repository includes 3 baseline banking knowledge assets in `backend/app/data/`:
1. `banking_interest_rates.json`: Tiered savings accounts APY, 1/3/5-year fixed deposit schemes, and home/personal/auto lending rates.
2. `loan_compliance_rules.txt`: General eligibility criteria, LTV ratios, CIBIL thresholds, foreclosure rules, and penalty policies.
3. `banking_policy.pdf`: Comprehensive official banking operating manual and customer guidelines.

---

## 💡 How to Ingest New Documents & Optimize Tokens

### Uploading New Documents
- **Via Swagger UI:** Navigate to `POST /api/v1/ingest` on [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), authenticate with the Admin token, and upload any `.pdf`, `.json`, or `.txt` file.
- **Via cURL:**
  ```powershell
  curl -X POST "http://127.0.0.1:8000/api/v1/ingest" `
    -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" `
    -F "file=@C:\path\to\your_document.pdf" `
    -F "title=Card Rewards Policy 2026"
  ```

### Built-in Token-Saving Mechanisms
1. **Conversational Query Caching (`query_cache`):** Duplicate policy queries are resolved via normalized SHA-256 hash lookup in MS SQL, returning in **~5ms with 0 LLM tokens consumed**.
2. **Intent Classifier Bypasses:** Account balance queries (`USER_SQL`) and prompt injections (`REFUSE_OOS`) are handled locally, consuming **0 LLM tokens**.
3. **800-Token Chunking with 120-Token Overlap:** Ensures chunks remain concise, eliminating unnecessary prompt bloating.
4. **Sliding-Window Memory:** Limits conversation context to the **last 4 turns**, preventing historical token accumulation.

---

## 📁 Repository Directory Structure

```
BankingAppRAG/
├── HLD.md                          # High-Level Design Document
├── LLD.md                          # Low-Level Design Document
├── README.md                       # Comprehensive User & Developer Guide
├── backend/
│   ├── .env                        # Secrets and connection strings
│   ├── requirements.txt            # Python dependencies
│   ├── api-testing.http            # 28-point REST client test script
│   ├── tests/
│   │   └── test_api_suite.py       # End-to-end integration test runner
│   └── app/
│       ├── main.py                 # FastAPI application & startup lifecycle
│       ├── core/                   # Config, security, guardrails, masking
│       ├── db/                     # SQLAlchemy MS SQL sessionmaker
│       ├── models/                 # 13 SQL tables
│       ├── schemas/                # Pydantic v2 schemas
│       ├── services/               # Business logic services
│       ├── ai/                     # RAG, Text-to-SQL, cache, intent classifier
│       ├── api/                    # API v1 routers & RBAC dependencies
│       └── data/                   # Sample JSON, TXT, and PDF assets
└── frontend/
    ├── angular.json
    ├── package.json
    └── src/
        ├── app/
        │   ├── app.ts              # Root standalone component
        │   ├── app.config.ts       # Application config with provideHttpClient
        │   ├── app.routes.ts       # Protected client-side routes
        │   ├── guards/role.guard.ts# RBAC route guard
        │   ├── services/           # Angular services (Auth, API, Chat)
        │   └── components/         # Auth, Customer, Staff, Admin, Chat
        └── styles.css              # Dark mode design tokens
```

---

## 📜 Documentation Links
- **High-Level Design (HLD):** [HLD.md](file:///c:/Users/vkuma141/OneDrive%20-%20Capgemini/Desktop/capg/L2/BankingAppRAG-HLD.md)
- **Low-Level Design (LLD):** [LLD.md](file:///c:/Users/vkuma141/OneDrive%20-%20Capgemini/Desktop/capg/L2/BankingAppRAG-LLD.md)
- **Prompt Engineering & Testing Guide:** [BankingAppRAG-Prompts.md](file:///c:/Users/vkuma141/OneDrive%20-%20Capgemini/Desktop/capg/L2/BankingAppRAG-Prompts.md)
- **REST Testing File:** [api-testing.http](file:///c:/Users/vkuma141/OneDrive%20-%20Capgemini/Desktop/capg/L2/BankingAppRAG/backend/api-testing.http)

# Command to run
1. Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
2. frontend
npm start

---
• Total AI Queries Processed: The total number of questions or requests sent to and handled by the AI system (20 in this case).
• Average Model Latency: The average time it takes for the AI to generate a response, measured in milliseconds (2912.82 ms is about 2.9 seconds).
• Total Tokens Consumed: The total amount of text data processed by the AI, where tokens are chunks of words or characters (9,091 tokens total).
• Cache Memory Hit Rate: How often the system reuses previously saved answers to respond instantly instead of generating a new answer from scratch.


---
What is the primary purpose of the Retail Account Ownership and Maintenance policy?
