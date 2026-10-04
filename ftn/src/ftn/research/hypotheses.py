"""Typed ``Hypothesis`` records emitted by the FTN month layers.

Each record is a *claim to be tested*, never a result. The claim's lecture lineage is
``ict_source``. How the conditioning variable is computed from 1m bars is always
``hermes_interpretation`` (ICT never defined these as bar formulas). Scored on Month 9
kernel tickets only (the sole ticket authority).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

CONTEXT_MONTHS = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M10", "M11", "M12", "M13")


@dataclass(frozen=True)
class Hypothesis:
    id: str
    source_month: str            # M1..M8, M10..M12, M13 (Charter Model 13 bridge)
    source_slice: str            # doc that carries the lecture lineage
    lecture: str                 # official lecture title(s)
    claim: str                   # plain-language claim (never a result)
    metric: str                  # "mean_R" | "win_rate"
    conditioning_variable: str   # feature name in ftn.research.features
    expected_direction: str      # "higher_when_true" | "lower_when_true"
    claim_provenance: str        # ict_source | user_lecture_notes
    operationalisation: str      # bar formula (always hermes_interpretation)
    operationalisation_provenance: str = "hermes_interpretation"
    scope: str = "Month 9 kernel tickets (REV unless interpretation triggers on)"
    status: str = "EXPLORATORY — not registered; pending CASSANDRA + DATA"

    def to_dict(self) -> dict:
        return asdict(self)


def _h(n, month, slice_, lecture, claim, metric, var, op, prov="ict_source", d="higher_when_true"):
    return Hypothesis(f"FTN-H{n:03d}", month, slice_, lecture, claim, metric, var, d, prov, op)


HYPOTHESES: tuple[Hypothesis, ...] = (
    _h(1, "M1", "docs/MONTH1_ESSENCE.md (lessons 4–5)", "Equilibrium Vs. Discount / Equilibrium Vs. Premium",
       "Kernel buys taken in discount (sells in premium) of the previous-day range earn more R than those taken on the wrong side of equilibrium.",
       "mean_R", "m1_correct_side_of_eq",
       "buy: entry < (PDH+PDL)/2; sell: entry > (PDH+PDL)/2"),
    _h(2, "M2", "docs/MONTH2_ESSENCE.md (lesson 8)", "Market Maker Trap False Breakouts",
       "When the raided named extreme is a false breakout (the raid bar closes back inside the previous-day range), kernel tickets earn more R.",
       "mean_R", "m2_false_breakout",
       "15m raid bar close back inside [PDL, PDH] (above PDL for a low raid, below PDH for a high raid)"),
    _h(3, "M3", "docs/MONTH3_ESSENCE.md (lessons 2–3)", "Institutional Order Flow / Institutional Sponsorship",
       "Kernel tickets with fully aligned daytrade IOF (daily = 4h = 60m) earn more R than qualified ones.",
       "mean_R", "m3_iof_aligned",
       "InstitutionalContext.confidence == 'aligned' (candle-colour IOF, see D16)"),
    _h(4, "M4", "docs/MONTH4_ESSENCE.md (lesson 12)", "ICT Fair Value Gaps FVG",
       "Kernel tickets whose post-raid displacement leaves a 15m FVG in the trade direction earn more R.",
       "mean_R", "m4_fvg_in_displacement",
       "3-bar 15m gap (buy: low[i] > high[i-2]; sell: high[i] < low[i-2]) between the raid bar and entry"),
    _h(5, "M5", "docs/MONTH5_ESSENCE.md (lessons 1, 3)", "Quarterly Shifts & IPDA Data Ranges / Using IPDA Data Ranges",
       "Kernel buys in the lower half (sells in the upper half) of the 20-session IPDA range earn more R.",
       "mean_R", "m5_ipda20_discount",
       "buy: entry < mid(20-session high/low); sell: entry > mid"),
    _h(6, "M6", "docs/MONTH6_ESSENCE.md (lessons 1–2)", "Ideal Swing Conditions / Elements To Successful Swing Trading",
       "Kernel tickets in the direction of the 20-session swing (HTF sponsorship) earn more R.",
       "mean_R", "m6_with_20d_swing",
       "side agrees with sign(close[D-1] - close[D-21]) on session closes"),
    _h(7, "M7", "docs/MONTH7_ESSENCE.md (lessons 1–2, OSOK)", "Monthly & Weekly Ranges / Weekly Range Profiles",
       "An OSOK-style weekly profile (Mon–Wed raid of the week-so-far or previous-day extreme on the side opposite the trade) raises the REV win rate.",
       "win_rate", "m7_osok_profile",
       "weekday in Mon–Wed AND raided level on the opposite side to the trade (low raid for buys, high raid for sells)"),
    _h(8, "M8", "docs/MONTH8_ESSENCE.md (CBDR <40 ideal)", "ICT Day Trading Model — CBDR",
       "A tight CBDR (below its trailing 20-session median) precedes better kernel tickets.",
       "mean_R", "m8_cbdr_tight",
       "CBDR (14:00–20:00 NY prior evening) range < median of the previous 20 CBDRs (relative scaling of ICT's <40-pip FX rule)"),
    _h(9, "M8", "docs/MONTH9_BLUEPRINT.md §6 / MONTH8_ESSENCE.md (London gate)", "ICT Day Trading Model — London → NY",
       "NY AM kernel tickets that continue London's direction earn more R ('NY continues London by default').",
       "mean_R", "m8_ny_continues_london",
       "NY AM tickets only: sign(London 02:00–05:00 close - open) matches the side"),
    _h(10, "M10", "docs/MONTH10_ESSENCE.md (lessons 10–14, 19)", "Index Futures series / Importance Of Multi-Asset Analysis",
       "When the correlated index (US500) moves with the trade from the raid bar to entry, US100 kernel tickets earn more R.",
       "mean_R", "m10_us500_confirms",
       "sign(US500 close at entry - US500 close at the US100 raid bar) matches the side"),
    _h(11, "M11", "docs/MONTH11_ESSENCE.md (SMT / relative-strength note)", "Forex & Currency / Stock Mega-Trades — SMT note",
       "SMT divergence at the raid (US100 takes the named extreme, US500 does not take its own) raises kernel ticket R.",
       "mean_R", "m11_smt_divergence",
       "US500 low since 00:00 > its PDL for a US100 low raid (high < its PDH for a high raid), at entry time"),
    _h(12, "M12", "docs/MONTH12_ESSENCE.md (lessons 1–4)", "Long / Intermediate / Short / Intraday Top Down Analysis",
       "Kernel tickets where weekly, daily and 4h candle direction all agree with the side earn more R.",
       "mean_R", "m12_topdown_agree",
       "sign(prev week close-open) = sign(prev session close-open) = last completed 4h block = side"),
    _h(13, "M13", "docs/MONTH13_RESEARCH_CARD.md (user lecture notes kNlySn81dmo)", "Charter Price Action Model 13 (2022 model bridge)",
       "Kernel tickets inside the index window (08:30–11:00 ET) with a displacement FVG on the correct side of EQ earn more R.",
       "mean_R", "m13_bridge_window_fvg",
       "entry time 08:30–11:00 NY AND m4_fvg_in_displacement AND FVG midpoint ≤ dealing-range EQ (buy) / ≥ EQ (sell)",
       prov="user_lecture_notes"),
)


def by_month(month: str) -> tuple[Hypothesis, ...]:
    return tuple(h for h in HYPOTHESES if h.source_month == month)
