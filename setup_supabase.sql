-- ═══════════════════════════════════════════════════════════════════════════
--  RiskGuard Pro — Supabase Table Setup SQL
--  Run this ONCE in your Supabase Dashboard → SQL Editor → New Query
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Risks Table
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

-- 2. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    risk_id BIGINT,
    risk_name TEXT,
    action TEXT NOT NULL,
    details TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    source TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════
--  Enable Row Level Security (RLS) — set to public access for dev
--  For production, add proper RLS policies!
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE risks ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Allow all operations for anon/authenticated users (dev mode)
CREATE POLICY "Allow all on risks" ON risks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on audit_logs" ON audit_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on alerts" ON alerts FOR ALL USING (true) WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════════════
--  Auto-update 'updated_at' trigger for risks table
-- ═══════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_risks_updated_at
    BEFORE UPDATE ON risks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
