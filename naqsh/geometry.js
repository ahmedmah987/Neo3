/* Naqsh geometry: Archimedean tilings + Hankin's "polygons in contact" method.
   Loads as a plain <script> in the browser and as an import in Node; both expose globalThis.Naqsh. */
(function (root) {
  'use strict';

  const S2 = Math.SQRT2, S3 = Math.sqrt(3), RAD = Math.PI / 180;

  // Regular n-gon with unit edge, vertices counter-clockwise, first vertex at angle `deg`.
  function ngon(c, n, deg) {
    const R = 1 / (2 * Math.sin(Math.PI / n)), pts = [];
    for (let k = 0; k < n; k++) {
      const a = (deg + 360 * k / n) * RAD;
      pts.push([c[0] + R * Math.cos(a), c[1] + R * Math.sin(a)]);
    }
    return pts;
  }
  // Same polygon, placed by the direction of its first edge's midpoint instead.
  const byMid = (c, n, deg) => ngon(c, n, deg - 180 / n);
  const lin = (p, s, q = [0, 0], t = 0) => [p[0] * s + q[0] * t, p[1] * s + q[1] * t];
  const O = [0, 0];

  // Hexagonal-lattice tilings put one big polygon at the origin, polygons on the three
  // lattice half-steps (between neighbours) and two at the centroids of the lattice triangles.
  function hexLattice(L) { return { a: [L, 0], b: [L / 2, L * S3 / 2] }; }

  // Each tiling: lattice vectors a, b and the polygons of one translational cell (unit edge).
  const TILINGS = [
    { id: '4.4.4.4', a: [1, 0], b: [0, 1],
      cell: () => [byMid([0.5, 0.5], 4, 0)] },

    { id: '6.6.6', ...hexLattice(S3),
      cell: () => [byMid(O, 6, 0)] },

    { id: '3.6.3.6', a: [2, 0], b: [1, S3],
      cell: () => [ngon(O, 6, 0), ngon([1, S3 / 3], 3, 270), ngon([2, 2 * S3 / 3], 3, 90)] },

    { id: '3.4.6.4', ...hexLattice(1 + S3),
      cell() {
        const { a, b } = this, c1 = lin(a, 1 / 3, b, 1 / 3), c2 = lin(a, 2 / 3, b, 2 / 3);
        return [byMid(O, 6, 0),
          byMid(lin(a, 0.5), 4, 0), byMid(lin(b, 0.5), 4, 60), byMid(lin(b, 0.5, a, -0.5), 4, 120),
          ngon(c1, 3, 210), ngon(c2, 3, 30)];
      } },

    { id: '4.8.8', a: [1 + S2, 0], b: [0, 1 + S2],
      cell: () => { const h = (1 + S2) / 2; return [byMid(O, 8, 0), ngon([h, h], 4, 0)]; } },

    { id: '3.12.12', ...hexLattice(2 + S3),
      cell() {
        const { a, b } = this;
        return [byMid(O, 12, 0), byMid(lin(a, 1 / 3, b, 1 / 3), 3, 210), byMid(lin(a, 2 / 3, b, 2 / 3), 3, 30)];
      } },

    { id: '4.6.12', ...hexLattice(3 + S3),
      cell() {
        const { a, b } = this;
        return [byMid(O, 12, 0),
          byMid(lin(a, 0.5), 4, 0), byMid(lin(b, 0.5), 4, 60), byMid(lin(b, 0.5, a, -0.5), 4, 120),
          byMid(lin(a, 1 / 3, b, 1 / 3), 6, 30), byMid(lin(a, 2 / 3, b, 2 / 3), 6, 30)];
      } },

    // Snub square: squares twisted ±15° meet corner to corner; a triangle sits on every square edge.
    { id: '3.3.4.3.4', a: [Math.sqrt(2 + S3), 0], b: [0, Math.sqrt(2 + S3)],
      cell() {
        const p = this.a[0], out = [ngon(O, 4, 30), ngon([p / 2, p / 2], 4, 60)];
        for (let k = 0; k < 4; k++) {
          const d = (75 + 90 * k) * RAD, r = 0.5 + S3 / 6;
          out.push(ngon([r * Math.cos(d), r * Math.sin(d)], 3, 75 + 90 * k));
        }
        return out;
      } },
  ];

  const byId = {};
  for (const t of TILINGS) {
    t.polys = t.cell();
    t.area = Math.abs(t.a[0] * t.b[1] - t.a[1] * t.b[0]);
    byId[t.id] = t;
  }

  // All polygons of tiling `t` whose cell lies near the world rectangle [x0,x1] x [y0,y1].
  function polygonsIn(t, x0, y0, x1, y1, margin = 2) {
    const { a, b } = t, det = a[0] * b[1] - a[1] * b[0];
    let i0 = Infinity, i1 = -Infinity, j0 = Infinity, j1 = -Infinity;
    for (const [x, y] of [[x0, y0], [x1, y0], [x0, y1], [x1, y1]]) {
      const i = (x * b[1] - y * b[0]) / det, j = (a[0] * y - a[1] * x) / det;
      i0 = Math.min(i0, i); i1 = Math.max(i1, i); j0 = Math.min(j0, j); j1 = Math.max(j1, j);
    }
    const out = [];
    for (let i = Math.floor(i0) - margin; i <= Math.ceil(i1) + margin; i++) {
      for (let j = Math.floor(j0) - margin; j <= Math.ceil(j1) + margin; j++) {
        const dx = i * a[0] + j * b[0], dy = i * a[1] + j * b[1];
        for (const poly of t.polys) out.push(poly.map(([x, y]) => [x + dx, y + dy]));
      }
    }
    return out;
  }

  // Hankin's method on one regular polygon. From each edge midpoint two rays leave at the
  // contact angle θ; the ray heading toward a vertex meets its mirror image from the next
  // edge on the line joining the centre to that vertex. Returns, per edge i:
  //   mids[i]  the edge midpoint
  //   fwd[i]   unit direction of the ray from mids[i] toward vertex i+1
  //   tips[i]  where that ray meets the ray coming back from mids[i+1]
  //   len[i]   distance from mids[i] to tips[i]
  // so mids[0], tips[0], mids[1], tips[1], ... traces the star inside the polygon.
  function motif(poly, theta) {
    const n = poly.length, c = Math.cos(theta), s = Math.sin(theta);
    let cx = 0, cy = 0;
    for (const [x, y] of poly) { cx += x; cy += y; }
    cx /= n; cy /= n;
    const mids = [], fwd = [], tips = [], len = [];
    for (let i = 0; i < n; i++) {
      const p = poly[i], q = poly[(i + 1) % n];
      let ux = q[0] - p[0], uy = q[1] - p[1];
      const d = Math.hypot(ux, uy); ux /= d; uy /= d;
      const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
      const fx = c * ux - s * uy, fy = s * ux + c * uy;   // edge direction turned θ toward the interior
      const vx = q[0] - cx, vy = q[1] - cy;
      const t = ((cx - mx) * vy - (cy - my) * vx) / (fx * vy - fy * vx);
      mids.push([mx, my]); fwd.push([fx, fy]); tips.push([mx + t * fx, my + t * fy]); len.push(t);
    }
    return { mids, fwd, tips, len };
  }

  root.Naqsh = { TILINGS, byId, polygonsIn, motif };
})(typeof globalThis !== 'undefined' ? globalThis : this);
