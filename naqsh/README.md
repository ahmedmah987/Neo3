# Naqsh (نقش)

An Islamic geometric star-pattern generator using the "polygons in contact" method.

- **Page:** https://claude.ai/artifact/XgxPpEAEcJ3r4C1QSgLEzP
- **Locally:** open `index.html` in a desktop browser; no server needed.

## The idea

Start with a tiling of regular polygons. From the midpoint of every edge, two lines leave in an X, each making the contact angle θ with the edge. Each line runs into its polygon until it meets the line from the neighbouring edge, and a star appears inside every polygon. Because both lines pass straight through the midpoint, the stars of neighbouring polygons join into one continuous network.

In a regular polygon, the two rays heading toward the same vertex meet on the line from the centre to that vertex (by symmetry), so one intersection per vertex is enough.

**Interlacing:** at every edge midpoint, the ray heading "forward" (counter-clockwise around its polygon) passes over. Walking along any band, the crossings alternate: over at one midpoint, under at the next. Neighbouring polygons always agree, because their forward rays lie on the same line.

## Files

| File | Contents |
|---|---|
| `geometry.js` | The eight tilings (`4.4.4.4` · `6.6.6` · `3.6.3.6` · `3.4.6.4` · `4.8.8` · `3.12.12` · `4.6.12` · `3.3.4.3.4`) and `motif`, Hankin's construction on one polygon |
| `index.html` | The interface: canvas drawing, controls and live tiling thumbnails |
| `check.mjs` | Mathematical checks of the tilings and the construction |

## Checks

```sh
node naqsh/check.mjs
```

Verifies that every edge is shared by exactly two polygons with opposite orientation, the angles around every vertex sum to 360°, the polygons of one cell fill exactly the cell's area, the rays cross every edge midpoint on one line, and every star tip lies inside its polygon.

## References

- E. H. Hankin, *The Drawing of Geometric Patterns in Saracenic Art*, Memoirs of the Archaeological Survey of India, 1925.
- Craig S. Kaplan, *Islamic Star Patterns from Polygons in Contact*, Graphics Interface 2005.
