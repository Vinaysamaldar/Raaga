# -*- coding: utf-8 -*-
with open('mobile/web_preview/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

checks = {
    'era-glass-bar': 'era-glass-bar' in text,
    'KANNADA MUSICAL HERITAGE': 'KANNADA MUSICAL HERITAGE' in text,
    'rail-btn-az': 'rail-btn-az' in text,
    'rail-btn-recognize': 'rail-btn-recognize' in text,
    'railOfflineBtn': 'railOfflineBtn' in text,
    'nav-btn-recognize': 'nav-btn-recognize' in text,
    'offline-slim-banner': 'offline-slim-banner' in text,
    'searchInput with Recognize button': 'switchNav(\'recognize\')' in text
}

print("VERIFICATION RESULTS:")
for k, v in checks.items():
    print(f"  {k}: {v}")
