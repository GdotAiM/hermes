export class Chart {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.bars = [];
    this.overlays = {};
    this.toggles = {};
    this.resize();
    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    const r = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = r.width * dpr;
    this.canvas.height = r.height * dpr;
    this.canvas.style.width = `${r.width}px`;
    this.canvas.style.height = `${r.height}px`;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.w = r.width;
    this.h = r.height;
    this.draw();
  }

  set(bars, overlays, toggles) {
    this.bars = bars;
    this.overlays = overlays;
    this.toggles = toggles;
    this.draw();
  }

  draw() {
    const { ctx, w, h, bars } = this;
    ctx.clearRect(0, 0, w, h);
    if (!bars.length) return;
    const padR = 64;
    const padB = 18;
    const hi = Math.max(...bars.map((b) => b.h));
    const lo = Math.min(...bars.map((b) => b.l));
    const extra = this._overlayExtrema();
    const maxP = Math.max(hi, ...extra);
    const minP = Math.min(lo, ...extra);
    const span = maxP - minP || 0.001;
    const y = (p) => 12 + ((maxP - p) / span) * (h - 28 - padB);
    const bw = Math.max(3, ((w - padR) / bars.length) * 0.7);
    const gap = (w - padR) / bars.length;

    this._bands(ctx, y, w - padR);

    bars.forEach((b, i) => {
      const x = i * gap + gap / 2;
      const up = b.c >= b.o;
      ctx.strokeStyle = up ? "#26a69a" : "#ef5350";
      ctx.fillStyle = ctx.strokeStyle;
      ctx.beginPath();
      ctx.moveTo(x, y(b.h));
      ctx.lineTo(x, y(b.l));
      ctx.stroke();
      const top = y(Math.max(b.o, b.c));
      const bot = y(Math.min(b.o, b.c));
      ctx.fillRect(x - bw / 2, top, bw, Math.max(1, bot - top));
    });

    this._levels(ctx, y, w - padR);
    ctx.fillStyle = "#8b93a7";
    ctx.font = "11px system-ui";
    ctx.fillText(maxP.toFixed(5), w - padR + 6, 14);
    ctx.fillText(minP.toFixed(5), w - padR + 6, h - padB);
  }

  _overlayExtrema() {
    const o = this.overlays;
    const vals = [];
    if (!o) return vals;
    if (this.toggles.pivots && o.pivots) vals.push(...Object.values(o.pivots));
    ["cbdr", "asian", "flout"].forEach((k) => {
      if (this.toggles[k] && o[k]) vals.push(o[k].high, o[k].low);
    });
    if (this.toggles.four && o.four) o.four.forEach((l) => vals.push(l.price));
    return vals.length ? vals : [0];
  }

  _bands(ctx, y, width) {
    const o = this.overlays;
    const drawBand = (on, range, color) => {
      if (!on || !range) return;
      ctx.fillStyle = color;
      const top = y(range.high);
      const bot = y(range.low);
      ctx.fillRect(0, top, width, bot - top);
    };
    drawBand(this.toggles.cbdr, o.cbdr, "rgba(110,168,254,0.08)");
    drawBand(this.toggles.asian, o.asian, "rgba(38,166,154,0.07)");
    drawBand(this.toggles.flout, o.flout, "rgba(201,162,39,0.06)");
    if (this.toggles.pd && o.pd) {
      o.pd.forEach((g) => {
        ctx.fillStyle = "rgba(239,83,80,0.12)";
        ctx.fillRect(0, y(g.high), width, y(g.low) - y(g.high));
      });
    }
  }

  _levels(ctx, y, width) {
    const line = (price, color, dash, label) => {
      const yy = y(price);
      ctx.strokeStyle = color;
      ctx.setLineDash(dash);
      ctx.beginPath();
      ctx.moveTo(0, yy);
      ctx.lineTo(width, yy);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = color;
      ctx.font = "10px system-ui";
      ctx.fillText(label, 8, yy - 3);
    };
    const o = this.overlays;
    if (this.toggles.pivots && o.pivots) {
      Object.entries(o.pivots).forEach(([k, v]) => line(v, "#8b93a7", [4, 4], k));
    }
    if (this.toggles.four && o.four) {
      o.four.forEach((lv) => line(lv.price, "#6ea8fe", [], `L${lv.index} ${lv.name}`));
    }
  }
}
