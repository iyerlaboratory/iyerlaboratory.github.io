// Iyer Lab — microglia hero
// A ramified microglial cell drawn as a fine particle field: a lumpy soma with a
// nucleus and lysosomes, and branched processes that extend and retract as the
// cell surveys its territory. Process tips that touch drifting debris engulf it
// and carry it back to a lysosome. Moving the cursor releases a "signal" and the
// nearest processes reach toward it, the way microglia converge on an injury.
(function () {
  "use strict";

  var canvas = document.getElementById("microgliaHero");
  if (!canvas || !canvas.getContext) return;
  var stage = canvas.parentElement;
  var ctx = canvas.getContext("2d");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var TAU = Math.PI * 2;

  // ---- palette (Rice University brand colors) ----
  var INK = [0, 24, 70];       // deep shade of Rice Blue
  var NAVY = [0, 32, 91];      // Rice Blue
  var BLUE = [0, 32, 91];      // Rice Blue
  var SKY = [191, 199, 214];   // light tint of Rice Blue
  var GRAY = [124, 126, 127];  // Rice Gray
  function rgba(c, a) { return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a + ")"; }
  function mix(a, b, t) {
    return [a[0] + (b[0] - a[0]) * t | 0, a[1] + (b[1] - a[1]) * t | 0, a[2] + (b[2] - a[2]) * t | 0];
  }
  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }

  // ---- seeded random so the cell has the same shape on every visit ----
  var seed = 1792024;
  function rand() {
    seed = (seed + 0x6D2B79F5) | 0;
    var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  // All lengths are fractions of S, the stage's shorter side.
  var SOMA_R = 0.125;
  var BEAD = 0.0105;

  function makeBranch(depth, angle, len, attach) {
    var n = Math.max(3, Math.round(len / BEAD));
    var cap = Math.ceil(n * 1.8) + 2;
    var b = {
      depth: depth, angle: angle, len: len, attach: attach, n: n,
      phase: rand() * TAU, speed: 0.16 + rand() * 0.28, curl: (rand() - 0.5) * 1.5,
      ext: 0, bend: 0, jit: [], halo: [], kids: []
    };
    for (var i = 0; i < cap; i++) {
      b.jit.push(rand() - 0.5);
      b.halo.push(rand() < 0.5 ? { dx: rand() - 0.5, dy: rand() - 0.5, r: 0.35 + rand() * 0.6 } : null);
    }
    if (depth < 3) {
      var k = depth === 0 ? 2 + (rand() < 0.45 ? 1 : 0) : (rand() < 0.7 ? 2 : 1);
      for (var j = 0; j < k; j++) {
        var side = j % 2 === 0 ? -1 : 1;
        b.kids.push(makeBranch(depth + 1, side * (0.3 + rand() * 0.7), len * (0.42 + rand() * 0.3), 0.3 + rand() * 0.55));
      }
    }
    return b;
  }

  var PRIMARIES = [];
  var NP = 8;
  for (var p = 0; p < NP; p++) {
    PRIMARIES.push(makeBranch(0, (p / NP) * TAU + (rand() - 0.5) * 0.75, 0.13 + rand() * 0.09, 0));
  }

  var SOMA = [];
  for (var s = 0; s < 560; s++) {
    SOMA.push({ a: rand() * TAU, u: Math.sqrt(rand()), r: 0.55 + rand() * 1.15, al: 0.4 + rand() * 0.5, w: rand() * TAU });
  }
  var NUC = [];
  for (var q = 0; q < 96; q++) NUC.push({ a: (q / 96) * TAU, j: rand() - 0.5 });
  var LYSO = [];
  for (var l = 0; l < 9; l++) {
    LYSO.push({ a: rand() * TAU, rr: 0.5 + rand() * 0.3, r: 2.6 + rand() * 1.8, sp: (rand() < 0.5 ? -1 : 1) * (0.05 + rand() * 0.08), pulse: 0 });
  }
  var DEBRIS = [];
  function placeDebris(d, fresh) {
    var ang = rand() * TAU, rad = 0.25 + rand() * 0.18;
    d.x = Math.cos(ang) * rad; d.y = Math.sin(ang) * rad;
    d.vx = (rand() - 0.5) * 0.006; d.vy = (rand() - 0.5) * 0.006;
    d.state = "free"; d.k = 0; d.alpha = fresh ? 0 : 1;
    d.bits = [];
    var nb = 3 + (rand() * 3 | 0);
    for (var i = 0; i < nb; i++) d.bits.push({ dx: (rand() - 0.5) * 0.012, dy: (rand() - 0.5) * 0.012, r: 0.9 + rand() * 1.3 });
  }
  for (var d = 0; d < 7; d++) { var deb = {}; placeDebris(deb, false); DEBRIS.push(deb); }

  var flashes = [];
  var tips = [];

  // ---- pointer = an injury signal ----
  var pointer = { x: 0, y: 0, w: 0, active: false, until: 0 };
  function setPointer(e, hold) {
    var r = canvas.getBoundingClientRect();
    pointer.x = e.clientX - r.left; pointer.y = e.clientY - r.top;
    pointer.active = true;
    pointer.until = hold ? performance.now() + hold : 0;
  }
  if (!reduceMotion) {
    canvas.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse") setPointer(e, 0); });
    canvas.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") pointer.active = false; });
    canvas.addEventListener("pointerdown", function (e) { setPointer(e, e.pointerType === "mouse" ? 0 : 2600); });
  }
  var hint = stage.querySelector(".stage-hint");
  if (hint && window.matchMedia && window.matchMedia("(hover: none)").matches) hint.textContent = "Tap and watch the microglia respond";
  if (hint && reduceMotion) hint.hidden = true;

  // ---- sizing ----
  var W = 0, H = 0, dpr = 1;
  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = stage.clientWidth; H = stage.clientHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    if (reduceMotion) draw(14, 1);
  }

  function angDiff(a, b) {
    var d = a - b;
    while (d > Math.PI) d -= TAU;
    while (d < -Math.PI) d += TAU;
    return d;
  }

  function somaShape(a, t) {
    return 1 + 0.11 * Math.sin(3 * a + 0.7) + 0.07 * Math.sin(5 * a + 2.1 + t * 0.3) + 0.04 * Math.sin(2 * a - t * 0.25);
  }

  // ---- one branch, recursively ----
  function drawBranch(b, x, y, dir, gate, t, S, ease, cx, cy) {
    var base = 0.56 + 0.4 * (0.5 + 0.5 * Math.sin(t * b.speed + b.phase)) + 0.07 * Math.sin(t * b.speed * 2.3 + b.phase * 1.7);
    var target = base, bendT = 0;
    if (pointer.w > 0.01) {
      var pa = Math.atan2(pointer.y - cy, pointer.x - cx);
      var dd = angDiff(pa, dir);
      var g = Math.exp(-(dd * dd) / (2 * 0.42 * 0.42)) * pointer.w;
      var reach = Math.hypot(pointer.x - x, pointer.y - y) / (b.len * S);
      target += g * clamp(reach - base, 0, 0.75);
      bendT = dd * g * 0.6;
    }
    b.ext += (target - b.ext) * ease;
    b.bend += (bendT - b.bend) * ease;

    var e = clamp(b.ext, 0, 1.75) * gate;
    if (e < 0.03) return;
    var step = BEAD * S;
    var count = (b.len * S * e) / step;
    var N = Math.max(1, Math.ceil(count));
    var unit = S / 640;

    var pts = [{ x: x, y: y, a: dir }];
    var px = x, py = y;
    for (var i = 1; i <= N; i++) {
      var f = i / b.n;
      var a = dir + b.bend * Math.min(1, f) + b.curl * f + 0.2 * f * Math.sin(t * b.speed * 1.6 + i * 0.35 + b.phase);
      var len = i === N ? (count - (N - 1)) * step : step;
      px += Math.cos(a) * len; py += Math.sin(a) * len;
      pts.push({ x: px, y: py, a: a });
    }

    // thread
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
    ctx.strokeStyle = rgba(NAVY, 0.34 - b.depth * 0.04);
    ctx.lineWidth = Math.max(0.45, (1.7 - 0.38 * b.depth)) * unit;
    ctx.stroke();

    // daughter branches grow only once the parent has reached past them
    var frac = count / b.n;
    for (var k = 0; k < b.kids.length; k++) {
      var kid = b.kids[k];
      var kg = clamp((frac - kid.attach) / 0.25, 0, 1);
      var ai = kid.attach * b.n;
      if (ai > count) ai = count;
      var i0 = Math.floor(ai), i1 = Math.min(pts.length - 1, i0 + 1), ft = ai - i0;
      var P0 = pts[Math.min(i0, pts.length - 1)], P1 = pts[i1];
      drawBranch(kid, P0.x + (P1.x - P0.x) * ft, P0.y + (P1.y - P0.y) * ft, P0.a + kid.angle, gate * kg, t, S, ease, cx, cy);
    }

    // beads + fine halo dust
    for (i = b.depth === 0 ? 1 : 2; i < pts.length; i++) {
      var pf = i / pts.length;
      var nx = -Math.sin(pts[i].a), ny = Math.cos(pts[i].a);
      var off = b.jit[i] * 2.4 * unit;
      var bx = pts[i].x + nx * off, by = pts[i].y + ny * off;
      var r = Math.max(0.55, (2.5 - 0.48 * b.depth) * (1 - 0.42 * pf)) * unit;
      ctx.fillStyle = rgba(mix(NAVY, BLUE, Math.min(1, b.depth / 2.5 + pf * 0.35)), 0.88);
      ctx.beginPath(); ctx.arc(bx, by, r, 0, TAU); ctx.fill();
      var h = b.halo[i];
      if (h) {
        ctx.fillStyle = rgba(BLUE, 0.35);
        ctx.beginPath(); ctx.arc(bx + h.dx * 11 * unit, by + h.dy * 11 * unit, h.r * unit, 0, TAU); ctx.fill();
      }
    }

    // bulbous process tip
    var tp = pts[pts.length - 1];
    var tr = (2.3 - 0.32 * b.depth) * unit;
    ctx.fillStyle = rgba(SKY, 0.9);
    ctx.beginPath(); ctx.arc(tp.x, tp.y, tr * 1.25, 0, TAU); ctx.fill();
    ctx.strokeStyle = rgba(BLUE, 0.95);
    ctx.lineWidth = 0.9 * unit;
    ctx.stroke();
    if (b.kids.length === 0 || frac < 0.6) tips.push(tp);
  }

  // ---- full frame ----
  var last = 0;
  function draw(t, ease) {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    var S = Math.min(W, H);
    if (S < 10) return;
    var unit = S / 640;
    var cx = W / 2, cy = H / 2;
    var R = SOMA_R * S * (1 + 0.025 * Math.sin(t * 0.6));
    tips.length = 0;

    // injury signal rings
    if (pointer.w > 0.02) {
      for (var ring = 0; ring < 3; ring++) {
        var ph = (t * 0.55 + ring / 3) % 1;
        ctx.strokeStyle = rgba(SKY, (1 - ph) * 0.55 * pointer.w);
        ctx.lineWidth = 1.2 * unit;
        ctx.beginPath(); ctx.arc(pointer.x, pointer.y, (6 + ph * 46) * unit, 0, TAU); ctx.stroke();
      }
      ctx.fillStyle = rgba(BLUE, 0.6 * pointer.w);
      ctx.beginPath(); ctx.arc(pointer.x, pointer.y, 2.4 * unit, 0, TAU); ctx.fill();
    }

    // soft glow behind the cell body
    var gl = ctx.createRadialGradient(cx, cy, R * 0.2, cx, cy, R * 3.2);
    gl.addColorStop(0, rgba(SKY, 0.38));
    gl.addColorStop(1, rgba(SKY, 0));
    ctx.fillStyle = gl;
    ctx.beginPath(); ctx.arc(cx, cy, R * 3.2, 0, TAU); ctx.fill();

    // processes
    for (var i = 0; i < PRIMARIES.length; i++) {
      var b = PRIMARIES[i];
      var sr = R * somaShape(b.angle, t) * 0.86;
      drawBranch(b, cx + Math.cos(b.angle) * sr, cy + Math.sin(b.angle) * sr, b.angle, 1, t, S, ease, cx, cy);
    }

    // soma body
    ctx.beginPath();
    for (var a = 0; a <= 64; a++) {
      var ang = (a / 64) * TAU, rr = R * somaShape(ang, t);
      if (a === 0) ctx.moveTo(cx + Math.cos(ang) * rr, cy + Math.sin(ang) * rr);
      else ctx.lineTo(cx + Math.cos(ang) * rr, cy + Math.sin(ang) * rr);
    }
    ctx.fillStyle = rgba(BLUE, 0.1);
    ctx.fill();
    for (i = 0; i < SOMA.length; i++) {
      var sp = SOMA[i], srr = R * somaShape(sp.a, t) * sp.u;
      var wob = Math.sin(t * 0.8 + sp.w) * 0.7 * unit;
      ctx.fillStyle = rgba(mix(INK, BLUE, sp.u), sp.al);
      ctx.beginPath();
      ctx.arc(cx + Math.cos(sp.a) * srr + wob, cy + Math.sin(sp.a) * srr - wob, sp.r * unit, 0, TAU);
      ctx.fill();
    }

    // nucleus
    var nx = cx - R * 0.14, ny = cy - R * 0.1;
    for (i = 0; i < NUC.length; i++) {
      var np = NUC[i], nr = R * 0.44 * (1 + 0.08 * Math.sin(2 * np.a + 1)) + np.j * 2 * unit;
      ctx.fillStyle = rgba(SKY, 0.95);
      ctx.beginPath(); ctx.arc(nx + Math.cos(np.a) * nr, ny + Math.sin(np.a) * nr * 0.86, 1.3 * unit, 0, TAU); ctx.fill();
    }

    // lysosomes
    for (i = 0; i < LYSO.length; i++) {
      var ly = LYSO[i], la = ly.a + t * ly.sp;
      var lr = R * ly.rr * somaShape(la, t);
      var lx = cx + Math.cos(la) * lr, lyy = cy + Math.sin(la) * lr;
      var rad = ly.r * unit * (1 + 0.7 * ly.pulse);
      ctx.fillStyle = rgba(SKY, 0.95);
      ctx.beginPath(); ctx.arc(lx, lyy, rad, 0, TAU); ctx.fill();
      ctx.strokeStyle = rgba(INK, 0.9);
      ctx.lineWidth = 0.9 * unit;
      ctx.stroke();
      ly.pulse *= 0.97;
      ly.x = lx; ly.y = lyy;
    }

    // debris, and engulfment by process tips
    for (i = 0; i < DEBRIS.length; i++) {
      var d = DEBRIS[i];
      var dx, dy;
      if (d.state === "free") {
        d.alpha = Math.min(1, d.alpha + 0.01);
        d.vx += (Math.random() - 0.5) * 0.0004; d.vy += (Math.random() - 0.5) * 0.0004;
        d.vx *= 0.99; d.vy *= 0.99;
        var dist = Math.hypot(d.x, d.y);
        if (dist > 0.47) { d.vx -= d.x * 0.0004; d.vy -= d.y * 0.0004; }
        if (dist < 0.16) { d.vx += d.x * 0.0005; d.vy += d.y * 0.0005; }
        d.x += d.vx * 0.05; d.y += d.vy * 0.05;
        dx = cx + d.x * S; dy = cy + d.y * S;
        for (var tI = 0; tI < tips.length; tI++) {
          if (Math.hypot(tips[tI].x - dx, tips[tI].y - dy) < 0.022 * S && !reduceMotion) {
            d.state = "eaten"; d.k = 0; d.sx = dx; d.sy = dy; break;
          }
        }
      } else if (d.state === "eaten") {
        d.k += 0.006;
        var e = d.k < 0.5 ? 2 * d.k * d.k : 1 - Math.pow(-2 * d.k + 2, 2) / 2;
        dx = d.sx + (cx - d.sx) * e; dy = d.sy + (cy - d.sy) * e;
        if (d.k >= 1) {
          var near = LYSO[(Math.random() * LYSO.length) | 0];
          near.pulse = 1;
          flashes.push({ x: near.x, y: near.y, k: 0 });
          d.state = "gone"; d.respawn = t + 2.5;
        }
      } else {
        if (t > d.respawn) placeDebris(d, true);
        continue;
      }
      var shrink = d.state === "eaten" ? 1 - 0.6 * d.k : 1;
      ctx.fillStyle = rgba(GRAY, 0.75 * d.alpha);
      for (var bI = 0; bI < d.bits.length; bI++) {
        var bit = d.bits[bI];
        ctx.beginPath();
        ctx.arc(dx + bit.dx * S * shrink, dy + bit.dy * S * shrink, bit.r * unit * shrink, 0, TAU);
        ctx.fill();
      }
    }

    // lysosome flashes after a meal
    for (i = flashes.length - 1; i >= 0; i--) {
      var fl = flashes[i];
      fl.k += 0.02;
      if (fl.k >= 1) { flashes.splice(i, 1); continue; }
      ctx.strokeStyle = rgba(BLUE, (1 - fl.k) * 0.7);
      ctx.lineWidth = 1.1 * unit;
      ctx.beginPath(); ctx.arc(fl.x, fl.y, (3 + fl.k * 16) * unit, 0, TAU); ctx.stroke();
    }
  }

  function loop(now) {
    var dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016;
    last = now;
    if (pointer.until && now > pointer.until) { pointer.active = false; pointer.until = 0; }
    pointer.w += ((pointer.active ? 1 : 0) - pointer.w) * Math.min(1, dt * 2.4);
    draw(now / 1000, 1 - Math.pow(1 - 0.035, dt * 60));
    if (running) raf = requestAnimationFrame(loop);
  }

  var raf = 0, running = false, onScreen = true;
  function start() {
    if (running || reduceMotion || !onScreen || document.hidden) return;
    running = true; last = 0; raf = requestAnimationFrame(loop);
  }
  function stop() { running = false; cancelAnimationFrame(raf); }

  if (window.ResizeObserver) new ResizeObserver(resize).observe(stage);
  else window.addEventListener("resize", resize);
  resize();

  if (reduceMotion) {
    // Settle the cell into a still pose instead of animating.
    for (var it = 0; it < 120; it++) draw(14, 0.08);
    return;
  }
  if (window.IntersectionObserver) {
    new IntersectionObserver(function (entries) {
      onScreen = entries[0].isIntersecting;
      if (onScreen) start(); else stop();
    }).observe(stage);
  }
  document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });
  start();
})();
