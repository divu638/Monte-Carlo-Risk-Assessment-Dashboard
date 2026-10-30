-- ═══════════════════════════════════════════════════════════════════════════
--  RiskGuard Pro — Enterprise Supabase Schema Initialization
--  Run this ONCE in: Supabase Dashboard → SQL Editor → New Query → Run
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    firstname TEXT NOT NULL,
    lastname TEXT DEFAULT '',
    company TEXT DEFAULT '',
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    is_verified INTEGER DEFAULT 1,
    is_blocked INTEGER DEFAULT 0,
    mfa_enabled INTEGER DEFAULT 0,
    mfa_secret TEXT DEFAULT '',
    failed_attempts INTEGER DEFAULT 0,
    lockout_until TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Risks Table
CREATE TABLE IF NOT EXISTS risks (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT NOT NULL,
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 5),
    score INTEGER NOT NULL,
    level TEXT NOT NULL,
    financial_impact DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    owner TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    velocity TEXT DEFAULT 'Medium',
    trend TEXT DEFAULT 'stable',
    mitigation TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Audit Logs Table (Tamper-Evident Append-Only Chain)
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    risk_id BIGINT,
    risk_name TEXT,
    action TEXT NOT NULL,
    details TEXT DEFAULT '',
    user_id BIGINT DEFAULT 1,
    before_val TEXT DEFAULT '',
    after_val TEXT DEFAULT '',
    prev_hash TEXT DEFAULT 'GENESIS_ROOT_HASH_00000000000000000000000000000000000000000000000000000000',
    hash TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Assessments Table
CREATE TABLE IF NOT EXISTS assessments (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL DEFAULT 1,
    company_name TEXT NOT NULL,
    industry TEXT DEFAULT 'General',
    health_score INTEGER NOT NULL,
    var_exposure DOUBLE PRECISION NOT NULL,
    status TEXT DEFAULT 'Completed',
    step_data TEXT DEFAULT '{}',
    ratios_data TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Industry Benchmarks Table
CREATE TABLE IF NOT EXISTS industry_benchmarks (
    industry TEXT PRIMARY KEY,
    current_ratio DOUBLE PRECISION DEFAULT 1.8,
    de_ratio DOUBLE PRECISION DEFAULT 1.0,
    net_margin DOUBLE PRECISION DEFAULT 0.07,
    roe DOUBLE PRECISION DEFAULT 0.12,
    asset_turnover DOUBLE PRECISION DEFAULT 0.80,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Action Tasks Table (ISO 31000 Mitigation Tracker)
CREATE TABLE IF NOT EXISTS action_tasks (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL DEFAULT 1,
    risk_id BIGINT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT DEFAULT 'Operations',
    status TEXT DEFAULT 'Open',
    owner TEXT DEFAULT 'Risk Committee',
    priority TEXT DEFAULT 'High',
    due_date TEXT DEFAULT '',
    cost_estimate TEXT DEFAULT '',
    treatment_type TEXT DEFAULT 'Reduce',
    residual_risk DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
--  Enable Row Level Security (RLS) with Permissive Policy for API Access
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE industry_benchmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_tasks ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    DROP POLICY IF EXISTS "Allow all on users" ON users;
    CREATE POLICY "Allow all on users" ON users FOR ALL USING (true) WITH CHECK (true);

    DROP POLICY IF EXISTS "Allow all on risks" ON risks;
    CREATE POLICY "Allow all on risks" ON risks FOR ALL USING (true) WITH CHECK (true);

    DROP POLICY IF EXISTS "Allow all on audit_logs" ON audit_logs;
    CREATE POLICY "Allow all on audit_logs" ON audit_logs FOR ALL USING (true) WITH CHECK (true);

    DROP POLICY IF EXISTS "Allow all on alerts" ON alerts;
    CREATE POLICY "Allow all on alerts" ON alerts FOR ALL USING (true) WITH CHECK (true);

    DROP POLICY IF EXISTS "Allow all on assessments" ON assessments;
    CREATE POLICY "Allow all on assessments" ON assessments FOR ALL USING (true) WITH CHECK (true);

    DROP POLICY IF EXISTS "Allow all on industry_benchmarks" ON industry_benchmarks;
    CREATE POLICY "Allow all on industry_benchmarks" ON industry_benchmarks FOR ALL USING (true) WITH CHECK (true);

    DROP POLICY IF EXISTS "Allow all on action_tasks" ON action_tasks;
    CREATE POLICY "Allow all on action_tasks" ON action_tasks FOR ALL USING (true) WITH CHECK (true);
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
--  Seed Industry Benchmarks (Damodaran Industry Baseline)
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO industry_benchmarks (industry, current_ratio, de_ratio, net_margin, roe, asset_turnover)
VALUES
    ('Technology', 2.10, 0.45, 0.16, 0.19, 0.95),
    ('Manufacturing', 1.65, 1.20, 0.06, 0.11, 1.10),
    ('Healthcare', 2.30, 0.60, 0.11, 0.15, 0.85),
    ('Retail', 1.40, 1.40, 0.04, 0.14, 2.10),
    ('Financial Services', 1.15, 2.50, 0.18, 0.13, 0.35),
    ('Energy', 1.35, 1.80, 0.08, 0.09, 0.60),
    ('Construction', 1.45, 1.60, 0.05, 0.10, 1.25)
ON CONFLICT (industry) DO NOTHING;
