"""Running paper book for the scorer (post-H015b fix 4). EXPLORATORY research tool: no orders.

``ftn score`` historically gated every ticket against a FLAT book (``kernel_log.FLAT_BOOK``), so the 2% daily-loss
and 5% drawdown caps never bound. ``RunningBook`` replays the book in time order: each taken trade risks
``max_trade_risk_pct`` of current equity; P&L is realised at the trade's exit time; the risk gate sees the book as
of the ticket time (realised trades only — an open trade's risk is not pre-counted; at most one ticket per session).

* daily_loss_pct = realised loss today (NY date) as % of equity at the start of that day (0 if the day is up).
* drawdown_pct   = (high-water mark - equity) / high-water mark x 100.

Drawdown reset (``risk_caps.drawdown_reset`` in config.yaml) — a HUMAN DECISION, proposed default
``next_calendar_month``: once the 5% cap has blocked a ticket, the book stays halted for the rest of that calendar
month; at the first ticket in a later month the high-water mark is reset to current equity (stands in for the
month-end human review). ``none`` = never reset (the cap freezes the book for good once tripped).
"""

from __future__ import annotations

from datetime import datetime

RESETS = ("none", "next_calendar_month")


class RunningBook:
    def __init__(self, risk_pct: float = 0.5, start_equity: float = 100.0, reset: str = "next_calendar_month"):
        if reset not in RESETS:
            raise ValueError(f"drawdown reset {reset!r} not in {RESETS}")
        self.risk_pct, self.reset = float(risk_pct), reset
        self.equity = self.peak = float(start_equity)
        self.pending: list[tuple[datetime, float]] = []   # (exit_time, R) not yet realised
        self.day = None
        self.day_start_equity = self.equity
        self.day_pnl = 0.0
        self.trip_month = None
        self.events: list[dict] = []

    def _realise(self, t: datetime) -> None:
        self.pending.sort()
        while self.pending and self.pending[0][0] <= t:
            xt, r = self.pending.pop(0)
            self._roll_day(xt)
            pnl = r * self.risk_pct / 100.0 * self.equity
            self.equity += pnl
            self.day_pnl += pnl
            self.peak = max(self.peak, self.equity)

    def _roll_day(self, t: datetime) -> None:
        if self.day != t.date():
            self.day, self.day_start_equity, self.day_pnl = t.date(), self.equity, 0.0

    def state(self, t: datetime) -> dict:
        self._realise(t)
        self._roll_day(t)
        if self.reset == "next_calendar_month" and self.trip_month is not None and (t.year, t.month) != self.trip_month:
            self.events.append({"t": t.isoformat(), "event": "drawdown_reset", "peak_before": self.peak, "equity": self.equity})
            self.peak, self.trip_month = self.equity, None
        dd = 100.0 * (self.peak - self.equity) / self.peak if self.peak > 0 else 0.0
        dl = max(0.0, -100.0 * self.day_pnl / self.day_start_equity) if self.day_start_equity > 0 else 0.0
        return {"daily_loss_pct": dl, "drawdown_pct": dd, "equity_pct": self.equity, "source": "scorer_running_book",
                "reset": self.reset}

    def blocked(self, t: datetime, reason: str) -> None:
        if reason == "max_drawdown_cap" and self.trip_month is None:
            self.trip_month = (t.year, t.month)
            self.events.append({"t": t.isoformat(), "event": "drawdown_cap_tripped", "equity": self.equity, "peak": self.peak})

    def record(self, exit_time: datetime, r: float) -> None:
        self.pending.append((exit_time, float(r)))
