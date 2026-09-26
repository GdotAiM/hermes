/**
 * HERMES Desk — HERMES-X Research Context Adapter (Slice J)
 *
 * Read-only adapter that consumes structured research artifacts from HERMES-X.
 * Accepts a JSON file via URL or local path. Validates against the research
 * contract schema and exposes parsed fields for rendering.
 *
 * Contract schema (what Desk expects from HERMES-X):
 * {
 *   schemaVersion: "1",
 *   researchId: "...",
 *   symbol: "NQ1!",
 *   timeframe: "15m",
 *   session: "NY AM",
 *   asOf: "...",
 *   hypothesis: "...",
 *   evidence: [{ type, description, source }],
 *   levels: { pdh, pdl, liquidity: [], pdArrays: [] },
 *   marketStructure: { bias, events: [] },
 *   statistics: { sampleSize, winRate, reachRate },
 *   dataset: { name, source, oos }
 * }
 *
 * Fields are optional — missing keys render as "—".
 *
 * Also accepts the research board-lock markdown format
 * (research/summaries/*_BOARD_LOCK.md: "# INTELLIGENCE SUMMARY — H004b board lock",
 * **Date:** / **Tape:**, "## WHAT DID WE THINK?", "## Decision (locked)" with
 * "**H004b = FAILS.**"). Those are mapped onto the same contract with
 * format: 'board-lock-md'.
 */

const BOARD_STATUS_RE = /\b(VERIFY COMPLETE|SURVIVES|FAILS|INCONCLUSIVE|OPEN|HOLD|VERIFY)\b/;

export class HermesXAdapter {
  /**
   * @param {string} source — HTTP(S) URL or relative file path
   */
  constructor(source) {
    this.source = source;
  }

  /**
   * Load and parse a HERMES-X research artifact.
   * @returns {Promise<{ ok: boolean, artifact: object|null, error: string|null, draft: boolean }>}
   */
  async load() {
    let text = null;
    try {
      text = await this._fetch(this.source);
    } catch (err) {
      return { ok: false, artifact: null, error: err instanceof Error ? err.message : String(err), draft: false };
    }
    // Board-lock markdown (research/summaries/*_BOARD_LOCK.md)
    if (HermesXAdapter.looksLikeBoardLock(text, this.source)) {
      const artifact = this._parseBoardLock(text);
      if (artifact) return { ok: true, artifact, error: null, draft: false };
    }
    try {
      const raw = JSON.parse(text);
      const artifact = this._validate(raw);
      return { ok: true, artifact, error: null, draft: false };
    } catch (err) {
      // Try treating as a draft (partial JSON / key: value text) with more forgiving parsing
      const draft = this._parseDraft(text);
      if (draft && (draft.researchId !== 'unknown' || draft.hypothesis)) {
        return { ok: true, artifact: draft, error: null, draft: true };
      }
      return {
        ok: false,
        artifact: null,
        error: err instanceof Error ? err.message : String(err),
        draft: false,
      };
    }
  }

  static looksLikeBoardLock(text, source = '') {
    if (!text || typeof text !== 'string') return false;
    if (/_BOARD_LOCK\.md(\?|#|$)/i.test(source)) return true;
    return /^#\s*INTELLIGENCE SUMMARY/im.test(text) && /^##\s*Decision/im.test(text);
  }

  /** Split markdown into { heading → body } using "## " headings. */
  static _sections(text) {
    const out = {};
    let key = '_preamble';
    out[key] = [];
    for (const line of text.split(/\r?\n/)) {
      const h = line.match(/^##\s+(.+?)\s*$/);
      if (h) {
        key = h[1].trim().toUpperCase();
        out[key] = [];
      } else {
        out[key].push(line);
      }
    }
    for (const k of Object.keys(out)) out[k] = out[k].join('\n').trim();
    return out;
  }

  static _stripMd(s) {
    return String(s || '')
      .replace(/\*\*|__|`/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\s+/g, ' ')
      .trim();
  }

  static _bullets(body) {
    return (body || '')
      .split(/\r?\n/)
      .map((l) => l.match(/^\s*[-*]\s+(.+)$/))
      .filter(Boolean)
      .map((m) => HermesXAdapter._stripMd(m[1]));
  }

  /** Table rows (excluding header + separator) → "cell · cell · …" lines. */
  static _tableRows(body) {
    const rows = (body || '').split(/\r?\n/).filter((l) => /^\s*\|/.test(l));
    if (rows.length < 3) return [];
    const header = rows[0].split('|').slice(1, -1).map((c) => HermesXAdapter._stripMd(c));
    return rows.slice(2).map((r) => {
      const cells = r.split('|').slice(1, -1).map((c) => HermesXAdapter._stripMd(c));
      return cells.map((c, i) => (i === 0 || !header[i] ? c : `${header[i]} ${c}`)).join(' · ');
    });
  }

  /** Parse a research board-lock markdown file into the research contract. */
  _parseBoardLock(text) {
    const S = HermesXAdapter._sections(text);
    const title = (text.match(/^#\s+(.+)$/m) || [])[1] || '';
    const idMatch = title.match(/\b(H\d{3}[a-z]?)\b/i);
    const date = HermesXAdapter._stripMd((text.match(/\*\*Date:\*\*\s*(.+)$/m) || [])[1] || '');
    const tape = HermesXAdapter._stripMd((text.match(/\*\*Tape:\*\*\s*(.+)$/m) || [])[1] || '');
    const decisionKey = Object.keys(S).find((k) => k.startsWith('DECISION'));
    const decisionBody = decisionKey ? S[decisionKey] : '';
    // "**H004b = FAILS.**" — first "<id> = STATUS" in the decision block
    const dm = decisionBody.match(/([A-Za-z0-9]+)\s*=\s*(VERIFY COMPLETE|SURVIVES|FAILS|INCONCLUSIVE|HOLD|OPEN|VERIFY)\b/);
    const researchId = (dm && dm[1]) || (idMatch && idMatch[1]) || 'unknown';
    const boardStatus = dm ? dm[2].toUpperCase() : ((decisionBody.match(BOARD_STATUS_RE) || [])[1] || null);
    const decisionLines = decisionBody
      .split(/\r?\n/)
      .map((l) => HermesXAdapter._stripMd(l))
      .filter(Boolean);

    const evidence = [];
    for (const row of HermesXAdapter._tableRows(S['WHAT DID WE OBSERVE?']).slice(0, 3)) {
      evidence.push({ type: 'observed', description: row });
    }
    for (const b of HermesXAdapter._bullets(S['WHAT SURVIVED?']).slice(0, 2)) evidence.push({ type: 'survived', description: b });
    for (const b of HermesXAdapter._bullets(S['WHAT FAILED?']).slice(0, 2)) evidence.push({ type: 'failed', description: b });

    const nextKey = Object.keys(S).find((k) => k.startsWith('HIGHEST-VALUE NEXT'));
    const next = nextKey ? HermesXAdapter._stripMd(S[nextKey].split(/\r?\n\s*\r?\n/)[0]) : '';

    const artifact = this._validate({
      schemaVersion: '1',
      researchId,
      symbol: /\bNQ/i.test(tape) ? 'NQ' : '—',
      timeframe: /1M\b/i.test(tape) ? '1m tape' : '—',
      session: '—',
      asOf: date || undefined,
      hypothesis: HermesXAdapter._stripMd(S['WHAT DID WE THINK?']),
      evidence,
      dataset: { name: tape, source: this.source, oos: false },
      boardStatus,
    });
    artifact.format = 'board-lock-md';
    artifact.title = HermesXAdapter._stripMd(title.replace(/^INTELLIGENCE SUMMARY\s*[—-]\s*/i, ''));
    artifact.decision = decisionLines.join(' ');
    artifact.unknowns = HermesXAdapter._bullets(S['WHAT REMAINS UNKNOWN?']);
    artifact.next = next;
    return artifact;
  }

  /** Validate against contract schema — returns normalized artifact. */
  _validate(raw) {
    const artifact = { ...raw };

    // Fill defaults for missing fields
    artifact.schemaVersion = artifact.schemaVersion || '1';
    artifact.researchId = artifact.researchId || raw.researchId || 'unknown';
    artifact.symbol = artifact.symbol || '—';
    artifact.timeframe = artifact.timeframe || '—';
    artifact.session = artifact.session || '—';
    artifact.asOf = artifact.asOf || this._now();
    artifact.hypothesis = artifact.hypothesis || '';

    artifact.evidence = Array.isArray(artifact.evidence) ? artifact.evidence : [];
    artifact.levels = artifact.levels || {};
    artifact.levels.pdh = artifact.levels.pdh ?? null;
    artifact.levels.pdl = artifact.levels.pdl ?? null;
    artifact.levels.liquidity = artifact.levels.liquidity || [];
    artifact.levels.pdArrays = artifact.levels.pdArrays || [];

    artifact.marketStructure = artifact.marketStructure || {};
    artifact.marketStructure.bias = artifact.marketStructure.bias || null;
    artifact.marketStructure.events = artifact.marketStructure.events || [];

    artifact.statistics = artifact.statistics || {};
    artifact.statistics.sampleSize = artifact.statistics.sampleSize ?? null;
    artifact.statistics.winRate = artifact.statistics.winRate ?? null;
    artifact.statistics.reachRate = artifact.statistics.reachRate ?? null;

    artifact.dataset = artifact.dataset || {};
    artifact.dataset.name = artifact.dataset.name || '';
    artifact.dataset.source = artifact.dataset.source || '';
    artifact.dataset.oos = !!artifact.dataset.oos;

    // Extract board status from hypothesis or explicit field
    artifact.boardStatus = artifact.boardStatus || this._extractBoardStatus(artifact.hypothesis);

    return artifact;
  }

  /** Parse board status label from hypothesis text (SURVIVES, FAILS, VERIFY, INCONCLUSIVE, etc.) */
  _extractBoardStatus(hypothesis) {
    if (!hypothesis) return null;
    const match = hypothesis.match(/\b(SURVIVES|FAILS|VERIFY COMPLETE|INCONCLUSIVE|OPEN|HOLD)\b/i);
    return match ? match[1].toUpperCase() : null;
  }

  /**
   * Attempt to parse a draft/incomplete JSON artifact.
   * Tries to recover useful fields from partial data.
   */
  _parseDraft(text) {
    if (!text || typeof text !== 'string') return null;
    try {
      // Try strict parse first
      return this._validate(JSON.parse(text));
    } catch {
      // Fallback: try to extract key-value pairs from text
      const result = { hypothesis: '', evidence: [], levels: {}, marketStructure: {}, statistics: {}, dataset: {} };
      const proto = { ...result, ...this._extractFields(text) };
      return this._validate(proto);
    }
  }

  /** Extract recognizable fields from raw text when JSON parsing fails. */
  _extractFields(text) {
    const fields = {};
    const lines = text.split('\n');
    for (const line of lines) {
      const m = line.match(/^\s*(researchId|symbol|timeframe|session|hypothesis|bias|source|name)\s*[:\-]\s*(.+)$/i);
      if (m) {
        const key = m[1].toLowerCase().replace(/\s/g, '');
        const val = m[2].trim();
        if (key === 'researchid') fields.researchId = val;
        else if (key === 'symbol') fields.symbol = val;
        else if (key === 'timeframe') fields.timeframe = val;
        else if (key === 'session') fields.session = val;
        else if (key === 'hypothesis') fields.hypothesis = val;
        else if (key === 'bias') fields.bias = val;
        else if (key === 'source' || key === 'datasetname') fields.source = val;
      }
    }
    return fields;
  }

  /** Render evidence array as plain-text summary lines. */
  static renderEvidence(evidence) {
    if (!Array.isArray(evidence) || evidence.length === 0) return null;
    return evidence.map((e) => {
      const type = e.type ? `[${e.type}] ` : '';
      return `${type}${e.description || ''}`;
    }).filter(Boolean);
  }

  /** Render market structure summary. */
  static renderMarketStructure(marketStructure) {
    if (!marketStructure) return null;
    const parts = [];
    if (marketStructure.bias) parts.push(`Bias: ${marketStructure.bias}`);
    if (Array.isArray(marketStructure.events) && marketStructure.events.length > 0) {
      parts.push('Events: ' + marketStructure.events.join(', '));
    }
    return parts.length > 0 ? parts.join(' · ') : null;
  }

  /** Get status label from hypothesis text (extracts SURVIVES/FAILS etc.). */
  static getBoardStatus(hypothesis) {
    if (!hypothesis) return null;
    const match = hypothesis.match(/\b(SURVIVES|FAILS|VERIFY COMPLETE|INCONCLUSIVE|OPEN|HOLD)\b/i);
    return match ? match[1].toUpperCase() : null;
  }

  /** Format statistics for display. */
  static formatStats(stats) {
    const parts = [];
    if (stats?.sampleSize != null) parts.push(`N=${stats.sampleSize}`);
    if (stats?.winRate != null) parts.push(`WR=${Math.round(stats.winRate * 100)}%`);
    if (stats?.reachRate != null) parts.push(`RR=${Math.round(stats.reachRate * 100)}%`);
    return parts.join(' · ');
  }

  // -- private --

  async _fetch(source) {
    if (source.startsWith('http://') || source.startsWith('https://')) {
      const resp = await fetch(source);
      if (!resp.ok) throw new Error(`HTTP ${resp.status} loading ${source}`);
      return await resp.text();
    }
    const resp = await fetch(source);
    if (!resp.ok) throw new Error(`HTTP ${resp.status} loading ${source}`);
    return await resp.text();
  }

  _now() {
    return new Date().toISOString().slice(0, 19).replace('T', ' ');
  }
}

/** Convenience: instantiate and immediately load. */
export async function loadHermesX(source) {
  const adapter = new HermesXAdapter(source);
  return adapter.load();
}
