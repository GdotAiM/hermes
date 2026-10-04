export function pivots(h, l, c) {
  const pp = (h + l + c) / 3;
  const r1 = 2 * pp - l;
  const s1 = 2 * pp - h;
  const r2 = pp + (h - l);
  const s2 = pp - (h - l);
  return { PP: pp, R1: r1, S1: s1, R2: r2, S2: s2 };
}

export function project(low, high, n = 4) {
  const w = high - low;
  return {
    low,
    high,
    eq: (low + high) / 2,
    up: Array.from({ length: n }, (_, i) => high + i * w),
    down: Array.from({ length: n }, (_, i) => low - i * w),
  };
}

export function countFour(levels, price, bias) {
  const sorted = [...levels].sort((a, b) => a.price - b.price);
  if (bias === "bullish") return sorted.filter((x) => x.price > price).slice(0, 4);
  return [...sorted].reverse().filter((x) => x.price < price).slice(0, 4);
}
