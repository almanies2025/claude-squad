# FloatYield — Product Requirements

**Version:** 1.0-draft
**Status:** Requirements Analysis
**Date:** 2026-04-30
**Author:** requirements-analyst

---

## Executive Summary

- **Product:** FloatYield — B2B yield infrastructure platform
- **Core Function:** Enable banks and fintechs to offer interest-bearing payment accounts to end customers
- **Target Users:** Sponsor Banks (primary), Fintechs (secondary integration partners)
- **Complexity:** High
- **Risk Level:** High (regulatory, financial, operational)
- **Estimated Autonomous Sessions to MVP:** 4-6 sessions

---

## 1. Sponsor Bank Architecture — Money Flow

### 1.1 End-to-End Fund Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FLOATYIELD ARCHITECTURE                                 │
│                                                                                      │
│  CUSTOMER                  SPONSOR BANK                 CUSTODIAN           FED      │
│  ─────────                 ─────────────               ──────────          ───      │
│                                                                                      │
│  [Payment Account]                                                                         │
│       │                          │                                                    │
│       │ ① Deposit ( ACH, Wires ) │                                                    │
│       ▼                          ▼                                                    │
│  ┌──────────────────────────────────────────────┐                                    │
│  │  CUSTOMER DEPOSITS HELD IN BANK's MASTER    │                                    │
│  │  ACCOUNT AT FED (Dacy.001 / Reserve Account) │                                   │
│  └──────────────────────────────────────────────┘                                    │
│       │                          │                                                    │
│       │              ┌────────────┴────────────┐                                     │
│       │              │  YIELD CALCULATION      │                                     │
│       │              │  FloatYield Engine       │                                     │
│       │              └────────────┬────────────┘                                     │
│       │                           │                                                  │
│       │              ┌────────────┴────────────┐                                     │
│       │              │  RESERVE MANAGEMENT    │                                     │
│       │              │  Bank invests reserves │                                     │
│       │              │  in Treasuries via     │                                     │
│       │              │  Custodian             │                                     │
│       │              └────────────┬────────────┘                                     │
│       │                           │                                                  │
│       │                    ┌──────┴──────┐                                           │
│       │                    │ TREASURIES  │                                           │
│       │                    │ (UST bills, │                                           │
│       │                    │  notes, bonds)│                                         │
│       │                    └──────┬──────┘                                           │
│       │                           │                                                  │
│       │ ② Daily Yield Accrual    │                                                  │
│       │    (bank's reserve        │                                                  │
│       │     generates yield)       │                                                 │
│       │                           │                                                  │
│       │ ③ FloatYield calculates    │                                                  │
│       │    customer yield:         │                                                  │
│       │    balance × rate × days/365                                       │
│       │                           │                                                  │
│       │ ④ Bank transfers yield    │                                                  │
│       │    funds to FloatYield     │                                                  │
│       │    (settlement account)    │                                                 │
│       │                           │                                                  │
│       │ ⑤ FloatYield distributes   │                                                  │
│       │    yield to customer       │                                                  │
│       │    accounts (net of fee)   │                                                  │
│       │                           │                                                  │
│       │ ⑥ FloatYield deducts      │                                                  │
│       │    platform fee           │                                                  │
│       │                           │                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Money Flow Steps

| Step | Actor           | Action                                   | Mechanism                       | Timing                |
| ---- | --------------- | ---------------------------------------- | ------------------------------- | --------------------- |
| 1    | Customer        | Deposits funds                           | ACH, wire transfer              | T+1 settlement        |
| 2    | Federal Reserve | Credits bank's reserve account           | Fedwire, ACH                    | T+1                   |
| 3    | Sponsor Bank    | Holds deposits in reserve account        | Passive                         | Continuous            |
| 4    | Sponsor Bank    | Invests in Treasuries via custodian      | Custodian API                   | T+1                   |
| 5    | US Treasury     | Pays interest on T-bills/notes/bonds     | Coupon payment                  | Maturity + T+1        |
| 6    | FloatYield      | Calculates daily yield per account       | `balance × annual_rate × 1/365` | EOD                   |
| 7    | Sponsor Bank    | Transfers yield to FloatYield settlement | ACH, internal transfer          | T+1 after calculation |
| 8    | FloatYield      | Distributes yield to customer accounts   | Internal ledger                 | Same day as receipt   |
| 9    | FloatYield      | Deducts platform fee                     | Fee calculation                 | At distribution       |

### 1.3 Account Hierarchy

```
SPONSOR BANK
├── Master Account (at Fed)
│   └── Segregated Reserve Tranche (FloatYield-designated)
│       └── Customer Deposit Pool
│           ├── Customer Account A
│           ├── Customer Account B
│           └── Customer Account N
└── Settlement Account (for yield transfers)
    └── FloatYield's Bank Account
        └── FloatYield Fee Account
```

### 1.4 Key Architectural Questions

1. **Who holds the reserves?** Sponsor Bank holds at Fed. FloatYield tracks via daily reconciliation.
2. **Who invests?** Sponsor Bank (or its designated investment manager) buys Treasuries through a custodian.
3. **Who calculates yield?** FloatYield — this is the core intellectual property.
4. **Who distributes?** FloatYield executes yield distribution instructions; bank executes the actual funds transfer.

---

## 2. API Design

### 2.1 Integration Model

FloatYield provides a **REST API** that the Sponsor Bank and Fintech partners integrate with. The API is hosted by FloatYield; bank/fintech systems call it.

### 2.2 Core Endpoints

#### Account Management

| Endpoint                                  | Method | Description                                             | Auth           |
| ----------------------------------------- | ------ | ------------------------------------------------------- | -------------- |
| `/v1/accounts`                            | POST   | Create a new interest-bearing account                   | API Key + HMAC |
| `/v1/accounts/{account_id}`               | GET    | Retrieve account details and current balance            | API Key + HMAC |
| `/v1/accounts/{account_id}/balance`       | GET    | Real-time balance inquiry                               | API Key + HMAC |
| `/v1/accounts/{account_id}/yield-balance` | GET    | Current accrued yield balance                           | API Key + HMAC |
| `/v1/accounts/{account_id}/yield-summary` | GET    | Yield YTD, prior periods                                | API Key + HMAC |
| `/v1/accounts/{account_id}/close`         | POST   | Request account closure; final balance + yield paid out | API Key + HMAC |

#### Transaction History

| Endpoint                                   | Method | Description                                                          | Auth           |
| ------------------------------------------ | ------ | -------------------------------------------------------------------- | -------------- |
| `/v1/accounts/{account_id}/transactions`   | GET    | Paginated transaction history (deposits, withdrawals, yield credits) | API Key + HMAC |
| `/v1/accounts/{account_id}/yield-payments` | GET    | Historical yield payment records                                     | API Key + HMAC |

#### Yield Schedule

| Endpoint                                   | Method | Description                                        | Auth           |
| ------------------------------------------ | ------ | -------------------------------------------------- | -------------- |
| `/v1/accounts/{account_id}/yield-schedule` | GET    | Upcoming yield payment dates and projected amounts | API Key + HMAC |
| `/v1/yield-rates`                          | GET    | Current annual yield rates by account tier         | API Key + HMAC |

#### Webhooks

| Event               | Description                            | Payload                                         |
| ------------------- | -------------------------------------- | ----------------------------------------------- |
| `yield.credited`    | Yield payment posted to account        | `{account_id, amount, date, new_yield_balance}` |
| `account.created`   | New account activated                  | `{account_id, customer_id, timestamp}`          |
| `balance.threshold` | Balance crossed configurable threshold | `{account_id, balance, threshold}`              |

### 2.3 Request/Response Shapes

#### Create Account

```json
// Request
POST /v1/accounts
{
  "customer": {
    "id": "string (partner's customer ID)",
    "type": "individual" | "business",
    "kyc_reference": "string ( bank's KYC record ID )"
  },
  "account_type": "interest_checking",
  "initial_balance": "decimal (optional)"
}

// Response
{
  "account_id": "fy_acct_...",
  "status": "active",
  "yield_rate": "decimal (e.g., 0.0450 for 4.50%)",
  "created_at": "ISO8601"
}
```

#### Yield Balance

```json
// Response
GET /v1/accounts/{account_id}/yield-balance
{
  "account_id": "fy_acct_...",
  "current_balance": "decimal",
  "accrued_yield_today": "decimal",
  "yield_balance": "decimal (total accrued, unpaid)",
  "last_yield_payment_date": "ISO8601",
  "last_yield_payment_amount": "decimal",
  "ytd_yield_earned": "decimal",
  "annual_rate": "decimal"
}
```

### 2.4 Rate Tiers (MVP)

| Tier      | Balance Range        | Annual Rate | Accrual |
| --------- | -------------------- | ----------- | ------- |
| Standard  | $0 - $9,999.99       | 4.25%       | Daily   |
| Preferred | $10,000 - $49,999.99 | 4.50%       | Daily   |
| Premier   | $50,000+             | 4.75%       | Daily   |

---

## 3. Reserve Management

### 3.1 Reserve Holdings

| Question                                 | Answer                                                                                |
| ---------------------------------------- | ------------------------------------------------------------------------------------- |
| Who buys the Treasuries?                 | Sponsor Bank (or its investment manager)                                              |
| Who is the custodian?                    | Bank's existing custodian (e.g., BNY Mellon, State Street) or designated custodian    |
| Who owns the FloatYield reserve tranche? | Sponsor Bank — FloatYield is a tracker/calculator, not a holder                       |
| What securities?                         | US Treasury bills, notes, bonds; short-duration only (<2 year maturity for liquidity) |
| What is the target reserve ratio?        | Bank-defined; FloatYield monitors and alerts                                          |

### 3.2 Daily Reconciliation Process

```
T+1 DAILY RECONCILIATION CYCLE
══════════════════════════════

1. FLOATYIELD CALCULATES (EOD T)
   ├── Sum all customer account balances
   ├── Apply tiered rates per account
   ├── Compute individual daily yield: balance × rate × 1/365
   └── Aggregate total yield liability for the day

2. SPONSOR BANK RECONCILES
   ├── Confirms total deposits at Fed (master account balance)
   ├── Confirms Treasury holdings via custodian statement
   ├── Computes actual yield income from Treasury portfolio
   └── Verifies yield liability matches FloatYield calculation (or flags variance)

3. CUSTODIAN PROVIDES
   ├── T-bill portfolio valuation (market value)
   ├── Accrued interest report
   └── Settlement statements for new purchases/maturities

4. VARIANCE CHECK
   ├── FloatYield yield liability vs Bank yield income
   ├── Tolerance: ±1 basis point (0.01%) before escalation
   └── If variance > tolerance: manual review; bank has 24h to resolve

5. SETTLEMENT AUTHORIZATION
   ├── Bank authorizes transfer of yield funds to FloatYield settlement account
   └── FloatYield confirms receipt and books to customer accounts

6. FLOATYIELD BOOKS
   ├── Credits yield to each customer account (net of fee)
   ├── Updates yield balance ledger
   └── Triggers webhook notifications
```

### 3.3 Reconciliation Data Flow

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   BANK       │         │  CUSTODIAN   │         │  FLOATYIELD  │
│  (Fed Acct)  │         │  (Treasuries)│         │   (Engine)   │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  Reserve Balance       │                        │
       │───────────────────────►│                        │
       │                        │                        │
       │  Custodian Statement  │                        │
       │◄──────────────────────│                        │
       │                        │                        │
       │                        │   Aggregated Yield    │
       │                        │◄─────────────────────│  (calculated)
       │                        │                        │
       │  Treasury Income       │                        │
       │───────────────────────►│                        │
       │                        │                        │
       │  Yield Transfer Auth   │                        │
       │────────────────────────┼───────────────────────►│
       │                        │                        │
```

---

## 4. Yield Calculation Engine

### 4.1 Core Formula

```
daily_yield = account_balance × annual_rate × days_elapsed / 365
```

**Where:**

- `account_balance`: End-of-day balance (or average balance if configured)
- `annual_rate`: Expressed as decimal (e.g., 4.50% = 0.0450)
- `days_elapsed`: Calendar days in the accrual period (normally 1 for daily accrual)
- `365`: Fixed day-count basis (actual/365 convention)

### 4.2 Daily Accrual Algorithm

```python
# Pseudocode — FloatYield Yield Accrual Engine

def calculate_daily_yield(account_id: str, date: date) -> Decimal:
    account = get_account(account_id)
    balance = get_end_of_day_balance(account_id, date)
    rate = get_applicable_rate(account, date)  # tiered by balance

    # Standard accrual
    daily_yield = balance * rate * 1 / 365

    # Partial-day handling (first day / last day)
    if is_partial_day(date):
        fraction = get_fraction_of_day(date)
        daily_yield = balance * rate * fraction / 365

    return round(daily_yield, 8)  # 8 decimal places for precision
```

### 4.3 Partial Day Handling

Partial days occur when:

- Account opened mid-day (first day): `fraction = hours_remaining / 24`
- Account closed mid-day (last day): `fraction = hours_elapsed / 24`
- Daylight saving time transitions: treated as 23 or 25 hour days

For MVP: **Full-day accrual only** (accounts opened/closed at start of business day). Partial day support is Phase 2.

### 4.4 Yield Distribution Frequency

| Option        | Frequency          | Pros                                   | Cons                                        |
| ------------- | ------------------ | -------------------------------------- | ------------------------------------------- |
| **Daily**     | Every business day | Simple; customers see frequent credits | Higher processing cost; more reconciliation |
| **Weekly**    | Every Friday       | Balanced; reasonable frequency         | Slight delay in credit                      |
| **Monthly**   | 1st of month       | Simple reconciliation; lower cost      | Customers don't see frequent rewards        |
| **On-Demand** | Customer requests  | Flexibility                            | Complexity in tracking                      |

**MVP Decision: Monthly** — Simplifies reconciliation for pilot. Transition to daily in Phase 2.

**Post-MVP: Daily** — Industry expectation for competitive yield products.

### 4.5 Yield Cap and Floor

- **Floor:** 0% — yield cannot go negative (even if Treasury yields drop)
- **Cap:** 5.00% (configurable) — protects bank margin if rates rise sharply
- **Rate Change Grace:** When bank changes rates, a 5-day grace period applies before new rate affects customer accounts (bank's published rate applies from day 6 forward)

---

## 5. KYC/AML Compliance

### 5.1 Ownership Matrix

| Obligation                           | Owner            | FloatYield Role                                            |
| ------------------------------------ | ---------------- | ---------------------------------------------------------- |
| Customer Identity Verification (KYC) | **Sponsor Bank** | Receives KYC reference ID; stores mapping                  |
| Customer Risk Scoring                | **Sponsor Bank** | Receives risk tier; applies enhanced monitoring if flagged |
| Beneficial Ownership (BO)            | **Sponsor Bank** | Receives BO certification; stores                          |
| AML Transaction Monitoring           | **Sponsor Bank** | Receives FloatYield transaction data; monitors             |
| Suspicious Activity Reporting (SAR)  | **Sponsor Bank** | Files with FinCEN; FloatYield assists with data            |
| Customer Due Diligence (CDD/EDD)     | **Sponsor Bank** | Stores CDD/EDD records reference                           |
| OFAC Screening                       | **Sponsor Bank** | Screens customer list daily; FloatYield gets match alerts  |
| 314(b) Information Sharing           | **Both**         | Protocol established for SAR investigations                |

### 5.2 FloatYield's Compliance Infrastructure

FloatYield must build:

```
COMPLIANCE INFRASTRUCTURE
├── KYC Record Storage
│   ├── Store KYC reference IDs (not full KYC data — bank owns)
│   ├── KYC status tracking (verified, pending, failed)
│   └── KYC refresh schedule (annual re-verification)
│
├── AML Monitoring Feed
│   ├── Daily transaction report to bank (all FloatYield transactions)
│   ├── Structured data format (JSON/XML via SFTP or API)
│   └── 90-day rolling window retained
│
├── OFAC Compliance
│   ├── Daily customer list sync to bank's screening system
│   ├── Block account activation if OFAC match pending
│   └── Alert bank immediately on OFAC hit
│
├── Enhanced Due Diligence (EDD)
│   ├── Trigger on thresholds (balance > $100k, rapid accumulation)
│   ├── Flag to bank for review before yield distribution
│   └── Log EDD status in account record
│
├── Audit Trail
│   ├── Immutable log of all compliance events
│   ├── 5-year retention (，符合 FINRA/FinCEN requirements)
│   └── Export capability for bank examiners
│
└── Compliance Reporting
    ├── Monthly compliance summary to bank
    ├── Quarterly risk dashboard
    └── Annual compliance certification
```

### 5.3 Customer Risk Tiers

| Tier       | Criteria                                  | FloatYield Action                                 |
| ---------- | ----------------------------------------- | ------------------------------------------------- |
| Standard   | Identity verified; no red flags           | Normal yield accrual and distribution             |
| Elevated   | Large balance, rapid growth, PEP-adjacent | Enhanced monitoring; bank notified                |
| Restricted | SAR filed, OFAC match, fraud confirmed    | Block yield credit; freeze account; bank notified |

---

## 6. Regulatory Reporting

### 6.1 IRS 1099-INT

| Question                  | Answer                                                        |
| ------------------------- | ------------------------------------------------------------- |
| Who files?                | **Sponsor Bank** (as the payer of record)                     |
| What triggers?            | Total interest paid ≥ $10 in calendar year                    |
| What FloatYield provides? | Annual yield summary per account (IRS 1099-INT data)          |
| Deadline                  | January 31 (1099-INT) for prior year; February 15 (if no TIN) |
| Copy sent to?             | Customer, IRS, state tax authority                            |

**FloatYield's obligation:** Provide accurate 1099-INT data to bank by January 10 each year.

### 6.2 State Unclaimed Property

| Question                    | Answer                                                                                                   |
| --------------------------- | -------------------------------------------------------------------------------------------------------- |
| What is unclaimed property? | Accounts with no activity for state-dormancy period (typically 1-5 years); balances turned over to state |
| Who is responsible?         | **Sponsor Bank** (escheatment obligation)                                                                |
| What FloatYield provides?   | Dormant account list; last-known address; balance at escheatment date                                    |
| Triggering events           | No customer-initiated activity (login, withdrawal, transfer) for dormancy period                         |

### 6.3 Other Regulatory Filings

| Filing                                  | Owner          | FloatYield Data Needed                   |
| --------------------------------------- | -------------- | ---------------------------------------- |
| FinCEN SAR (Suspicious Activity Report) | Bank           | Transaction records for flagged accounts |
| BSA/AML Compliance                      | Bank           | Annual AML program certification         |
| Call Report (bank regulators)           | Bank           | Yield account volumes, balances          |
| state money transmitter license         | **FloatYield** | Compliance with state MLT requirements   |
| Federal Reserve Master Account          | Bank           | Reserve account balances                 |

### 6.4 State Money Transmitter License

**Critical Path Item:** FloatYield may need money transmitter licenses (MTL) in states where it operates, depending on how its service is characterized. This must be resolved before launch.

---

## 7. MVP Scope

### 7.1 MVP Definition

**One bank partner, one product (interest-bearing checking), US only, manual reconciliation acceptable for pilot (6-month period).**

### 7.2 MVP Feature List (10 Features)

1. **Account Creation** — Bank creates interest-bearing account via API; FloatYield returns account ID and assigns yield rate tier

2. **Balance Tracking** — FloatYield tracks account balance in real-time (polled from bank's system or pushed via webhook); end-of-day snapshot for accrual

3. **Daily Yield Accrual** — FloatYield computes `balance × rate × 1/365` each business day; stores accrual in yield ledger

4. **Monthly Yield Distribution** — FloatYield instructs bank to transfer yield funds; bank executes transfer; FloatYield credits accounts

5. **Yield Balance Inquiry API** — `/v1/accounts/{id}/yield-balance` returns current accrued and paid yield

6. **Transaction History API** — `/v1/accounts/{id}/transactions` returns full transaction log including yield credits

7. **Rate Tier Management** — FloatYield maintains 3 tiers; rate changes published via API; grace period applied

8. **Bank Reconciliation Report** — Daily CSV/PDF report from FloatYield to bank: total liability, per-account breakdown, variance vs bank calculation

9. **1099-INT Data Export** — Annual file (by Jan 10) with per-account yield totals for bank's 1099-INT filing

10. **KYC Reference Storage** — FloatYield stores KYC reference ID per account; does not store KYC data; KYC status check at account activation

### 7.3 MVP Non-Scope (Phase 2+)

- Partial day accrual
- Daily yield distribution
- Multiple bank partners
- Multiple product types (savings, money market)
- EU/MiCA compliance
- Real-time reconciliation automation
- Mobile app
- White-label interface

---

## 8. Architecture Decisions (ADRs)

### ADR-001: Sponsor Bank Model

**Decision:** FloatYield operates as a **Yield Calculation and Distribution Platform** (not a bank). The Sponsor Bank holds deposits, manages reserves, and is the regulated entity. FloatYield is a B2B SaaS layer that calculates yield, distributes funds, and provides compliance reporting.

**Why:**

- FloatYield avoids bank charter requirements
- Bank retains regulatory relationship with Fed/OCC
- FloatYield focuses on its core competency (yield math + distribution)
- Clear legal liability: bank is the account provider

**Alternatives Considered:**

- **Model B: FloatYield as the account issuer** — REJECTED: Would require bank charter or partnership with a licensed bank; dramatically increases regulatory burden
- **Model C: FloatYield holds reserves directly** — REJECTED: Would require trust company license; not core to value proposition

---

### ADR-002: Reserve Custody

**Decision:** Sponsor Bank holds reserves at the Federal Reserve; Sponsor Bank (or its investment manager) purchases Treasuries through its existing custodian. FloatYield does not hold securities or interact with custodians directly.

**Why:**

- Leverages bank's existing custodian relationships
- No new counterparty risk introduced
- Bank controls investment decisions (duration, allocation) within regulatory constraints
- FloatYield monitors yield income and flags discrepancies without touching securities

**Alternatives Considered:**

- **FloatYield selects and interfaces with custodian directly** — REJECTED: Adds complexity; bank already has custodial infrastructure; introduces operational risk
- **Third-party reserve manager** — REJECTED: Bank must approve any entity managing Fed reserves; adds approval cycle

---

### ADR-003: Yield Calculation Frequency

**Decision:** FloatYield calculates yield **daily** but distributes **monthly** during MVP.

**Why:**

- Daily calculation allows precision and frequent rate changes
- Monthly distribution simplifies reconciliation for pilot
- Bank's Treasury income accrues daily; FloatYield tracks the liability daily but settles monthly
- Preserves ability to switch to daily distribution post-MVP with no architectural change

**Alternatives Considered:**

- **Monthly calculation only** — REJECTED: Too coarse; customers expect daily accrual tracking
- **Real-time (continuous) accrual** — REJECTED: Unnecessary complexity for MVP; micro-accruals add reconciliation overhead

---

### ADR-004: Compliance Ownership

**Decision:** **Sponsor Bank owns KYC/AML**. FloatYield is the compliance data provider and report generator. FloatYield does not perform KYC, file SARs, or conduct AML monitoring. FloatYield stores KYC reference IDs only.

**Why:**

- Regulatory obligation for account opening belongs to the bank (Bank Secrecy Act, FinCEN rules)
- FloatYield cannot practically perform KYC without becoming a data processor with regulated obligations
- Bank has existing KYC infrastructure; FloatYield integrates with it
- FloatYield minimizes its own regulatory surface

**Alternatives Considered:**

- **FloatYield performs independent KYC** — REJECTED: Would make FloatYield a data processor under BSA; adds regulatory obligations; conflicts with bank's KYC ownership
- **Shared KYC responsibility (joint liability)** — REJECTED: Creates ambiguity in regulatory accountability; increases legal cost

---

### ADR-005: API Design Approach

**Decision:** **REST API with synchronous responses** for queries; **webhook notifications** for asynchronous events. Not event-driven (Kafka/SQS) for MVP; REST polling acceptable for pilot volume.

**Why:**

- REST is well-understood by bank integration teams
- Webhooks handle low-latency events (yield credited, account created)
- Bank's internal systems are synchronous; REST fits their architecture
- Avoids infrastructure complexity of event streaming for pilot scale
- Supports OpenAPI spec generation for bank developer experience

**Alternatives Considered:**

- **Event-driven (Kafka/SQS)** — REJECTED: Over-engineered for MVP; bank systems not set up for event streaming; high operational overhead
- **GraphQL** — REJECTED: Bank integration teams less familiar; unnecessary flexibility at MVP stage
- **Webhook-only (no REST)** — REJECTED: Insufficient for balance inquiry and yield schedule queries which require request/response

---

## Appendix A: Glossary

| Term                      | Definition                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| Sponsor Bank              | The FDIC-insured bank that holds deposits and issues interest-bearing accounts                  |
| Custodian                 | Entity (e.g., BNY Mellon) that holds Treasuries on behalf of the bank                           |
| Fed Reserve Account       | Bank's master account at the Federal Reserve where deposits are held                            |
| Yield Accrual             | Daily calculation of interest earned (liability for bank)                                       |
| Yield Distribution        | Transfer of calculated yield from bank to customer account                                      |
| Basis Point (bp)          | 0.01% — used to measure yield rate differences                                                  |
| 1099-INT                  | IRS form reporting interest income paid to customers                                            |
| SAR                       | Suspicious Activity Report — filed with FinCEN for potentially fraudulent activity              |
| OFAC                      | Office of Foreign Assets Control — Treasury department that screens for sanctioned parties      |
| KYC                       | Know Your Customer — identity verification requirements                                         |
| AML                       | Anti-Money Laundering — regulations to prevent financial crimes                                 |
| Money Transmitter License | State license required to transmit money; may apply to FloatYield depending on characterization |

---

## Appendix B: Open Questions

| #   | Question                                                                     | Priority              | Owner             |
| --- | ---------------------------------------------------------------------------- | --------------------- | ----------------- |
| 1   | Does FloatYield need state money transmitter licenses?                       | Critical (pre-launch) | Legal             |
| 2   | How does bank handle Treasury yield vs customer yield rate differential?     | Critical (pricing)    | Bank + FloatYield |
| 3   | What is the maximum balance per account for FDIC coverage?                   | High                  | Bank              |
| 4   | How are account overdrafts handled?                                          | High                  | Bank              |
| 5   | What happens when a customer closes account mid-month — yield paid pro-rata? | Medium                | FloatYield        |
| 6   | Does FloatYield need to be SOC 2 certified before bank will integrate?       | High                  | FloatYield        |
| 7   | How does the yield transfer interact with the bank's internal ledger?        | High                  | Bank IT           |
| 8   | What is the minimum balance that earns yield?                                | Medium                | Product           |

---

_End of Product Requirements v1.0_
