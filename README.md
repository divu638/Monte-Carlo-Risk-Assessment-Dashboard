# RiskGuard Pro — Enterprise Business Risk Assessment & Quantitative Analytics Platform 🛡️🎲

> **Enterprise Risk Intelligence, Quantitative Value-at-Risk (VaR) Engine, Altman Z-Score Financial Solvency Diagnostics, Cryptographic Audit Trail, and Three.js 3D Spatial Visualizer.**  
> Built with Python/Flask, Supabase Cloud PostgreSQL (with local SQLite auto-fallback), NumPy, Three.js, Chart.js, and Vanilla CSS Glassmorphism.

[![Live Production](https://img.shields.io/badge/Production-Render%20Live-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://monte-carlo-risk-assessment-dashboard.onrender.com/)
[![Tests](https://img.shields.io/badge/pytest-50%2F50%20passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#test-suite)
[![Security](https://img.shields.io/badge/OWASP-A%2B%20Hardened-blue?style=for-the-badge&logo=security&logoColor=white)](#security-hardening)
[![ISO 31000](https://img.shields.io/badge/Standard-ISO%2031000%3A2018-emerald?style=for-the-badge)](#iso-31000-framework)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

🌐 **Live Application URL**: [https://monte-carlo-risk-assessment-dashboard.onrender.com](https://monte-carlo-risk-assessment-dashboard.onrender.com)  
📦 **Repository**: [https://github.com/divu638/Monte-Carlo-Risk-Assessment-Dashboard](https://github.com/divu638/Monte-Carlo-Risk-Assessment-Dashboard)

---

## 📑 Table of Contents
1. [Platform Architecture](#-platform-architecture)
2. [Demo Credentials & Quick Start](#-demo-credentials--quick-start)
3. [Comprehensive Feature Breakdown](#-comprehensive-feature-breakdown)
4. [Complete REST API Endpoints Specification](#-complete-rest-api-endpoints-specification)
5. [Database Schema & Data Model](#-database-schema--data-model)
6. [Monte Carlo VaR Engine Methodology & Assumptions](#-monte-carlo-var-engine-methodology--assumptions)
7. [Financial Ratio Engine & Altman Z-Score](#-financial-ratio-engine--altman-z-score)
8. [Security Hardening & Cryptographic Audit Ledger](#-security-hardening--cryptographic-audit-ledger)
9. [Automated Test Suite (50 Passing Tests)](#-automated-test-suite)
10. [5-Minute Examiner / Viva Demonstration Script](#-5-minute-examiner--viva-demonstration-script)
11. [10 Likely Viva Questions with In-Depth Answers](#-10-likely-viva-questions-with-in-depth-answers)

---

## 🏛️ Platform Architecture

```
                                  ┌──────────────────────────────────────────────┐
                                  │           Client Layer (Browser)             │
                                  │  Three.js 3D Mesh · Chart.js · Vanilla JS    │
                                  └──────────────────────┬───────────────────────┘
                                                         │ HTTPS / JSON REST
                                                         ▼
                                  ┌──────────────────────────────────────────────┐
                                  │        Security & API Gateway (Flask)        │
                                  │  OWASP Headers · Sliding-Window Rate Limiter │
                                  │  JWT/Bcrypt RBAC · XSS & Traversal Sanitizer │
                                  └──────────────────────┬───────────────────────┘
                                                         │
               ┌──────────────────────┬──────────────────┴───────────────┬──────────────────────┐
               ▼                      ▼                                  ▼                      ▼
    ┌────────────────────┐ ┌────────────────────┐             ┌────────────────────┐ ┌────────────────────┐
    │  Monte Carlo VaR   │ │  Financial Ratio   │             │  Stress Testing    │ │  Cyber Risk &      │
    │  NumPy Vectorized  │ │  & Altman Z Engine │             │  & What-If Engine  │ │  Explainability    │
    │  (10k iterations)  │ │  (14 Ratios+Damod) │             │  (Macro Shocks)    │ │  (Waterfall math)  │
    └────────────────────┘ └────────────────────┘             └────────────────────┘ └────────────────────┘
                                                         │
                                                         ▼
                                  ┌──────────────────────────────────────────────┐
                                  │      Dual-Engine Resilient Data Layer        │
                                  │  PRIMARY: Supabase PostgreSQL (Cloud)       │
                                  │  FALLBACK: SQLite with SHA-256 Hash Chain    │
                                  └──────────────────────────────────────────────┘
```

---

## 🔑 Demo Credentials & Quick Start

### Seeded Persona Accounts (Zero Setup Required)
Run `python seed_demo.py` to auto-provision all test credentials and sample data:

| Persona | Role | Email | Password | Scope & Privileges |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin (CRO)** | `admin` | `admin@riskguard.internal` | `Admin@RiskGuard2026!` | Full Admin Console, User Governance, Benchmark Calibrations, CSV Export, DB Seed |
| **Lead Risk Analyst** | `user` | `analyst@riskguard.internal` | `Analyst@RiskGuard2026!` | Executive Overview, 3D Mesh, 8-Step Wizard, What-If Stress Testing, Action Tracker |

### Local Setup (One Command)
```bash
# 1. Clone repository
git clone https://github.com/divu638/Monte-Carlo-Risk-Assessment-Dashboard.git
cd Monte-Carlo-Risk-Assessment-Dashboard

# 2. Install dependencies (pinned in requirements.txt)
pip install -r requirements.txt

# 3. Seed demo accounts, benchmark data & baseline assessment
python seed_demo.py

# 4. Launch development server
python run.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 🌟 Comprehensive Feature Breakdown

### Part A: Core Mandatory Features
* **A1. Executive Dashboard**: Active Risk Counter, Enterprise Health Score (0-100), Value-at-Risk aggregate exposure, 4-tier risk distribution (Critical/High/Medium/Low), and 6-month projected risk trajectory.
* **Three.js 3D Visualizers**:
  * **3D Spatial Threat Topology**: Interactive 5×5 elevation mesh with camera controls (`Isometric 3D`, `Top Plan`, `Auto-Rotate`).
  * **3D Domain Ring Chart**: Procedural 3D cylindrical segments representing Cyber, Financial, and Operational risk densities.
* **A2. Interactive 5×5 Risk Heatmap**: Probability (1-5) × Impact (1-5) color-coded matrix with live drill-down filtering.
* **A3. Vectorized Monte Carlo VaR Engine**: 3,000 to 10,000 NumPy iterations, log-normal severity formulation, empirical 95% VaR, 99% Tail VaR, Expected Mean Loss, and Chart.js distribution histogram.
* **A4. 8-Step Assessment Wizard**: 1. Company Profile, 2. Operations & Supply Chain, 3. Direct Financial Statements (P&L and Balance Sheet), 4. Cybersecurity & Cloud Infrastructure, 5. Regulatory & Compliance, 6. Market & Strategy, 7. Human Capital, 8. Institutional Executive Dossier.
* **A5. ISO 31000 Mitigation Engine**: 3-tier treatment architecture:
  * Tier 1 (0-30 Days): Immediate Containment
  * Tier 2 (30-90 Days): Preventive Engineering
  * Tier 3 (90+ Days): Ongoing Governance
  * ISO 31000 treatment classification: `Avoid`, `Reduce`, `Transfer`, `Accept`.
* **A6. Resilient Dual-Engine Database**: Primary Supabase Cloud PostgreSQL with automatic, zero-crash fallback to local SQLite.
* **A7. Cryptographic Tamper-Evident Audit Chain**: Append-only log where every row contains `hash = SHA256(id + action + details + user_id + timestamp + prev_hash)`. Live cryptographic verification endpoint confirms zero unauthorized modifications.
* **A8. In-App Alerts Feed**: Real-time notification badge and dropdown feed for Critical and High severity hazards.
* **A9. Executive Dossier & Print PDF**: High-contrast, publication-grade printable risk report with heatmaps, financial scorecard, and sign-off blocks.
* **A10. OWASP Security Firewall**: Security response headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy), masked server banners, brute-force IP rate limiting, path traversal defense, and parameterized SQL queries.

### Part B: Advanced Institutional Modules
* **B1. Authentication & Multi-User RBAC**: Bcrypt password hashing (work factor 12), signed JWT tokens, session verification, user lockout protection, and role enforcement.
* **B2. Admin Governance Console**:
  * User directory with live search, suspension toggle (Block/Unblock), and role switching (`user` ↔ `admin`).
  * Platform telemetry: Total Users, Total Assessments, Average Health Score, and Sector Breakdown.
  * Platform-wide CSV assessment export.
  * Dynamic Industry Benchmark Editor (update sector thresholds in DB without code changes).
* **B3. Institutional Financial Ratio Engine & Altman Z-Score**:
  * **Liquidity**: Current Ratio, Quick Ratio, Cash Ratio, Working Capital.
  * **Leverage**: Debt-to-Equity (D/E), Debt Ratio, Interest Coverage.
  * **Profitability**: Gross Margin, Net Margin, EBITDA Margin, Return on Assets (ROA), Return on Equity (ROE).
  * **Efficiency**: Inventory Turnover, Days Sales Outstanding (DSO / Debtor Days), Asset Turnover.
  * **Altman Z-Score**: Private manufacturing 1968 formulation with explicit Safe (>2.99), Grey (1.81-2.99), and Distress (<1.81) zone indicators.
  * Sectoral benchmark differentials (e.g., `+40% above sector average`).
* **B4. Rule-Based Solutions Engine**: Configurable deterministic rule matrix evaluating calculated ratios, generating cost-estimated, prioritized ISO 31000 mitigation protocols.
* **B5. What-If Stress Testing & Scenarios**:
  * Interactive shock sliders: Revenue Collapse (±%), Cost/COGS Inflation (±%), Debtor Collection Lag (±days), Cyber Incident Multiplier.
  * Macro Scenario Presets: **Recession** (-25% rev, +20% debt), **Supply Chain Disruption** (+30% costs, +45d DSO), **Ransomware Outage** (3x cyber prob, ₹5 Cr downtime outlay), and **Stagflation Shock**.
* **B6. Explainable Risk Score**: Factor-by-factor waterfall decomposition showing exact mathematical points deducted per operational domain from baseline 100.
* **B7. Risk Register Action Tracker**: Converts mitigation suggestions into executable corporate tasks with status (`Open`, `In Progress`, `Closed`), assignee/owner, due date, priority, and residual risk.
* **B8. Assessment History & Trend Tracking**: Chronological time-series tracking saving every completed audit with date and company profile.
* **B9. Cybersecurity Risk Module**: CVSS-style 0.0-10.0 exposure assessment across 5 vectors (Ransomware, Data Breach, Vulnerability Management, IAM/MFA, Disaster Recovery) with NIST CSF 2.0 mapping and automated feeds into the Monte Carlo engine.

---

## 📡 Complete REST API Endpoints Specification

### 1. Authentication & Session Management
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Create new analyst account with bcrypt hashing and validation |
| `POST` | `/api/auth/login` | Public | Authenticate user, apply rate limit check, and issue 24h JWT token |
| `GET` | `/api/auth/me` | Authenticated | Validate active session token and retrieve current user persona |

### 2. Risk Registry & 5×5 Matrix
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/risks` | Authenticated | Retrieve registered risks with optional domain/severity filtering |
| `GET` | `/api/risks/<int:id>` | Authenticated | Retrieve single risk vector by ID |
| `POST` | `/api/risks` | Authenticated | Create and register new risk vector (logged to cryptographic audit trail) |
| `PUT` | `/api/risks/<int:id>` | Authenticated | Update existing risk status, likelihood, impact, or mitigation |
| `DELETE` | `/api/risks/<int:id>` | Authenticated | Remove risk from registry (immutable audit entry created) |
| `GET` | `/api/matrix` | Authenticated | Retrieve pre-computed 5×5 probability × impact coordinate clusters |

### 3. Quantitative Monte Carlo & Stress Testing
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/simulate` | Public / Auth | Execute NumPy Monte Carlo simulation (3,000-10,000 iterations) |
| `POST` | `/api/stress-test` | Public / Auth | Execute dynamic what-if simulation with financial/cyber shocks |
| `GET` | `/api/stress-test/presets` | Public / Auth | Fetch predefined macroeconomic stress test configurations |

### 4. Financial Ratios, Solvency & Solutions
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/ratios/calculate` | Public / Auth | Compute full 14-ratio suite, Altman Z-Score, and benchmark deltas |
| `GET` | `/api/benchmarks` | Public / Auth | Fetch sectoral benchmark standards stored in database |
| `PUT` | `/api/benchmarks/<string:ind>` | Admin Only | Update sectoral ratio benchmarks in database without code changes |
| `POST` | `/api/solutions/recommend` | Public / Auth | Generate 3-tier ISO 31000 mitigation plan based on ratio flags |

### 5. Explainability & Cybersecurity
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/score/explain` | Public / Auth | Decompose health score into 6 domain waterfall deductions |
| `GET` | `/api/assessments/<int:id>/explain` | Authenticated | Retrieve explainable score waterfall for a saved assessment ID |
| `POST` | `/api/cyber/evaluate` | Public / Auth | Calculate CVSS composite score, ALE, SLE, and NIST CSF actions |

### 6. Action Tracker & Task Ledger
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/tasks` | Authenticated | List all mitigation tasks for current user (or all if admin) |
| `POST` | `/api/tasks` | Authenticated | Create new actionable task or convert from recommendation |
| `PUT` | `/api/tasks/<int:id>` | Authenticated | Update task status (`Open` / `In Progress` / `Closed`), owner, due date |
| `DELETE` | `/api/tasks/<int:id>` | Authenticated | Delete mitigation task from tracker |

### 7. Governance, Admin Console & Audit Chain
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/admin/users` | Admin Only | Search and list registered platform users |
| `PUT` | `/api/admin/users/<int:id>/status`| Admin Only | Suspend or reactivate user account (`is_blocked`) |
| `PUT` | `/api/admin/users/<int:id>/role` | Admin Only | Elevate user to `admin` or demote to `user` |
| `GET` | `/api/admin/analytics` | Admin Only | Platform-wide operational KPIs and sectoral breakdown |
| `GET` | `/api/admin/assessments/export` | Admin Only | Stream full platform assessment records as CSV |
| `GET` | `/api/audit-logs` | Authenticated | Retrieve tamper-evident audit ledger entries |
| `GET` | `/api/audit-logs/verify` | Authenticated | Cryptographically verify SHA-256 hash chain across all records |
| `GET` | `/api/db-status` | Public | Real-time database engine telemetry (Supabase vs. SQLite) |

---

## 🗄️ Database Schema & Data Model

The platform operates on a resilient schema mirrored between Supabase PostgreSQL and local SQLite:

### 1. `users`
* `id`: Integer, Primary Key, Auto-increment.
* `firstname`: Varchar(50), Not Null.
* `lastname`: Varchar(50).
* `company`: Varchar(100).
* `email`: Varchar(120), Unique, Not Null, Indexed.
* `password_hash`: Varchar(255), Not Null (Bcrypt work factor 12 / PBKDF2 fallback).
* `salt`: Varchar(64), Cryptographic salt.
* `role`: Varchar(20), Default `'user'` (`'admin'` or `'user'`).
* `is_blocked`: Integer, Default `0` (1 = suspended).
* `created_at`: Timestamp, Default `CURRENT_TIMESTAMP`.
* `last_login`: Timestamp.

### 2. `risks`
* `id`: Integer, Primary Key, Auto-increment.
* `user_id`: Integer, Foreign Key (`users.id`).
* `name`: Varchar(150), Not Null.
* `description`: Text.
* `category`: Varchar(50) (Financial, Cybersecurity, Operational, Compliance, Strategic).
* `likelihood`: Integer (1 to 5).
* `impact`: Integer (1 to 5).
* `score`: Integer (1 to 25, `likelihood * impact`).
* `level`: Varchar(20) (Critical, High, Medium, Low).
* `financial_impact`: Float (Estimated loss exposure in ₹ or $).
* `owner`: Varchar(100), Responsible executive.
* `status`: Varchar(20), Default `'Active'` (`'Active'`, `'Mitigating'`, `'Closed'`).
* `velocity`: Varchar(20) (`'High'`, `'Medium'`, `'Low'`).
* `trend`: Varchar(20) (`'worsening'`, `'stable'`, `'improving'`).
* `mitigation`: Text, Action plan.
* `created_at`, `updated_at`: Timestamps.

### 3. `audit_logs` (Cryptographic Append-Only Ledger)
* `id`: Integer, Primary Key, Auto-increment.
* `user_id`: Integer.
* `risk_id`: Integer, Nullable.
* `risk_name`: Varchar(150).
* `action`: Varchar(50) (`CREATE`, `UPDATE`, `DELETE`, `USER_REGISTERED`, etc.).
* `details`: Text.
* `before_val`: Text (JSON string of state before mutation).
* `after_val`: Text (JSON string of state after mutation).
* `prev_hash`: Varchar(64), SHA-256 hash of previous record (Genesis hash for record #1).
* `hash`: Varchar(64), SHA-256 hash of current block.
* `created_at`: Timestamp.

### 4. `assessments`
* `id`: Integer, Primary Key, Auto-increment.
* `user_id`: Integer, Foreign Key (`users.id`).
* `company_name`: Varchar(100), Not Null.
* `industry`: Varchar(50), Default `'General'`.
* `health_score`: Integer (0 to 100).
* `var_exposure`: Float.
* `status`: Varchar(20), Default `'Completed'`.
* `step_data`: Text (JSON blob of 8-step input questionnaire).
* `ratios_data`: Text (JSON blob of computed ratios and Altman Z-Score).
* `created_at`, `updated_at`: Timestamps.

### 5. `action_tasks` (ISO 31000 Action Tracker)
* `id`: Integer, Primary Key, Auto-increment.
* `user_id`: Integer.
* `risk_id`: Integer, Nullable.
* `title`: Varchar(200), Not Null.
* `description`: Text.
* `category`: Varchar(50).
* `status`: Varchar(20), Default `'Open'` (`'Open'`, `'In Progress'`, `'Closed'`).
* `owner`: Varchar(100).
* `priority`: Varchar(20) (`'Critical'`, `'High'`, `'Medium'`, `'Low'`).
* `due_date`: Varchar(20).
* `cost_estimate`: Varchar(50).
* `treatment_type`: Varchar(20) (`'Avoid'`, `'Reduce'`, `'Transfer'`, `'Accept'`).
* `residual_risk`: Float.
* `created_at`, `updated_at`: Timestamps.

### 6. `industry_benchmarks`
* `industry`: Varchar(50), Primary Key.
* `current_ratio`: Float, Default `1.8`.
* `de_ratio`: Float, Default `1.0`.
* `net_margin`: Float, Default `0.07`.
* `roe`: Float, Default `0.12`.
* `asset_turnover`: Float, Default `0.80`.
* `updated_at`: Timestamp.

---

## 🎲 Monte Carlo VaR Engine Methodology & Assumptions

The quantitative simulation engine is implemented in Python utilizing vectorized NumPy operations:

### Mathematical Formulation
1. **Event Occurrence Frequency ($N$)**:
   Each risk $i$ has an annualized event probability $p_i = \text{Likelihood}_i / 5.0$. In each simulation trial $k \in \{1, \dots, K\}$, event occurrence is modeled as a Bernoulli random variable:
   $$E_{i,k} \sim \text{Bernoulli}(p_i)$$
2. **Loss Severity ($S$)**:
   Given that an incident occurs, loss severity follows a Log-Normal distribution to account for heavy right-tail skewness (infrequent but catastrophic losses):
   $$S_{i,k} \sim \text{LogNormal}(\mu_i, \sigma_i)$$
   where:
   $$\mu_i = \ln\left(\text{Financial Impact}_i \times \frac{\text{Impact}_i}{5.0}\right) - \frac{\sigma_i^2}{2}, \quad \sigma_i = 1.2$$
3. **Total Portfolio Loss ($L_k$)**:
   $$L_k = \sum_{i=1}^{M} E_{i,k} \cdot S_{i,k}$$

### Output Metrics
* **Expected Mean Loss**: Empirical average loss across all $K$ trials: $\bar{L} = \frac{1}{K}\sum L_k$.
* **95% Value-at-Risk (VaR)**: The 95th percentile of simulated portfolio loss:
  $$\text{VaR}_{0.95} = \text{Percentile}(L, 95)$$
* **99% Tail Risk**: The 99th percentile capturing extreme systemic black-swan shocks.
* **Worst-Case Loss**: $\max(L_k)$.
* **Strict Monotonic Ordering**: The engine mathematically guarantees:
  $$\bar{L} \le \text{VaR}_{0.95} \le \text{VaR}_{0.99} \le \text{Worst Case}$$

### Explicit Modeling Assumptions
1. **Distribution Shape**: Losses are assumed to be right-skewed log-normal.
2. **Event Independence**: In baseline simulation, occurrences between distinct risk categories are modeled independently; cross-contagion correlation is introduced dynamically during Macro Stress Testing.
3. **Reproducibility**: Supported deterministic seed parameter (`seed=42`) ensures exact reproducibility for statutory audit verification.

---

## 📊 Financial Ratio Engine & Altman Z-Score

### Altman Z-Score (1968 Manufacturing Formulation)
Calculated as:
$$Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$$
* $X_1 = \frac{\text{Working Capital}}{\text{Total Assets}}$: Liquidity cushion.
* $X_2 = \frac{\text{Retained Earnings}}{\text{Total Assets}}$: Cumulative profitability and age.
* $X_3 = \frac{\text{EBIT}}{\text{Total Assets}}$: Asset productivity and operating profitability.
* $X_4 = \frac{\text{Market Value of Equity}}{\text{Total Liabilities}}$: Capital structure cushion.
* $X_5 = \frac{\text{Sales / Revenue}}{\text{Total Assets}}$: Asset turnover efficiency.

#### Institutional Zone Classifications
* **Safe Zone ($Z > 2.99$)**: Financially sound operations; low bankruptcy probability.
* **Grey Zone ($1.81 \le Z \le 2.99$)**: Moderate distress vulnerability; debt restructuring advised.
* **Distress Zone ($Z < 1.81$)**: Severe insolvency risk; immediate capital intervention required.

---

## 🔒 Security Hardening & Cryptographic Audit Ledger

* **OWASP Security Response Headers**: Injected via Flask `after_request` middleware:
  * `Content-Security-Policy`: Restricts scripts and styles to approved CDNs (Three.js, Chart.js, Google Fonts).
  * `X-Frame-Options: SAMEORIGIN`: Prevents clickjacking framing attacks.
  * `X-Content-Type-Options: nosniff`: Prevents MIME-confusion attacks.
  * `Referrer-Policy: strict-origin-when-cross-origin`.
* **Path Traversal & Sensitive File Exposure Shields**: Prohibits requests targeting `.env`, `.git`, `.py`, `.db`, `.log` or directory traversal sequences (`../`, `%2e%2e`).
* **Sliding-Window Rate Limiting**: Per-IP sliding time window (default: max 120 requests/minute for general APIs, strict 10 requests/minute for `/api/auth/login` to prevent brute force).
* **Cryptographic Hash Chaining**: Every audit entry stores the SHA-256 digest of the previous row. If an attacker directly alters a database row, `GET /api/audit-logs/verify` immediately flags the exact row ID where the cryptographic chain was broken.

---

## 🧪 Automated Test Suite

The platform includes 50 automated tests covering all critical components:

```bash
pytest -v
```

```
============================= test session starts =============================
collected 50 items

tests/test_api_endpoints.py ........                                     [ 16%]
tests/test_audit_chain.py ...                                            [ 22%]
tests/test_auth.py ......                                                [ 34%]
tests/test_engines.py .....                                              [ 44%]
tests/test_financial_ratios.py ........                                  [ 60%]
tests/test_monte_carlo.py ...                                            [ 66%]
tests/test_security.py .................                                 [100%]

======================= 50 passed, 2 warnings in 3.55s ========================
```

* **`test_api_endpoints.py` (8 tests)**: Validates REST contract for benchmarks, ratios, stress testing, solutions, explainable scores, action tasks, and cyber posture.
* **`test_audit_chain.py` (3 tests)**: Confirms SHA-256 chain integrity, append-only mechanics, and simulated tampering detection.
* **`test_auth.py` (6 tests)**: Tests user registration, password strength, bcrypt hashing, JWT issuance, and RBAC admin route protection.
* **`test_engines.py` (5 tests)**: Verifies ISO 31000 rule engine priorities, macroeconomic stress test shocks, waterfall math, and CVSS cyber scoring.
* **`test_financial_ratios.py` (8 tests)**: Validates 14 financial ratios, Altman Z-score in each zone, zero-division guards, and sector comparisons.
* **`test_monte_carlo.py` (3 tests)**: Verifies statistical monotonicity ($\bar{L} \le \text{VaR}_{0.95} \le \text{Worst Case}$) and reproducible random seeds.
* **`test_security.py` (17 tests)**: Verifies OWASP security headers, path traversal blocks, rate limiting, and server masking.

---

## ⏱️ 5-Minute Examiner / Viva Demonstration Script

Use this exact chronological script to ace your presentation:

* **0:00 - 0:45 | Introduction & Architecture**:
  * "Good morning/afternoon. Today I present **RiskGuard Pro**, an enterprise business risk assessment and quantitative analytics platform adhering to **ISO 31000:2018** guidelines."
  * Show the landing page (`/home.html`), explain the dual-engine database resilience (Supabase PostgreSQL cloud with automatic SQLite local fallback).
* **0:45 - 1:45 | Authentication, RBAC & Executive 3D Dashboard**:
  * Log in as Super Admin (`admin@riskguard.internal`).
  * Showcase the **Executive Overview**: KPI Cards (Health Score, VaR Exposure), the **Three.js 3D Spatial Threat Topology** (click `3D Isometric`, `Top Plan`, and `Auto-Rotate`), and the **3D Domain Ring Chart**.
  * Switch to **Admin Console**: Show user management (search, role switching, block/unblock), live platform analytics, and the Dynamic Benchmark Editor.
* **1:45 - 2:45 | 8-Step Wizard & Financial Ratio Solvency (Altman Z)**:
  * Click `Start 8-Step Assessment`. Show live input validation.
  * Navigate to Step 3: Direct Financial Statements. Fill sample balance sheet/P&L numbers.
  * Show instant calculation of all 14 ratios and the **Altman Z-Score Solvency Badge** with Safe, Grey, or Distress zone classifications and sector benchmark differentials (e.g., `+40% above sector average`).
* **2:45 - 3:45 | Quantitative Monte Carlo VaR Engine & Stress Testing**:
  * Switch to **Analytics Tab**: Explain the mathematical assumptions (NumPy log-normal severity, Bernoulli frequency).
  * Run 5,000 iterations: Point out the mathematical ordering ($\text{Mean Loss} \le \text{VaR}_{95} \le \text{Worst Case}$).
  * Switch to **Financial Tab / Stress Testing**: Click preset scenario chips (**Recession**, **Supply Chain Paralysis**, **Ransomware Outage**), showing how shocks immediately re-run the Monte Carlo engine and shift health scores.
* **3:45 - 4:30 | Action Tracker & Explainable Score Waterfall**:
  * Show Step 8: Final Report with the **Explainable Health Score Waterfall** (exact points deducted per domain starting from 100).
  * Go to **Risk Registry / Action Tracker**: Show tasks created from suggestions (`Open` / `In Progress` / `Closed`) with assignees and due dates.
* **4:30 - 5:00 | Security, Cryptographic Audit Ledger & Conclusion**:
  * Open `/api/audit-logs/verify` or the Audit Tab: Show the **cryptographic SHA-256 hash chain** confirming tamper-evident logging.
  * Show terminal running `pytest`: "All 50 unit and security integration tests pass." Conclude the presentation.

---

## 💡 10 Likely Viva Questions with In-Depth Answers

#### Q1: How does your Monte Carlo simulation model financial risk, and why did you choose a Log-Normal distribution?
**Answer**: Our engine uses a compound Poisson-LogNormal loss model implemented in vectorized NumPy. For each iteration, event occurrence is modeled using a Bernoulli distribution based on likelihood ($p = \text{Likelihood}/5.0$). If an event occurs, its severity is sampled from a Log-Normal distribution ($\mu, \sigma=1.2$). We chose Log-Normal because financial losses are strictly non-negative, bounded at zero, and exhibit heavy positive right-tail skewness—meaning normal distributions would severely underestimate black-swan catastrophic losses.

#### Q2: What is the mathematical formulation of Value-at-Risk (VaR), and what does 95% VaR mean here?
**Answer**: Mathematically, 95% Value-at-Risk is the 95th percentile of the simulated loss distribution: $\text{VaR}_{0.95} = \inf \{ l \in \mathbb{R} : P(L > l) \le 0.05 \}$. In our platform, it means that over a 1-year horizon, there is only a 5% statistical probability that portfolio operational losses will exceed this threshold.

#### Q3: How is the Altman Z-Score calculated, and how do you prevent division-by-zero errors?
**Answer**: We implement the 1968 private manufacturing formulation: $Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$. All ratio calculations in `server/services/financial_ratios.py` pass through a zero-safe helper `_safe_div(n, d, fallback=None)`. If total assets or liabilities are 0 or missing, the calculator safely returns an `Unknown` classification without raising a `ZeroDivisionError`.

#### Q4: How does your platform ensure dual-engine database resilience?
**Answer**: In `server/database.py`, `init_db()` queries the Supabase cloud PostgreSQL client. If unreachable due to network outage, DNS failure, or unconfigured credentials, the system catches the exception and immediately falls back to local SQLite with identical schema migrations and seeding. The application never crashes on database unavailability.

#### Q5: What makes your Audit Trail "tamper-evident"?
**Answer**: Our audit log is an append-only cryptographic ledger. Each entry contains a `prev_hash` pointing to the previous row and a current `hash = SHA256(id + action + details + user_id + timestamp + prev_hash)`. If a malicious party edits a record directly in the database, the cryptographic hash chain breaks, and `/api/audit-logs/verify` flags the exact row that was altered.

#### Q6: How do you enforce Role-Based Access Control (RBAC)?
**Answer**: RBAC is enforced on the backend via Python decorators `@require_auth` and `@require_role("admin")` in `server/app.py`. When a request arrives, the server extracts the `Authorization: Bearer <JWT>` header, validates the signature using `PyJWT`, checks whether `is_blocked == 0`, and confirms the user's role before executing the route handler.

#### Q7: What OWASP security measures have you implemented?
**Answer**: We implemented five layers of OWASP defense:
1. Strict Security Headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy).
2. Rate Limiting via sliding-window IP buckets to stop DoS and brute force.
3. Path Traversal filters blocking access to `.env`, `.git`, `.py`, and `riskguard.db`.
4. Input sanitization escaping HTML special characters to prevent stored XSS.
5. Parameterized SQL queries preventing SQL Injection.

#### Q8: How does the What-If Stress Testing Engine differ from the standard simulation?
**Answer**: The standard simulation uses static baseline parameters. The Stress Testing engine (`server/services/stress_testing.py`) applies macroeconomic shocks (revenue collapse %, debt increase %, cost inflation %, and cyber incident multipliers) directly to the financial statements, recalculates the stressed financial ratios and Altman Z-Score, and passes the elevated variance parameters into the Monte Carlo engine.

#### Q9: Explain the Explainable Health Score Waterfall feature.
**Answer**: Instead of treating the Enterprise Health Score as an opaque black box, our engine (`server/services/explainability.py`) starts at a baseline ideal health score of 100.0 and decomposes the final score into 6 weighted domains (Financial Solvency 25%, Cybersecurity 20%, Operations 18%, Compliance 15%, Market 12%, Human Capital 10%). It calculates exact point deductions and key drivers, visualized as an intuitive waterfall chart in Step 8 of the report.

#### Q10: How does the Cybersecurity Module map into the Monte Carlo engine?
**Answer**: `server/services/cyber_engine.py` evaluates 5 CVSS-style 0-10 posture metrics (Ransomware, Data Breach, Vulnerability Management, IAM, Backup Posture). It calculates a composite CVSS score, Annual Breach Probability ($p$), and Single Loss Expectancy (SLE). These parameters are directly mapped into the Monte Carlo engine as equivalent likelihood and financial impact values.
