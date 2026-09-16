#!/usr/bin/env python3
"""Build the self-hosted Font Awesome subset for dcinsuranceagency.com.

Input:  icons.json (from inventory.py) and the three FA 6.5.0 woff2 files
        downloaded next to this script from
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/webfonts/
        (fa-solid-900, fa-regular-400, fa-brands-400). inventory.py also needs
        that release's css/all.min.css beside it.
Usage:  python3 inventory.py <repo>  then  python3 build.py <N> <repo>/fonts
        Bump N whenever the icon set changes (fonts/ is cached immutable),
        append fa-subset.css to styles.css in place of the old block, and bump
        the styles.css?v= query on every page.
Output: fonts/fa-solid-sub.v<N>.woff2, fonts/fa-regular-sub.v<N>.woff2,
        fonts/fa-brands-sub.v<N>.woff2 and fa-subset.css (the CSS block to
        append to styles.css).
Every requested codepoint is verified present in the output cmap; the build
fails loudly if one is missing.
"""
import json, os, sys, subprocess
from fontTools.ttLib import TTFont

here = os.path.dirname(os.path.abspath(__file__))
ver = sys.argv[1] if len(sys.argv) > 1 else '1'
out_fonts = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'out')
os.makedirs(out_fonts, exist_ok=True)
icons = json.load(open(os.path.join(here, 'icons.json')))

fonts = {
    'solid':   ('fa-solid-900.woff2',   '"Font Awesome 6 Free"',   900),
    'regular': ('fa-regular-400.woff2', '"Font Awesome 6 Free"',   400),
    'brands':  ('fa-brands-400.woff2',  '"Font Awesome 6 Brands"', 400),
}
css = ['/* Font Awesome 6.5.0 self-hosted subset, built by tools/fa-subset/build.py. '
       'Icons not in the subset render blank: re-run the build after adding a new fa-* class. */']
for style, (src, family, weight) in fonts.items():
    cps = sorted(set(icons[style].values()))
    if not cps:
        continue
    dst = os.path.join(out_fonts, f'fa-{style}-sub.v{ver}.woff2')
    subprocess.run(['pyftsubset', os.path.join(here, src),
                    '--unicodes=' + ','.join('U+' + c for c in cps),
                    '--flavor=woff2', '--no-hinting', '--desubroutinize',
                    '--layout-features=', '--name-IDs=1,2', '--output-file=' + dst], check=True)
    cmap = TTFont(dst).getBestCmap()
    missing = [n for n, c in icons[style].items() if int(c, 16) not in cmap]
    if missing:
        sys.exit(f'MISSING glyphs in {style}: {missing}')
    print(style, len(cps), 'glyphs', os.path.getsize(dst), 'bytes')
    css.append(f'@font-face{{font-family:{family};font-style:normal;font-weight:{weight};font-display:swap;'
               f'src:url(/fonts/fa-{style}-sub.v{ver}.woff2) format("woff2")}}')

# Core rules, copied from FA 6.5.0 all.min.css, trimmed to what the site uses.
css.append('.fa,.fa-brands,.fa-regular,.fa-solid,.fab,.far,.fas{-moz-osx-font-smoothing:grayscale;'
           '-webkit-font-smoothing:antialiased;display:var(--fa-display,inline-block);font-style:normal;'
           'font-variant:normal;line-height:1;text-rendering:auto}')
css.append('.fa,.fa-solid,.fas{font-family:"Font Awesome 6 Free";font-weight:900}')
css.append('.fa-regular,.far{font-family:"Font Awesome 6 Free";font-weight:400}')
css.append('.fa-brands,.fab{font-family:"Font Awesome 6 Brands";font-weight:400}')
css.append('.fa-fw{text-align:center;width:1.25em}.fa-lg{font-size:1.25em;line-height:.05em;vertical-align:-.075em}')
names = {}
for style in fonts:
    for n, c in icons[style].items():
        names.setdefault(c, set()).add(n)
for c in sorted(names):
    sel = ','.join(f'.fa-{n}:before' for n in sorted(names[c]))
    css.append(f'{sel}{{content:"\\{c}"}}')
open(os.path.join(here, 'fa-subset.css'), 'w').write('\n'.join(css) + '\n')
print('css bytes', os.path.getsize(os.path.join(here, 'fa-subset.css')))
