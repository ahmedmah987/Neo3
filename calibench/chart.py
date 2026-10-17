"""A chart of where the true answers fell, as a standalone SVG with no dependencies."""
from xml.sax.saxutils import escape

from .scoring import BIN_SHARES

LABELS = ("below the 90%", "lower 90% band", "lower 50% band", "upper 50% band", "upper 90% band", "above the 90%")
COLOURS = {"expected": "#9e9e9e", "instinct": "#8ab4f8", "worked": "#1a73e8"}
TEXT = "#808080"                       # readable on light and dark backgrounds


def calibration_svg(report):
    """Grouped bars: the share of true answers in each of the six bins, expected against observed."""
    series = {"expected": list(BIN_SHARES)}
    for phase in ("instinct", "worked"):
        fell = report["phases"][phase].get("fell")
        if fell and fell["n"]:
            series[phase] = [count / fell["n"] for count in fell["bins"]]
    width, height, left, right, top, bottom = 660, 320, 48, 12, 52, 54
    plot_w, plot_h = width - left - right, height - top - bottom
    peak = max(max(values) for values in series.values())
    ceiling = max(0.3, -(-peak * 10 // 1) / 10)                     # round up to the next 10%

    def y(share):
        return top + plot_h * (1 - share / ceiling)

    group = plot_w / 6
    bar = group * 0.8 / len(series)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
           f'font-family="sans-serif" font-size="12">',
           f'<text x="{left}" y="18" fill="{TEXT}" font-size="14">Where the true answers fell: '
           f'{escape(report["meta"]["model"])}</text>']
    for i, name in enumerate(series):                               # legend
        x = left + i * 130
        out.append(f'<rect x="{x}" y="28" width="12" height="12" fill="{COLOURS[name]}"/>'
                   f'<text x="{x + 17}" y="38" fill="{TEXT}">{name}</text>')
    step = 0.1
    level = 0.0
    while level <= ceiling + 1e-9:                                  # grid and axis labels
        out.append(f'<line x1="{left}" x2="{width - right}" y1="{y(level):.1f}" y2="{y(level):.1f}" '
                   f'stroke="{TEXT}" stroke-opacity="0.25"/>'
                   f'<text x="{left - 6}" y="{y(level) + 4:.1f}" fill="{TEXT}" text-anchor="end">{level:.0%}</text>')
        level += step
    for b, label in enumerate(LABELS):
        x0 = left + b * group + group * 0.1
        for s, (name, values) in enumerate(series.items()):
            x = x0 + s * bar
            out.append(f'<rect x="{x:.1f}" y="{y(values[b]):.1f}" width="{bar - 1:.1f}" '
                       f'height="{y(0) - y(values[b]):.1f}" fill="{COLOURS[name]}"><title>{name}: {values[b]:.0%}'
                       f'</title></rect>')
        out.append(f'<text x="{left + (b + 0.5) * group:.1f}" y="{height - bottom + 18}" fill="{TEXT}" '
                   f'text-anchor="middle">{label}</text>')
    out.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 12}" fill="{TEXT}" text-anchor="middle">'
               f'Where the true answer fell against the stated estimate and intervals. Grey is a calibrated model.</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"
