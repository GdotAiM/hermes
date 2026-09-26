/**
 * HERMES Desk — wire UI toggles, timeframe, symbol header, right rail
 * Slice A: persist TF + overlay prefs in localStorage
 */

import { generateSeries, activeSessionLabel, SYMBOLS } from './data.js';
import { Chart } from './chart.js';
import { createOverlays } from './overlays.js';
import { ReplayController } from './replay.js';
import { loadCsv } from './adapters/csv.js';
import { loadHermesX, HermesXAdapter } from './adapters/hermesX.js';

const PREFS_KEY = 'hermes-desk:prefs:v1';
const LEVELS_PREFIX = 'hermes-desk:levels:v1';

/** Slice E — per symbol/TF (or per CSV source/TF) storage key for user levels. */
function levelsKey(sym, tf, csv) {
  const scope = csv ? `csv:${csv}` : sym;
  return `${LEVELS_PREFIX}:${scope}:${tf}`;
}

function loadPrefs() {
  try {
    return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}') || {};
  } catch {
    return {};
  }
}

function savePrefs(partial) {
  const next = { ...loadPrefs(), ...partial, updatedAt: Date.now() };
  localStorage.setItem(PREFS_KEY, JSON.stringify(next));
  return next;
}

let series = null;
let chart = null;
let currentTf = 15;
let currentSymbol = 'NQ';
// Slice G — optional CSV source (file path or URL); empty = synthetic fallback
let csvSource = '';
// Slice J — optional HERMES-X research artifact source; empty = no context
let hermesXSource = '';
// Slice K — board status of the loaded research artifact (null = none loaded)
let researchStatus = null; // { status, id }
// Slice I — optional split (2-up layout)
let splitEnabled = false;
let chartB = null;

// Slice F — replay controller
let replay = null;

function $(sel) {
  return document.querySelector(sel);
}

const FLAG_MAP = [
  ['togSessions', 'sessions'],
  ['togPDH', 'pdh'],
  ['togFVG', 'fvg'],
  ['togCE', 'ce'],
  ['togOR', 'or'],
];

function readFlagsFromDom() {
  const flags = {};
  for (const [id, key] of FLAG_MAP) {
    const el = document.getElementById(id);
    flags[key] = !!(el && el.checked);
  }
  return flags;
}

function applyFlagsToDom(flags) {
  if (!flags) return;
  for (const [id, key] of FLAG_MAP) {
    const el = document.getElementById(id);
    if (el && typeof flags[key] === 'boolean') el.checked = flags[key];
  }
}

function applyTfChip(tf) {
  document.querySelectorAll('.tf-chip').forEach((b) => {
    b.classList.toggle('active', Number(b.dataset.tf) === tf);
  });
}

function init() {
  const prefs = loadPrefs();
  if (typeof prefs.tf === 'number') currentTf = prefs.tf;
  if (prefs.symbol && SYMBOLS[prefs.symbol]) currentSymbol = prefs.symbol;
  if (typeof prefs.csvSource === 'string' && prefs.csvSource) csvSource = prefs.csvSource;
  if (typeof prefs.hermesXSource === 'string' && prefs.hermesXSource) hermesXSource = prefs.hermesXSource;
  splitEnabled = !!prefs.split;
  applyFlagsToDom(prefs.overlays);

  const canvas = $('#chart');
  const hud = $('#ohlcHud');
  chart = new Chart(canvas, hud);
  replay = new ReplayController(chart);

  let metaHolder = { meta: null };
  chart.setOverlays(createOverlays(() => metaHolder.meta));

  // Slice I — split layout: chart B is created lazily the first time 2-up is shown.
  const metaHolderB = { meta: null };

  function ensureChartB() {
    if (chartB) return chartB;
    const canvasB = $('#chartB');
    const hudB = $('#ohlcHudB');
    if (!canvasB) return null;
    chartB = new Chart(canvasB, hudB);
    chartB.setOverlays(createOverlays(() => metaHolderB.meta));
    chartB._setSplitMode(true);
    chartB.setOverlayFlags(readFlagsFromDom());
    chartB.setTool(chart.tool);
    return chartB;
  }

  /** Chart B shows the same symbol on the next-higher timeframe. */
  function loadChartB() {
    if (!chartB || !splitEnabled) return;
    const tfB = companionTf(currentTf);
    let bars;
    let meta;
    if (csvSource && series && series.meta && series.meta.source) {
      bars = series.bars; // CSV has a single native TF — mirror it
      meta = series.meta;
      chartB.setLevelsKey(levelsKey(currentSymbol, currentTf, csvSource) + ':B');
      setTag('#chartTagB', `${meta.symbol || 'CSV'} · CSV`);
    } else {
      const sB = generateSeries(currentSymbol, tfB);
      bars = sB.bars;
      meta = sB.meta;
      chartB.setLevelsKey(levelsKey(currentSymbol, tfB, ''));
      setTag('#chartTagB', `${meta.symbol} · ${tfLabel(tfB)}`);
    }
    metaHolderB.meta = meta;
    chartB.setBars(bars);
  }

  function setTag(sel, text) {
    const el = $(sel);
    if (el) el.textContent = text;
  }

  function applySplit(enabled) {
    splitEnabled = !!enabled;
    const main = document.querySelector('.main');
    const stageB = $('#chartStageB');
    main?.classList.toggle('split', splitEnabled);
    if (stageB) stageB.hidden = !splitEnabled;
    $('#btnSplit')?.classList.toggle('active', splitEnabled);
    if (splitEnabled) {
      ensureChartB();
      chartB?.resize();
      loadChartB();
    }
    chart.resize();
  }

  /**
   * Load bars from csvSource (if set) or fall back to synthetic.
   * Sets series, metaHolder, chart, replay, and updates header/status.
   */
  async function loadData() {
    const tf = currentTf;
    const sym = currentSymbol;
    if (csvSource) {
      try {
        const result = await loadCsv(csvSource);
        series = result;
        metaHolder.meta = result.meta;
        chart.setLevelsKey(levelsKey(sym, tf, csvSource));
        chart.setBars(result.bars);
        setTag('#chartTagA', `${result.meta.symbol || 'CSV'} · CSV`);
        replay.setBars(result.bars);
        updateHeader(result.meta);
        updateStatus(result.meta);
        renderMarketRead(result, sym);
        // Update symbol desc when CSV loads (CSV may have its own symbol hint)
        const descEl = $('#symbolDesc');
        if (descEl) descEl.textContent = `CSV · ${result.meta.rowsParsed ?? result.bars.length} bars`;
        applySymbolChip(sym); // keep chip highlight
        savePrefs({ symbol: sym });
        loadChartB();
        updateReplayUI();
        return;
      } catch (err) {
        console.warn('CsvAdapter failed, falling back to synthetic:', err);
        csvSource = '';
        savePrefs({ csvSource: '' });
      }
    }
    series = generateSeries(sym, tf);
    metaHolder.meta = series.meta;
    chart.setLevelsKey(levelsKey(sym, tf, ''));
    chart.setBars(series.bars);
    setTag('#chartTagA', `${series.meta.symbol} · ${tfLabel(tf)}`);
    loadChartB();
    replay.setBars(series.bars);
    updateHeader(series.meta);
    updateStatus(series.meta);
    renderMarketRead(series, sym);
    updateReplayUI();
  }

  function loadTf(tf) {
    currentTf = tf;
    loadData();
    applyTfChip(tf);
    savePrefs({ tf });
  }

  function loadSymbol(sym) {
    currentSymbol = sym;
    loadData();
    // Update symbol display from SYMBOLS registry (or CSV hint preserved above)
    const symEl = $('#symbolName');
    const descEl = $('#symbolDesc');
    if (symEl && !csvSource) symEl.textContent = SYMBOLS[sym].id;
    if (descEl && !csvSource) descEl.textContent = SYMBOLS[sym].name;
    applySymbolChip(sym);
    savePrefs({ symbol: sym });
  }

  function applySymbolChip(sym) {
    document.querySelectorAll('.sym-chip').forEach((b) => {
      b.classList.toggle('active', b.dataset.sym === sym);
    });
  }

  function applyTfChip(tf) {
    document.querySelectorAll('.tf-chip').forEach((b) => {
      b.classList.toggle('active', Number(b.dataset.tf) === tf);
    });
  }

  // Slice D — symbol chips
  document.querySelectorAll('.sym-chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      loadSymbol(btn.dataset.sym);
    });
  });

  document.querySelectorAll('.tf-chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      loadTf(Number(btn.dataset.tf));
    });
  });

  document.querySelectorAll('.tool-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tool-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      chart.setTool(btn.dataset.tool);
      if (chartB) chartB.setTool(btn.dataset.tool);
      savePrefs({ tool: btn.dataset.tool });
    });
  });

  if (prefs.tool) {
    document.querySelectorAll('.tool-btn').forEach((b) => {
      const on = b.dataset.tool === prefs.tool;
      b.classList.toggle('active', on);
      if (on) chart.setTool(prefs.tool);
    });
  }

  function syncFlags() {
    const flags = readFlagsFromDom();
    chart.setOverlayFlags(flags);
    if (chartB) chartB.setOverlayFlags(flags);
    savePrefs({ overlays: flags });
  }

  for (const [id] of FLAG_MAP) {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', syncFlags);
  }

  loadTf(currentTf);
  syncFlags();

  // Slice G — CSV data source input
  const csvInput = $('#csvSourceInput');
  const btnLoadCsv = $('#btnLoadCsv');
  const btnClearCsv = $('#btnClearCsv');
  if (csvInput && csvSource) csvInput.value = csvSource;
  if (btnLoadCsv) {
    btnLoadCsv.addEventListener('click', () => {
      const url = csvInput.value.trim();
      if (url) {
        csvSource = url;
        savePrefs({ csvSource: url });
        loadData();
      }
    });
  }
  if (btnClearCsv) {
    btnClearCsv.addEventListener('click', () => {
      csvSource = '';
      if (csvInput) csvInput.value = '';
      savePrefs({ csvSource: '' });
      loadData();
    });
  }

  // Slice J — HERMES-X research source input
  const researchInput = $('#researchSourceInput');
  const btnLoadResearch = $('#btnLoadResearch');
  const btnClearResearch = $('#btnClearResearch');
  if (researchInput && hermesXSource) researchInput.value = hermesXSource;
  if (btnLoadResearch) {
    btnLoadResearch.addEventListener('click', async () => {
      const url = researchInput.value.trim();
      if (!url) return;
      const card = $('#researchCard');
      const body = $('#researchBody');
      if (card) card.hidden = false;
      if (body) body.innerHTML = '<span class="card-research-loading">Loading research…</span>';
      try {
        const result = await loadHermesX(url);
        if (result.ok && result.artifact) {
          hermesXSource = url;
          savePrefs({ hermesXSource: url });
          if (card) card.hidden = false;
          renderResearchCard(result.artifact, result.draft);
        } else {
          throw new Error(result.error || 'Invalid artifact');
        }
      } catch (err) {
        console.warn('HERMES-X adapter failed:', err);
        clearResearchCard({ keepCard: true });
        if (body) body.innerHTML = `<span style="color:var(--down);font-size:11px">Failed to load: ${escHtml(err.message)}</span>`;
        hermesXSource = '';
        savePrefs({ hermesXSource: '' });
      }
    });
  }
  if (btnClearResearch) {
    btnClearResearch.addEventListener('click', () => {
      hermesXSource = '';
      if (researchInput) researchInput.value = '';
      savePrefs({ hermesXSource: '' });
      clearResearchCard();
    });
  }
  // Render existing research on init if pref is set
  if (hermesXSource) {
    const card = $('#researchCard');
    const body = $('#researchBody');
    if (card) card.hidden = false;
    if (body) body.innerHTML = '<span class="card-research-loading">Loading research…</span>';
    loadHermesX(hermesXSource).then((result) => {
      if (result.ok && result.artifact) {
        renderResearchCard(result.artifact, result.draft);
      } else {
        clearResearchCard();
        hermesXSource = '';
        savePrefs({ hermesXSource: '' });
      }
    }).catch(() => {
      clearResearchCard();
      hermesXSource = '';
      savePrefs({ hermesXSource: '' });
    });
  }

  // Slice C — PNG export
  const exportBtn = $('#btnExport');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const sym = ($('#symbolName')?.textContent || 'hermes-desk').trim();
      const stamp = new Date().toISOString().replace(/[:.]/g, '-');
      chart.exportPng(`${sym}-${currentTf}m-${stamp}.png`);
    });
  }

  // Slice I — Split layout toggle (works live; chart B created on demand)
  const btnSplit = $('#btnSplit');
  applySplit(splitEnabled);
  if (btnSplit) {
    btnSplit.addEventListener('click', () => {
      applySplit(!splitEnabled);
      savePrefs({ split: splitEnabled });
    });
  }

  // Slice H — Paper ticket → MINT stub
  const btnPaperTicket = $('#btnPaperTicket');
  if (btnPaperTicket) {
    btnPaperTicket.addEventListener('click', () => openTicketModal());
  }

  function openTicketModal() {
    const meta = metaHolder.meta;
    const symEl = $('#ticketSymbol');
    const tfEl = $('#ticketTf');
    const lastEl = $('#ticketLastBar');
    if (symEl && meta?.symbol) symEl.textContent = meta.symbol;
    if (tfEl) tfEl.textContent = tfLabel(currentTf);
    if (lastEl && meta?.last != null) lastEl.textContent = meta.last.toFixed(2);

    const boardEl = $('#ticketBoard');
    if (boardEl) {
      boardEl.textContent = researchStatus
        ? `${researchStatus.status}${researchStatus.id ? ' · ' + researchStatus.id : ''}`
        : 'idle · Wave 1 (no research loaded)';
      boardEl.className = 'ticket-val' + (researchStatus ? ' ticket-board-' + researchStatus.status.toLowerCase().replace(/\s+/g, '-') : '');
    }

    const deeplinkEl = $('#ticketDeeplink');
    const symId = meta?.symbol || currentSymbol;
    if (deeplinkEl) deeplinkEl.textContent = `mint://desk?sym=${encodeURIComponent(symId)}&tf=${tfLabel(currentTf)}`;

    const modal = $('#ticketModal');
    if (modal) modal.hidden = false;
  }

  // Close modal on backdrop click or Escape
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeTicketModal();
  });

  function closeTicketModal() {
    const modal = $('#ticketModal');
    if (modal) modal.hidden = true;
  }

  const btnTicketClose = $('#btnTicketClose');
  if (btnTicketClose) {
    btnTicketClose.addEventListener('click', closeTicketModal);
  }
  const ticketModal = $('#ticketModal');
  if (ticketModal) {
    ticketModal.addEventListener('click', (e) => {
      if (e.target === ticketModal) closeTicketModal();
    });
  }

  window.addEventListener('resize', () => {
    chart.resize();
    if (chartB) chartB.resize();
  });

  // Slice B — keyboard shortcuts
  window.addEventListener('keydown', (e) => {
    if (e.target && /^(INPUT|TEXTAREA|SELECT)$/i.test(e.target.tagName)) return;
    const tfKeys = { '1': 1, '2': 5, '3': 15, '4': 60, '5': 240, '6': 1440 };
    if (tfKeys[e.key] != null) {
      e.preventDefault();
      loadTf(tfKeys[e.key]);
      return;
    }
    const overlayKeys = {
      s: 'togSessions',
      l: 'togPDH',
      f: 'togFVG',
      e: 'togCE',
      o: 'togOR',
    };
    if (overlayKeys[e.key]) {
      e.preventDefault();
      const el = document.getElementById(overlayKeys[e.key]);
      if (el) {
        el.checked = !el.checked;
        syncFlags();
      }
      return;
    }
    if (e.key === 'c' || e.key === 'C') {
      e.preventDefault();
      const cursorBtn = document.querySelector('.tool-btn[data-tool="cursor"]');
      if (cursorBtn) cursorBtn.click();
    }
  });

  // Slice E — Delete removes selected level
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      if (e.target && /^(INPUT|TEXTAREA|SELECT)$/i.test(e.target.tagName)) return;
      for (const c of [chart, chartB]) {
        if (c && c.hasSelection()) {
          e.preventDefault();
          c.deleteSelected();
        }
      }
    }
  });

}

const TF_LABELS = { 1: '1m', 5: '5m', 15: '15m', 60: '1H', 240: '4H', 1440: 'D' };
function tfLabel(tf) {
  return TF_LABELS[tf] || `${tf}m`;
}

/** Next-higher timeframe for the 2-up companion chart (D pairs with 4H). */
function companionTf(tf) {
  const ladder = [1, 5, 15, 60, 240, 1440];
  const i = ladder.indexOf(tf);
  if (i < 0) return 60;
  return i === ladder.length - 1 ? ladder[i - 1] : ladder[i + 1];
}

function updateHeader(meta) {
  const last = $('#lastPrice');
  const chg = $('#priceChg');
  if (!meta || !last) return;
  last.textContent = meta.last.toFixed(2);
  const sign = meta.chg >= 0 ? '+' : '';
  chg.textContent = `${sign}${meta.chg.toFixed(2)} (${sign}${meta.chgPct.toFixed(2)}%)`;
  chg.classList.toggle('up', meta.chg >= 0);
  chg.classList.toggle('down', meta.chg < 0);
}

/**
 * Right rail "Market read" — generated from the loaded bars/meta for the
 * current symbol (descriptive, synthetic). Also sets the Lab clears note.
 */
function renderMarketRead(data, sym) {
  const list = $('#marketReadList');
  const symEl = $('#marketReadSym');
  const meta = data?.meta || {};
  const bars = data?.bars || [];
  const last = bars[bars.length - 1];
  if (symEl) symEl.textContent = `${meta.symbol || sym} · ${meta.source ? 'CSV' : 'synthetic'}`;
  const note = $('#labClearsNote');
  if (note) {
    note.textContent = sym === 'NQ' && !meta.source
      ? 'Board locks on CONTINUOUS-KAGGLE-NQ1M — priors & falsifications, not edges.'
      : `No ${meta.source ? 'CSV-tape' : sym} hypotheses on the research board — NQ Wave-1 results shown for reference only.`;
  }
  if (!list || !last) return;
  const px = (v) => (v == null ? '—' : Number(v).toFixed(2));
  const pdh = meta.pdh ?? last.pdh;
  const pdl = meta.pdl ?? last.pdl;
  const rows = [];

  // Structure: where are we vs the prior-day range, and day change
  let structure;
  if (pdh != null && pdl != null) {
    if (last.close > pdh) structure = `Trading above PDH ${px(pdh)} (+${px(last.close - pdh)}).`;
    else if (last.close < pdl) structure = `Trading below PDL ${px(pdl)} (${px(last.close - pdl)}).`;
    else structure = `Inside prior-day range ${px(pdl)} – ${px(pdh)}.`;
  } else {
    structure = 'No prior-day range in the loaded bars.';
  }
  if (meta.chg != null) structure += ` Day ${meta.chg >= 0 ? '+' : ''}${px(meta.chg)} (${meta.chg >= 0 ? '+' : ''}${Number(meta.chgPct || 0).toFixed(2)}%).`;
  rows.push(['Structure', structure]);

  // Liquidity: nearest prior-day extreme
  if (pdh != null && pdl != null) {
    const dH = Math.abs(pdh - last.close);
    const dL = Math.abs(last.close - pdl);
    const near = dH <= dL ? `PDH ${px(pdh)} (${px(dH)} pts away)` : `PDL ${px(pdl)} (${px(dL)} pts away)`;
    const far = dH <= dL ? `PDL ${px(pdl)}` : `PDH ${px(pdh)}`;
    rows.push(['Liquidity', `Nearest prior-day extreme: ${near}; opposite side ${far}.`]);
  }

  // Sessions: last bar session + latest opening range + open FVGs
  const ors = meta.openingRanges || [];
  const lastOr = ors[ors.length - 1];
  const openFvgs = (meta.fvgs || []).filter((f) => !f.mitigated).length;
  let sess = `Last bar: ${last.session || '—'} session.`;
  if (lastOr) sess += ` Latest OR ${px(lastOr.low)} – ${px(lastOr.high)}.`;
  sess += ` ${openFvgs} unmitigated FVG${openFvgs === 1 ? '' : 's'} in the loaded bars.`;
  rows.push(['Sessions', sess]);

  list.innerHTML = rows
    .map(([k, v]) => `<li><span class="read-label">${escHtml(k)}</span><span class="read-body">${escHtml(v)}</span></li>`)
    .join('');
}

function updateStatus(meta) {
  const sessEl = $('#statusSession');
  if (!sessEl) return;
  const live = activeSessionLabel(Date.now());
  const chartSess = meta?.session || live;
  sessEl.textContent = `Session: ${live} (chart last bar: ${chartSess})`;
}

/**
 * Render a HERMES-X research artifact into the right-rail card.
 * @param {object} artifact — validated research contract
 * @param {boolean} [draft=false] — true if parsed from text fallback
 */
function renderResearchCard(artifact, draft = false) {
  const card = $('#researchCard');
  const body = $('#researchBody');
  const badgeEl = $('#researchDraftBadge');

  if (!card || !body) return;

  // Header meta — only fields the artifact actually provides
  const metaEl = $('#researchMeta');
  if (metaEl) {
    const bits = [artifact.researchId, artifact.symbol, artifact.timeframe, artifact.session, artifact.asOf]
      .filter((v) => v && v !== '—' && v !== 'unknown');
    metaEl.innerHTML = bits
      .map((b, i) => `${i ? '<span class="sep">·</span>' : ''}<span class="${i === 0 ? 'research-id' : ''}">${escHtml(b)}</span>`)
      .join('');
  }
  if (badgeEl) badgeEl.hidden = !draft;
  const lockBadge = $('#researchLockBadge');
  if (lockBadge) lockBadge.hidden = artifact.format !== 'board-lock-md';

  // Update board status chip in topbar (+ remembered for the paper ticket)
  const statusChip = $('#boardStatusChip');
  const boardStatus = artifact.boardStatus || null;
  researchStatus = boardStatus ? { status: boardStatus, id: artifact.researchId !== 'unknown' ? artifact.researchId : '' } : null;
  if (statusChip) {
    if (boardStatus) {
      statusChip.textContent = researchStatus.id ? `${researchStatus.id} · ${boardStatus}` : boardStatus;
      statusChip.title = `Research board status: ${boardStatus}`;
      statusChip.hidden = false;
      statusChip.className = 'board-status-chip board-status-' + boardStatus.toLowerCase().replace(/\s+/g, '-');
    } else {
      statusChip.hidden = true;
    }
  }

  // Build body HTML
  const parts = [];

  // Decision (board-lock markdown)
  if (artifact.decision) {
    parts.push(`<div class="research-section">
      <div class="research-section-title">Decision (locked)</div>
      <div class="research-section-body research-decision">${escHtml(artifact.decision)}</div>
    </div>`);
  }

  // Hypothesis
  if (artifact.hypothesis) {
    parts.push(`<div class="research-section">
      <div class="research-section-title">Hypothesis</div>
      <div class="research-section-body">${escHtml(artifact.hypothesis)}</div>
    </div>`);
  }

  // Evidence
  const evidenceLines = HermesXAdapter.renderEvidence(artifact.evidence);
  if (evidenceLines && evidenceLines.length > 0) {
    const items = evidenceLines.map((e) => `<li>${escHtml(e)}</li>`).join('');
    parts.push(`<div class="research-section">
      <div class="research-section-title">Evidence</div>
      <ul class="research-evidence-list">${items}</ul>
    </div>`);
  }

  // Levels
  const levels = artifact.levels || {};
  if (levels.pdh != null || levels.pdl != null || levels.liquidity?.length || levels.pdArrays?.length) {
    const rows = [];
    if (levels.pdh != null) rows.push(`<div class="research-level-item"><span class="research-level-key">PDH</span><span class="research-level-val">${levels.pdh}</span></div>`);
    if (levels.pdl != null) rows.push(`<div class="research-level-item"><span class="research-level-key">PDL</span><span class="research-level-val">${levels.pdl}</span></div>`);
    if (levels.liquidity?.length) rows.push(`<div class="research-level-item" style="grid-column:1/-1"><span class="research-level-key">Liquidity</span><span class="research-level-val">${escHtml(levels.liquidity.join(', '))}</span></div>`);
    if (levels.pdArrays?.length) rows.push(`<div class="research-level-item" style="grid-column:1/-1"><span class="research-level-key">PD Arrays</span><span class="research-level-val">${escHtml(levels.pdArrays.join(', '))}</span></div>`);
    parts.push(`<div class="research-section">
      <div class="research-section-title">Levels</div>
      <div class="research-levels-grid">${rows.join('')}</div>
    </div>`);
  }

  // Market structure
  const msSummary = HermesXAdapter.renderMarketStructure(artifact.marketStructure);
  if (msSummary) {
    parts.push(`<div class="research-section">
      <div class="research-section-title">Market structure</div>
      <div class="research-section-body">${escHtml(msSummary)}</div>
    </div>`);
  }

  // Statistics
  const statsText = HermesXAdapter.formatStats(artifact.statistics);
  if (statsText) {
    parts.push(`<div class="research-section">
      <div class="research-section-title">Statistics</div>
      <div class="research-stats-inline">${escHtml(statsText)}</div>
    </div>`);
  }

  // Next experiment (board-lock markdown)
  if (artifact.next) {
    parts.push(`<div class="research-section">
      <div class="research-section-title">Next experiment</div>
      <div class="research-section-body">${escHtml(artifact.next)}</div>
    </div>`);
  }

  // Dataset info
  const ds = artifact.dataset || {};
  if (ds.name || ds.source || ds.oos != null) {
    const dsParts = [];
    if (ds.name) dsParts.push(`${artifact.format === 'board-lock-md' ? 'Tape' : 'Dataset'}: ${escHtml(ds.name)}`);
    if (ds.source) dsParts.push(`Source: ${escHtml(ds.source)}`);
    if (artifact.format !== 'board-lock-md' && ds.oos != null) dsParts.push(ds.oos ? 'OOS ✓' : 'In-sample');
    parts.push(`<div class="research-section">
      <div class="research-section-title">Dataset</div>
      <div class="research-section-body">${dsParts.join(' · ')}</div>
    </div>`);
  }

  body.innerHTML = parts.join('');
}

/** Hide the research card (unless keepCard) and reset the chip + ticket status. */
function clearResearchCard({ keepCard = false } = {}) {
  researchStatus = null;
  const card = $('#researchCard');
  const body = $('#researchBody');
  const metaEl = $('#researchMeta');
  const chip = $('#boardStatusChip');
  if (chip) {
    chip.hidden = true;
    chip.textContent = '';
  }
  if (metaEl) metaEl.innerHTML = '';
  const lockBadge = $('#researchLockBadge');
  if (lockBadge) lockBadge.hidden = true;
  const draftBadge = $('#researchDraftBadge');
  if (draftBadge) draftBadge.hidden = true;
  if (!keepCard) {
    if (body) body.innerHTML = '';
    if (card) card.hidden = true;
  }
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// — Slice F — Replay / Scrubber UI wiring
function updateReplayUI() {
  if (!replay) return;
  const s = replay.state;
  const frameEl = $('#replayFrame');
  const playBtn = $('#replayPlay');
  const exitBtn = $('#replayExit');
  const scrubber = $('#replayScrub');
  if (frameEl) frameEl.textContent = s.active ? `${s.frame + 1}/${s.barsCount}` : '—';
  // Header must not leak the future while replaying: show the playhead bar's close
  if (s.active && replay.bars[s.frame]) {
    const bar = replay.bars[s.frame];
    const last = $('#lastPrice');
    const chg = $('#priceChg');
    if (last) last.textContent = bar.close.toFixed(2);
    if (chg) {
      chg.textContent = 'replay';
      chg.classList.remove('up', 'down');
    }
  } else if (series?.meta) {
    updateHeader(series.meta);
  }
  if (playBtn) playBtn.textContent = s.playing ? '⏸' : '▶';
  if (exitBtn) exitBtn.hidden = !s.active;
  if (scrubber) {
    const max = Math.max(0, s.barsCount - 1);
    scrubber.min = '0';
    scrubber.max = String(max);
    scrubber.value = String(s.active ? s.frame : max);
  }
  document.querySelectorAll('.replay-speed-btn').forEach((b) => {
    b.classList.toggle('active', Number(b.dataset.ms) === s.speed);
  });
}

(function setupReplayUI() {
  const playBtn = $('#replayPlay');
  const prevBtn = $('#replayPrev');
  const nextBtn = $('#replayNext');
  const exitBtn = $('#replayExit');
  const scrubber = $('#replayScrub');

  if (playBtn) playBtn.addEventListener('click', () => replay.togglePlay());
  if (prevBtn) prevBtn.addEventListener('click', () => replay.step(-1));
  if (nextBtn) nextBtn.addEventListener('click', () => replay.step(1));
  if (exitBtn) exitBtn.addEventListener('click', () => replay.reset());
  if (scrubber) {
    scrubber.addEventListener('input', () => {
      replay.setFrame(Number(scrubber.value));
    });
  }
  document.querySelectorAll('.replay-speed-btn').forEach((btn) => {
    btn.addEventListener('click', () => replay.setSpeed(Number(btn.dataset.ms)));
  });

  window.addEventListener('replay:frame', () => updateReplayUI());
  window.addEventListener('replay:state', () => updateReplayUI());

  // Space = play/pause
  window.addEventListener('keydown', (e) => {
    if (e.target && /^(INPUT|TEXTAREA|SELECT|BUTTON)$/i.test(e.target.tagName)) return;
    if (e.key === ' ') {
      e.preventDefault();
      replay.togglePlay();
    }
  });

  updateReplayUI();
})();
