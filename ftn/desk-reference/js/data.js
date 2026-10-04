/** Synthetic FX path around the sample fixture. */
export function synthBars(last = 1.0872, n = 96) {
  const bars = [];
  let p = last + 0.004;
  const t0 = Date.now() - n * 3600_000;
  for (let i = 0; i < n; i++) {
    const drift = -0.00004;
    const noise = (Math.sin(i / 7) + Math.cos(i / 3)) * 0.00035;
    const o = p;
    const c = o + drift + noise;
    const h = Math.max(o, c) + 0.00025;
    const l = Math.min(o, c) - 0.00022;
    bars.push({ t: t0 + i * 3600_000, o, h, l, c });
    p = c;
  }
  bars[bars.length - 1].c = last;
  return bars;
}

export const FIXTURE = {
  symbol: "EURUSD",
  last: 1.0872,
  htf_bias: "bearish",
  previous_day: { high: 1.0931, low: 1.0842, close: 1.0884 },
  cbdr: { high: 1.0904, low: 1.0871 },
  asian: { high: 1.0892, low: 1.0864 },
  flout: { high: 1.0918, low: 1.0859 },
  pd_arrays: [
    { id: "D_FVG_bear", kind: "FVG", low: 1.0858, high: 1.0866 },
    { id: "H4_OB_bear", kind: "OB", low: 1.0898, high: 1.0909 },
  ],
  setup: {
    killzone: "ny_am",
    liquidity_raid: true,
    displacement: true,
    mss: true,
    pd_retrace: true,
  },
};
