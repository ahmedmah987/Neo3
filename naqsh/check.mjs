// Geometry checks for Naqsh. Run with: node naqsh/check.mjs
import './geometry.js';

const { TILINGS, polygonsIn, motif } = globalThis.Naqsh;
const EPS = 1e-6;
let failures = 0;
const fail = (msg) => { failures++; console.log('  FAIL ' + msg); };
const key = (p) => `${Math.round(p[0] / EPS)},${Math.round(p[1] / EPS)}`;
const signedArea = (poly) => poly.reduce((s, p, i) => {
  const q = poly[(i + 1) % poly.length];
  return s + (p[0] * q[1] - q[0] * p[1]) / 2;
}, 0);
const inside = (pt, poly) => {          // strict containment for a convex CCW polygon
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i], q = poly[(i + 1) % poly.length];
    if ((q[0] - p[0]) * (pt[1] - p[1]) - (q[1] - p[1]) * (pt[0] - p[0]) <= EPS) return false;
  }
  return true;
};

for (const t of TILINGS) {
  console.log(t.id);
  const R = 3, polys = polygonsIn(t, -R * 2, -R * 2, R * 2, R * 2);
  const near = (p) => Math.abs(p[0]) < R && Math.abs(p[1]) < R;

  // 1. Unit edges, counter-clockwise, and one cell's polygons exactly fill the cell.
  for (const poly of polys) {
    if (signedArea(poly) <= 0) fail('polygon is not counter-clockwise');
    poly.forEach((p, i) => {
      const q = poly[(i + 1) % poly.length];
      if (Math.abs(Math.hypot(q[0] - p[0], q[1] - p[1]) - 1) > EPS) fail('edge length != 1');
    });
  }
  const cellArea = t.polys.reduce((s, p) => s + signedArea(p), 0);
  if (Math.abs(cellArea - t.area) > EPS) fail(`cell area ${cellArea} != lattice area ${t.area}`);

  // 2. Every edge near the origin is shared by exactly two polygons, traversed in opposite directions.
  const edges = new Map();
  polys.forEach((poly, pi) => poly.forEach((p, i) => {
    const q = poly[(i + 1) % poly.length], m = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
    const k = key(m);
    if (!edges.has(k)) edges.set(k, []);
    edges.get(k).push({ pi, i, m, dir: [q[0] - p[0], q[1] - p[1]] });
  }));
  for (const list of edges.values()) {
    if (!near(list[0].m)) continue;
    if (list.length !== 2) { fail(`edge at ${list[0].m} shared by ${list.length} polygons`); continue; }
    const [e, f] = list;
    if (Math.abs(e.dir[0] + f.dir[0]) > EPS || Math.abs(e.dir[1] + f.dir[1]) > EPS) fail('shared edge not opposite');
  }

  // 3. Interior angles around every vertex near the origin add up to a full turn.
  const corners = new Map();
  for (const poly of polys) {
    const n = poly.length, ang = Math.PI * (n - 2) / n;
    for (const p of poly) if (near(p)) corners.set(key(p), (corners.get(key(p)) || 0) + ang);
  }
  for (const [k, sum] of corners) if (Math.abs(sum - 2 * Math.PI) > 1e-9) fail(`vertex ${k} angle sum ${sum}`);

  // 4. Hankin's construction: at each shared midpoint the two polygons' forward rays lie on one
  //    line pointing opposite ways (so lines run straight through, and "forward is over" is consistent),
  //    and every star tip lies inside its polygon.
  for (const deg of [12, 30, 45, 60, 72, 85]) {
    const th = deg * Math.PI / 180, motifs = polys.map((p) => motif(p, th));
    for (const list of edges.values()) {
      if (list.length !== 2 || !near(list[0].m)) continue;
      const [e, f] = list, a = motifs[e.pi].fwd[e.i], b = motifs[f.pi].fwd[f.i];
      if (Math.abs(a[0] + b[0]) > EPS || Math.abs(a[1] + b[1]) > EPS) fail(`θ=${deg}: rays not collinear`);
    }
    polys.forEach((poly, pi) => {
      if (!near(poly[0])) return;
      motifs[pi].tips.forEach((tip, i) => {
        if (!inside(tip, poly)) fail(`θ=${deg}: tip outside its ${poly.length}-gon`);
        if (!(motifs[pi].len[i] > 0)) fail(`θ=${deg}: non-positive ray length`);
      });
    });
  }
  console.log(`  ${t.polys.length} polygons per cell, ${corners.size} vertices checked`);
}

console.log(failures ? `\n${failures} failure(s)` : '\nall checks passed');
process.exit(failures ? 1 : 0);
