"""
QuickBooks GL account mapper — translates QBO account objects to canonical account keys
and computes canonical metric values from a list of mapped QBO accounts with balances.

The mapping rules below are documented placeholders for the real QBO→canonical mapping.
They will be replaced with actual classification logic once the QBO sandbox
connection is available for empirical validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class QBOMapperError(Exception):
    """Raised when QBO account mapping fails."""

    pass


# Canonical account keys supported by this mapper.
CANONICAL_ACCOUNT_KEYS: list[str] = [
    "revenue_net",
    "other_income",
    "cogs_total",
    "opex_total",
    "depreciation",
    "amortization",
    "da_other",
    "ebitda",
    "ebitda_margin_pct",
    "gross_profit",
    "gross_margin_pct",
    "dso",
    "dio",
    "dpo",
    "working_capital",
    "cash_balance",
    "net_debt",
    "operating_cash_flow",
]


@dataclass
class MappedAccount:
    """A QBO account that has been resolved to a canonical key."""

    canonical_key: str
    balance: float
    qbo_name: str
    qbo_account_type: str
    qbo_sub_type: Optional[str] = None


class QBOAccountMapper:
    """
    Maps QuickBooks GL account objects to the portfolio monitor's canonical account keys.

    QBO account object shape::
        {
            "name": "Sales",
            "account_type": "Income",        # AccountType enum as string
            "sub_type": "SalesOfProductIncome",
            "balance": 125000.00,
            ...
        }

    Canonical keys produced:
        revenue_net, other_income, cogs_total, opex_total,
        depreciation, amortization, da_other,
        ebitda, ebitda_margin_pct,
        gross_profit, gross_margin_pct,
        dso, dio, dpo, working_capital,
        cash_balance, net_debt, operating_cash_flow
    """

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def map_account(self, qbo_account: dict) -> Optional[str]:
        """
        Map a single QBO account object to a canonical account key.

        Args:
            qbo_account: QBO account dict with at least ``name``, ``account_type``,
                         and optionally ``sub_type`` keys.

        Returns:
            Canonical account key string, or ``None`` if the account has no
            canonical mapping (e.g. equity accounts are skipped).
        """
        account_type = (qbo_account.get("account_type") or "").strip()
        name = (qbo_account.get("name") or "").strip()

        # Income accounts
        if account_type == "Income":
            return self._classify_revenue(qbo_account)

        # Expense accounts
        if account_type == "Expense":
            cogs = self._classify_cogs(qbo_account)
            if cogs:
                return cogs
            return self._classify_opex(qbo_account)

        # Asset accounts
        if account_type == "Asset":
            return self._classify_balance_sheet(qbo_account)

        # Liability accounts
        if account_type == "Liability":
            return self._classify_balance_sheet(qbo_account)

        # Equity — skip
        if account_type == "Equity":
            return None

        # Other QBO types (e.g. Non-Posting) — skip
        return None

    def get_canonical_accounts(self) -> list[str]:
        """Return all supported canonical account keys."""
        return list(CANONICAL_ACCOUNT_KEYS)

    # -------------------------------------------------------------------------
    # Revenue classification
    # -------------------------------------------------------------------------

    def _classify_revenue(self, qbo_account: dict) -> Optional[str]:
        """
        Map a QBO Income account to ``revenue_net`` or ``other_income``.

        Mock rules (placeholder for real mapping):
            - If name contains "Sales", "Revenue", "Income" → revenue_net
            - Otherwise → other_income
        """
        name = (qbo_account.get("name") or "").lower()
        sub_type = (qbo_account.get("sub_type") or "").lower()

        # Primary operating revenue
        revenue_keywords = ("sales", "revenue", "income from operations", "operating income")
        if any(kw in name for kw in revenue_keywords):
            return "revenue_net"

        # Sales-of-product-income sub-type always maps to revenue_net
        if "salesofproductincome" in sub_type:
            return "revenue_net"

        # Default non-operating / other income
        return "other_income"

    # -------------------------------------------------------------------------
    # COGS classification
    # -------------------------------------------------------------------------

    def _classify_cogs(self, qbo_account: dict) -> Optional[str]:
        """
        Map a QBO Expense account to ``cogs_total`` if it represents cost of goods sold.

        Mock rules (placeholder for real mapping):
            - If name or sub_type contains "COGS", "Cost of Goods", "Cost of Sales"
              → cogs_total
            - Otherwise → None (caller falls through to opex classification)
        """
        name = (qbo_account.get("name") or "").lower()
        sub_type = (qbo_account.get("sub_type") or "").lower()

        cogs_keywords = ("cogs", "cost of goods", "cost of sales", "cost revenue")
        if any(kw in name for kw in cogs_keywords) or any(kw in sub_type for kw in cogs_keywords):
            return "cogs_total"

        return None

    # -------------------------------------------------------------------------
    # EBITDA / D&A classification
    # -------------------------------------------------------------------------

    def _classify_ebitda(self, qbo_account: dict) -> Optional[str]:
        """
        Map a QBO account to a D&A canonical key (``depreciation``, ``amortization``, ``da_other``).

        Mock rules (placeholder for real mapping):
            - If name contains "Depreciation" → depreciation
            - If name contains "Amortization" → amortization
            - If name contains "Depletion" or "D&A" → da_other
        """
        name = (qbo_account.get("name") or "").lower()

        if "depreciation" in name:
            return "depreciation"
        if "amortization" in name:
            return "amortization"
        if "depletion" in name or "d&a" in name:
            return "da_other"

        return None

    # -------------------------------------------------------------------------
    # OPEX classification
    # -------------------------------------------------------------------------

    def _classify_opex(self, qbo_account: dict) -> Optional[str]:
        """
        Map a QBO Expense account (non-COGS) to ``opex_total``.

        All non-COGS expenses default to opex_total, which the KPI engine
        will distribute across opex_sga_rent / opex_sga_salaries / opex_sga_other.
        """
        return "opex_total"

    # -------------------------------------------------------------------------
    # Balance sheet classification
    # -------------------------------------------------------------------------

    def _classify_balance_sheet(self, qbo_account: dict) -> Optional[str]:
        """
        Map QBO Asset and Liability accounts to balance-sheet canonical keys.

        Mock rules (placeholder for real mapping):

        Asset accounts:
            - "Bank", "Cash" in name → cash_balance
            - "Accounts Receivable", "AR", "Receivable" → dso (AR)
            - "Inventory", "Inventory" → dio (inventory)
            - "Prepaid" → skip (not a working-capital component)

        Liability accounts:
            - "Credit Card", "Loan", "Note Payable", "Debt" → net_debt
            - "Accounts Payable", "AP", "Payable" → dpo (AP)
        """
        account_type = (qbo_account.get("account_type") or "").strip()
        name = (qbo_account.get("name") or "").lower()

        if account_type == "Asset":
            return self._classify_asset(qbo_account)
        if account_type == "Liability":
            return self._classify_liability(qbo_account)

        return None

    def _classify_asset(self, qbo_account: dict) -> Optional[str]:
        name = (qbo_account.get("name") or "").lower()
        sub_type = (qbo_account.get("sub_type") or "").lower()

        # Cash and cash equivalents
        if any(kw in name for kw in ("bank", "cash", "money market", "petty cash")):
            return "cash_balance"

        # Accounts receivable → DSO
        if (
            any(kw in name for kw in ("receivable", "accounts receivable", "ar "))
            or "accountsreceivable" in sub_type
        ):
            return "dso"

        # Inventory → DIO
        if (
            any(kw in name for kw in ("inventory", "inventories", "stock"))
            or "inventory" in sub_type
        ):
            return "dio"

        # Other asset types not currently mapped
        return None

    def _classify_liability(self, qbo_account: dict) -> Optional[str]:
        name = (qbo_account.get("name") or "").lower()
        sub_type = (qbo_account.get("sub_type") or "").lower()

        # Debt instruments → net_debt
        debt_keywords = ("credit card", "loan", "note payable", "mortgage", "debt", "borrow")
        if any(kw in name for kw in debt_keywords) or any(kw in sub_type for kw in debt_keywords):
            return "net_debt"

        # Accounts payable → DPO
        if (
            any(kw in name for kw in ("payable", "accounts payable", "ap "))
            or "accountspayable" in sub_type
        ):
            return "dpo"

        # Other liability types not currently mapped
        return None

    # -------------------------------------------------------------------------
    # Metric computation
    # -------------------------------------------------------------------------

    def _compute_metric_from_accounts(
        self, accounts: list[dict], metric_key: str
    ) -> Optional[float]:
        """
        Compute the value of a canonical metric from a list of mapped QBO accounts.

        Args:
            accounts: List of QBO account dicts, each with ``balance`` and the
                      fields required by ``map_account``.
            metric_key: One of the supported canonical metric keys.

        Returns:
            Computed metric value as a float, or ``None`` if the metric cannot
            be computed from the supplied accounts.

        Computation rules:
            - ``revenue_net``: sum of all accounts mapped to ``revenue_net``
            - ``other_income``: sum of all accounts mapped to ``other_income``
            - ``cogs_total``: sum of all accounts mapped to ``cogs_total``
            - ``opex_total``: sum of all accounts mapped to ``opex_total``
            - ``depreciation``, ``amortization``, ``da_other``: direct sum
            - ``gross_profit``: revenue_net - cogs_total
            - ``gross_margin_pct``: gross_profit / revenue_net * 100
            - ``ebitda``: gross_profit - opex_total + depreciation + amortization + da_other
            - ``ebitda_margin_pct``: ebitda / revenue_net * 100
            - ``dso``: (sum of dso balances) / revenue_net * 30
            - ``dio``: (sum of dio balances) / cogs_total * 30
            - ``dpo``: (sum of dpo balances) / cogs_total * 30
            - ``working_capital``: dso + dio - dpo
            - ``cash_balance``: direct sum of cash_balance accounts
            - ``net_debt``: net_debt - cash_balance  (net of cash)
            - ``operating_cash_flow``: not computed from accounts alone (requires cash flow statement)
        """
        if not accounts:
            return None

        # First pass — aggregate balances by canonical key
        canonical_balances: dict[str, float] = {}
        for acc in accounts:
            key = self.map_account(acc)
            if key is None:
                continue
            balance = acc.get("balance", 0.0) or 0.0
            canonical_balances[key] = canonical_balances.get(key, 0.0) + balance

        # Resolve the requested metric
        revenue_net = canonical_balances.get("revenue_net", 0.0)
        other_income = canonical_balances.get("other_income", 0.0)
        cogs_total = canonical_balances.get("cogs_total", 0.0)
        opex_total = canonical_balances.get("opex_total", 0.0)
        depreciation = canonical_balances.get("depreciation", 0.0)
        amortization = canonical_balances.get("amortization", 0.0)
        da_other = canonical_balances.get("da_other", 0.0)
        cash_balance = canonical_balances.get("cash_balance", 0.0)
        dso_balance = canonical_balances.get("dso", 0.0)
        dio_balance = canonical_balances.get("dio", 0.0)
        dpo_balance = canonical_balances.get("dpo", 0.0)
        net_debt_balance = canonical_balances.get("net_debt", 0.0)

        # Composite metrics
        if metric_key == "revenue_net":
            return revenue_net + other_income  # revenue_net includes other_income
        if metric_key == "other_income":
            return other_income
        if metric_key == "cogs_total":
            return cogs_total
        if metric_key == "opex_total":
            return opex_total
        if metric_key == "depreciation":
            return depreciation
        if metric_key == "amortization":
            return amortization
        if metric_key == "da_other":
            return da_other

        if metric_key == "gross_profit":
            return revenue_net - cogs_total

        if metric_key == "gross_margin_pct":
            if revenue_net == 0:
                return None
            gross_profit = revenue_net - cogs_total
            return (gross_profit / revenue_net) * 100

        if metric_key == "ebitda":
            gross_profit = revenue_net - cogs_total
            return gross_profit - opex_total + depreciation + amortization + da_other

        if metric_key == "ebitda_margin_pct":
            if revenue_net == 0:
                return None
            gross_profit = revenue_net - cogs_total
            ebitda = gross_profit - opex_total + depreciation + amortization + da_other
            return (ebitda / revenue_net) * 100

        if metric_key == "dso":
            if revenue_net == 0:
                return None
            return (dso_balance / revenue_net) * 30

        if metric_key == "dio":
            if cogs_total == 0:
                return None
            return (dio_balance / cogs_total) * 30

        if metric_key == "dpo":
            if cogs_total == 0:
                return None
            return (dpo_balance / cogs_total) * 30

        if metric_key == "working_capital":
            return dso_balance + dio_balance - dpo_balance

        if metric_key == "cash_balance":
            return cash_balance

        if metric_key == "net_debt":
            # net_debt = debt liabilities - cash (higher net_debt = more debt)
            return net_debt_balance - cash_balance

        if metric_key == "operating_cash_flow":
            # Cannot be derived from GL accounts alone; requires cash flow statement
            return None

        return None
