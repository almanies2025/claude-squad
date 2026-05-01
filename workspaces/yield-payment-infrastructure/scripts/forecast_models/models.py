"""
Three forecasting models for daily yield:
1. Naive Persistence   — "tomorrow = today"
2. Holt-Winters (Dbl Exp) — level + trend, no seasonality
3. Simple ARIMA(1,1,1)  — level + momentum + recent shock
"""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd


# ─── Model Interface ───────────────────────────────────────────────────────────

class YieldModel(ABC):
    name: str = ""

    @abstractmethod
    def fit(self, series: pd.Series) -> "YieldModel":
        """Fit on training portion of a walk-forward window."""

    @abstractmethod
    def predict(self, n: int) -> np.ndarray:
        """Return n-step-ahead forecasts."""

    @abstractmethod
    def reset(self):
        """Clear state for next walk-forward window."""


# ─── 1. Naive Persistence ─────────────────────────────────────────────────────

class NaiveYield(YieldModel):
    """
    tomorrow = today.
    The industry standard baseline. Any model that can't beat this isn't worth running.
    """
    name = "Naive (Persistence)"

    def __init__(self):
        self._last = None

    def fit(self, series: pd.Series) -> "NaiveYield":
        self._last = series.iloc[-1]
        return self

    def predict(self, n: int) -> np.ndarray:
        return np.full(n, self._last)

    def reset(self):
        self._last = None


# ─── 2. Holt's Double Exponential Smoothing ───────────────────────────────────

class HoltYield(YieldModel):
    """
    Maintains a level (smoothed value) and a trend (slope).
    Alpha = level smoothing, Beta = trend smoothing.
    No seasonality — appropriate for daily yield which has no meaningful weekly cycle.
    """
    name = "Holt (Double Exp Smoothing)"

    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta

    def fit(self, series: pd.Series) -> "HoltYield":
        values = series.values.astype(float)
        n = len(values)

        # Init level and trend
        level = values[0]
        trend = (values[min(4, n-1)] - values[0]) / min(4, n-1) if n > 1 else 0.0

        for t in range(1, n):
            prev_level = level
            level = self.alpha * values[t] + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - prev_level) + (1 - self.beta) * trend

        self._level = level
        self._trend = trend
        return self

    def predict(self, n: int) -> np.ndarray:
        return np.array([self._level + (i + 1) * self._trend for i in range(n)])

    def reset(self):
        self._level = None
        self._trend = None


# ─── 3. ARIMA(1,1,1) ──────────────────────────────────────────────────────────

class ARIMAYield(YieldModel):
    """
    ARIMA(1,1,1): autoregressive order 1, differencing order 1, moving average order 1.
    - AR(1): pulls toward recent value (momentum)
    - I(1): first-difference stationarizes the random-walk-like yield
    - MA(1): absorbs the most recent shock

    Fitted via OLS on the AR(1) representation of the differenced series.
    """
    name = "ARIMA(1,1,1)"

    def fit(self, series: pd.Series) -> "ARIMAYield":
        y = series.values.astype(float)
        n = len(y)

        # First difference
        dy = np.diff(y)

        # AR(1) on differenced series: dy[t] = phi * dy[t-1] + e[t] + theta * e[t-1]
        # Approximate with OLS on AR(1) component only (simplified fit)
        dy_lag = dy[:-1]
        dy_curr = dy[1:]

        if len(dy_lag) < 5:
            # Not enough data — fall back to naive
            self._last = y[-1]
            self._phi = 0.0
        else:
            # OLS: dy_curr ≈ phi * dy_lag
            phi = np.corrcoef(dy_lag, dy_curr)[0, 1] if np.std(dy_lag) > 0 and np.std(dy_curr) > 0 else 0.0
            phi = float(np.clip(phi, -0.9, 0.9))
            self._phi = phi
            # Residual variance for MA component
            residuals = dy_curr - phi * dy_lag
            self._theta = float(np.clip(np.mean(residuals) / (np.std(residuals) + 1e-9), -0.9, 0.9))
            self._last = y[-1]
            self._dy_last = dy[-1]

        return self

    def predict(self, n: int) -> np.ndarray:
        if hasattr(self, "_last") and self._phi == 0.0:
            return np.full(n, self._last)

        forecasts = []
        cur = self._last
        dy_prev = getattr(self, "_dy_last", 0.0)
        for _ in range(n):
            dy_hat = self._phi * dy_prev
            next_val = cur + dy_hat
            forecasts.append(next_val)
            cur = next_val
            dy_prev = dy_hat
        return np.array(forecasts)

    def reset(self):
        self._last = None
        self._phi = None
        self._theta = None
        self._dy_last = None
