"use client";

import { useState, useEffect } from "react";

const API = "http://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────

interface Account {
  id: number;
  partner_name: string;
  balance: number;
  yield_rate: number;
  created_at: string;
}

interface ModelResult {
  model_name: string;
  total_projected_yield: number;
  avg_daily: number;
  recon_gap_bps: number;
  lower_bound: number;
  upper_bound: number;
}

interface MultiModelForecast {
  account_id: number;
  partner_name: string;
  current_balance: number;
  yield_rate: number;
  forecast_days: number;
  models: ModelResult[];
  recon_gap_description: string;
  scenario_description: string;
}

interface SummaryStats {
  total_accounts: number;
  total_balance: number;
  weighted_avg_rate: number;
  annualized_yield: number;
  projected_30d_yield: number;
}

// ─── Model Colors (neon palette) ─────────────────────────────────────

const MODEL_COLORS: Record<
  string,
  { bar: string; glow: string; label: string }
> = {
  "Naive (Persistence)": { bar: "#4A5568", glow: "#718096", label: "NAIVE" },
  "Holt (Double Exp)": { bar: "#00D4FF", glow: "#00D4FF88", label: "HOLT" },
  "ARIMA(1,1,1)": { bar: "#7C3AED", glow: "#7C3AED88", label: "ARIMA" },
};

const MODEL_ORDER = [
  "Naive (Persistence)",
  "Holt (Double Exp)",
  "ARIMA(1,1,1)",
];

// ─── Formatters ───────────────────────────────────────────────────────

function fmt(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(n);
}

function fmtPct(n: number) {
  return (n * 100).toFixed(4) + "%";
}

function fmtShort(n: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n);
}

// ─── Sub-components ──────────────────────────────────────────────────

function NeonBar({
  value,
  max,
  color,
  glow,
  label,
  sublabel,
}: {
  value: number;
  max: number;
  color: string;
  glow: string;
  label: string;
  sublabel: string;
}) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div style={{ marginBottom: "1.25rem" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "0.4rem",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "0.7rem",
            fontWeight: 500,
            color: "var(--text-secondary)",
            letterSpacing: "0.08em",
          }}
        >
          {label}
        </span>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "0.8rem",
            fontWeight: 600,
            color,
          }}
        >
          {fmt(value)}
        </span>
      </div>
      <div
        style={{
          background: "#0B1220",
          borderRadius: 4,
          height: 8,
          overflow: "hidden",
          border: "1px solid #1E2D45",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${color}44 0%, ${color} 100%)`,
            boxShadow: `0 0 8px ${glow}`,
            borderRadius: 4,
            transition: "width 0.6s cubic-bezier(0.22,1,0.36,1)",
            minWidth: pct > 0 ? "4px" : 0,
          }}
        />
      </div>
      <div
        style={{
          fontSize: "0.65rem",
          color: "var(--text-dim)",
          marginTop: "0.2rem",
          fontFamily: "var(--font-mono)",
        }}
      >
        {sublabel}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string;
  icon: string;
  accent: string;
}) {
  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border-dim)",
        borderRadius: 10,
        padding: "0.85rem 1rem",
        flex: "1 1 160px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Accent line top */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "2px",
          background: `linear-gradient(90deg, transparent, ${accent}, transparent)`,
        }}
      />
      <div
        style={{
          fontSize: "0.65rem",
          color: "var(--text-dim)",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: "0.25rem",
        }}
      >
        {icon} {label}
      </div>
      <div
        style={{
          fontSize: "1.1rem",
          fontWeight: 700,
          color: "var(--text-primary)",
          fontFamily: "var(--font-mono)",
        }}
      >
        {value}
      </div>
    </div>
  );
}

function ScenarioPill({
  value,
  label,
  active,
  onClick,
  color,
}: {
  value: string;
  label: string;
  active: boolean;
  onClick: () => void;
  color: string;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "0.4rem 0.9rem",
        borderRadius: 20,
        border: active ? `1px solid ${color}` : "1px solid var(--border-dim)",
        background: active ? `${color}18` : "transparent",
        color: active ? color : "var(--text-secondary)",
        cursor: "pointer",
        fontSize: "0.75rem",
        fontWeight: 600,
        fontFamily: "var(--font-mono)",
        letterSpacing: "0.05em",
        boxShadow: active ? `0 0 10px ${color}44` : "none",
        transition: "all 0.2s ease",
      }}
    >
      {label}
    </button>
  );
}

function AccountChip({
  name,
  active,
  onClick,
  accent,
}: {
  name: string;
  active: boolean;
  onClick: () => void;
  accent: string;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "0.4rem 1rem",
        borderRadius: 6,
        border: active ? `1px solid ${accent}` : "1px solid var(--border-dim)",
        background: active ? `${accent}15` : "transparent",
        color: active ? accent : "var(--text-secondary)",
        cursor: "pointer",
        fontSize: "0.8rem",
        fontWeight: active ? 600 : 400,
        fontFamily: "var(--font-body)",
        transition: "all 0.2s ease",
        boxShadow: active ? `0 0 8px ${accent}33` : "none",
      }}
    >
      {name}
    </button>
  );
}

// ─── Main Dashboard ────────────────────────────────────────────────────

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [forecast, setForecast] = useState<MultiModelForecast | null>(null);
  const [summary, setSummary] = useState<SummaryStats | null>(null);
  const [days, setDays] = useState(30);
  const [scenario, setScenario] = useState("base");
  const [loading, setLoading] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  // Accent colors per account for chip/chart theming
  const accountAccents = ["#00D4FF", "#00F5A0", "#7C3AED"];
  const currentAccent = accountAccents[(selectedId ?? 1) - 1] ?? "#00D4FF";

  useEffect(() => {
    fetch(`${API}/accounts`)
      .then((r) => r.json())
      .then((data: Account[]) => {
        setAccounts(data);
        if (data.length > 0) setSelectedId(data[0].id);
        setBackendOk(true);
      })
      .catch(() => setBackendOk(false));
  }, []);

  useEffect(() => {
    if (!backendOk) return;
    fetch(`${API}/forecast/summary?days=${days}`)
      .then((r) => r.json())
      .then(setSummary)
      .catch(() => {});
  }, [backendOk, days]);

  useEffect(() => {
    if (!selectedId || !backendOk) return;
    setLoading(true);
    fetch(`${API}/forecast/all`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        account_id: selectedId,
        days,
        rate_scenario: scenario,
      }),
    })
      .then((r) => r.json())
      .then((data: MultiModelForecast) => {
        setForecast(data);
        setLoading(false);
      })
      .catch(() => {
        setForecast(null);
        setLoading(false);
      });
  }, [selectedId, days, scenario, backendOk]);

  const sortedModels = forecast
    ? [...forecast.models].sort((a, b) => {
        const ai = MODEL_ORDER.indexOf(a.model_name);
        const bi = MODEL_ORDER.indexOf(b.model_name);
        return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      })
    : [];

  const maxYield = sortedModels.length
    ? Math.max(...sortedModels.map((m) => m.total_projected_yield))
    : 1;

  // Scenario config
  const scenarioConfig: Record<
    string,
    { label: string; color: string; icon: string }
  > = {
    base: { label: "BASE", color: "#00D4FF", icon: "◆" },
    stress: { label: "STRESS", color: "#FF6B6B", icon: "▼" },
    upside: { label: "UPSIDE", color: "#00F5A0", icon: "▲" },
  };
  const scen = scenarioConfig[scenario] ?? scenarioConfig.base;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg-void)",
        position: "relative",
        zIndex: 1,
      }}
    >
      {/* ── HEADER ─────────────────────────────────────── */}
      <header
        style={{
          borderBottom: "1px solid var(--border-dim)",
          padding: "1.5rem 2rem 1.25rem",
          position: "sticky",
          top: 0,
          background: "rgba(6,9,18,0.85)",
          backdropFilter: "blur(12px)",
          zIndex: 100,
        }}
      >
        <div
          style={{
            maxWidth: "1100px",
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}
            >
              {/* Yield pulse icon (SVG) */}
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <circle
                  cx="14"
                  cy="14"
                  r="13"
                  stroke="#00D4FF"
                  strokeWidth="1.5"
                  opacity="0.3"
                />
                <circle
                  cx="14"
                  cy="14"
                  r="13"
                  stroke="#00D4FF"
                  strokeWidth="1.5"
                  strokeDasharray="81.4"
                  strokeDashoffset="20"
                  style={{
                    animation:
                      "spin 8s linear infinite, pulse-glow 2s ease-in-out infinite",
                  }}
                />
                <path
                  d="M8 14 L11 10 L14 16 L17 11 L20 14"
                  stroke="#00D4FF"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <h1
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "1.35rem",
                  fontWeight: 900,
                  color: "#00D4FF",
                  letterSpacing: "0.15em",
                  textShadow: "0 0 20px #00D4FF88, 0 0 40px #00D4FF33",
                }}
              >
                FLOATYIELD
              </h1>
            </div>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "0.6rem",
                color: "var(--text-dim)",
                letterSpacing: "0.2em",
                marginTop: "0.15rem",
                paddingLeft: "2.3rem",
              }}
            >
              YIELD INFRASTRUCTURE · SPRINT 1
            </div>
          </div>

          {/* Live status dot */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: backendOk === false ? "#FF6B6B" : "#00F5A0",
                boxShadow:
                  backendOk === false ? "0 0 6px #FF6B6B" : "0 0 8px #00F5A0",
                animation:
                  backendOk !== false
                    ? "pulse-glow 2s ease-in-out infinite"
                    : "none",
              }}
            />
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "0.65rem",
                color: backendOk === false ? "#FF6B6B" : "#00F5A0",
                letterSpacing: "0.1em",
              }}
            >
              {backendOk === false ? "OFFLINE" : "LIVE"}
            </span>
          </div>
        </div>
      </header>

      <main
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
          padding: "1.5rem 2rem 3rem",
        }}
      >
        {/* ── DEMO BANNER ─────────────────────────────── */}
        <div
          style={{
            background: "linear-gradient(135deg, #1A1200 0%, #1A0F00 100%)",
            border: "1px solid #FFD93D44",
            borderRadius: 8,
            padding: "0.7rem 1rem",
            marginBottom: "1.5rem",
            display: "flex",
            alignItems: "center",
            gap: "0.6rem",
            fontSize: "0.78rem",
            color: "#FFD93D",
          }}
        >
          <span style={{ fontSize: "1rem" }}>⚠</span>
          <span>
            <strong style={{ fontFamily: "var(--font-mono)" }}>
              DEMO MODE
            </strong>
            {" — "}Synthetic data. Models are structurally verified but not
            statistically validated on live Fed rate environments. All yield
            projections are for demonstration purposes only.
          </span>
        </div>

        {/* ── SUMMARY STATS ────────────────────────────── */}
        {summary && (
          <div
            style={{
              display: "flex",
              gap: "0.75rem",
              marginBottom: "1.5rem",
              flexWrap: "wrap",
            }}
          >
            <StatCard
              label="Total Balance"
              value={fmtShort(summary.total_balance)}
              icon="◈"
              accent="#00D4FF"
            />
            <StatCard
              label="Avg Yield Rate"
              value={fmtPct(summary.weighted_avg_rate)}
              icon="◆"
              accent="#FFD93D"
            />
            <StatCard
              label="Annualized"
              value={fmtShort(summary.annualized_yield)}
              icon="◇"
              accent="#00F5A0"
            />
            <StatCard
              label="30d Projected"
              value={fmtShort(summary.projected_30d_yield)}
              icon="▷"
              accent="#7C3AED"
            />
          </div>
        )}

        {/* ── ACCOUNT + CONTROLS ───────────────────────── */}
        <div
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border-dim)",
            borderRadius: 10,
            padding: "1.1rem 1.25rem",
            marginBottom: "1.5rem",
          }}
        >
          {/* Account selector */}
          <div style={{ marginBottom: "1rem" }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "0.65rem",
                color: "var(--text-dim)",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                marginBottom: "0.6rem",
              }}
            >
              ▼ PARTNER ACCOUNTS
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {accounts.map((a, i) => (
                <AccountChip
                  key={a.id}
                  name={a.partner_name}
                  active={selectedId === a.id}
                  onClick={() => setSelectedId(a.id)}
                  accent={accountAccents[i] ?? "#00D4FF"}
                />
              ))}
            </div>
          </div>

          {/* Scenario + horizon controls */}
          <div
            style={{
              display: "flex",
              gap: "1rem",
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            {/* Scenario pills */}
            <div
              style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}
            >
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.6rem",
                  color: "var(--text-dim)",
                  letterSpacing: "0.1em",
                  marginRight: "0.25rem",
                }}
              >
                SCENARIO
              </span>
              {Object.entries(scenarioConfig).map(([val, cfg]) => (
                <ScenarioPill
                  key={val}
                  value={val}
                  label={`${cfg.icon} ${cfg.label}`}
                  active={scenario === val}
                  onClick={() => setScenario(val)}
                  color={cfg.color}
                />
              ))}
            </div>

            {/* Divider */}
            <div
              style={{ width: 1, height: 20, background: "var(--border-dim)" }}
            />

            {/* Horizon selector */}
            <div
              style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}
            >
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.6rem",
                  color: "var(--text-dim)",
                  letterSpacing: "0.1em",
                }}
              >
                HORIZON
              </span>
              {[7, 14, 30, 60, 90].map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  style={{
                    padding: "0.25rem 0.6rem",
                    borderRadius: 4,
                    border:
                      days === d
                        ? "1px solid var(--cyan)"
                        : "1px solid var(--border-dim)",
                    background: days === d ? "var(--cyan-glow)" : "transparent",
                    color: days === d ? "var(--cyan)" : "var(--text-secondary)",
                    cursor: "pointer",
                    fontSize: "0.7rem",
                    fontFamily: "var(--font-mono)",
                    fontWeight: days === d ? 600 : 400,
                    transition: "all 0.15s ease",
                  }}
                >
                  {d}d
                </button>
              ))}
            </div>

            {/* Scenario description inline */}
            <div
              style={{
                marginLeft: "auto",
                fontSize: "0.7rem",
                color: "var(--text-dim)",
                fontFamily: "var(--font-mono)",
                display: scenario === "base" ? "none" : "block",
              }}
            >
              {scenario === "stress"
                ? "Fed −50bps → yield ×0.85"
                : "Fed +30bps → yield ×1.10"}
            </div>
          </div>
        </div>

        {/* ── LOADING ──────────────────────────────────── */}
        {loading && (
          <div
            style={{
              textAlign: "center",
              padding: "3rem",
              fontFamily: "var(--font-mono)",
              fontSize: "0.8rem",
              color: "var(--text-dim)",
              letterSpacing: "0.15em",
            }}
          >
            <div style={{ marginBottom: "0.5rem" }}>◌ PROCESSING</div>
            <div
              style={{
                width: "100%",
                height: 2,
                background: "var(--border-dim)",
                borderRadius: 2,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  background: "var(--cyan)",
                  boxShadow: "0 0 8px var(--cyan)",
                  animation: "loading-sweep 1.2s ease-in-out infinite",
                  width: "40%",
                }}
              />
            </div>
          </div>
        )}

        {/* ── FORECAST PANEL ──────────────────────────── */}
        {!loading && forecast && (
          <>
            {/* Account header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: "1rem",
              }}
            >
              <div>
                <div
                  style={{
                    fontFamily: "var(--font-display)",
                    fontSize: "1rem",
                    fontWeight: 700,
                    color: currentAccent,
                    textShadow: `0 0 12px ${currentAccent}66`,
                    letterSpacing: "0.05em",
                  }}
                >
                  {forecast.partner_name.toUpperCase()}
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.7rem",
                    color: "var(--text-secondary)",
                    marginTop: "0.2rem",
                  }}
                >
                  {fmt(forecast.current_balance)} @{" "}
                  {(forecast.yield_rate * 100).toFixed(3)}%{" · "}
                  {forecast.forecast_days}-day horizon
                </div>
              </div>
              {/* Recon gap badge */}
              <div
                style={{
                  background: "#0B1220",
                  border: "1px solid var(--border-dim)",
                  borderRadius: 6,
                  padding: "0.35rem 0.75rem",
                  fontSize: "0.7rem",
                  fontFamily: "var(--font-mono)",
                  color: "var(--text-secondary)",
                  textAlign: "right",
                }}
              >
                <div
                  style={{
                    color: "var(--text-dim)",
                    fontSize: "0.6rem",
                    marginBottom: "0.1rem",
                  }}
                >
                  RECON GAP
                </div>
                <div style={{ color: "#00F5A0" }}>
                  {forecast.models[0]?.recon_gap_bps.toFixed(4)} bps
                </div>
              </div>
            </div>

            {/* Yield bar chart */}
            <div
              style={{
                background: "var(--bg-card)",
                border: `1px solid ${currentAccent}22`,
                borderRadius: 10,
                padding: "1.25rem 1.5rem",
                marginBottom: "1rem",
                boxShadow: `0 0 0 1px ${currentAccent}11 inset, 0 4px 24px #00000066`,
              }}
            >
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: "var(--text-dim)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "1.25rem",
                }}
              >
                ◈ {forecast.forecast_days}-Day Yield Projection
              </div>

              {sortedModels.map((model) => {
                const cfg = MODEL_COLORS[model.model_name] ?? {
                  bar: "#4A5568",
                  glow: "#718096",
                  label: "???",
                };
                const pct = (model.total_projected_yield / maxYield) * 100;
                const ciWidth =
                  ((model.upper_bound - model.lower_bound) / maxYield) * 100;
                const ciLeft = (model.lower_bound / maxYield) * 100;
                return (
                  <div
                    key={model.model_name}
                    style={{ marginBottom: "1.4rem" }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginBottom: "0.35rem",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.5rem",
                        }}
                      >
                        <div
                          style={{
                            width: 6,
                            height: 6,
                            borderRadius: "50%",
                            background: cfg.bar,
                            boxShadow: `0 0 6px ${cfg.glow}`,
                          }}
                        />
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.72rem",
                            fontWeight: 500,
                            color: "var(--text-secondary)",
                            letterSpacing: "0.05em",
                          }}
                        >
                          {cfg.label}
                        </span>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.85rem",
                            fontWeight: 700,
                            color: cfg.bar,
                          }}
                        >
                          {fmt(model.total_projected_yield)}
                        </span>
                      </div>
                    </div>

                    {/* Bar + CI range overlay */}
                    <div style={{ position: "relative" }}>
                      <div
                        style={{
                          background: "#0B1220",
                          borderRadius: 4,
                          height: 10,
                          overflow: "hidden",
                          border: "1px solid #1E2D45",
                        }}
                      >
                        <div
                          style={{
                            position: "absolute",
                            left: `${Math.max(0, ciLeft)}%`,
                            width: `${Math.min(ciWidth, 100 - Math.max(0, ciLeft))}%`,
                            top: 0,
                            height: "100%",
                            background: `${cfg.bar}18`,
                            borderLeft: `2px solid ${cfg.bar}88`,
                            borderRight: `2px solid ${cfg.bar}88`,
                            boxSizing: "border-box",
                          }}
                        />
                        <div
                          style={{
                            width: `${pct}%`,
                            height: "100%",
                            background: `linear-gradient(90deg, ${cfg.bar}33 0%, ${cfg.bar} 100%)`,
                            boxShadow: `0 0 6px ${cfg.glow}`,
                            borderRadius: 4,
                            transition:
                              "width 0.6s cubic-bezier(0.22,1,0.36,1)",
                            minWidth: pct > 0 ? "4px" : 0,
                          }}
                        />
                      </div>
                    </div>

                    {/* CI + avg row */}
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: "0.62rem",
                        color: "var(--text-dim)",
                        fontFamily: "var(--font-mono)",
                        marginTop: "0.25rem",
                      }}
                    >
                      <span>avg/day: {fmt(model.avg_daily)}</span>
                      <span style={{ color: `${cfg.bar}99` }}>
                        80% CI: {fmtShort(model.lower_bound)} →{" "}
                        {fmtShort(model.upper_bound)}
                      </span>
                    </div>
                  </div>
                );
              })}

              {/* Chart legend */}
              <div
                style={{
                  display: "flex",
                  gap: "1rem",
                  marginTop: "0.5rem",
                  fontSize: "0.6rem",
                  color: "var(--text-dim)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.3rem",
                  }}
                >
                  <div
                    style={{
                      width: 16,
                      height: 4,
                      background: "#0B1220",
                      border: "1px solid #1E2D45",
                      borderRadius: 2,
                    }}
                  />
                  CI range (80%)
                </div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.3rem",
                  }}
                >
                  <div
                    style={{
                      width: 16,
                      height: 4,
                      background: "linear-gradient(90deg, #00D4FF33, #00D4FF)",
                      borderRadius: 2,
                      boxShadow: "0 0 4px #00D4FF44",
                    }}
                  />
                  Point forecast
                </div>
              </div>
            </div>

            {/* Scenario + recon descriptions */}
            <div
              style={{
                display: "flex",
                gap: "0.75rem",
                flexWrap: "wrap",
                marginBottom: "1.5rem",
              }}
            >
              <div
                style={{
                  flex: "1 1 300px",
                  background: `${scen.color}0D`,
                  border: `1px solid ${scen.color}33`,
                  borderRadius: 8,
                  padding: "0.65rem 0.9rem",
                  fontSize: "0.72rem",
                  color: "var(--text-secondary)",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.6rem",
                    color: scen.color,
                    letterSpacing: "0.12em",
                    marginBottom: "0.3rem",
                    textTransform: "uppercase",
                  }}
                >
                  {scen.icon} SCENARIO
                </div>
                {forecast.scenario_description}
              </div>
              <div
                style={{
                  flex: "1 1 300px",
                  background: "#FFD93D0D",
                  border: "1px solid #FFD93D33",
                  borderRadius: 8,
                  padding: "0.65rem 0.9rem",
                  fontSize: "0.72rem",
                  color: "var(--text-secondary)",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.6rem",
                    color: "#FFD93D",
                    letterSpacing: "0.12em",
                    marginBottom: "0.3rem",
                    textTransform: "uppercase",
                  }}
                >
                  ◎ RECONCILIATION
                </div>
                {forecast.recon_gap_description}
              </div>
            </div>

            {/* Model detail table */}
            <div
              style={{
                background: "var(--bg-card)",
                border: "1px solid var(--border-dim)",
                borderRadius: 10,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  padding: "0.65rem 1rem",
                  borderBottom: "1px solid var(--border-dim)",
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.6rem",
                  color: "var(--text-dim)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                }}
              >
                ◈ Model Breakdown
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#0B1220" }}>
                    {[
                      "Model",
                      "30d Yield",
                      "80% CI Range",
                      "Avg/Day",
                      "Recon Gap",
                    ].map((h) => (
                      <th
                        key={h}
                        style={{
                          padding: "0.5rem 1rem",
                          textAlign: "left",
                          fontFamily: "var(--font-mono)",
                          fontWeight: 500,
                          fontSize: "0.65rem",
                          color: "var(--text-dim)",
                          letterSpacing: "0.08em",
                          borderBottom: "1px solid var(--border-dim)",
                        }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sortedModels.map((model) => {
                    const cfg = MODEL_COLORS[model.model_name] ?? {
                      bar: "#4A5568",
                      glow: "#718096",
                    };
                    return (
                      <tr
                        key={model.model_name}
                        style={{ borderBottom: "1px solid #0B1220" }}
                      >
                        <td style={{ padding: "0.6rem 1rem" }}>
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "0.5rem",
                            }}
                          >
                            <div
                              style={{
                                width: 6,
                                height: 6,
                                borderRadius: "50%",
                                background: cfg.bar,
                                boxShadow: `0 0 5px ${cfg.glow}`,
                              }}
                            />
                            <span
                              style={{
                                fontFamily: "var(--font-mono)",
                                fontSize: "0.75rem",
                                color: "var(--text-primary)",
                              }}
                            >
                              {model.model_name}
                            </span>
                          </div>
                        </td>
                        <td
                          style={{
                            padding: "0.6rem 1rem",
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.8rem",
                            fontWeight: 600,
                            color: cfg.bar,
                          }}
                        >
                          {fmt(model.total_projected_yield)}
                        </td>
                        <td
                          style={{
                            padding: "0.6rem 1rem",
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.72rem",
                            color: "var(--text-secondary)",
                          }}
                        >
                          {fmt(model.lower_bound)} → {fmt(model.upper_bound)}
                        </td>
                        <td
                          style={{
                            padding: "0.6rem 1rem",
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.72rem",
                            color: "var(--text-secondary)",
                          }}
                        >
                          {fmt(model.avg_daily)}
                        </td>
                        <td
                          style={{
                            padding: "0.6rem 1rem",
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.72rem",
                            color: "#00F5A0",
                          }}
                        >
                          {model.recon_gap_bps.toFixed(4)} bps
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}

        {/* ── FOOTER ─────────────────────────────────── */}
        <footer
          style={{
            marginTop: "3rem",
            paddingTop: "1rem",
            borderTop: "1px solid var(--border-dim)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "0.5rem",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "0.65rem",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            FLOATYIELD API · SPRINT 1 · {new Date().getFullYear()}
          </span>
          <div style={{ display: "flex", gap: "1rem" }}>
            <a
              href="http://localhost:8000/docs"
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "0.65rem",
                color: "var(--cyan)",
                textDecoration: "none",
                letterSpacing: "0.05em",
              }}
            >
              [ SWAGGER DOCS ]
            </a>
            <a
              href="http://localhost:8000/docs#post-/forecast/all"
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "0.65rem",
                color: "var(--text-dim)",
                textDecoration: "none",
                letterSpacing: "0.05em",
              }}
            >
              [ POST /forecast/all ]
            </a>
          </div>
        </footer>
      </main>

      {/* ── KEYFRAME ANIMATIONS ─────────────────────────────────── */}
      <style>{`
        @keyframes pulse-glow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        @keyframes spin {
          from { stroke-dashoffset: 81.4; }
          to { stroke-dashoffset: 0; }
        }
        @keyframes loading-sweep {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(350%); }
        }
      `}</style>
    </div>
  );
}
