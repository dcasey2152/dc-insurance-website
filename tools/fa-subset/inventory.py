#!/usr/bin/env python3
"""Inventory Font Awesome icon usage across the site.

Parses every class attribute in every HTML file, decides the style
(solid / regular / brands) per element from its prefix classes, maps
icon names to codepoints from FA's all.min.css, and reports coverage.
Writes fa/icons.json: {"solid": {...name: cp}, "regular": {...}, "brands": {...},
"helpers": [...]}.
"""
import json, os, re, sys, glob

repo = sys.argv[1]
css = open(os.path.join(os.path.dirname(__file__), 'all.min.css'), encoding='utf-8').read()

# FA 6.5 css: .fa-name{--fa:"\f0e0"}  and sometimes several selectors share a rule
cp = {}
for sel, body in re.findall(r'((?:\.fa-[a-z0-9-]+:before,?)+)\{content:"\\([0-9a-f]+)"', css):
    for name in re.findall(r'\.fa-([a-z0-9-]+)', sel):
        cp.setdefault(name, body)
print('codepoints known:', len(cp))

STYLE_PREFIX = {'fa-solid': 'solid', 'fas': 'solid', 'fa': 'solid',
                'fa-regular': 'regular', 'far': 'regular',
                'fa-brands': 'brands', 'fab': 'brands'}
HELPERS = {'fa-fw', 'fa-lg', 'fa-xs', 'fa-sm', 'fa-xl', 'fa-2x', 'fa-3x', 'fa-4x', 'fa-5x',
           'fa-spin', 'fa-pulse', 'fa-2xs', 'fa-2xl', 'fa-flip-horizontal', 'fa-rotate-90',
           'fa-inverse', 'fa-li', 'fa-ul', 'fa-stack', 'fa-beat', 'fa-fade', 'fa-bounce', 'fa-shake'}

used = {'solid': {}, 'regular': {}, 'brands': {}}
helpers = set()
unknown = []
files = [f for f in glob.glob(os.path.join(repo, '**', '*.html'), recursive=True) if '/.git/' not in f]
for f in files:
    html = open(f, encoding='utf-8', errors='replace').read()
    for cls in re.findall(r'class="([^"]*)"', html):
        toks = cls.split()
        styles = [STYLE_PREFIX[t] for t in toks if t in STYLE_PREFIX]
        icons = [t for t in toks if t.startswith('fa-') and t not in HELPERS and t not in STYLE_PREFIX]
        helpers.update(t for t in toks if t in HELPERS)
        if not icons:
            continue
        if not styles:
            unknown.append((os.path.relpath(f, repo), cls, 'no style prefix'))
            continue
        # fa-solid/fa-regular/fa-brands explicit wins over bare 'fa'
        style = next((s for t, s in ((t, STYLE_PREFIX.get(t)) for t in toks) if t not in ('fa',) and s), styles[0])
        for ic in icons:
            name = ic[3:]
            if name not in cp:
                unknown.append((os.path.relpath(f, repo), cls, 'unknown icon ' + name))
                continue
            used[style].setdefault(name, cp[name])

for s in used:
    print(s, len(used[s]), sorted(used[s]))
print('helpers', sorted(helpers))
print('problems', len(unknown))
for u in unknown[:40]:
    print('  ', u)
json.dump({'solid': used['solid'], 'regular': used['regular'], 'brands': used['brands'],
           'helpers': sorted(helpers)}, open(os.path.join(os.path.dirname(__file__), 'icons.json'), 'w'), indent=1)
