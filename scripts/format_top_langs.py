#!/usr/bin/env python3
"""Rebuild profile/top-langs.svg as a 467x195 card that matches stats.svg.

Reads the languages produced by github-readme-stats (compact layout),
keeps the top 4, and writes them into a fixed-size template.
"""
import re
import sys
from html import escape

PATH = sys.argv[1] if len(sys.argv) > 1 else "profile/top-langs.svg"
BAR_WIDTH = 417
MAX_LANGS = 4

src = open(PATH, encoding="utf-8").read()

pattern = re.compile(
    r'<circle[^>]*fill="(#[0-9a-fA-F]{3,8})"[^>]*/>\s*'
    r'<text[^>]*data-testid="lang-name"[^>]*>\s*(.*?)\s*</text>',
    re.DOTALL,
)

langs = []
for color, label in pattern.findall(src):
    name, pct = label.rsplit(" ", 1)
    langs.append((name.strip(), float(pct.rstrip("%")), color))

if not langs:
    sys.exit("No languages found in " + PATH)

langs = langs[:MAX_LANGS]
total = sum(p for _, p, _ in langs) or 1

# progress bar segments
bars, x = [], 0.0
for i, (name, pct, color) in enumerate(langs):
    w = BAR_WIDTH - x if i == len(langs) - 1 else BAR_WIDTH * pct / total
    bars.append(
        f'      <rect mask="url(#rect-mask)" x="{x:.2f}" y="0" width="{w:.2f}" height="8" fill="{color}"/>'
    )
    x += w

# legend rows
rows = []
for i, (name, pct, color) in enumerate(langs):
    rows.append(f'''      <g transform="translate(0, {25 + 25 * i})">
        <g class="stagger" style="animation-delay: {450 + 150 * i}ms">
          <circle cx="5" cy="6" r="5" fill="{color}"/>
          <text x="25" y="11" class="stat bold">{escape(name)}</text>
          <text x="224" y="11" class="stat bold">{pct:.2f}%</text>
        </g>
      </g>''')

desc = ", ".join(f"{escape(n)} {p:.2f}%" for n, p, _ in langs)

svg = f'''<svg width="467" height="195" viewBox="0 0 467 195" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="titleId descId">
  <title id="titleId">Vidhaan Mathur's Most Used Languages</title>
  <desc id="descId">{desc}</desc>
  <style>
    .header {{ font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: #35F5D0; animation: fadeInAnimation 0.8s ease-in-out forwards; }}
    @supports(-moz-appearance: auto) {{ .header {{ font-size: 15.5px; }} }}
    .stat {{ font: 600 14px 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif; fill: #E8FFFB; }}
    @supports(-moz-appearance: auto) {{ .stat {{ font-size: 12px; }} }}
    .bold {{ font-weight: 700 }}
    .stagger {{ opacity: 0; animation: fadeInAnimation 0.3s ease-in-out forwards; }}
    @keyframes fadeInAnimation {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  </style>

  <rect x="0.5" y="0.5" rx="4.5" width="466" height="194" fill="#050505" stroke="#e4e2e2" stroke-opacity="0"/>

  <g transform="translate(25, 35)">
    <text x="0" y="0" class="header">Vidhaan Mathur's Most Used Languages</text>
  </g>

  <g transform="translate(0, 55)">
    <svg x="25">
      <mask id="rect-mask"><rect x="0" y="0" width="{BAR_WIDTH}" height="8" fill="white" rx="4"/></mask>
{chr(10).join(bars)}

{chr(10).join(rows)}
    </svg>
  </g>
</svg>
'''

open(PATH, "w", encoding="utf-8").write(svg)
print(f"Wrote {PATH} with {len(langs)} languages")
