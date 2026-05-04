"use client";

import { useState, useEffect } from "react";
import VideoCityscape from "../components/VideoCityscape";

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

interface Dispute {
  id: number;
  account_id: number;
  partner_name: string;
  dispute_date: string;
  filed_by: string;
  gap_bps: number;
  gap_dollar_amount: number;
  dispute_type: string;
  reason: string;
  status: string;
  notes: string | null;
  created_at: string;
}

interface ThresholdAlert {
  id: number;
  account_id: number;
  partner_name: string;
  alert_date: string;
  gap_bps: number;
  threshold_bps: number;
  severity: string;
  acknowledged: boolean;
  created_at: string;
}

interface PortfolioStats {
  total_accounts: number;
  total_balance: number;
  total_disputes: number;
  open_disputes: number;
  threshold_alerts: number;
  unacknowledged_alerts: number;
  avg_gap_bps: number;
  max_gap_bps: number;
  annualized_yield: number;
  projected_30d_yield: number;
}

interface RegulatoryReport {
  account_id: number;
  partner_name: string;
  report_type: string;
  tax_year: number;
  total_yield: number;
  account_balance: number;
  yield_rate: number;
  generated_at: string;
}

interface DisputeCreate {
  account_id: number;
  dispute_date: string;
  filed_by: string;
  gap_bps: number;
  gap_dollar_amount: number;
  dispute_type: string;
  reason: string;
  notes?: string;
}

interface RateDiscrepancy {
  id: number;
  account_id: number;
  partner_name: string;
  discrepancy_date: string;
  contract_rate: number;
  applied_rate: number;
  discrepancy_bps: number;
  status: string;
  notes: string | null;
  created_at: string;
}

interface RateDiscrepancyCreate {
  account_id: number;
  discrepancy_date: string;
  contract_rate: number;
  applied_rate: number;
  discrepancy_bps: number;
  notes?: string;
}

// ─── Model Colors (Premium Dark palette) ─────────────────────────────

const MODEL_COLORS: Record<string, { bar: string; label: string }> = {
  "Naive (Persistence)": { bar: "#2EA866", label: "NAIVE" },
  "Holt (Double Exp)": { bar: "#F0B429", label: "HOLT" },
  "ARIMA(1,1,1)": { bar: "#58A6FF", label: "ARIMA" },
};

const MODEL_ORDER = [
  "Naive (Persistence)",
  "Holt (Double Exp)",
  "ARIMA(1,1,1)",
];

// ─── Theme constants ─────────────────────────────────────────────────

const C = {
  bg: "#0D1117",
  surface: "#161B22",
  border: "#30363D",
  borderSub: "#21262D",
  green: "#2EA866",
  greenDim: "#2EA86618",
  gold: "#F0B429",
  goldDim: "#F0B42918",
  red: "#F85149",
  redDim: "#F8514918",
  blue: "#58A6FF",
  blueDim: "#58A6FF18",
  text: "#E6EDF3",
  textSec: "#8B949E",
  textDim: "#484F58",
};

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

function YieldBar({
  value,
  max,
  color,
  label,
  sublabel,
}: {
  value: number;
  max: number;
  color: string;
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
            color: C.textSec,
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
          background: C.bg,
          borderRadius: 4,
          height: 8,
          overflow: "hidden",
          border: `1px solid ${C.borderSub}`,
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: color,
            borderRadius: 4,
            transition: "width 0.6s cubic-bezier(0.22,1,0.36,1)",
            minWidth: pct > 0 ? "4px" : 0,
          }}
        />
      </div>
      <div
        style={{
          fontSize: "0.65rem",
          color: C.textDim,
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
        background: C.surface,
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: "1.5rem 1.25rem",
        flex: "1 1 180px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Top accent line */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "2px",
          background: accent,
          opacity: 0.7,
        }}
      />
      <div
        style={{
          fontSize: "0.65rem",
          color: C.textDim,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: "0.5rem",
          fontFamily: "var(--font-mono)",
        }}
      >
        {icon} {label}
      </div>
      <div
        style={{
          fontSize: "2rem",
          fontWeight: 700,
          color: C.text,
          fontFamily: "var(--font-mono)",
          lineHeight: 1.1,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function ScenarioPill({
  label,
  active,
  onClick,
  color,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
  color: string;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "0.35rem 0.85rem",
        borderRadius: 6,
        border: active ? `1px solid ${color}` : `1px solid ${C.border}`,
        background: active ? `${color}18` : "transparent",
        color: active ? color : C.textSec,
        cursor: "pointer",
        fontSize: "0.75rem",
        fontWeight: 600,
        fontFamily: "var(--font-mono)",
        letterSpacing: "0.05em",
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
        border: active ? `1px solid ${accent}` : `1px solid ${C.border}`,
        background: active ? `${accent}15` : "transparent",
        color: active ? accent : C.textSec,
        cursor: "pointer",
        fontSize: "0.8rem",
        fontWeight: active ? 600 : 400,
        fontFamily: "var(--font-body)",
        transition: "all 0.2s ease",
      }}
    >
      {name}
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { color: string; bg: string }> = {
    open: { color: C.gold, bg: C.goldDim },
    resolved: { color: C.green, bg: C.greenDim },
    escalated: { color: C.red, bg: C.redDim },
    closed: { color: C.textDim, bg: "#ffffff08" },
  };
  const c = config[status] ?? { color: C.textDim, bg: "#ffffff08" };
  return (
    <span
      style={{
        padding: "0.2rem 0.5rem",
        borderRadius: 4,
        background: c.bg,
        border: `1px solid ${c.color}44`,
        color: c.color,
        fontSize: "0.65rem",
        fontFamily: "var(--font-mono)",
        fontWeight: 600,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}
    >
      {status}
    </span>
  );
}

// ─── Form Widgets ────────────────────────────────────────────────────

function DisputeFormWidget({
  accounts,
  onClose,
  onCreated,
}: {
  accounts: Account[];
  onClose: () => void;
  onCreated: (d: Dispute) => void;
}) {
  const [accountId, setAccountId] = useState(accounts[0]?.id ?? 1);
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [filedBy, setFiledBy] = useState("");
  const [gapBps, setGapBps] = useState("");
  const [amount, setAmount] = useState("");
  const [reason, setReason] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!filedBy || !gapBps || !amount || !reason) return;
    setSaving(true);
    const body: DisputeCreate = {
      account_id: accountId,
      dispute_date: date,
      filed_by: filedBy,
      gap_bps: parseFloat(gapBps),
      gap_dollar_amount: parseFloat(amount),
      dispute_type: "recon_gap",
      reason,
    };
    fetch(`${API}/disputes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then((r) => r.json())
      .then((d: Dispute) => {
        onCreated(d);
        setSaving(false);
      })
      .catch(() => setSaving(false));
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        background: C.surface,
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: "1.25rem",
        marginBottom: "1rem",
      }}
    >
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "0.65rem",
          color: C.green,
          letterSpacing: "0.12em",
          marginBottom: "0.85rem",
          textTransform: "uppercase",
        }}
      >
        + FILE NEW DISPUTE
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr 1fr",
          gap: "0.6rem",
          marginBottom: "0.6rem",
        }}
      >
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            PARTNER
          </span>
          <select
            value={accountId}
            onChange={(e) => setAccountId(Number(e.target.value))}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          >
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.partner_name}
              </option>
            ))}
          </select>
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            DISPUTE DATE
          </span>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            FILED BY
          </span>
          <input
            type="text"
            placeholder="e.g. Sarah Chen"
            value={filedBy}
            onChange={(e) => setFiledBy(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            GAP (BPS)
          </span>
          <input
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g. 2.45"
            value={gapBps}
            onChange={(e) => setGapBps(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            GAP AMOUNT ($)
          </span>
          <input
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g. 1234.56"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
      </div>
      <label
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "0.2rem",
          marginBottom: "0.75rem",
        }}
      >
        <span
          style={{
            fontSize: "0.6rem",
            color: C.textDim,
            fontFamily: "var(--font-mono)",
          }}
        >
          REASON
        </span>
        <textarea
          placeholder="Describe the basis for this dispute..."
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={2}
          maxLength={2000}
          style={{
            background: C.bg,
            border: `1px solid ${C.border}`,
            borderRadius: 4,
            padding: "0.4rem 0.5rem",
            color: C.text,
            fontSize: "0.72rem",
            fontFamily: "var(--font-mono)",
            resize: "vertical",
          }}
        />
      </label>
      <div
        style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}
      >
        <button
          type="button"
          onClick={onClose}
          style={{
            padding: "0.35rem 0.85rem",
            borderRadius: 6,
            border: `1px solid ${C.border}`,
            background: "transparent",
            color: C.textSec,
            cursor: "pointer",
            fontSize: "0.7rem",
            fontFamily: "var(--font-mono)",
          }}
        >
          CANCEL
        </button>
        <button
          type="submit"
          disabled={saving || !filedBy || !gapBps || !amount || !reason}
          style={{
            padding: "0.35rem 0.85rem",
            borderRadius: 6,
            border: `1px solid ${C.green}`,
            background: saving ? C.greenDim : C.green,
            color: "#fff",
            cursor: saving ? "not-allowed" : "pointer",
            fontSize: "0.7rem",
            fontFamily: "var(--font-mono)",
            fontWeight: 700,
            opacity:
              saving || !filedBy || !gapBps || !amount || !reason ? 0.5 : 1,
          }}
        >
          {saving ? "FILING..." : "FILE DISPUTE"}
        </button>
      </div>
    </form>
  );
}

function DisputeEditWidget({
  dispute,
  accounts,
  onClose,
  onSaved,
}: {
  dispute: Dispute;
  accounts: Account[];
  onClose: () => void;
  onSaved: (d: Dispute) => void;
}) {
  const [status, setStatus] = useState(dispute.status);
  const [notes, setNotes] = useState(dispute.notes ?? "");
  const [saving, setSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    fetch(`${API}/disputes/${dispute.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, notes }),
    })
      .then((r) => r.json())
      .then((d: Dispute) => {
        onSaved(d);
        setSaving(false);
      })
      .catch(() => setSaving(false));
  };

  return (
    <form
      onSubmit={handleSave}
      style={{
        background: C.surface,
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: "1.25rem",
        marginBottom: "1rem",
      }}
    >
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "0.65rem",
          color: C.green,
          letterSpacing: "0.12em",
          marginBottom: "0.85rem",
          textTransform: "uppercase",
        }}
      >
        EDIT DISPUTE #{dispute.id}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "0.6rem",
          marginBottom: "0.6rem",
        }}
      >
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            PARTNER
          </span>
          <div
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.textSec,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          >
            {dispute.partner_name}
          </div>
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            DISPUTE DATE
          </span>
          <div
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.textSec,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          >
            {dispute.dispute_date}
          </div>
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            STATUS
          </span>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          >
            <option value="open">open</option>
            <option value="resolved">resolved</option>
            <option value="escalated">escalated</option>
          </select>
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            GAP (BPS)
          </span>
          <div
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.red,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          >
            {dispute.gap_bps.toFixed(2)}
          </div>
        </label>
      </div>
      <label
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "0.2rem",
          marginBottom: "0.75rem",
        }}
      >
        <span
          style={{
            fontSize: "0.6rem",
            color: C.textDim,
            fontFamily: "var(--font-mono)",
          }}
        >
          NOTES
        </span>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          maxLength={2000}
          style={{
            background: C.bg,
            border: `1px solid ${C.border}`,
            borderRadius: 4,
            padding: "0.4rem 0.5rem",
            color: C.text,
            fontSize: "0.72rem",
            fontFamily: "var(--font-mono)",
            resize: "vertical",
          }}
        />
      </label>
      <div
        style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}
      >
        <button
          type="button"
          onClick={onClose}
          style={{
            padding: "0.35rem 0.85rem",
            borderRadius: 6,
            border: `1px solid ${C.border}`,
            background: "transparent",
            color: C.textSec,
            cursor: "pointer",
            fontSize: "0.7rem",
            fontFamily: "var(--font-mono)",
          }}
        >
          CANCEL
        </button>
        <button
          type="submit"
          disabled={saving}
          style={{
            padding: "0.35rem 0.85rem",
            borderRadius: 6,
            border: `1px solid ${C.green}`,
            background: saving ? C.greenDim : C.green,
            color: "#fff",
            cursor: saving ? "not-allowed" : "pointer",
            fontSize: "0.7rem",
            fontFamily: "var(--font-mono)",
            fontWeight: 700,
            opacity: saving ? 0.5 : 1,
          }}
        >
          {saving ? "SAVING..." : "SAVE CHANGES"}
        </button>
      </div>
    </form>
  );
}

function RateDiscrepancyFormWidget({
  accounts,
  onClose,
  onCreated,
}: {
  accounts: Account[];
  onClose: () => void;
  onCreated: (d: RateDiscrepancy) => void;
}) {
  const [accountId, setAccountId] = useState(accounts[0]?.id ?? 1);
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [contractRate, setContractRate] = useState("");
  const [appliedRate, setAppliedRate] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!contractRate || !appliedRate) return;
    setSaving(true);
    const contract = parseFloat(contractRate);
    const applied = parseFloat(appliedRate);
    const discrepancy_bps = Math.abs(contract - applied) * 10000;
    const body: RateDiscrepancyCreate = {
      account_id: accountId,
      discrepancy_date: date,
      contract_rate: contract,
      applied_rate: applied,
      discrepancy_bps,
      notes: notes || undefined,
    };
    fetch(`${API}/rate-discrepancies`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then((r) => r.json())
      .then((d: RateDiscrepancy) => {
        onCreated(d);
        setSaving(false);
      })
      .catch(() => setSaving(false));
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        background: C.surface,
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: "1.25rem",
        marginBottom: "1rem",
      }}
    >
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "0.65rem",
          color: C.blue,
          letterSpacing: "0.12em",
          marginBottom: "0.85rem",
          textTransform: "uppercase",
        }}
      >
        + FILE RATE DISCREPANCY
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr 1fr",
          gap: "0.6rem",
          marginBottom: "0.6rem",
        }}
      >
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            PARTNER
          </span>
          <select
            value={accountId}
            onChange={(e) => setAccountId(Number(e.target.value))}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          >
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.partner_name}
              </option>
            ))}
          </select>
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            DISCREPANCY DATE
          </span>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            CONTRACT RATE
          </span>
          <input
            type="number"
            step="0.0001"
            min="0"
            placeholder="e.g. 0.0450"
            value={contractRate}
            onChange={(e) => setContractRate(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            APPLIED RATE
          </span>
          <input
            type="number"
            step="0.0001"
            min="0"
            placeholder="e.g. 0.0448"
            value={appliedRate}
            onChange={(e) => setAppliedRate(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
        <label
          style={{ display: "flex", flexDirection: "column", gap: "0.2rem" }}
        >
          <span
            style={{
              fontSize: "0.6rem",
              color: C.textDim,
              fontFamily: "var(--font-mono)",
            }}
          >
            NOTES
          </span>
          <input
            type="text"
            placeholder="Optional note..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            style={{
              background: C.bg,
              border: `1px solid ${C.border}`,
              borderRadius: 4,
              padding: "0.35rem 0.5rem",
              color: C.text,
              fontSize: "0.72rem",
              fontFamily: "var(--font-mono)",
            }}
          />
        </label>
      </div>
      <div
        style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}
      >
        <button
          type="button"
          onClick={onClose}
          style={{
            padding: "0.35rem 0.85rem",
            borderRadius: 6,
            border: `1px solid ${C.border}`,
            background: "transparent",
            color: C.textSec,
            cursor: "pointer",
            fontSize: "0.7rem",
            fontFamily: "var(--font-mono)",
          }}
        >
          CANCEL
        </button>
        <button
          type="submit"
          disabled={saving || !contractRate || !appliedRate}
          style={{
            padding: "0.35rem 0.85rem",
            borderRadius: 6,
            border: `1px solid ${C.blue}`,
            background: saving ? C.blueDim : C.blue,
            color: "#fff",
            cursor: saving ? "not-allowed" : "pointer",
            fontSize: "0.7rem",
            fontFamily: "var(--font-mono)",
            fontWeight: 700,
            opacity: saving || !contractRate || !appliedRate ? 0.5 : 1,
          }}
        >
          {saving ? "FILING..." : "FILE DISCREPANCY"}
        </button>
      </div>
    </form>
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
  const [activeTab, setActiveTab] = useState<
    "dashboard" | "disputes" | "portfolio" | "regulatory"
  >("dashboard");
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [alerts, setAlerts] = useState<ThresholdAlert[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioStats | null>(null);
  const [regReports, setRegReports] = useState<RegulatoryReport[]>([]);
  const [unclaimedReports, setUnclaimedReports] = useState<RegulatoryReport[]>(
    [],
  );
  const [showDisputeForm, setShowDisputeForm] = useState(false);
  const [showRateDiscrepancyForm, setShowRateDiscrepancyForm] = useState(false);
  const [rateDiscrepancies, setRateDiscrepancies] = useState<RateDiscrepancy[]>(
    [],
  );
  const [editingDispute, setEditingDispute] = useState<Dispute | null>(null);

  // Accent colors per account
  const accountAccents = [C.green, C.gold, C.blue];
  const currentAccent = accountAccents[(selectedId ?? 1) - 1] ?? C.green;

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

  useEffect(() => {
    if (!backendOk) return;
    fetch(`${API}/disputes`)
      .then((r) => r.json())
      .then(setDisputes)
      .catch(() => {});
  }, [backendOk]);

  useEffect(() => {
    if (!backendOk) return;
    fetch(`${API}/alerts`)
      .then((r) => r.json())
      .then(setAlerts)
      .catch(() => {});
  }, [backendOk]);

  useEffect(() => {
    if (!backendOk) return;
    fetch(`${API}/rate-discrepancies`)
      .then((r) => r.json())
      .then(setRateDiscrepancies)
      .catch(() => {});
  }, [backendOk]);

  useEffect(() => {
    if (!backendOk) return;
    fetch(`${API}/portfolio`)
      .then((r) => r.json())
      .then(setPortfolio)
      .catch(() => {});
  }, [backendOk]);

  useEffect(() => {
    if (!backendOk) return;
    Promise.all([
      fetch(`${API}/regulatory/1099-int/1`).then((r) => r.json()),
      fetch(`${API}/regulatory/1099-int/2`).then((r) => r.json()),
      fetch(`${API}/regulatory/1099-int/3`).then((r) => r.json()),
    ])
      .then(setRegReports)
      .catch(() => {});
  }, [backendOk]);

  useEffect(() => {
    if (!backendOk) return;
    Promise.all([
      fetch(`${API}/regulatory/unclaimed-property/1`).then((r) => r.json()),
      fetch(`${API}/regulatory/unclaimed-property/2`).then((r) => r.json()),
      fetch(`${API}/regulatory/unclaimed-property/3`).then((r) => r.json()),
    ])
      .then(setUnclaimedReports)
      .catch(() => {});
  }, [backendOk]);

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
  const scenarioConfig: Record<string, { label: string; color: string }> = {
    base: { label: "BASE", color: C.blue },
    stress: { label: "STRESS", color: C.red },
    upside: { label: "UPSIDE", color: C.green },
  };
  const scen = scenarioConfig[scenario] ?? scenarioConfig.base;

  const unackAlerts = alerts.filter((a) => !a.acknowledged).length;

  return (
    <>
      <VideoCityscape />
      <div
        style={{
          minHeight: "100vh",
          background: "transparent",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* ── HEADER ─────────────────────────────────────── */}
        <header
          style={{
            borderBottom: `1px solid ${C.border}`,
            padding: "1.25rem 2rem",
            position: "sticky",
            top: 0,
            background: "rgba(13,17,23,0.95)",
            backdropFilter: "blur(12px)",
            zIndex: 100,
          }}
        >
          <div
            style={{
              maxWidth: "1200px",
              margin: "0 auto",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            {/* Wordmark */}
            <div
              style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}
            >
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  border: `2px solid ${C.green}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: C.green,
                  }}
                />
              </div>
              <h1
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  color: C.text,
                  letterSpacing: "0.18em",
                }}
              >
                FLOATYIELD
              </h1>
            </div>

            {/* Live status */}
            <div
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: backendOk === false ? C.red : C.green,
                }}
              />
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: backendOk === false ? C.red : C.green,
                  letterSpacing: "0.1em",
                  fontWeight: 600,
                }}
              >
                {backendOk === false ? "OFFLINE" : "LIVE"}
              </span>
            </div>

            {/* Alert badge */}
            {unackAlerts > 0 && (
              <div
                onClick={() => setActiveTab("disputes")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  background: C.redDim,
                  border: `1px solid ${C.red}55`,
                  borderRadius: 6,
                  padding: "0.25rem 0.6rem",
                  cursor: "pointer",
                }}
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill={C.red}>
                  <path d="M6 1a1 1 0 011 1v3.5L8.5 7H9a1 1 0 110 2H8a1 1 0 01-.8-.4L5.5 7H6a1 1 0 110-2H4a1 1 0 01.8-.4L6 3.5V2a1 1 0 011-1zM5 10a1 1 0 100 2 1 1 0 001-1H5a1 1 0 00-1 1z" />
                </svg>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.65rem",
                    color: C.red,
                    fontWeight: 600,
                  }}
                >
                  {unackAlerts} ALERT{unackAlerts > 1 ? "S" : ""}
                </span>
              </div>
            )}
          </div>
        </header>

        <main
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "2rem 2rem 3rem",
          }}
        >
          {/* ── DEMO BANNER ─────────────────────────────── */}
          <div
            style={{
              background: C.goldDim,
              border: `1px solid ${C.gold}33`,
              borderRadius: 8,
              padding: "0.65rem 1rem",
              marginBottom: "1.75rem",
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              fontSize: "0.75rem",
              color: C.gold,
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill={C.gold}>
              <path d="M7 0a7 7 0 100 14A7 7 0 007 0zm.5 3.5v4.25l2.75 1.6-.5.87L6.5 8V3.5h1z" />
            </svg>
            <span>
              <strong style={{ fontFamily: "var(--font-mono)" }}>
                DEMO MODE
              </strong>
              {" — "}Synthetic data. Models are structurally verified but not
              statistically validated on live Fed rate environments.
            </span>
          </div>

          {/* ── KPI ROW ──────────────────────────────────── */}
          {summary && (
            <div
              style={{
                display: "flex",
                gap: "1rem",
                marginBottom: "1.75rem",
                flexWrap: "wrap",
              }}
            >
              <StatCard
                label="Total Balance"
                value={fmtShort(summary.total_balance)}
                icon="◈"
                accent={C.blue}
              />
              <StatCard
                label="Avg Yield Rate"
                value={fmtPct(summary.weighted_avg_rate)}
                icon="◆"
                accent={C.gold}
              />
              <StatCard
                label="Annualized"
                value={fmtShort(summary.annualized_yield)}
                icon="◇"
                accent={C.green}
              />
              <StatCard
                label="30d Projected"
                value={fmtShort(summary.projected_30d_yield)}
                icon="▷"
                accent={C.green}
              />
            </div>
          )}

          {/* ── ACCOUNT + CONTROLS ───────────────────────── */}
          <div
            style={{
              background: C.surface,
              border: `1px solid ${C.border}`,
              borderRadius: 8,
              padding: "1.25rem",
              marginBottom: "1.5rem",
            }}
          >
            {/* Account selector */}
            <div style={{ marginBottom: "1rem" }}>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: C.textDim,
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "0.6rem",
                }}
              >
                PARTNER ACCOUNTS
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {accounts.map((a, i) => (
                  <AccountChip
                    key={a.id}
                    name={a.partner_name}
                    active={selectedId === a.id}
                    onClick={() => setSelectedId(a.id)}
                    accent={accountAccents[i] ?? C.green}
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
                    color: C.textDim,
                    letterSpacing: "0.1em",
                    marginRight: "0.25rem",
                  }}
                >
                  SCENARIO
                </span>
                {Object.entries(scenarioConfig).map(([val, cfg]) => (
                  <ScenarioPill
                    key={val}
                    label={cfg.label}
                    active={scenario === val}
                    onClick={() => setScenario(val)}
                    color={cfg.color}
                  />
                ))}
              </div>

              {/* Divider */}
              <div style={{ width: 1, height: 20, background: C.border }} />

              {/* Horizon selector */}
              <div
                style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.6rem",
                    color: C.textDim,
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
                          ? `1px solid ${C.green}`
                          : `1px solid ${C.border}`,
                      background: days === d ? C.greenDim : "transparent",
                      color: days === d ? C.green : C.textSec,
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

              {/* Scenario description */}
              <div
                style={{
                  marginLeft: "auto",
                  fontSize: "0.7rem",
                  color: C.textDim,
                  fontFamily: "var(--font-mono)",
                  display: scenario === "base" ? "none" : "block",
                }}
              >
                {scenario === "stress"
                  ? "Fed -50bps \u2192 yield \u00d70.85"
                  : "Fed +30bps \u2192 yield \u00d71.10"}
              </div>
            </div>
          </div>

          {/* ── TAB SWITCHER ─────────────────────────────── */}
          <div
            style={{
              display: "flex",
              gap: "0",
              marginBottom: "1.5rem",
              borderBottom: `1px solid ${C.border}`,
              paddingBottom: 0,
            }}
          >
            {(
              [
                ["dashboard", "FORECAST"],
                ["disputes", "DISPUTES"],
                ["portfolio", "PORTFOLIO"],
                ["regulatory", "REGULATORY"],
              ] as [typeof activeTab, string][]
            ).map(([tab, label]) => {
              const isActive = activeTab === tab;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: "0.5rem 1.1rem",
                    background: "transparent",
                    border: "none",
                    borderBottom: isActive
                      ? `2px solid ${C.green}`
                      : `2px solid transparent`,
                    color: isActive ? C.green : C.textDim,
                    cursor: "pointer",
                    fontSize: "0.7rem",
                    fontFamily: "var(--font-mono)",
                    fontWeight: isActive ? 600 : 400,
                    letterSpacing: "0.08em",
                    transition: "all 0.15s ease",
                    marginBottom: "-1px",
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>

          {/* ── LOADING ──────────────────────────────────── */}
          {loading && (
            <div
              style={{
                textAlign: "center",
                padding: "3rem",
                fontFamily: "var(--font-mono)",
                fontSize: "0.8rem",
                color: C.textDim,
                letterSpacing: "0.15em",
              }}
            >
              <div style={{ marginBottom: "0.5rem" }}>PROCESSING</div>
              <div
                style={{
                  width: "100%",
                  height: 2,
                  background: C.border,
                  borderRadius: 2,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    background: C.green,
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
                      fontFamily: "var(--font-mono)",
                      fontSize: "1.05rem",
                      fontWeight: 700,
                      color: currentAccent,
                      letterSpacing: "0.05em",
                    }}
                  >
                    {forecast.partner_name.toUpperCase()}
                  </div>
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.7rem",
                      color: C.textSec,
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
                    background: C.bg,
                    border: `1px solid ${C.border}`,
                    borderRadius: 6,
                    padding: "0.35rem 0.75rem",
                    fontSize: "0.7rem",
                    fontFamily: "var(--font-mono)",
                    color: C.textSec,
                    textAlign: "right",
                  }}
                >
                  <div
                    style={{
                      color: C.textDim,
                      fontSize: "0.6rem",
                      marginBottom: "0.1rem",
                    }}
                  >
                    RECON GAP
                  </div>
                  <div style={{ color: C.green }}>
                    {forecast.models[0]?.recon_gap_bps.toFixed(4)} bps
                  </div>
                </div>
              </div>

              {/* Yield bar chart */}
              <div
                style={{
                  background: C.surface,
                  border: `1px solid ${C.border}`,
                  borderRadius: 8,
                  padding: "1.5rem",
                  marginBottom: "1rem",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.65rem",
                    color: C.textDim,
                    letterSpacing: "0.15em",
                    textTransform: "uppercase",
                    marginBottom: "1.25rem",
                  }}
                >
                  {forecast.forecast_days}-Day Yield Projection
                </div>

                {sortedModels.map((model) => {
                  const cfg = MODEL_COLORS[model.model_name] ?? {
                    bar: C.textDim,
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
                              width: 8,
                              height: 8,
                              borderRadius: "50%",
                              background: cfg.bar,
                            }}
                          />
                          <span
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              fontWeight: 500,
                              color: C.textSec,
                              letterSpacing: "0.05em",
                            }}
                          >
                            {cfg.label}
                          </span>
                        </div>
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

                      {/* Bar + CI range */}
                      <div style={{ position: "relative" }}>
                        <div
                          style={{
                            background: C.bg,
                            borderRadius: 4,
                            height: 10,
                            overflow: "hidden",
                            border: `1px solid ${C.borderSub}`,
                          }}
                        >
                          {/* CI range */}
                          <div
                            style={{
                              position: "absolute",
                              left: `${Math.max(0, ciLeft)}%`,
                              width: `${Math.min(ciWidth, 100 - Math.max(0, ciLeft))}%`,
                              top: 0,
                              height: "100%",
                              background: `${cfg.bar}18`,
                              borderLeft: `2px solid ${cfg.bar}66`,
                              borderRight: `2px solid ${cfg.bar}66`,
                              boxSizing: "border-box",
                            }}
                          />
                          {/* Bar */}
                          <div
                            style={{
                              width: `${pct}%`,
                              height: "100%",
                              background: cfg.bar,
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
                          color: C.textDim,
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
                    color: C.textDim,
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
                        background: C.bg,
                        border: `1px solid ${C.borderSub}`,
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
                        background: C.green,
                        borderRadius: 2,
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
                    background: `${scen.color}10`,
                    border: `1px solid ${scen.color}33`,
                    borderRadius: 8,
                    padding: "0.75rem 1rem",
                    fontSize: "0.72rem",
                    color: C.textSec,
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
                    SCENARIO
                  </div>
                  {forecast.scenario_description}
                </div>
                <div
                  style={{
                    flex: "1 1 300px",
                    background: C.goldDim,
                    border: `1px solid ${C.gold}33`,
                    borderRadius: 8,
                    padding: "0.75rem 1rem",
                    fontSize: "0.72rem",
                    color: C.textSec,
                  }}
                >
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.6rem",
                      color: C.gold,
                      letterSpacing: "0.12em",
                      marginBottom: "0.3rem",
                      textTransform: "uppercase",
                    }}
                  >
                    RECONCILIATION
                  </div>
                  {forecast.recon_gap_description}
                </div>
              </div>

              {/* Model detail table */}
              <div
                style={{
                  background: C.surface,
                  border: `1px solid ${C.border}`,
                  borderRadius: 8,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    padding: "0.65rem 1rem",
                    borderBottom: `1px solid ${C.border}`,
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.6rem",
                    color: C.textDim,
                    letterSpacing: "0.15em",
                    textTransform: "uppercase",
                  }}
                >
                  Model Breakdown
                </div>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: C.bg }}>
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
                            color: C.textDim,
                            letterSpacing: "0.08em",
                            borderBottom: `1px solid ${C.border}`,
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
                        bar: C.textDim,
                      };
                      return (
                        <tr
                          key={model.model_name}
                          style={{ borderBottom: `1px solid ${C.borderSub}` }}
                        >
                          <td style={{ padding: "0.65rem 1rem" }}>
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
                                }}
                              />
                              <span
                                style={{
                                  fontFamily: "var(--font-mono)",
                                  fontSize: "0.75rem",
                                  color: C.text,
                                }}
                              >
                                {model.model_name}
                              </span>
                            </div>
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
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
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {fmt(model.lower_bound)} → {fmt(model.upper_bound)}
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {fmt(model.avg_daily)}
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.green,
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

          {/* ── DISPUTES PANEL ──────────────────────────── */}
          {activeTab === "disputes" && (
            <>
              {/* Header */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "1rem",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.65rem",
                    color: C.textDim,
                    letterSpacing: "0.15em",
                  }}
                >
                  RECONCILIATION DISPUTES
                </div>
                <button
                  onClick={() => setShowDisputeForm(!showDisputeForm)}
                  style={{
                    padding: "0.35rem 0.85rem",
                    borderRadius: 6,
                    border: `1px solid ${C.green}`,
                    background: showDisputeForm ? C.greenDim : "transparent",
                    color: C.green,
                    cursor: "pointer",
                    fontSize: "0.7rem",
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                  }}
                >
                  {showDisputeForm ? "CANCEL" : "+ FILE DISPUTE"}
                </button>
              </div>

              {/* Dispute form */}
              {showDisputeForm && (
                <DisputeFormWidget
                  accounts={accounts}
                  onClose={() => setShowDisputeForm(false)}
                  onCreated={(d) => {
                    setDisputes((prev) => [d, ...prev]);
                    setShowDisputeForm(false);
                  }}
                />
              )}

              {/* Edit dispute form */}
              {editingDispute && (
                <DisputeEditWidget
                  dispute={editingDispute}
                  accounts={accounts}
                  onClose={() => setEditingDispute(null)}
                  onSaved={(updated) => {
                    setDisputes((prev) =>
                      prev.map((d) => (d.id === updated.id ? updated : d)),
                    );
                    setEditingDispute(null);
                  }}
                />
              )}

              {/* Alerts section */}
              {alerts.length > 0 && (
                <div
                  style={{
                    background: C.redDim,
                    border: `1px solid ${C.red}33`,
                    borderRadius: 8,
                    padding: "0.75rem 1rem",
                    marginBottom: "1rem",
                  }}
                >
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "0.6rem",
                      color: C.red,
                      letterSpacing: "0.12em",
                      marginBottom: "0.6rem",
                      textTransform: "uppercase",
                    }}
                  >
                    THRESHOLD BREACH ALERTS
                  </div>
                  {alerts
                    .filter((a) => !a.acknowledged)
                    .map((alert) => (
                      <div
                        key={alert.id}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: "0.3rem 0",
                          borderBottom: `1px solid ${C.red}22`,
                        }}
                      >
                        <div
                          style={{
                            fontSize: "0.72rem",
                            color: C.textSec,
                            fontFamily: "var(--font-mono)",
                          }}
                        >
                          <span
                            style={{
                              color:
                                alert.severity === "critical" ? C.red : C.gold,
                            }}
                          >
                            [{alert.severity.toUpperCase()}]
                          </span>{" "}
                          {alert.partner_name} — {alert.gap_bps.toFixed(2)} bps
                          (threshold: {alert.threshold_bps} bps)
                        </div>
                        <button
                          onClick={() => {
                            fetch(`${API}/alerts/${alert.id}/acknowledge`, {
                              method: "POST",
                            }).then(() => {
                              setAlerts((prev) =>
                                prev.map((a) =>
                                  a.id === alert.id
                                    ? { ...a, acknowledged: true }
                                    : a,
                                ),
                              );
                            });
                          }}
                          style={{
                            padding: "0.2rem 0.5rem",
                            borderRadius: 4,
                            border: `1px solid ${C.red}55`,
                            background: "transparent",
                            color: C.red,
                            cursor: "pointer",
                            fontSize: "0.65rem",
                            fontFamily: "var(--font-mono)",
                          }}
                        >
                          ACKNOWLEDGE
                        </button>
                      </div>
                    ))}
                  {alerts.filter((a) => !a.acknowledged).length === 0 && (
                    <div
                      style={{
                        fontSize: "0.72rem",
                        color: C.textDim,
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      No unacknowledged alerts
                    </div>
                  )}
                </div>
              )}

              {/* Disputes table */}
              {disputes.length === 0 ? (
                <div
                  style={{
                    background: C.surface,
                    border: `1px solid ${C.border}`,
                    borderRadius: 8,
                    padding: "2rem",
                    textAlign: "center",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.75rem",
                    color: C.textDim,
                  }}
                >
                  No disputes filed. Use &quot;File Dispute&quot; to log a
                  reconciliation gap.
                </div>
              ) : (
                <div
                  style={{
                    background: C.surface,
                    border: `1px solid ${C.border}`,
                    borderRadius: 8,
                    overflow: "hidden",
                    marginBottom: "1.5rem",
                  }}
                >
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ background: C.bg }}>
                        {[
                          "Partner",
                          "Date",
                          "Filed By",
                          "Gap (bps)",
                          "Amount",
                          "Type",
                          "Status",
                        ].map((h) => (
                          <th
                            key={h}
                            style={{
                              padding: "0.5rem 0.75rem",
                              textAlign: "left",
                              fontFamily: "var(--font-mono)",
                              fontWeight: 500,
                              fontSize: "0.6rem",
                              color: C.textDim,
                              letterSpacing: "0.08em",
                              borderBottom: `1px solid ${C.border}`,
                            }}
                          >
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {disputes.map((d) => (
                        <tr
                          key={d.id}
                          onClick={() => setEditingDispute(d)}
                          style={{
                            borderBottom: `1px solid ${C.borderSub}`,
                            cursor: "pointer",
                          }}
                        >
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.text,
                            }}
                          >
                            {d.partner_name}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {d.dispute_date}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {d.filed_by}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.red,
                            }}
                          >
                            {d.gap_bps.toFixed(2)}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {fmt(d.gap_dollar_amount)}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {d.dispute_type}
                          </td>
                          <td style={{ padding: "0.5rem 0.75rem" }}>
                            <StatusBadge status={d.status} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* ── RATE DISCREPANCIES ─────────────────────── */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "1rem",
                  marginTop: "0.5rem",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.65rem",
                    color: C.textDim,
                    letterSpacing: "0.15em",
                  }}
                >
                  RATE DISCREPANCIES
                </div>
                <button
                  onClick={() =>
                    setShowRateDiscrepancyForm(!showRateDiscrepancyForm)
                  }
                  style={{
                    padding: "0.35rem 0.85rem",
                    borderRadius: 6,
                    border: `1px solid ${C.blue}`,
                    background: showRateDiscrepancyForm
                      ? C.blueDim
                      : "transparent",
                    color: C.blue,
                    cursor: "pointer",
                    fontSize: "0.7rem",
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                  }}
                >
                  {showRateDiscrepancyForm ? "CANCEL" : "+ FILE DISCREPANCY"}
                </button>
              </div>

              {showRateDiscrepancyForm && (
                <RateDiscrepancyFormWidget
                  accounts={accounts}
                  onClose={() => setShowRateDiscrepancyForm(false)}
                  onCreated={(d) => {
                    setRateDiscrepancies((prev) => [d, ...prev]);
                    setShowRateDiscrepancyForm(false);
                  }}
                />
              )}

              {rateDiscrepancies.length === 0 ? (
                <div
                  style={{
                    background: C.surface,
                    border: `1px solid ${C.border}`,
                    borderRadius: 8,
                    padding: "2rem",
                    textAlign: "center",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.75rem",
                    color: C.textDim,
                  }}
                >
                  No rate discrepancies filed.
                </div>
              ) : (
                <div
                  style={{
                    background: C.surface,
                    border: `1px solid ${C.border}`,
                    borderRadius: 8,
                    overflow: "hidden",
                  }}
                >
                  <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ background: C.bg }}>
                        {[
                          "Partner",
                          "Date",
                          "Contract",
                          "Applied",
                          "Gap (bps)",
                          "Status",
                          "Notes",
                        ].map((h) => (
                          <th
                            key={h}
                            style={{
                              padding: "0.5rem 0.75rem",
                              textAlign: "left",
                              fontFamily: "var(--font-mono)",
                              fontWeight: 500,
                              fontSize: "0.6rem",
                              color: C.textDim,
                              letterSpacing: "0.08em",
                              borderBottom: `1px solid ${C.border}`,
                            }}
                          >
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rateDiscrepancies.map((rd) => (
                        <tr
                          key={rd.id}
                          style={{ borderBottom: `1px solid ${C.borderSub}` }}
                        >
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.text,
                            }}
                          >
                            {rd.partner_name}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {rd.discrepancy_date}
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {(rd.contract_rate * 100).toFixed(4)}%
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textSec,
                            }}
                          >
                            {(rd.applied_rate * 100).toFixed(4)}%
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.blue,
                            }}
                          >
                            {rd.discrepancy_bps.toFixed(2)}
                          </td>
                          <td style={{ padding: "0.5rem 0.75rem" }}>
                            <StatusBadge status={rd.status} />
                          </td>
                          <td
                            style={{
                              padding: "0.5rem 0.75rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.72rem",
                              color: C.textDim,
                              maxWidth: 160,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {rd.notes ?? "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}

          {/* ── PORTFOLIO PANEL ──────────────────────────── */}
          {activeTab === "portfolio" && portfolio && (
            <>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: C.textDim,
                  letterSpacing: "0.15em",
                  marginBottom: "1rem",
                }}
              >
                AGGREGATE PORTFOLIO VIEW
              </div>
              <div
                style={{
                  display: "flex",
                  gap: "1rem",
                  marginBottom: "1rem",
                  flexWrap: "wrap",
                }}
              >
                <StatCard
                  label="Total Balance"
                  value={fmtShort(portfolio.total_balance)}
                  icon="◈"
                  accent={C.blue}
                />
                <StatCard
                  label="Annualized Yield"
                  value={fmtShort(portfolio.annualized_yield)}
                  icon="◆"
                  accent={C.green}
                />
                <StatCard
                  label="30d Projected"
                  value={fmtShort(portfolio.projected_30d_yield)}
                  icon="▷"
                  accent={C.green}
                />
                <StatCard
                  label="Open Disputes"
                  value={String(portfolio.open_disputes)}
                  icon="◎"
                  accent={portfolio.open_disputes > 0 ? C.red : C.green}
                />
                <StatCard
                  label="Avg Gap (bps)"
                  value={portfolio.avg_gap_bps.toFixed(2)}
                  icon="◇"
                  accent={C.gold}
                />
                <StatCard
                  label="Max Gap (bps)"
                  value={portfolio.max_gap_bps.toFixed(2)}
                  icon="◇"
                  accent={C.gold}
                />
              </div>
              {/* Account-level breakdown */}
              <div
                style={{
                  background: C.surface,
                  border: `1px solid ${C.border}`,
                  borderRadius: 8,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    padding: "0.65rem 1rem",
                    borderBottom: `1px solid ${C.border}`,
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.6rem",
                    color: C.textDim,
                    letterSpacing: "0.15em",
                    textTransform: "uppercase",
                  }}
                >
                  Account Breakdown
                </div>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: C.bg }}>
                      {[
                        "Partner",
                        "Balance",
                        "Rate",
                        "Annualized",
                        "30d Projected",
                      ].map((h) => (
                        <th
                          key={h}
                          style={{
                            padding: "0.5rem 1rem",
                            textAlign: "left",
                            fontFamily: "var(--font-mono)",
                            fontWeight: 500,
                            fontSize: "0.6rem",
                            color: C.textDim,
                            letterSpacing: "0.08em",
                            borderBottom: `1px solid ${C.border}`,
                          }}
                        >
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {accounts.map((a) => {
                      const ann = a.balance * a.yield_rate;
                      const proj30 = (ann / 365) * 30;
                      return (
                        <tr
                          key={a.id}
                          style={{ borderBottom: `1px solid ${C.borderSub}` }}
                        >
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.75rem",
                              color: C.text,
                            }}
                          >
                            {a.partner_name}
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.75rem",
                              color: C.textSec,
                            }}
                          >
                            {fmt(a.balance)}
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.75rem",
                              color: C.textSec,
                            }}
                          >
                            {(a.yield_rate * 100).toFixed(3)}%
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.75rem",
                              color: C.textSec,
                            }}
                          >
                            {fmt(ann)}
                          </td>
                          <td
                            style={{
                              padding: "0.65rem 1rem",
                              fontFamily: "var(--font-mono)",
                              fontSize: "0.75rem",
                              color: C.green,
                            }}
                          >
                            {fmt(proj30)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* ── REGULATORY PANEL ────────────────────────── */}
          {activeTab === "regulatory" && (
            <>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: C.textDim,
                  letterSpacing: "0.15em",
                  marginBottom: "1rem",
                }}
              >
                REGULATORY REPORTS
              </div>
              {regReports.map((rep) => (
                <div
                  key={`${rep.report_type}-${rep.account_id}-${rep.tax_year}`}
                  style={{
                    background: C.surface,
                    border: `1px solid ${C.border}`,
                    borderRadius: 8,
                    padding: "1.25rem",
                    marginBottom: "0.85rem",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "0.75rem",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          color: C.text,
                        }}
                      >
                        {rep.report_type}
                      </div>
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.65rem",
                          color: C.textDim,
                          marginTop: "0.15rem",
                        }}
                      >
                        {rep.partner_name} · Tax Year {rep.tax_year}
                      </div>
                    </div>
                    <div
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "0.6rem",
                        color: C.textDim,
                        textAlign: "right",
                      }}
                    >
                      Generated {rep.generated_at}
                    </div>
                  </div>
                  <div
                    style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: "0.6rem",
                          color: C.textDim,
                          fontFamily: "var(--font-mono)",
                          marginBottom: "0.15rem",
                        }}
                      >
                        TOTAL YIELD
                      </div>
                      <div
                        style={{
                          fontSize: "0.9rem",
                          fontWeight: 700,
                          color: C.green,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {fmt(rep.total_yield)}
                      </div>
                    </div>
                    <div>
                      <div
                        style={{
                          fontSize: "0.6rem",
                          color: C.textDim,
                          fontFamily: "var(--font-mono)",
                          marginBottom: "0.15rem",
                        }}
                      >
                        ACCOUNT BALANCE
                      </div>
                      <div
                        style={{
                          fontSize: "0.9rem",
                          fontWeight: 700,
                          color: C.text,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {fmt(rep.account_balance)}
                      </div>
                    </div>
                    <div>
                      <div
                        style={{
                          fontSize: "0.6rem",
                          color: C.textDim,
                          fontFamily: "var(--font-mono)",
                          marginBottom: "0.15rem",
                        }}
                      >
                        YIELD RATE
                      </div>
                      <div
                        style={{
                          fontSize: "0.9rem",
                          fontWeight: 700,
                          color: C.text,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {(rep.yield_rate * 100).toFixed(3)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Unclaimed Property */}
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: C.textDim,
                  letterSpacing: "0.15em",
                  marginBottom: "0.3rem",
                  marginTop: "1.5rem",
                }}
              >
                UNCLAIMED PROPERTY NOTICES
              </div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.6rem",
                  color: C.textDim,
                  marginBottom: "1rem",
                  opacity: 0.7,
                }}
              >
                Triggered for closed accounts with residual balances — all demo
                accounts are active
              </div>
              {unclaimedReports.map((rep) => (
                <div
                  key={`${rep.report_type}-${rep.account_id}-${rep.tax_year}`}
                  style={{
                    background: C.surface,
                    border: `1px solid ${C.border}`,
                    borderRadius: 8,
                    padding: "1.25rem",
                    marginBottom: "0.85rem",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "0.75rem",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          color: C.text,
                        }}
                      >
                        {rep.report_type}
                      </div>
                      <div
                        style={{
                          fontFamily: "var(--font-mono)",
                          fontSize: "0.65rem",
                          color: C.textDim,
                          marginTop: "0.15rem",
                        }}
                      >
                        {rep.partner_name} · Tax Year {rep.tax_year}
                      </div>
                    </div>
                    <div
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "0.6rem",
                        color: C.textDim,
                        textAlign: "right",
                      }}
                    >
                      Generated {rep.generated_at}
                    </div>
                  </div>
                  <div
                    style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: "0.6rem",
                          color: C.textDim,
                          fontFamily: "var(--font-mono)",
                          marginBottom: "0.15rem",
                        }}
                      >
                        UNCLAIMED YIELD
                      </div>
                      <div
                        style={{
                          fontSize: "0.9rem",
                          fontWeight: 700,
                          color: C.gold,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {fmt(rep.total_yield)}
                      </div>
                    </div>
                    <div>
                      <div
                        style={{
                          fontSize: "0.6rem",
                          color: C.textDim,
                          fontFamily: "var(--font-mono)",
                          marginBottom: "0.15rem",
                        }}
                      >
                        ACCOUNT BALANCE
                      </div>
                      <div
                        style={{
                          fontSize: "0.9rem",
                          fontWeight: 700,
                          color: C.text,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {fmt(rep.account_balance)}
                      </div>
                    </div>
                    <div>
                      <div
                        style={{
                          fontSize: "0.6rem",
                          color: C.textDim,
                          fontFamily: "var(--font-mono)",
                          marginBottom: "0.15rem",
                        }}
                      >
                        YIELD RATE
                      </div>
                      <div
                        style={{
                          fontSize: "0.9rem",
                          fontWeight: 700,
                          color: C.text,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {(rep.yield_rate * 100).toFixed(3)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}

          {/* ── FOOTER ─────────────────────────────────── */}
          <footer
            style={{
              marginTop: "3rem",
              paddingTop: "1rem",
              borderTop: `1px solid ${C.border}`,
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
                color: C.textDim,
                letterSpacing: "0.1em",
              }}
            >
              FLOATYIELD API · {new Date().getFullYear()}
            </span>
            <div style={{ display: "flex", gap: "1rem" }}>
              <a
                href="http://localhost:8000/docs"
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.65rem",
                  color: C.blue,
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
                  color: C.textDim,
                  textDecoration: "none",
                  letterSpacing: "0.05em",
                }}
              >
                [ POST /forecast/all ]
              </a>
            </div>
          </footer>
        </main>

        {/* ── KEYFRAME ANIMATIONS ─────────────────────────── */}
        <style>{`
          @keyframes loading-sweep {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(350%); }
          }
        `}</style>
      </div>
    </>
  );
}
