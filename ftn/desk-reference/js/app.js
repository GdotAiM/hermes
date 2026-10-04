import { Chart } from "./chart.js";
import { FIXTURE, synthBars } from "./data.js";
import { countFour, pivots, project } from "./levels.js";
import { OS_STATE } from "./os_state.js";

const chart = new Chart(document.getElementById("chart"));

function toggles() {
  return {
    pivots: document.getElementById("togPivots").checked,
    cbdr: document.getElementById("togCbdr").checked,
    asian: document.getElementById("togAsian").checked,
    flout: document.getElementById("togFlout").checked,
    four: document.getElementById("togFour").checked,
    pd: document.getElementById("togPd").checked,
  };
}

function compute(fix) {
  const p = pivots(fix.previous_day.high, fix.previous_day.low, fix.previous_day.close);
  const cbdr = project(fix.cbdr.low, fix.cbdr.high);
  const fourOs = (OS_STATE.ftn && OS_STATE.ftn.four) || [];
  const four = fourOs.length ? fourOs : countFour(
    cbdr.down.map((price, i) => ({ name: `cbdr_dn_${i}`, price })),
    fix.last,
    fix.htf_bias
  );
  return { p, cbdr, four };
}

function renderMarketState() {
  const s = OS_STATE;
  document.getElementById("profileChip").textContent = s.profile;
  document.getElementById("fpLine").textContent = "snapshot " + s.fingerprint + " · " + s.date;
  document.getElementById("msSent").textContent = s.sentiment.direction + " / " + s.sentiment.expected_delivery;
  document.getElementById("msWr").textContent = s.sentiment.wr + " (" + s.sentiment.wr_state + ")";
  document.getElementById("msProbe").textContent = "pref " + s.sentiment.preferred + " · obs " + s.sentiment.observed;
  document.getElementById("msSpon").textContent = "D " + s.institutional.sponsorship_daily + " · 4H " + s.institutional.sponsorship_h4;
  document.getElementById("msIof").textContent = s.institutional.state + " / " + s.institutional.confidence + " (60m " + s.institutional.day_m60 + ")";
  document.getElementById("msDxy").textContent = s.dxy + " from " + s.dxy_from;
  document.getElementById("msOrigin").textContent = s.origin + " → " + (s.targets || []).join(", ");
  var ch = s.charter || {};
  var elc;
  if ((elc = document.getElementById("msCharter"))) elc.textContent = ch.charter_recognition ? String(ch.charter_recognition.flag) : "—";
  if ((elc = document.getElementById("msPam"))) {
    var pams = (ch.recognized_pams || []).map(function(e){ return e.pam_id; }).filter(Boolean);
    elc.textContent = pams.length ? pams.join(",") : "—";
  }
  var m12 = s.month12 || {};
  var el12;
  if ((el12 = document.getElementById("msM12Top"))) el12.textContent = m12.top_down ? String(m12.top_down.flag) : "—";
  if ((el12 = document.getElementById("msM12Id"))) el12.textContent = m12.identified_top_down || "—";
  var m11 = s.month11 || {};
  var el11;
  if ((el11 = document.getElementById("msM11Mega"))) el11.textContent = m11.mega_trade ? String(m11.mega_trade.flag) : "—";
  if ((el11 = document.getElementById("msM11Family"))) el11.textContent = m11.mega_trade_family || "—";
  var m10 = s.month10 || {};
  var el10;
  if ((el10 = document.getElementById("msM10Ctx"))) el10.textContent = m10.multi_asset_context ? String(m10.multi_asset_context.flag) : "—";
  if ((el10 = document.getElementById("msM10Asset"))) el10.textContent = m10.asset_class || "—";
  var m1 = s.month1 || {};
  var el1;
  if ((el1 = document.getElementById("msM1Setup"))) el1.textContent = m1.setup_elements ? String(m1.setup_elements.flag) : "—";
  if ((el1 = document.getElementById("msM1Side"))) el1.textContent = m1.dealing_range_side || "—";
  var m2 = s.month2 || {};
  var el2;
  if ((el2 = document.getElementById("msM2Frame"))) el2.textContent = m2.low_risk_frame ? String(m2.low_risk_frame.flag) : "—";
  var m3 = s.month3 || {};
  var el3;
  if ((el3 = document.getElementById("msM3Tf"))) el3.textContent = m3.selected_timeframe || "—";
  if ((el3 = document.getElementById("msM3Next"))) el3.textContent = m3.next_setup ? String(m3.next_setup.flag) : "—";
  var m4 = s.month4 || {};
  var el4;
  if ((el4 = document.getElementById("msM4Cat"))) {
    var arrs = (m4.arrays || []).map(function (a) { return a.kind; }).filter(function (k) { return k && k !== "none"; });
    el4.textContent = arrs.length ? arrs.join(",") : "—";
  }
  if ((el4 = document.getElementById("msM4Opp"))) el4.textContent = m4.array_opportunity ? String(m4.array_opportunity.flag) : "—";
  var m5 = s.month5 || {};
  var el5;
  if ((el5 = document.getElementById("msM5Qs"))) el5.textContent = (m5.quarterly_shift && m5.quarterly_shift.state) || "—";
  if ((el5 = document.getElementById("msM5Swing"))) el5.textContent = (m5.institutional_swing && m5.institutional_swing.kind) || "—";
  if ((el5 = document.getElementById("msM5Opp"))) el5.textContent = m5.position_opportunity ? String(m5.position_opportunity.flag) : "—";
  var m6 = s.month6 || {};
  var el6;
  if ((el6 = document.getElementById("msM6Family"))) el6.textContent = m6.swing_family || "—";
  if ((el6 = document.getElementById("msM6Md"))) el6.textContent = (m6.million_dollar_swing && m6.million_dollar_swing.state) || "—";
  if ((el6 = document.getElementById("msM6Opp"))) el6.textContent = m6.swing_opportunity ? String(m6.swing_opportunity.flag) : "—";
  var m7 = s.month7 || {};
  var el7;
  if ((el7 = document.getElementById("msM7Profile"))) el7.textContent = (m7.ict_weekly_profile && m7.ict_weekly_profile.name) || "—";
  if ((el7 = document.getElementById("msM7Lrlr"))) el7.textContent = (m7.lrlr && m7.lrlr.state) || "—";
  if ((el7 = document.getElementById("msM7Osok"))) el7.textContent = m7.osok_opportunity ? String(m7.osok_opportunity.flag) : "—";
  var m8 = s.month8 || {};
  var cb = m8.cbdr || {};
  var gate = m8.london_session_gate || {};
  var proj = m8.daily_extreme_projection || {};
  var ov = m8.htf_entry_overlap || {};
  var el;
  if ((el = document.getElementById("msM8Cbdr"))) el.textContent = (cb.height_pips != null ? cb.height_pips + " pips · " : "") + (cb.classification || "—");
  if ((el = document.getElementById("msM8London"))) el.textContent = gate.allowed === true ? "allowed" : (gate.allowed === false ? "avoid " + (gate.reason || "") : "—");
  if ((el = document.getElementById("msM8Profile"))) el.textContent = m8.ict_london_profile || "—";
  if ((el = document.getElementById("msM8Proj"))) el.textContent = (proj.draw || "—") + " " + (proj.selected_level != null ? proj.selected_level : "");
  if ((el = document.getElementById("msM8Htf"))) el.textContent = ov.present ? ((ov.array_id || "") + " · " + (ov.relationship || "seed_only")) : "—";
  document.getElementById("candList").innerHTML = s.candidates.map(function (c) {
    return "<li><span>" + c.module + "</span><span class=\"st-" + c.state + "\">" + c.state + "</span></li>";
  }).join("");
  const four = s.ftn.four || [];
  document.getElementById("lvlList").innerHTML = four.map(function (lv) {
    return "<li><span>L" + lv.index + " " + lv.name + "</span><span>" + Number(lv.price).toFixed(5) + "</span></li>";
  }).join("");
}

function render(fix) {
  const c = compute(fix);
  document.getElementById("symbolName").textContent = OS_STATE.symbol || fix.symbol;
  document.getElementById("lastPrice").textContent = Number(OS_STATE.last || fix.last).toFixed(5);
  renderMarketState();
  const ranges = OS_STATE.ranges || {};
  chart.set(synthBars(OS_STATE.last || fix.last), {
    pivots: c.p,
    cbdr: ranges.cbdr || fix.cbdr,
    asian: ranges.asian || fix.asian,
    flout: ranges.flout || fix.flout,
    four: (OS_STATE.ftn.four || c.four).map(function (lv, i) { return Object.assign({}, lv, { index: lv.index || i + 1 }); }),
    pd: fix.pd_arrays,
  }, toggles());
}

document.querySelectorAll(".overlay-toggles input").forEach(function (el) {
  el.addEventListener("change", function () { render(FIXTURE); });
});
document.querySelectorAll(".tf-chip").forEach(function (btn) {
  btn.addEventListener("click", function () {
    document.querySelectorAll(".tf-chip").forEach(function (b) { b.classList.remove("active"); });
    btn.classList.add("active");
  });
});
document.getElementById("btnRun").addEventListener("click", function () { render(FIXTURE); });
document.getElementById("btnTicket").addEventListener("click", function () {
  document.getElementById("ticketModal").hidden = false;
});
document.getElementById("btnClose").addEventListener("click", function () {
  document.getElementById("ticketModal").hidden = true;
});

render(FIXTURE);
if (location.hash === "#ticket") {
  document.getElementById("ticketModal").hidden = false;
}
