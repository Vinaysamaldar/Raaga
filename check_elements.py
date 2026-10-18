# -*- coding: utf-8 -*-
with open('mobile/web_preview/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    line_lower = l.lower()
    if 'id="screen-recognize"' in line_lower:
        print(f"Recognize screen at line {i+1}")
    if 'id="screen-az"' in line_lower:
        print(f"A-Z screen at line {i+1}")
    if 'function switchNav' in l:
        print(f"switchNav at line {i+1}")
    if 'function triggerRecognition' in l or 'function startRecognize' in l:
        print(f"Recognition trigger at line {i+1}: {l.strip()}")
