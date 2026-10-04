/**
 * HERMES Desk — FTN DayContext adapter (handoff.v1, read-only projection)
 *
 * Ported from FTN's old desk (ftn/desk-reference/js/os_state.js + levels.js):
 * - os_state.js was a baked snapshot → replaced by loading the real handoff
 *   (`ftn/dispatch/out/handoff_latest.json` or a committed sample) by relative
 *   path or a local file picker, like the HERMES-X research loader.
 * - levels.js computed pivots / range projections / the four-count in the
 *   browser → deliberately NOT ported.
 *
 * FTN I1 acceptance question (ftn/docs/HERMES_INTEGRATION_I0.md):
 *   "Can Desk display the same PAM1/Charter/Market State facts as the FTN
 *    handoff without any code that independently derives those facts?"
 *
 * How this module meets it: every value it emits is read verbatim from a
 * handoff JSON path (getPath) and carries that path, so the UI can show
 * provenance on hover. No ICT rule, pivot, range, count, ranking or
 * direction is computed here. The only transforms are presentation
 * (stringify, join arrays, flatten nested objects into labelled rows).
 * The node test desk/tests/dayContext.test.mjs checks that every projected
 * value equals the value at its path.
 *
 * Contract guard: refuses handoffs that are not schemaVersion "1" /
 * kind "day_context_handoff" / mode "paper", or that carry any banned field
 * (BUY/SELL calls, confidence, best_pam/pam_rank, broker_*, order fields).
 * That is validation, not derivation.
 */

export const DAY_CONTEXT_DEFAULT = '../ftn/dispatch/out/handoff_latest.json';
export const DAY_CONTEXT_SAMPLES = [
  '../ftn/dispatch/samples/handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json',
  '../ftn/dispatch/samples/handoff_v1_pam1_evidence_eurusd_2018-01-10.json',
  DAY_CONTEXT_DEFAULT,
];

// Mirrors ftn/src/ftn/os/handoff_contract.py (authoritative).
const BANNED_KEYS = new Set([
  'buy', 'sell', 'side', 'action', 'signal', 'signals', 'recommendation',
  'trade_direction', 'direction_recommendation', 'trade_signal',
  'confidence', 'confidence_score', 'best_pam', 'pam_rank', 'rank', 'ranking',
  'order', 'orders', 'order_id', 'order_type', 'client_order_id', 'qty',
  'quantity', 'limit_price', 'stop_price', 'stop_loss', 'take_profit',
  'time_in_force', 'tif', 'position_size', 'lots', 'notional', 'account_id',
  'place_order', 'submit_order', 'route', 'routing', 'auto_clear', 'automatic_clearance',
]);
const BANNED_KEY_SUBSTRINGS = ['broker', 'confidence', 'best_pam', 'pam_rank'];
const BANNED_VALUE_RE = /^\s*(strong[\s_-]*)?(buy|sell)\s*$/i;

/** Recursively list banned keys / buy-sell values. */
export function findBanViolations(obj, path = '$') {
  const out = [];
  if (Array.isArray(obj)) {
    obj.forEach((v, i) => out.push(...findBanViolations(v, `${path}[${i}]`)));
  } else if (obj && typeof obj === 'object') {
    for (const [k, v] of Object.entries(obj)) {
      const kl = k.toLowerCase();
      if (BANNED_KEYS.has(kl) || BANNED_KEY_SUBSTRINGS.some((s) => kl.includes(s))) out.push(`banned key ${path}.${k}`);
      out.push(...findBanViolations(v, `${path}.${k}`));
    }
  } else if (typeof obj === 'string' && BANNED_VALUE_RE.test(obj)) {
    out.push(`banned buy/sell value at ${path}`);
  }
  return out;
}

/** @returns {{ok:boolean, errors:string[]}} */
export function checkHandoff(h) {
  const errors = [];
  if (!h || typeof h !== 'object' || Array.isArray(h)) return { ok: false, errors: ['not a JSON object'] };
  if (h.schemaVersion !== '1') errors.push('schemaVersion must be "1"');
  if (h.kind !== 'day_context_handoff') errors.push('kind must be "day_context_handoff"');
  if (h.mode !== 'paper') errors.push('mode must be "paper"');
  if (!h.market_state || typeof h.market_state !== 'object') errors.push('market_state missing');
  errors.push(...findBanViolations(h));
  return { ok: errors.length === 0, errors };
}

/** Read a value at a dotted path with [i] indices, e.g. "candidates[0].module". */
export function getPath(obj, path) {
  const parts = path.replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean);
  let cur = obj;
  for (const p of parts) {
    if (cur == null || typeof cur !== 'object' || !(p in cur)) return undefined;
    cur = cur[p];
  }
  return cur;
}

/** Leaf rows for an object subtree: [{label, path, value}] (value verbatim). */
function leafRows(h, basePath, labelPrefix = '') {
  const root = getPath(h, basePath);
  const rows = [];
  const walk = (v, path, label) => {
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      const entries = Object.entries(v);
      if (!entries.length) rows.push({ label: label || '(empty)', path, value: v });
      for (const [k, sub] of entries) walk(sub, `${path}.${k}`, label ? `${label} › ${k}` : k);
    } else if (Array.isArray(v) && v.some((x) => x && typeof x === 'object')) {
      v.forEach((x, i) => walk(x, `${path}[${i}]`, `${label || basePath}[${i}]`));
    } else {
      rows.push({ label: label || labelPrefix || basePath, path, value: v });
    }
  };
  if (root === undefined) return rows;
  walk(root, basePath, labelPrefix);
  return rows;
}

function rowsAt(h, specs) {
  const rows = [];
  for (const [label, path] of specs) {
    const value = getPath(h, path);
    if (value === undefined) continue; // absent in this handoff → not shown
    if (value && typeof value === 'object' && !Array.isArray(value)) rows.push(...leafRows(h, path, label));
    else rows.push({ label, path, value });
  }
  return rows;
}

const MARKET_STATE_SPECS = [
  ['Profile', 'market_state.profile'],
  ['Sentiment', 'market_state.sentiment.direction'],
  ['Expected delivery', 'market_state.sentiment.expected_delivery'],
  ['Williams %R', 'market_state.sentiment.indicator.value'],
  ['%R state', 'market_state.sentiment.indicator.state'],
  ['Liquidity probe', 'market_state.sentiment.liquidity_probe'],
  ['Judas side', 'market_state.sentiment.judas_side'],
  ['PD-array reaction', 'market_state.sentiment.reaction.pd_array_reaction'],
  ['IOF state', 'market_state.institutional.state'],
  ['IOF qualification', 'market_state.institutional.qualification'],
  ['Sponsorship', 'market_state.institutional.sponsorship'],
  ['Daytrade IOF', 'market_state.institutional.daytrade_iof'],
  ['IOF notes', 'market_state.institutional.notes'],
  ['DXY relationship', 'market_state.dxy.relationship'],
  ['DXY from', 'market_state.dxy.from'],
  ['Origin PD array', 'market_state.origin_pd_array'],
  ['Opposing targets', 'market_state.opposing_target_arrays'],
  ['Scenario primary', 'market_state.scenarios.primary'],
  ['Scenario contrary', 'market_state.scenarios.contrary'],
];

const LEVEL_COLORS = { ftn: '#b388ff', open: '#c9a227', asia: '#6ea8fe' };

/**
 * Chart levels — prices copied verbatim from the handoff:
 *   ftn_annotation.four[i].price, market_state.opens.*, market_state.sentiment.asian_range.{high,low}
 */
export function projectLevels(h) {
  const levels = [];
  const four = getPath(h, 'ftn_annotation.four');
  if (Array.isArray(four)) {
    four.forEach((lv, i) => {
      if (!lv || typeof lv.price !== 'number') return;
      const idx = lv.index != null ? `${lv.index} ` : '';
      levels.push({ label: `FTN ${idx}${lv.name ?? ''}`.trim(), price: lv.price, path: `ftn_annotation.four[${i}].price`, color: LEVEL_COLORS.ftn });
    });
  }
  const opens = getPath(h, 'market_state.opens');
  if (opens && typeof opens === 'object') {
    for (const [k, v] of Object.entries(opens)) {
      if (typeof v === 'number') levels.push({ label: `open ${k}`, price: v, path: `market_state.opens.${k}`, color: LEVEL_COLORS.open });
    }
  }
  const asia = getPath(h, 'market_state.sentiment.asian_range');
  if (asia && typeof asia === 'object') {
    if (typeof asia.high === 'number') levels.push({ label: 'Asia H', price: asia.high, path: 'market_state.sentiment.asian_range.high', color: LEVEL_COLORS.asia });
    if (typeof asia.low === 'number') levels.push({ label: 'Asia L', price: asia.low, path: 'market_state.sentiment.asian_range.low', color: LEVEL_COLORS.asia });
  }
  return levels;
}

/**
 * Full read-only projection for the right-rail card.
 * @returns {{ header: object[], sections: {id,title,note,nullAt?,rows}[], levels: object[] }}
 */
export function projectDayContext(h) {
  const header = rowsAt(h, [
    ['Symbol', 'symbol'], ['Date', 'date'], ['Session', 'session'], ['Mode', 'mode'],
    ['Producer', 'producer'], ['Fingerprint', 'fingerprint'],
  ]);
  const sections = [];
  sections.push({ id: 'ms', title: 'Market State', note: 'Frozen by FTN; Desk must not mutate.', rows: rowsAt(h, MARKET_STATE_SPECS) });

  const charter = getPath(h, 'market_state.charter');
  sections.push(charter == null
    ? { id: 'charter', title: 'Charter', note: 'market_state.charter is null in this handoff.', nullAt: 'market_state.charter', rows: [] }
    : { id: 'charter', title: 'Charter', note: 'Recognition ≠ clearance ≠ execution.', rows: leafRows(h, 'market_state.charter') });

  const ev = getPath(h, 'market_state.pam1_evidence');
  const comp = getPath(h, 'market_state.pam1_completeness');
  const pamRows = [
    ...(ev == null ? [] : leafRows(h, 'market_state.pam1_evidence').map((r) => ({ ...r, label: `evidence › ${r.label}` }))),
    ...(comp == null ? [] : leafRows(h, 'market_state.pam1_completeness').map((r) => ({ ...r, label: `completeness › ${r.label}` }))),
  ];
  sections.push({
    id: 'pam1', title: 'PAM1',
    note: ev == null && comp == null
      ? 'market_state.pam1_evidence / pam1_completeness are null in this handoff.'
      : 'Research intelligence — not an execution instruction. MINT ignores PAM1 unless a strategy is cleared.',
    nullAt: ev == null && comp == null ? 'market_state.pam1_evidence' : undefined,
    rows: pamRows,
  });

  const cands = getPath(h, 'candidates') || [];
  sections.push({
    id: 'cands', title: 'Candidates', note: 'Annotation ≠ opportunity ≠ candidate ≠ ticket ≠ order.',
    rows: cands.map((c, i) => ({
      label: String(getPath(h, `candidates[${i}].module`)),
      path: `candidates[${i}]`,
      value: c, // verbatim candidate object
      display: `${c.state} · eligible=${c.eligible} · ${c.reason} · ${c.origin}`,
    })),
  });

  sections.push({ id: 'ftn', title: 'FTN annotation', note: 'Objectives only (FTN annotate). Prices drawn on chart as given.',
    rows: [...rowsAt(h, [['Family', 'ftn_annotation.family'], ['Bias', 'ftn_annotation.bias']]),
      ...((getPath(h, 'ftn_annotation.four') || []).map((lv, i) => ({ label: `four[${i}] ${lv.name ?? ''}`, path: `ftn_annotation.four[${i}].price`, value: lv.price })))] });

  const ticket = getPath(h, 'session_ticket');
  sections.push(ticket == null
    ? { id: 'ticket', title: 'Session ticket', note: 'session_ticket is null.', nullAt: 'session_ticket', rows: [] }
    : { id: 'ticket', title: 'Session ticket', note: 'FTN paper session ticket — not an order; MINT does not act on it.', rows: leafRows(h, 'session_ticket') });

  return { header, sections, levels: projectLevels(h) };
}

/** Load a handoff from a same-origin relative path / URL. */
export async function loadDayContextUrl(url) {
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return parseDayContext(await res.text());
}

/** Load a handoff from a File chosen via <input type=file>. */
export async function loadDayContextFile(file) {
  return parseDayContext(await file.text());
}

export function parseDayContext(text) {
  let h;
  try {
    h = JSON.parse(text);
  } catch (e) {
    throw new Error(`not JSON: ${e.message}`);
  }
  const chk = checkHandoff(h);
  if (!chk.ok) throw new Error(`rejected handoff.v1: ${chk.errors.slice(0, 3).join('; ')}`);
  return h;
}

/** Presentation only: stringify a verbatim value for display. */
export function displayValue(v) {
  if (v === null) return 'null';
  if (v === undefined) return '—';
  if (Array.isArray(v)) return v.length ? v.map((x) => (x && typeof x === 'object' ? JSON.stringify(x) : String(x))).join(' · ') : '[]';
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}
