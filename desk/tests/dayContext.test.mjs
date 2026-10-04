// FTN I1 acceptance test for the Desk DayContext adapter (node, no deps):
//   "Can Desk display the same PAM1/Charter/Market State facts as the FTN handoff
//    without any code that independently derives those facts?"
// Every projected row/level must equal the handoff value at its declared path.
// Run from repo root: node desk/tests/dayContext.test.mjs
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  checkHandoff, findBanViolations, getPath, parseDayContext, projectDayContext, projectLevels,
} from '../js/adapters/dayContext.js';

const here = dirname(fileURLToPath(import.meta.url));
const samplesDir = join(here, '..', '..', 'ftn', 'dispatch', 'samples');
const samples = readdirSync(samplesDir).filter((f) => f.startsWith('handoff_v1_') && f.endsWith('.json'));
assert.ok(samples.length >= 2, 'expected committed handoff samples');

let checks = 0;
for (const f of samples) {
  const text = readFileSync(join(samplesDir, f), 'utf8');
  const h = parseDayContext(text);
  assert.deepEqual(checkHandoff(h), { ok: true, errors: [] }, f);
  const view = projectDayContext(h);
  const rows = [...view.header, ...view.sections.flatMap((s) => s.rows)];
  assert.ok(rows.length > 10, `${f}: projection too thin`);
  for (const r of rows) {
    assert.deepEqual(r.value, getPath(h, r.path), `${f}: ${r.label} differs from handoff at ${r.path}`);
    checks++;
  }
  for (const s of view.sections) if (s.nullAt) assert.equal(getPath(h, s.nullAt), null, `${f}: ${s.title} claims null`);
  for (const lv of view.levels) {
    assert.equal(lv.price, getPath(h, lv.path), `${f}: level ${lv.label} not verbatim`);
    checks++;
  }
  const ids = view.sections.map((s) => s.id);
  for (const need of ['ms', 'charter', 'pam1']) assert.ok(ids.includes(need), `${f}: missing ${need} section`);
}

// m9 sample: four FTN levels + opens + Asian range all drawn verbatim
const m9 = JSON.parse(readFileSync(join(samplesDir, samples.find((f) => f.includes('m9_'))), 'utf8'));
const lv = projectLevels(m9);
assert.equal(lv.filter((l) => l.label.startsWith('FTN')).length, m9.ftn_annotation.four.length);
assert.deepEqual(lv.filter((l) => l.label.startsWith('FTN')).map((l) => l.price), m9.ftn_annotation.four.map((x) => x.price));
// pam1 sample: PAM1 + Charter rendered
const pam = JSON.parse(readFileSync(join(samplesDir, samples.find((f) => f.includes('pam1_'))), 'utf8'));
const pv = projectDayContext(pam);
assert.ok(pv.sections.find((s) => s.id === 'pam1').rows.some((r) => r.path === 'market_state.pam1_completeness.required_complete' && r.value === true));
assert.ok(pv.sections.find((s) => s.id === 'charter').rows.some((r) => r.path === 'market_state.charter.charter_recognition.flag' && r.value === true));

// guard rejects banned fields (recursive) and wrong kind
for (const mut of [
  (h) => { h.BUY = true; },
  (h) => { h.market_state.institutional.confidence = 'high'; },
  (h) => { h.candidates[0].pam_rank = 1; },
  (h) => { h.session_ticket = { broker_instruction: 'x' }; },
  (h) => { h.notes.push('SELL'); },
  (h) => { h.kind = 'month9_handoff'; },
]) {
  const h = structuredClone(m9);
  mut(h);
  assert.throws(() => parseDayContext(JSON.stringify(h)), /rejected/);
}
assert.deepEqual(findBanViolations({ buy_side: 'unclear', institutional_order_flow: true, note: 'sell-side probe' }), []);

// no derivation code: the adapter must not carry FTN's old client-side level math
const src = readFileSync(join(here, '..', 'js', 'adapters', 'dayContext.js'), 'utf8');
assert.ok(!/^\s*import[^;]*levels/m.test(src), 'dayContext.js must not import levels math');
for (const banned of ['countFour(', 'pivots(', 'project(']) {
  assert.ok(!src.includes(banned), `dayContext.js must not contain ${banned}`);
}
console.log(`dayContext acceptance: ${samples.length} samples, ${checks} verbatim value checks, guards OK`);
