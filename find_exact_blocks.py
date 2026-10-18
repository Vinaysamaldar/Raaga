# -*- coding: utf-8 -*-
with open('mobile/web_preview/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

def p(s):
    print(s.encode('ascii', 'replace').decode('ascii'))

# 1. Search bar block
idx1 = text.find('<!-- Big Rounded Pill Search Bar -->')
if idx1 != -1:
    p("Search bar found at " + str(idx1))
    p(text[idx1:idx1+700])

# 2. Era bar
idx2 = text.find('<!-- Era Switcher Segmented Bar')
if idx2 != -1:
    p("\nEra bar found at " + str(idx2))
    p(text[idx2:idx2+500])

# 3. Heritage block
idx3 = text.find('KANNADA MUSICAL HERITAGE (1934–2026)')
if idx3 != -1:
    p("\nHeritage block found at " + str(idx3))
    start_h = text.rfind('<div style="background:var(--surface);', 0, idx3)
    end_h = text.find('id="homeSubArchiveChips"', idx3)
    end_h_div = text.find('</div>', end_h)
    p("Heritage slice:\n" + text[start_h:end_h_div+100])
