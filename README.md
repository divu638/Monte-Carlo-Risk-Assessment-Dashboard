# RiskAssess PRO — Business Risk Assessment Dashboard 🛡️🎲

> **Enterprise Business Risk Assessment, Monte Carlo Value-at-Risk (VaR) Engine & Three.js 3D Visualizer**  
> Built with Python Flask, SQLite / Supabase Cloud PostgreSQL, Three.js, and Vanilla CSS Glassmorphism.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://monte-carlo-risk-assessment-dashboard.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black.svg)](https://threejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🌐 **Live Production App**: **[https://monte-carlo-risk-assessment-dashboard.onrender.com](https://monte-carlo-risk-assessment-dashboard.onrender.com)**

---

## 🌟 Key Features

1. **8-Step Guided Business Risk Assessment Wizard**:
   * Step-by-step diagnostic workflow: Business Profile, Working Capital & Balance Sheet, Operational Supplier/Customer Dependencies, Calculation & Classification, Actionable Suggestions, and Institutional Executive Dossier.
   * Instant ratio calculations (Current Ratio, Quick Ratio, Debt-to-Equity, Net Margin, Operating Margin, Interest Coverage, Collection Days).

2. **Executive Overview & Command Hub**:
   * Real-time metrics: Active Enterprise Risks, Critical/High Exposures, Total Financial VaR, and Governance Health Score (ISO 31000).
   * **3D Spatial Threat Topology (Three.js)**: Interactive 5×5 elevation heatmap with camera controls (3D Isometric, Top Plan, Horizon view, and Auto-Rotate).
   * **3D Domain Ring Chart (Three.js)**: Cylindrical animated 3D segments representing domain distributions with real-time risk counts.

3. **Risk Registry & CRUD**:
   * Complete risk inventory table with multi-criteria filtering (Domain, Severity, Status).
   * Live search (`/` shortcut), inline status toggle, bulk batch updates, and single-click CSV export.

4. **5×5 Risk Heatmap**:
   * Likelihood vs. Impact probability matrix with interactive cell drill-down.

5. **Monte Carlo VaR Simulation Engine**:
   * 1,000 to 10,000 statistical trials with log-normal severity distributions.
   * Calculates Mean Expected Loss, 95% Value-at-Risk (VaR), and Worst-Case Exposure with interactive distribution histograms.

6. **Financial Stress Testing & Sensitivity Analysis**:
   * Key financial ratio monitors and stress-testing scenario presets (Severe Demand Shock, Supply Chain Inflation, Liquidity Squeeze).
   * **Tornado Sensitivity Analysis** chart mapping key operational risk drivers.

7. **Audit Trail & Governance**:
   * Immutable chronological logging of all additions, modifications, and deletions.
   * RBAC preview (Chief Risk Officer, Risk Analyst, External Auditor, Board Member).
   * Risk appetite threshold sliders and JSON/SQL data export.

8. **Modern Linear/Stripe Deep Slate Aesthetics**:
   * **Linear Slate Dark** (Primary Enterprise Theme with soft pastel badges & glassmorphism).
   * **Classic White & Luxury Light** (High-contrast Executive Light Mode).
   * Global Header Back Button and Breadcrumb navigation across all tabs.

---

## 🚀 Quickstart (Run Locally)

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/monte-carlo-risk-engine.git
cd monte-carlo-risk-engine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Server
```bash
python run.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## ☁️ Live Cloud Deployment (Render / Railway / Heroku)

### Deploy to Render (Free Tier)
1. Push this repository to your GitHub account.
2. Sign in to [Render.com](https://render.com) and click **New + > Web Service**.
3. Connect your repository.
4. Set:
   * **Runtime**: Python
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python run.py` (or `gunicorn --chdir server app:app`)
5. Click **Deploy Web Service** — your app is live!

---

## 🗄️ Database Architecture (Dual Engine)

* **Default Mode**: Built-in SQLite database (`server/riskguard.db`) initializes automatically with 13 pre-seeded benchmark risks. Zero configuration needed.
* **Cloud Mode (Supabase PostgreSQL)**:
  1. Create a project at [supabase.com](https://supabase.com).
  2. Run the provided [`setup_supabase.sql`](./setup_supabase.sql) in your Supabase SQL Editor.
  3. Enter your Supabase Project URL and Key via the dashboard UI ("Connect Cloud" button) or add them to your `.env` file:
     ```env
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-anon-or-service-role-key
     ```

---

## 📁 Project Structure

```
├── client/
│   ├── index.html       # Single-page dashboard markup
│   ├── styles.css       # Glassmorphism styling, responsive media queries, Emerald & White themes
│   └── script.js        # Three.js 3D renderers, Chart.js graphs, REST API integration
├── server/
│   ├── app.py           # Flask REST API server
│   ├── database.py      # Dual-mode SQLite / Supabase database adapter
│   └── requirements.txt # Python server dependencies
├── run.py               # Root application launcher
├── requirements.txt     # Root dependencies
├── Procfile             # Cloud deployment entrypoint
├── render.yaml          # Render deployment blueprint
├── setup_supabase.sql   # PostgreSQL table schemas and seed dataset
└── README.md            # Project documentation
```

---

## 📄 License
MIT License. Feel free to use and customize for your organization.
