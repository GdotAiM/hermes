/**
 * HERMES Desk — synthetic OHLC (session-aware)
 * Times are America/New_York (ET). Sessions: Asia, London, NY.
 */

/** Symbol metadata — price level, seed, and volatility multiplier per symbol. */
const SYMBOLS = {
  NQ: { id: 'NQ1!', name: 'Nasdaq 100 Continuous', basePrice: 19850, volMult: 1.0, dp: 2, seed: 0x4e51000 },
  ES: { id: 'ES1!', name: 'S&P 500 E-mini Continuous', basePrice: 5620,  volMult: 1.0, dp: 2, seed: 0x7a2c300 },
  YM: { id: 'YM1!', name: 'Dow Futures Continuous',     basePrice: 42100, volMult: 1.0, dp: 2, seed: 0x1f8e500 },
  // FX / metal for FTN DayContext projection (FTN is forex-first). SYNTHETIC random
  // walks like the others — the scale (≈1.117 EURUSD, ≈1240 XAUUSD, i.e. the era of
  // FTN's 2017–18 fixtures) is only so FTN handoff levels land on-screen. volMult
  // rescales the index-point session volatility (15m base 8 pts → ≈8 pips EURUSD,
  // ≈2 USD XAUUSD).
  EURUSD: { id: 'EURUSD', name: 'Euro / US Dollar — SYNTHETIC', basePrice: 1.1170, volMult: 0.0001, dp: 5, seed: 0x3e0d500, synthetic: true },
  XAUUSD: { id: 'XAUUSD', name: 'Gold spot — SYNTHETIC',        basePrice: 1240,   volMult: 0.25,   dp: 2, seed: 0x5a0c700, synthetic: true },
};

const SESSION = {
  ASIA: { start: 18, end: 0, name: 'Asia' },      // 18:00–00:00 ET (prev evening)
  LONDON: { start: 2, end: 5, name: 'London' },  // 02:00–05:00 ET killzone-ish
  NY: { start: 9, end: 12, name: 'NY' },          // 09:30 approximated as 9–12
};

/** ET hour from Date (using fixed offset approximation: UTC-4 for prototype) */
function etParts(ms) {
  // Prototype uses ET = UTC-4 (EDT). Good enough for UI research.
  const d = new Date(ms - 4 * 3600 * 1000);
  return {
    y: d.getUTCFullYear(),
    m: d.getUTCMonth(),
    day: d.getUTCDate(),
    h: d.getUTCHours(),
    min: d.getUTCMinutes(),
    dow: d.getUTCDay(), // 0 Sun
  };
}

function isWeekday(ms) {
  const { dow } = etParts(ms);
  return dow >= 1 && dow <= 5;
}

function sessionForHour(h) {
  if (h >= 18 || h < 0) return 'Asia'; // 18–24
  if (h >= 18) return 'Asia';
  if (h >= 2 && h < 8) return 'London';
  if (h >= 8 && h < 17) return 'NY';
  return 'Asia'; // overnight / early
}

function classifySession(ms) {
  const { h } = etParts(ms);
  if (h >= 18 || h < 2) return 'Asia';
  if (h >= 2 && h < 8) return 'London';
  if (h >= 8 && h < 17) return 'NY';
  return 'Asia';
}

/** Mulberry32 PRNG for reproducible series */
function mulberry32(seed) {
  let t = seed >>> 0;
  return function () {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Generate synthetic bars for a given symbol + timeframe.
 * @param {string} [symbol] - 'NQ' | 'ES' | 'YM'
 * @param {number} tfMinutes - 1, 5, 15, 60, 240, 1440
 * @param {number} [count] - number of bars
 * @returns {{ bars: Array, meta: object }}
 */
export function generateSeries(symbol = 'NQ', tfMinutes = 15, count = null) {
  const defaults = { 1: 780, 5: 600, 15: 480, 60: 320, 240: 180, 1440: 120 };
  const n = count ?? defaults[tfMinutes] ?? 400;
  const step = tfMinutes * 60 * 1000;
  const sym = SYMBOLS[symbol] || SYMBOLS.NQ;
  const dp = sym.dp ?? 2;
  const vm = sym.volMult ?? 1;
  const roundPx = (x) => roundDp(x, dp);
  const rand = mulberry32(sym.seed + tfMinutes);

  // End near "now" rounded to TF, weekday
  let end = Date.now();
  end = end - (end % step);

  const bars = [];
  let price = sym.basePrice + rand() * sym.basePrice * 0.005;
  let i = 0;
  let t = end;

  // Walk backward collecting weekday bars, then reverse
  const raw = [];
  while (raw.length < n) {
    if (isWeekday(t)) {
      raw.push(t);
    }
    t -= step;
  }
  raw.reverse();

  // Volatility by session
  function volFor(ms) {
    const s = classifySession(ms);
    const base = tfMinutes <= 5 ? 4.5 : tfMinutes <= 15 ? 8 : tfMinutes <= 60 ? 18 : tfMinutes <= 240 ? 35 : 90;
    if (s === 'NY') return base * 1.35 * vm;
    if (s === 'London') return base * 1.1 * vm;
    return base * 0.75 * vm;
  }

  let dayOpen = null;
  let dayHigh = -Infinity;
  let dayLow = Infinity;
  let prevDayHigh = null;
  let prevDayLow = null;
  let lastDayKey = '';
  const dayBoundaries = []; // { dayKey, openMs, high, low, close }

  for (let idx = 0; idx < raw.length; idx++) {
    const time = raw[idx];
    const p = etParts(time);
    const dayKey = `${p.y}-${p.m}-${p.day}`;

    if (dayKey !== lastDayKey) {
      if (lastDayKey && dayHigh !== -Infinity) {
        prevDayHigh = dayHigh;
        prevDayLow = dayLow;
        dayBoundaries.push({
          dayKey: lastDayKey,
          high: dayHigh,
          low: dayLow,
        });
      }
      lastDayKey = dayKey;
      dayOpen = price;
      dayHigh = price;
      dayLow = price;
    }

    const vol = volFor(time);
    const drift = (rand() - 0.48) * vol * 0.15;
    // Mild mean-reversion toward rolling mid
    const open = price;
    let close = open + drift + (rand() - 0.5) * vol;
    // Occasional impulse in NY
    if (classifySession(time) === 'NY' && rand() < 0.04) {
      close += (rand() < 0.5 ? -1 : 1) * vol * (1.5 + rand());
    }
    const wickUp = rand() * vol * 0.55;
    const wickDn = rand() * vol * 0.55;
    const high = Math.max(open, close) + wickUp;
    const low = Math.min(open, close) - wickDn;

    dayHigh = Math.max(dayHigh, high);
    dayLow = Math.min(dayLow, low);
    price = close;

    raw[idx] = null; // help GC of times array refs if needed

    bars.push({
      time,
      open: roundPx(open),
      high: roundPx(high),
      low: roundPx(low),
      close: roundPx(close),
      session: classifySession(time),
      dayKey,
      pdh: prevDayHigh != null ? roundPx(prevDayHigh) : null,
      pdl: prevDayLow != null ? roundPx(prevDayLow) : null,
    });
  }

  // Opening range: first N bars of NY session for last complete-ish day
  const orBars = 4; // e.g. first hour on 15m = 4 bars
  const openingRanges = computeOpeningRanges(bars, orBars);

  // Fair value gaps (3-candle)
  const fvgs = detectFVGs(bars, dp);

  const last = bars[bars.length - 1];
  const firstOfDay = bars.find((b) => b.dayKey === last.dayKey);
  const dayChg = firstOfDay ? last.close - firstOfDay.open : 0;

  return {
    bars,
    tfMinutes,
    meta: {
      symbol: sym.id,
      last: last.close,
      chg: roundPx(dayChg),
      chgPct: firstOfDay ? roundDp((dayChg / firstOfDay.open) * 100, 2) : 0,
      session: last.session,
      pdh: last.pdh,
      pdl: last.pdl,
      openingRanges,
      fvgs,
      dp,
      synthetic: true,
    },
  };
}

function roundDp(x, dp = 2) {
  const f = 10 ** dp;
  return Math.round(x * f) / f;
}

function computeOpeningRanges(bars, nBars) {
  const byDay = new Map();
  for (const b of bars) {
    if (b.session !== 'NY') continue;
    if (!byDay.has(b.dayKey)) byDay.set(b.dayKey, []);
    const arr = byDay.get(b.dayKey);
    if (arr.length < nBars) arr.push(b);
  }
  const ranges = [];
  for (const [dayKey, arr] of byDay) {
    if (arr.length === 0) continue;
    ranges.push({
      dayKey,
      startTime: arr[0].time,
      endTime: arr[arr.length - 1].time,
      high: Math.max(...arr.map((x) => x.high)),
      low: Math.min(...arr.map((x) => x.low)),
    });
  }
  return ranges;
}

/** 3-candle FVG: gap between candle[i-2].high and candle[i].low (bull) or reverse */
function detectFVGs(bars, dp = 2) {
  const roundPx = (x) => roundDp(x, dp);
  const out = [];
  for (let i = 2; i < bars.length; i++) {
    const a = bars[i - 2];
    const c = bars[i];
    // Bullish FVG: low of C > high of A
    if (c.low > a.high) {
      const top = c.low;
      const bot = a.high;
      const mid = (top + bot) / 2;
      out.push({
        type: 'bull',
        startIdx: i - 2,
        endIdx: i,
        startTime: a.time,
        endTime: c.time,
        top: roundPx(top),
        bot: roundPx(bot),
        mid: roundPx(mid),
        mitigated: false,
      });
    }
    // Bearish FVG
    if (c.high < a.low) {
      const top = a.low;
      const bot = c.high;
      const mid = (top + bot) / 2;
      out.push({
        type: 'bear',
        startIdx: i - 2,
        endIdx: i,
        startTime: a.time,
        endTime: c.time,
        top: roundPx(top),
        bot: roundPx(bot),
        mid: roundPx(mid),
        mitigated: false,
      });
    }
  }
  // Mark mitigation lightly + keep recent ones for display
  for (const f of out) {
    for (let j = f.endIdx + 1; j < bars.length; j++) {
      const b = bars[j];
      if (f.type === 'bull' && b.low <= f.bot) {
        f.mitigated = true;
        f.mitigateIdx = j;
        break;
      }
      if (f.type === 'bear' && b.high >= f.top) {
        f.mitigated = true;
        f.mitigateIdx = j;
        break;
      }
    }
  }
  // Prefer unmitigated + recent
  return out.filter((f) => !f.mitigated || f.endIdx > bars.length - 80).slice(-24);
}

/**
 * Slice I — aggregate a series to a higher timeframe so the 2-up companion
 * chart shows the *same* price path (not an independently generated one).
 * Buckets are ET-aligned (D = ET calendar day). Session = first constituent
 * bar's session; PDH/PDL = last constituent bar's values. FVGs are recomputed
 * on the aggregated bars; opening ranges are reused from the source for
 * TF ≤ 1H (time-based) and omitted above that.
 * @param {{ bars: Array, meta: object, tfMinutes?: number }} src
 * @param {number} tfMinutes target timeframe (must be > source TF)
 */
export function resampleSeries(src, tfMinutes) {
  const step = tfMinutes * 60 * 1000;
  const ET_OFF = 4 * 3600 * 1000;
  const out = [];
  let cur = null;
  let curKey = null;
  for (const b of src.bars || []) {
    const key = tfMinutes >= 1440 ? b.dayKey : Math.floor((b.time - ET_OFF) / step);
    if (key !== curKey) {
      if (cur) out.push(cur);
      curKey = key;
      cur = { ...b };
    } else {
      cur.high = Math.max(cur.high, b.high);
      cur.low = Math.min(cur.low, b.low);
      cur.close = b.close;
      cur.pdh = b.pdh;
      cur.pdl = b.pdl;
    }
  }
  if (cur) out.push(cur);
  const last = out[out.length - 1];
  const meta = {
    ...(src.meta || {}),
    last: last ? last.close : src.meta?.last,
    session: last ? last.session : src.meta?.session,
    pdh: last ? last.pdh : src.meta?.pdh,
    pdl: last ? last.pdl : src.meta?.pdl,
    openingRanges: tfMinutes <= 60 ? (src.meta?.openingRanges || []) : [],
    fvgs: detectFVGs(out, src.meta?.dp ?? 2),
    resampledFrom: src.tfMinutes ?? null,
  };
  return { bars: out, tfMinutes, meta };
}

export function activeSessionLabel(ms = Date.now()) {
  return classifySession(ms);
}

export { SESSION, classifySession, etParts, SYMBOLS };
