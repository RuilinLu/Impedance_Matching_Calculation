/* ==========================================================================
   Smith chart + chart primitives (vanilla canvas, no dependencies)
   ========================================================================== */

(function () {
  "use strict";

  const PALETTE = ["#22d3ee", "#34d399", "#fbbf24", "#a78bfa", "#f87171", "#60a5fa"];
  const FONT = '11px "Microsoft YaHei", "Segoe UI", system-ui, sans-serif';
  const FONT_SMALL = '9px "Microsoft YaHei", "Segoe UI", system-ui, sans-serif';

  function setupCanvas(canvas) {
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(10, rect.width || canvas.clientWidth || 400);
    const h = Math.max(10, rect.height || canvas.clientHeight || 400);
    const dpr = Math.min(window.devicePixelRatio || 1, 2.5);
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    return { ctx, w, h };
  }

  function roundRect(ctx, x, y, w, h, r) {
    const rr = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + rr, y);
    ctx.arcTo(x + w, y, x + w, y + h, rr);
    ctx.arcTo(x + w, y + h, x, y + h, rr);
    ctx.arcTo(x, y + h, x, y, rr);
    ctx.arcTo(x, y, x + w, y, rr);
    ctx.closePath();
  }

  class SmithChart {
    constructor(canvas, options = {}) {
      this.canvas = canvas;
      this.mini = !!options.mini;
      this.tooltip = options.tooltip || null;
      this.onStateChange = options.onStateChange || null;
      this.data = { steps: [], load: null, z0: 50, scanPoints: [], coverage: null, gridSize: 0 };
      this.progress = 1;
      this.playing = false;
      this.speed = 45;
      this.hover = null;
      this._raf = null;
      this._last = 0;
      this.scanLayer = null;
      this.scanPointCache = [];
      this.scanCount = 0;
      this._drawPending = false;
      this._bind();
      this._observe();
    }

    _bind() {
      this._onMove = (e) => {
        if (this.mini) return;
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const g = this._toGamma(x, y);
        if (!g) {
          this.hover = null;
          if (this.tooltip) this.tooltip.style.opacity = "0";
          return;
        }
        const z0 = this.data.z0 || 50;
        const den = 1 - g.re;
        let ztxt;
        if (Math.abs(den) < 1e-6 && Math.abs(g.im) < 1e-6) {
          ztxt = "∞";
        } else {
          const zr = z0 * (1 - g.re * g.re - g.im * g.im) / (den * den + g.im * g.im);
          const zi = z0 * (2 * g.im) / (den * den + g.im * g.im);
          ztxt = `${zr.toFixed(1)} ${zi >= 0 ? "+" : "−"} j${Math.abs(zi).toFixed(1)} Ω`;
        }
        const mag = Math.hypot(g.re, g.im);
        const vswr = mag < 1 ? (1 + mag) / (1 - mag) : Infinity;
        this.hover = { x, y, g };
        if (this.tooltip) {
          this.tooltip.innerHTML = `Z = ${ztxt}<br>Γ = ${g.re.toFixed(3)} ${g.im >= 0 ? "+" : "−"} j${Math.abs(g.im).toFixed(3)} · VSWR ${vswr.toFixed(2)}`;
          this.tooltip.style.left = `${x}px`;
          this.tooltip.style.top = `${y}px`;
          this.tooltip.style.opacity = "1";
        }
        this.draw();
      };
      this._onLeave = () => {
        this.hover = null;
        if (this.tooltip) this.tooltip.style.opacity = "0";
        this.draw();
      };
      this.canvas.addEventListener("mousemove", this._onMove);
      this.canvas.addEventListener("mouseleave", this._onLeave);
    }

    _observe() {
      if (typeof ResizeObserver !== "undefined") {
        this._ro = new ResizeObserver(() => this.draw());
        this._ro.observe(this.canvas.parentElement || this.canvas);
      } else {
        window.addEventListener("resize", () => this.draw());
      }
    }

    setData(data) {
      this.data = Object.assign({ steps: [], load: null, z0: 50, scanPoints: [],
        coverage: null, gridSize: 0 }, data || {});
      this.progress = 1;
      this.playing = false;
      this.scanPointCache = (this.data.scanPoints || []).slice();
      this.scanCount = this.scanPointCache.length;
      this.scanLayer = null;
      this.draw();
    }

    setScanPoints(points) {
      this.data.scanPoints = points || [];
      this.scanPointCache = (points || []).slice();
      this.scanCount = this.scanPointCache.length;
      this.scanLayer = null;
      this.draw();
    }

    beginScan(z0, load) {
      this.data.steps = [];
      this.data.scanPoints = [];
      this.data.coverage = null;
      this.data.gridSize = 0;
      this.data.z0 = Number(z0) || 50;
      this.data.load = load || null;
      this.scanPointCache = [];
      this.scanCount = 0;
      this.scanLayer = null;
      this.draw();
    }

    addScanPoints(points) {
      const list = points || [];
      if (!list.length) return;
      const geom = this._geom();
      for (const point of list) {
        this.scanPointCache.push(point);
        this._paintScanPoint(point, geom);
      }
      this.scanCount = this.scanPointCache.length;
      if (!this._drawPending) {
        this._drawPending = true;
        setTimeout(() => {
          this._drawPending = false;
          this.draw();
        }, 16);
      }
    }

    finishScan(summary) {
      this.data.coverage = (summary && summary.coverage) || null;
      this.data.gridSize = Number(summary && summary.grid_size) || 0;
      this.data.scanPoints = [];
      this.draw();
    }

    clearScan() {
      this.data.scanPoints = [];
      this.data.coverage = null;
      this.data.gridSize = 0;
      this.scanPointCache = [];
      this.scanCount = 0;
      this.scanLayer = null;
      this.draw();
    }

    _ensureScanLayer(geom) {
      if (this.scanLayer && this.scanLayer.width === Math.round(geom.w)
          && this.scanLayer.height === Math.round(geom.h)) {
        return this.scanLayer;
      }
      const layer = document.createElement("canvas");
      layer.width = Math.max(10, Math.round(geom.w));
      layer.height = Math.max(10, Math.round(geom.h));
      this.scanLayer = layer;
      for (const point of this.scanPointCache) this._paintScanPoint(point, geom);
      return layer;
    }

    _paintScanPoint(point, geom) {
      const geometry = geom || this._geom();
      const layer = this._ensureScanLayer(geometry);
      const ctx = layer.getContext("2d");
      const g = point && (point.g || point);
      if (!g || !isFinite(g.re) || !isFinite(g.im)) return;
      const mag = Math.hypot(g.re, g.im);
      if (mag > 1.02) return;
      const x = geometry.cx + geometry.r * g.re;
      const y = geometry.cy - geometry.r * g.im;
      const near = mag < 0.34;
      ctx.fillStyle = near
        ? `rgba(34,211,238,${(0.28 + 0.5 * (1 - mag / 0.34)).toFixed(3)})`
        : "rgba(148,163,184,0.34)";
      const size = this.mini ? 1 : (near ? 1.9 : 1.4);
      ctx.fillRect(x - size / 2, y - size / 2, size, size);
    }

    _geom() {
      const rect = this.canvas.getBoundingClientRect();
      const w = Math.max(10, rect.width || this.canvas.clientWidth);
      const h = Math.max(10, rect.height || this.canvas.clientHeight);
      const pad = this.mini ? 6 : Math.max(18, Math.min(34, Math.min(w, h) * 0.065));
      const r = Math.max(10, Math.min(w, h) / 2 - pad);
      return { w, h, cx: w / 2, cy: h / 2, r };
    }

    _toGamma(x, y) {
      const { cx, cy, r } = this._geom();
      const re = (x - cx) / r;
      const im = -(y - cy) / r;
      if (re * re + im * im > 1.005) return null;
      return { re, im };
    }

    _toPixel(g, geom) {
      return { x: geom.cx + geom.r * g.re, y: geom.cy - geom.r * g.im };
    }

    draw() {
      const { ctx, w, h } = setupCanvas(this.canvas);
      const geom = this._geom();
      const { cx, cy, r } = geom;

      // background glow
      if (!this.mini) {
        const bg = ctx.createRadialGradient(cx, cy, r * 0.1, cx, cy, r * 1.2);
        bg.addColorStop(0, "rgba(20, 48, 72, 0.22)");
        bg.addColorStop(1, "rgba(6, 14, 26, 0)");
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, w, h);
      }

      // outer disc
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = this.mini ? "rgba(8, 18, 32, .35)" : "rgba(7, 17, 30, .55)";
      ctx.fill();
      ctx.strokeStyle = this.mini ? "rgba(148,163,184,.35)" : "rgba(148, 163, 184, .42)";
      ctx.lineWidth = this.mini ? 1 : 1.3;
      ctx.stroke();

      // clip grid
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();
      this._drawGrid(ctx, geom);
      ctx.restore();

      // scan points
      this._drawScan(ctx, geom);

      // trajectory
      this._drawSteps(ctx, geom);

      // markers
      this._drawMarkers(ctx, geom);

      // labels
      if (!this.mini) this._drawLabels(ctx, geom);

      // hover crosshair
      if (this.hover && !this.mini) {
        const p = this._toPixel(this.hover.g, geom);
        ctx.strokeStyle = "rgba(34, 211, 238, .55)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(p.x - 5, p.y);
        ctx.lineTo(p.x + 5, p.y);
        ctx.moveTo(p.x, p.y - 5);
        ctx.lineTo(p.x, p.y + 5);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = "#22d3ee";
        ctx.fill();
      }
    }

    _drawGrid(ctx, geom) {
      const { cx, cy, r } = geom;
      ctx.lineWidth = this.mini ? 0.6 : 0.8;
      ctx.strokeStyle = this.mini ? "rgba(148,163,184,.12)" : "rgba(148, 163, 184, .16)";
      const rvals = [0, 0.2, 0.5, 1, 2, 5, 10];
      for (const rv of rvals) {
        const ccx = cx + r * rv / (1 + rv);
        const rad = r / (1 + rv);
        ctx.beginPath();
        ctx.arc(ccx, cy, rad, 0, Math.PI * 2);
        ctx.stroke();
      }
      const xvals = [0.2, 0.5, 1, 2, 5, 10];
      for (const xv of xvals) {
        for (const sign of [1, -1]) {
          const ccy = cy - sign * r / xv;
          const rad = r / xv;
          ctx.beginPath();
          ctx.arc(cx + r, ccy, rad, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
      // real axis
      ctx.strokeStyle = this.mini ? "rgba(148,163,184,.16)" : "rgba(148, 163, 184, .24)";
      ctx.beginPath();
      ctx.moveTo(cx - r, cy);
      ctx.lineTo(cx + r, cy);
      ctx.stroke();
    }

    _drawScan(ctx, geom) {
      const coverage = this.data.coverage;
      if (coverage && Number(this.data.gridSize) > 0) {
        this._drawCoverage(ctx, geom, coverage, Number(this.data.gridSize));
      }
      if (!this.scanCount) return;
      const layer = this._ensureScanLayer(geom);
      if (!layer) return;
      ctx.save();
      ctx.globalAlpha = 0.92;
      ctx.drawImage(layer, 0, 0, geom.w, geom.h);
      ctx.restore();
    }

    _drawCoverage(ctx, geom, encoded, grid) {
      let bytes;
      try {
        const binary = atob(String(encoded || ""));
        bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      } catch (error) {
        return;
      }
      if (!grid || bytes.length < grid * grid) return;
      let max = 1;
      for (let i = 0; i < grid * grid; i++) if (bytes[i] > max) max = bytes[i];
      const { cx, cy, r } = geom;
      const cell = (2 * r) / grid;
      const alphaFor = (value) => {
        // Minimum alpha keeps a sparse but valid region visible; larger ranges
        // can lower the density but never hide the covered cells.
        const ratio = Math.pow(value / max, 0.6);
        return 0.11 + 0.44 * ratio;
      };
      for (let iy = 0; iy < grid; iy++) {
        for (let ix = 0; ix < grid; ix++) {
          const value = bytes[iy * grid + ix];
          if (!value) continue;
          const gx = -1 + (ix + 0.5) * (2 / grid);
          const gy = 1 - (iy + 0.5) * (2 / grid);
          if (gx * gx + gy * gy > 1.0) continue;
          const px = cx + r * gx - cell / 2;
          const py = cy - r * gy - cell / 2;
          ctx.fillStyle = `rgba(100, 116, 139, ${alphaFor(value).toFixed(3)})`;
          ctx.fillRect(px, py, cell + 0.7, cell + 0.7);
        }
      }
      // Stronger outline on cells that touch empty space.
      const occupied = (ix, iy) => ix >= 0 && iy >= 0 && ix < grid && iy < grid
        && bytes[iy * grid + ix] > 0;
      ctx.fillStyle = "rgba(148, 163, 184, 0.30)";
      for (let iy = 0; iy < grid; iy++) {
        for (let ix = 0; ix < grid; ix++) {
          if (!occupied(ix, iy)) continue;
          if (occupied(ix - 1, iy) && occupied(ix + 1, iy)
              && occupied(ix, iy - 1) && occupied(ix, iy + 1)) continue;
          const gx = -1 + (ix + 0.5) * (2 / grid);
          const gy = 1 - (iy + 0.5) * (2 / grid);
          if (gx * gx + gy * gy > 1.0) continue;
          const px = cx + r * gx;
          const py = cy - r * gy;
          ctx.fillRect(px - cell * 0.12, py - cell * 0.12, cell * 0.24, cell * 0.24);
        }
      }
    }

    _drawSteps(ctx, geom) {
      const steps = this.data.steps || [];
      if (!steps.length) return;
      const total = steps.reduce((n, s) => n + Math.max(1, (s.points_gamma || []).length), 0);
      const budget = Math.max(0, Math.min(1, this.progress)) * total;
      let used = 0;
      let moving = null;

      for (let si = 0; si < steps.length; si++) {
        const s = steps[si];
        const pts = s.points_gamma || [];
        if (!pts.length) continue;
        const color = PALETTE[si % PALETTE.length];
        const remain = budget - used;
        if (remain <= 0) break;
        const count = Math.min(pts.length, Math.max(1, Math.ceil(remain)));
        const fully = count >= pts.length;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = this.mini ? 1.6 : 2.5;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        if (!this.mini) {
          ctx.shadowColor = color;
          ctx.shadowBlur = 7;
        }
        ctx.beginPath();
        for (let i = 0; i < count; i++) {
          const g = pts[i];
          if (!isFinite(g.re) || !isFinite(g.im)) continue;
          const px = geom.cx + geom.r * g.re;
          const py = geom.cy - geom.r * g.im;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();
        ctx.restore();

        const last = pts[Math.max(0, count - 1)];
        if (!fully && last) moving = { g: last, color };
        if (fully) {
          const end = s.end && s.end.gamma ? s.end.gamma : last;
          if (end) {
            const px = geom.cx + geom.r * end.re;
            const py = geom.cy - geom.r * end.im;
            ctx.beginPath();
            ctx.arc(px, py, this.mini ? 2 : 3, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();
          }
        }
        used += pts.length;
      }

      if (moving) {
        const px = geom.cx + geom.r * moving.g.re;
        const py = geom.cy - geom.r * moving.g.im;
        ctx.save();
        ctx.beginPath();
        ctx.arc(px, py, this.mini ? 2.5 : 4.2, 0, Math.PI * 2);
        ctx.fillStyle = moving.color;
        ctx.shadowColor = moving.color;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.restore();
      }
    }

    _drawMarkers(ctx, geom) {
      const steps = this.data.steps || [];
      let loadGamma = null;
      if (this.data.load && isFinite(this.data.load.re)) {
        const z0 = this.data.z0 || 50;
        const z = { re: this.data.load.re, im: this.data.load.im };
        const d = { re: z.re + z0, im: z.im };
        const den = d.re * d.re + d.im * d.im;
        loadGamma = { re: ((z.re - z0) * d.re + z.im * d.im) / den, im: (z.im * d.re - (z.re - z0) * d.im) / den };
      } else if (steps.length && steps[0].start && steps[0].start.gamma) {
        loadGamma = steps[0].start.gamma;
      }
      if (loadGamma && Math.hypot(loadGamma.re, loadGamma.im) <= 1.05) {
        const px = geom.cx + geom.r * loadGamma.re;
        const py = geom.cy - geom.r * loadGamma.im;
        ctx.save();
        ctx.beginPath();
        ctx.arc(px, py, this.mini ? 3 : 5.5, 0, Math.PI * 2);
        ctx.fillStyle = "#fb923c";
        ctx.strokeStyle = "#fff4e8";
        ctx.lineWidth = 1.2;
        ctx.shadowColor = "#fb923c";
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.stroke();
        ctx.restore();
        if (!this.mini) {
          ctx.font = FONT_SMALL;
          ctx.fillStyle = "#fdba74";
          ctx.textAlign = px > geom.cx ? "right" : "left";
          ctx.fillText("负载", px + (px > geom.cx ? -9 : 9), py - 9);
        }
      }
      // match point
      ctx.save();
      ctx.beginPath();
      ctx.arc(geom.cx, geom.cy, this.mini ? 2.5 : 4, 0, Math.PI * 2);
      ctx.fillStyle = "#34d399";
      ctx.shadowColor = "#34d399";
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.restore();
      if (!this.mini) {
        ctx.font = FONT_SMALL;
        ctx.fillStyle = "#6ee7b7";
        ctx.textAlign = "center";
        ctx.fillText("匹配点", geom.cx, geom.cy + 30);
      }
    }

    _drawLabels(ctx, geom) {
      const { cx, cy, r } = geom;
      ctx.font = FONT_SMALL;
      ctx.textAlign = "center";
      ctx.fillStyle = "rgba(139, 160, 189, .85)";
      for (const rv of [0.2, 0.5, 1, 2, 5]) {
        const x = cx + r * rv / (1 + rv);
        ctx.fillText(String(rv), x, cy + 14);
      }
      ctx.textAlign = "right";
      ctx.fillText("0", cx - r + 2, cy - 7);
      ctx.textAlign = "left";
      ctx.fillText("∞", cx + r - 9, cy - 7);
      // reactance labels around the rim
      ctx.fillStyle = "rgba(139, 160, 189, .55)";
      for (const xv of [0.5, 1, 2, 5]) {
        for (const sign of [1, -1]) {
          const g = { re: (xv * xv - 1) / (xv * xv + 1), im: sign * (2 * xv) / (xv * xv + 1) };
          if (Math.abs(g.re) > 0.985 && Math.abs(g.im) < 0.05) continue;
          const px = cx + r * 1.055 * g.re;
          const py = cy - r * 1.055 * g.im;
          ctx.textAlign = g.re >= 0 ? "left" : "right";
          ctx.textBaseline = "middle";
          ctx.fillText(`${sign > 0 ? "+" : "−"}j${xv}`, px, py);
        }
      }
      // corner title
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      ctx.font = FONT_SMALL;
      ctx.fillStyle = "rgba(100, 120, 146, .8)";
      ctx.fillText("SMITH CHART · Z / Z0", 12, 18);
      // center label
      ctx.textAlign = "center";
      ctx.fillStyle = "rgba(52, 211, 153, .75)";
      ctx.fillText(`${this.data.z0 || 50}Ω`, cx, cy - 10);
    }

    play() {
      if (this._raf) cancelAnimationFrame(this._raf);
      if (this.progress >= 1) this.progress = 0;
      this.playing = true;
      this._last = performance.now();
      this._notify();
      const duration = 7000 - Math.max(0, Math.min(100, this.speed)) * 55;
      const tick = (now) => {
        const dt = Math.min(80, now - this._last);
        this._last = now;
        this.progress += dt / duration;
        if (this.progress >= 1) {
          this.progress = 1;
          this.playing = false;
          this.draw();
          this._notify();
          this._raf = null;
          return;
        }
        this.draw();
        this._raf = requestAnimationFrame(tick);
      };
      this._raf = requestAnimationFrame(tick);
    }

    pause() {
      this.playing = false;
      if (this._raf) cancelAnimationFrame(this._raf);
      this._raf = null;
      this._notify();
    }

    reset() {
      this.pause();
      this.progress = 0;
      this.draw();
      this._notify();
    }

    setSpeed(v) {
      this.speed = v;
    }

    _notify() {
      if (this.onStateChange) this.onStateChange(this.playing, this.progress);
    }
  }

  function convexHull(points) {
    if (!points || points.length < 3) return points || [];
    const sorted = points.slice().sort((a, b) => (a.x === b.x ? a.y - b.y : a.x - b.x));
    const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
    const lower = [];
    for (const point of sorted) {
      while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], point) <= 0) lower.pop();
      lower.push(point);
    }
    const upper = [];
    for (let index = sorted.length - 1; index >= 0; index--) {
      const point = sorted[index];
      while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], point) <= 0) upper.pop();
      upper.push(point);
    }
    lower.pop();
    upper.pop();
    return lower.concat(upper);
  }

  /* ------------------------------------------------------------------ */
  /* Line chart: VSWR vs frequency                                      */
  /* ------------------------------------------------------------------ */
  function drawLineChart(canvas, data) {
    const { ctx, w, h } = setupCanvas(canvas);
    const pts = (data && data.points) || [];
    if (!pts.length) return;
    const padL = 42, padR = 14, padT = 14, padB = 26;
    const fmin = pts[0].f_mhz, fmax = pts[pts.length - 1].f_mhz;
    let vmax = 3.0;
    for (const p of pts) vmax = Math.max(vmax, p.vswr);
    vmax = Math.min(10, Math.max(3, vmax));
    const x = (f) => padL + (f - fmin) / Math.max(1e-9, fmax - fmin) * (w - padL - padR);
    const y = (v) => h - padB - (Math.min(v, vmax) - 1) / Math.max(0.1, vmax - 1) * (h - padT - padB);

    // background grid
    ctx.strokeStyle = "rgba(148,163,184,.10)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const yy = padT + i * (h - padT - padB) / 4;
      ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(w - padR, yy); ctx.stroke();
    }
    // region
    if (data.low_mhz && data.high_mhz) {
      ctx.fillStyle = "rgba(34, 211, 238, .10)";
      ctx.fillRect(x(data.low_mhz), padT, Math.max(0, x(data.high_mhz) - x(data.low_mhz)), h - padT - padB);
      ctx.strokeStyle = "rgba(34, 211, 238, .35)";
      ctx.setLineDash([3, 3]);
      ctx.beginPath(); ctx.moveTo(x(data.low_mhz), padT); ctx.lineTo(x(data.low_mhz), h - padB); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x(data.high_mhz), padT); ctx.lineTo(x(data.high_mhz), h - padB); ctx.stroke();
      ctx.setLineDash([]);
    }
    // limit
    const limit = data.vswr_limit || 2;
    ctx.strokeStyle = "rgba(251, 191, 36, .5)";
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(padL, y(limit)); ctx.lineTo(w - padR, y(limit)); ctx.stroke();
    ctx.setLineDash([]);
    // curve
    ctx.beginPath();
    pts.forEach((p, i) => {
      const px = x(p.f_mhz), py = y(p.vswr);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    });
    const grad = ctx.createLinearGradient(0, padT, 0, h - padB);
    grad.addColorStop(0, "#22d3ee");
    grad.addColorStop(1, "#2dd4bf");
    ctx.strokeStyle = grad;
    ctx.lineWidth = 2.1;
    ctx.lineJoin = "round";
    ctx.stroke();
    // area
    ctx.lineTo(x(pts[pts.length - 1].f_mhz), h - padB);
    ctx.lineTo(x(pts[0].f_mhz), h - padB);
    ctx.closePath();
    const area = ctx.createLinearGradient(0, padT, 0, h - padB);
    area.addColorStop(0, "rgba(34, 211, 238, .14)");
    area.addColorStop(1, "rgba(34, 211, 238, 0)");
    ctx.fillStyle = area;
    ctx.fill();
    // axes labels
    ctx.fillStyle = "rgba(139,160,189,.85)";
    ctx.font = FONT_SMALL;
    ctx.textAlign = "right";
    for (const v of [1, 1.5, 2, 3]) {
      if (v > vmax) continue;
      ctx.fillText(String(v), padL - 6, y(v) + 3);
    }
    ctx.textAlign = "center";
    ctx.fillText(`${fmin.toFixed(0)} MHz`, padL, h - 8);
    ctx.textAlign = "right";
    ctx.fillText(`${fmax.toFixed(0)} MHz`, w - padR, h - 8);
    if (data.mark_mhz) {
      const px = x(data.mark_mhz);
      ctx.strokeStyle = "rgba(167, 139, 250, .5)";
      ctx.beginPath(); ctx.moveTo(px, padT); ctx.lineTo(px, h - padB); ctx.stroke();
    }
  }

  /* ------------------------------------------------------------------ */
  /* Horizontal bar chart                                               */
  /* ------------------------------------------------------------------ */
  function drawBars(canvas, items, options = {}) {
    const { ctx, w, h } = setupCanvas(canvas);
    const list = items || [];
    if (!list.length) return;
    const valueKey = options.valueKey || "value";
    const labelKey = options.labelKey || "label";
    const unit = options.unit || "";
    const maxVal = Math.max(1e-9, ...list.map((d) => Number(d[valueKey]) || 0));
    const rowH = Math.max(18, Math.min(34, (h - 16) / list.length));
    const padL = options.padLeft || 72;
    const padR = 54;
    const barMax = Math.max(20, w - padL - padR);
    ctx.font = FONT_SMALL;
    list.forEach((d, i) => {
      const yy = 14 + i * rowH;
      const value = Number(d[valueKey]) || 0;
      const bw = Math.max(2, (value / maxVal) * barMax);
      ctx.fillStyle = "rgba(139,160,189,.8)";
      ctx.textAlign = "right";
      ctx.fillText(String(d[labelKey] || ""), padL - 7, yy + rowH * 0.55);
      const gradient = ctx.createLinearGradient(padL, 0, padL + bw, 0);
      const color = options.colorFn ? options.colorFn(d) : "#22d3ee";
      gradient.addColorStop(0, color);
      gradient.addColorStop(1, color + "55");
      ctx.fillStyle = "rgba(148,163,184,.08)";
      roundRect(ctx, padL, yy + 3, barMax, Math.max(5, rowH - 9), 4);
      ctx.fill();
      ctx.fillStyle = gradient;
      roundRect(ctx, padL, yy + 3, bw, Math.max(5, rowH - 9), 4);
      ctx.fill();
      ctx.fillStyle = "rgba(232,240,252,.85)";
      ctx.textAlign = "left";
      const txt = options.format ? options.format(value, d) : `${value.toFixed(1)}${unit}`;
      ctx.fillText(txt, padL + bw + 6, yy + rowH * 0.55);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Generic numeric series chart                                        */
  /* ------------------------------------------------------------------ */
  function drawSeries(canvas, series, options = {}) {
    const { ctx, w, h } = setupCanvas(canvas);
    const list = (series || []).filter((item) => item && item.points && item.points.length);
    if (!list.length) return;
    const padL = options.padLeft || 52;
    const padR = 18;
    const padT = 26;
    const padB = 34;
    let xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity;
    for (const item of list) {
      for (const point of item.points) {
        const x = Number(point.x), y = Number(point.y);
        if (!isFinite(x) || !isFinite(y)) continue;
        xmin = Math.min(xmin, x); xmax = Math.max(xmax, x);
        ymin = Math.min(ymin, y); ymax = Math.max(ymax, y);
      }
    }
    if (!isFinite(xmin) || !isFinite(ymin)) return;
    if (xmax - xmin < 1e-12) { xmax = xmin + 1; xmin -= 1; }
    if (ymax - ymin < 1e-12) { ymax = ymin + 1; ymin = Math.max(0, ymin - 1); }
    const padY = (ymax - ymin) * 0.08;
    ymin = Math.max(0, ymin - padY);
    ymax += padY;
    const x = (value) => padL + (value - xmin) / (xmax - xmin) * (w - padL - padR);
    const y = (value) => h - padB - (value - ymin) / Math.max(1e-12, ymax - ymin) * (h - padT - padB);

    ctx.strokeStyle = "rgba(148,163,184,.10)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const yy = padT + i * (h - padT - padB) / 4;
      ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(w - padR, yy); ctx.stroke();
      const value = ymax - i * (ymax - ymin) / 4;
      ctx.fillStyle = "rgba(139,160,189,.8)";
      ctx.font = FONT_SMALL;
      ctx.textAlign = "right";
      ctx.fillText(value.toFixed(value >= 100 ? 0 : 1), padL - 6, yy + 3);
    }
    ctx.fillStyle = "rgba(139,160,189,.85)";
    ctx.font = FONT_SMALL;
    ctx.textAlign = "left";
    ctx.fillText(options.yLabel || "", 8, 14);
    ctx.textAlign = "center";
    ctx.fillText(`${xmin.toFixed(1)}`, padL, h - 10);
    ctx.textAlign = "right";
    ctx.fillText(`${xmax.toFixed(1)} ${options.xLabel || ""}`, w - padR, h - 10);

    list.forEach((item, index) => {
      const color = item.color || PALETTE[index % PALETTE.length];
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.1;
      ctx.lineJoin = "round";
      ctx.beginPath();
      item.points.forEach((point, pointIndex) => {
        const px = x(Number(point.x));
        const py = y(Math.min(Number(point.y), ymax));
        if (pointIndex === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      });
      ctx.stroke();
      ctx.fillStyle = color;
      ctx.font = FONT_SMALL;
      ctx.textAlign = "right";
      ctx.fillText(item.label || "", w - padR, 14);
    });
  }

  window.SmithChart = SmithChart;
  window.ChartKit = { drawLineChart, drawBars, drawSeries, PALETTE };
})();
