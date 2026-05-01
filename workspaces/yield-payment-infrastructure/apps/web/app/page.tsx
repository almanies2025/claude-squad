"use client";

import { useState, useEffect } from "react";

const API = "http://localhost:8000";

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

const MODEL_COLORS: Record<string, { bar: string; accent: string }> = {
  "Naive (Persistence)": { bar: "#6b7280", accent: "#374151" },
  "Holt (Double Exp)": { bar: "#f59e0b", accent: "#d97706" },
  "ARIMA(1,1,1)": { bar: "#2563eb", accent: "#1d4ed8" },
};

const MODEL_ORDER = [
  "Naive (Persistence)",
  "Holt (Double Exp)",
  "ARIMA(1,1,1)",
];

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

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [forecast, setForecast] = useState<MultiModelForecast | null>(null);
  const [summary, setSummary] = useState<SummaryStats | null>(null);
  const [days, setDays] = useState(30);
  const [scenario, setScenario] = useState("base");
  const [loading, setLoading] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

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

  // Sort models into consistent order
  const sortedModels = forecast
    ? [...forecast.models].sort((a, b) => {
        const ai = MODEL_ORDER.indexOf(a.model_name);
        const bi = MODEL_ORDER.indexOf(b.model_name);
        return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      })
    : [];

  // For bar chart scale
  const maxYield = sortedModels.length
    ? Math.max(...sortedModels.map((m) => m.total_projected_yield))
    : 1;

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
        maxWidth: "1100px",
        margin: "0 auto",
      }}
    >
      {/* Header */}
      <header
        style={{
          marginBottom: "2rem",
          borderBottom: "1px solid #e5e7eb",
          paddingBottom: "1rem",
        }}
      >
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>
          FloatYield
        </h1>
        <p style={{ color: "#6b7280", margin: "0.25rem 0 0" }}>
          B2B Yield-Bearing Payment Infrastructure — Sprint 1 Forecast
        </p>
      </header>

      {/* Demo banner */}
      <div
        style={{
          background: "#fef3c7",
          border: "1px solid #f59e0b",
          borderRadius: 8,
          padding: "0.75rem 1rem",
          marginBottom: "1.5rem",
          fontSize: "0.875rem",
          color: "#92400e",
        }}
      >
        <strong>DEMO MODE</strong> — All data is synthetic. No live bank
        accounts or yield data are connected. Model comparison requires live
        yield history — currently showing baseline structure only.
      </div>

      {/* Backend status */}
      {backendOk === false && (
        <div
          style={{
            background: "#fef2f2",
            border: "1px solid #fca5a5",
            borderRadius: 8,
            padding: "1rem",
            marginBottom: "1.5rem",
          }}
        >
          <strong style={{ color: "#dc2626" }}>Backend unreachable</strong> —
          start with <code>scripts/run_backend.sh</code>
        </div>
      )}

      {/* Summary Strip */}
      {summary && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "1rem",
            marginBottom: "2rem",
          }}
        >
          {[
            ["Total Balance", fmt(summary.total_balance)],
            ["Avg Yield Rate", fmtPct(summary.weighted_avg_rate)],
            ["Annualized Yield", fmt(summary.annualized_yield)],
            ["30d Projected", fmt(summary.projected_30d_yield)],
          ].map(([label, val]) => (
            <div
              key={String(label)}
              style={{
                background: "#f9fafb",
                border: "1px solid #e5e7eb",
                borderRadius: 8,
                padding: "0.75rem 1rem",
              }}
            >
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "#6b7280",
                  textTransform: "uppercase",
                }}
              >
                {label}
              </div>
              <div style={{ fontSize: "1.25rem", fontWeight: 600 }}>{val}</div>
            </div>
          ))}
        </div>
      )}

      {/* Account Selector */}
      <section style={{ marginBottom: "1.5rem" }}>
        <h2
          style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.75rem" }}
        >
          Partner Accounts
        </h2>
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            flexWrap: "wrap",
            marginBottom: "1rem",
          }}
        >
          {accounts.map((a) => (
            <button
              key={a.id}
              onClick={() => setSelectedId(a.id)}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: 6,
                border:
                  selectedId === a.id
                    ? "2px solid #2563eb"
                    : "1px solid #d1d5db",
                background: selectedId === a.id ? "#eff6ff" : "white",
                cursor: "pointer",
                fontWeight: selectedId === a.id ? 600 : 400,
                color: "#111827",
              }}
            >
              {a.partner_name}
            </button>
          ))}
        </div>

        {/* Controls */}
        <div
          style={{
            display: "flex",
            gap: "1rem",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontSize: "0.875rem",
            }}
          >
            Days:
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              style={{
                padding: "0.25rem 0.5rem",
                borderRadius: 4,
                border: "1px solid #d1d5db",
              }}
            >
              {[7, 14, 30, 60, 90].map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </label>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              fontSize: "0.875rem",
            }}
          >
            Scenario:
            <select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              style={{
                padding: "0.25rem 0.5rem",
                borderRadius: 4,
                border: "1px solid #d1d5db",
              }}
            >
              <option value="base">Base</option>
              <option value="stress">Stress (−15%)</option>
              <option value="upside">Upside (+10%)</option>
            </select>
          </label>
        </div>
      </section>

      {/* Three-Model Comparison */}
      {loading && <p style={{ color: "#6b7280" }}>Loading forecast...</p>}

      {forecast && (
        <section style={{ marginBottom: "2rem" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "1rem",
            }}
          >
            <div>
              <h2 style={{ fontSize: "1rem", fontWeight: 600, margin: 0 }}>
                {forecast.partner_name}
              </h2>
              <p
                style={{
                  color: "#6b7280",
                  margin: "0.25rem 0 0",
                  fontSize: "0.875rem",
                }}
              >
                {fmt(forecast.current_balance)} @{" "}
                {(forecast.yield_rate * 100).toFixed(3)}% ·{" "}
                {forecast.forecast_days} days
              </p>
            </div>
            <div style={{ fontSize: "0.75rem", color: "#9ca3af" }}>
              Est. recon gap: {forecast.models[0]?.recon_gap_bps.toFixed(4)} bps
            </div>
          </div>

          {/* Bar chart */}
          <div
            style={{
              background: "white",
              border: "1px solid #e5e7eb",
              borderRadius: 8,
              padding: "1.25rem",
              marginBottom: "1rem",
            }}
          >
            <div
              style={{
                fontSize: "0.75rem",
                color: "#6b7280",
                marginBottom: "0.75rem",
                textTransform: "uppercase",
              }}
            >
              Total Projected Yield ({forecast.forecast_days} days)
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.6rem",
              }}
            >
              {sortedModels.map((model) => {
                const barWidth = (model.total_projected_yield / maxYield) * 100;
                const colors = MODEL_COLORS[model.model_name] || {
                  bar: "#9ca3af",
                  accent: "#6b7280",
                };
                return (
                  <div key={model.model_name}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginBottom: "0.2rem",
                        fontSize: "0.8rem",
                      }}
                    >
                      <span>{model.model_name}</span>
                      <span style={{ fontWeight: 600 }}>
                        {fmt(model.total_projected_yield)}
                      </span>
                    </div>
                    <div
                      style={{
                        background: "#f3f4f6",
                        borderRadius: 4,
                        height: 28,
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${barWidth}%`,
                          height: "100%",
                          background: colors.bar,
                          borderRadius: 4,
                          transition: "width 0.3s ease",
                          minWidth: barWidth > 0 ? "4px" : 0,
                        }}
                      />
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: "0.7rem",
                        color: "#9ca3af",
                        marginTop: "0.15rem",
                      }}
                    >
                      <span>Avg/day: {fmt(model.avg_daily)} · 80% CI: [{fmtShort(model.lower_bound)} – {fmtShort(model.upper_bound)}]</span>
                      <span>
                        Est. gap: {model.recon_gap_bps.toFixed(4)} bps
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Scenario and recon gap descriptions */}
          {forecast.scenario_description && (
            <div
              style={{
                fontSize: "0.75rem",
                color: "#6b7280",
                marginBottom: "1rem",
                padding: "0.5rem 0.75rem",
                background: "#f0fdf4",
                border: "1px solid #bbf7d0",
                borderRadius: 6,
              }}
            >
              <span style={{ fontWeight: 600 }}>Scenario: </span>
              {forecast.scenario_description}
            </div>
          )}
          {forecast.recon_gap_description && (
            <div
              style={{
                fontSize: "0.75rem",
                color: "#6b7280",
                marginBottom: "1rem",
                padding: "0.5rem 0.75rem",
                background: "#fef9c3",
                border: "1px solid #fde047",
                borderRadius: 6,
              }}
            >
              <span style={{ fontWeight: 600 }}>Reconciliation: </span>
              {forecast.recon_gap_description}
            </div>
          )}

          {/* Model detail table */}
          <div
            style={{
              background: "white",
              border: "1px solid #e5e7eb",
              borderRadius: 8,
              overflow: "hidden",
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "0.875rem",
              }}
            >
              <thead>
                <tr style={{ background: "#f9fafb" }}>
                  {["Model", "30d Yield", "80% CI", "Avg/Day", "Est. Gap (bps)"].map(
                    (h) => (
                      <th
                        key={h}
                        style={{
                          padding: "0.5rem 1rem",
                          textAlign: "left",
                          fontWeight: 600,
                          color: "#374151",
                          borderBottom: "1px solid #e5e7eb",
                        }}
                      >
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {sortedModels.map((model) => {
                  const colors = MODEL_COLORS[model.model_name] || {
                    bar: "#9ca3af",
                  };
                  return (
                    <tr
                      key={model.model_name}
                      style={{ borderBottom: "1px solid #f3f4f6" }}
                    >
                      <td style={{ padding: "0.5rem 1rem" }}>
                        <span
                          style={{
                            display: "inline-block",
                            width: 10,
                            height: 10,
                            borderRadius: 2,
                            background: colors.bar,
                            marginRight: 8,
                            verticalAlign: "middle",
                          }}
                        />
                        {model.model_name}
                      </td>
                      <td style={{ padding: "0.5rem 1rem", fontWeight: 600 }}>
                        {fmt(model.total_projected_yield)}
                      </td>
                      <td style={{ padding: "0.5rem 1rem", fontSize: "0.8rem", color: "#6b7280" }}>
                        {fmt(model.lower_bound)} – {fmt(model.upper_bound)}
                      </td>
                      <td style={{ padding: "0.5rem 1rem" }}>
                        {fmt(model.avg_daily)}
                      </td>
                      <td style={{ padding: "0.5rem 1rem", color: "#6b7280" }}>
                        {model.recon_gap_bps.toFixed(4)} bps
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <footer
        style={{
          marginTop: "3rem",
          paddingTop: "1rem",
          borderTop: "1px solid #e5e7eb",
          color: "#9ca3af",
          fontSize: "0.75rem",
        }}
      >
        FloatYield API — Sprint 1 Forecast |{" "}
        <a href="http://localhost:8000/docs" style={{ color: "#2563eb" }}>
          Swagger docs
        </a>
        {" · "}
        <a
          href="http://localhost:8000/docs#post-/forecast/all"
          style={{ color: "#2563eb" }}
        >
          POST /forecast/all
        </a>
      </footer>
    </div>
  );
}
