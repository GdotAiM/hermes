/**
 * HERMES Desk — price formatting by instrument precision.
 * Index futures (NQ/ES/YM) and XAUUSD use 2 dp; EURUSD uses 5 dp.
 * Set once per load (setPriceDecimals) from series.meta.dp.
 */
let DP = 2;

export function setPriceDecimals(dp) {
  DP = Number.isInteger(dp) && dp >= 0 && dp <= 8 ? dp : 2;
}

export function priceDecimals() {
  return DP;
}

/** Guess precision for CSV tapes with no symbol metadata (FX-like < 10 → 5 dp). */
export function inferDecimals(price) {
  return Math.abs(Number(price)) < 10 ? 5 : 2;
}

export function fmtPx(v) {
  return v == null || Number.isNaN(Number(v)) ? '—' : Number(v).toFixed(DP);
}

export function roundToDp(v, dp = DP) {
  const f = 10 ** dp;
  return Math.round(v * f) / f;
}
