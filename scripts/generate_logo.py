# -*- coding: utf-8 -*-
"""
Cerca - Vector Logo Generator
Produces a pixel-perfect, font-independent SVG logo using pure vector paths.
"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.transformPen import TransformPen

font = TTFont('Outfit.ttf')
cmap = font['cmap'].getBestCmap()

# 1. cerca brand wordmark
font_bold = instantiateVariableFont(font, {'wght': 850})
glyph_set_bold = font_bold.getGlyphSet()
hmtx_bold = font_bold['hmtx']

def get_path(glyph_set, hmtx, word, font_size, start_x, baseline_y, letter_spacing=0):
    scale = font_size / 1000.0
    x = start_x
    cmds = []
    for ch in word:
        gname = cmap.get(ord(ch), ch)
        glyph = glyph_set[gname]
        adv, _ = hmtx[gname]
        pen = SVGPathPen(glyph_set)
        tpen = TransformPen(pen, (scale, 0, 0, -scale, x, baseline_y))
        glyph.draw(tpen)
        c = pen.getCommands().strip()
        if c:
            cmds.append(c)
        x += (adv + letter_spacing) * scale
    return ' '.join(cmds), x

cerca_path, cerca_end = get_path(glyph_set_bold, hmtx_bold, 'cerca', 33.0, 56.0, 34.5, 0)

# 2. Tagline
font_sub = instantiateVariableFont(font, {'wght': 650})
glyph_set_sub = font_sub.getGlyphSet()
hmtx_sub = font_sub['hmtx']

dot_cx = round(cerca_end + 6.0, 1)
dot_cy = 32.5
dot_r = 3.8

divider_x = round(dot_cx + 12.0, 1)
tag_start = round(divider_x + 11.0, 1)

tag1_path, tag1_end = get_path(glyph_set_sub, hmtx_sub, 'ETKİNLİK', 9.2, tag_start, 22.0, 50)
tag2_path, tag2_end = get_path(glyph_set_sub, hmtx_sub, 'REHBERİ', 9.2, tag_start, 33.5, 50)

total_w = round(max(tag1_end, tag2_end) + 12.0, 1)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} 48" width="{total_w}" height="48" fill="none">
  <defs>
    <linearGradient id="cercaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF7A00" />
      <stop offset="100%" stop-color="#FF4500" />
    </linearGradient>
    <filter id="cercaShadow" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#FF5500" flood-opacity="0.28" />
    </filter>
  </defs>

  <!-- Emblem Icon -->
  <g filter="url(#cercaShadow)">
    <rect x="4" y="4" width="40" height="40" rx="12" fill="url(#cercaGrad)" />
    <!-- Radar Waves -->
    <path d="M10 20 A 14 14 0 0 1 38 20" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity="0.4" fill="none" />
    <path d="M14 20 A 10 10 0 0 1 34 20" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" opacity="0.75" fill="none" />
    <!-- Location Pin -->
    <circle cx="24" cy="20" r="6" stroke="#FFFFFF" stroke-width="2.6" fill="none" />
    <circle cx="24" cy="20" r="2.2" fill="#FFFFFF" />
    <path d="M24 26 L24 35" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" />
  </g>

  <!-- Wordmark 'cerca' (Pure Vector Path) -->
  <path d="{cerca_path}" fill="#111827" />

  <!-- Accent Pulse Dot -->
  <circle cx="{dot_cx}" cy="{dot_cy}" r="{dot_r}" fill="#FF6000" />

  <!-- Elegant Divider -->
  <line x1="{divider_x}" y1="13" x2="{divider_x}" y2="35" stroke="#CBD5E1" stroke-width="1.5" stroke-linecap="round" />

  <!-- Subtitle Tagline (Pure Vector Path) -->
  <path d="{tag1_path}" fill="#FF6000" />
  <path d="{tag2_path}" fill="#64748B" />
</svg>
'''

with open('assets/img/cerca-logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg)
with open('docs/assets/img/cerca-logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg)

print(f"Generated logo with dimensions: {total_w}x48 (viewBox: 0 0 {total_w} 48)")
