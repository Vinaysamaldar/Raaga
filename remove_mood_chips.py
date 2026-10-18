# -*- coding: utf-8 -*-
"""
remove_mood_chips.py
Removes the Mood Chips row from Screen 1: Home
"""

import os

FILE_PATH = os.path.join('mobile', 'web_preview', 'index.html')

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove HTML
old_html = '''        <!-- Mood Chips Row -->
        <div class="chips-scroll" id="homeMoodChips"></div>'''

if old_html in text:
    text = text.replace(old_html, '', 1)
    print('Removed Mood Chips HTML row.')
else:
    # Try finding <div class="chips-scroll" id="homeMoodChips"></div>
    target = '<div class="chips-scroll" id="homeMoodChips"></div>'
    if target in text:
        text = text.replace(target, '', 1)
        print('Removed homeMoodChips div.')

# 2. Update JS to guard or bypass homeMoodChips
old_js = '''      document.getElementById('homeMoodChips').innerHTML = MOOD_CHIPS.map(m => `
        <button class="pill-chip ${state.moodFilter === m.id ? 'active' : ''}" onclick="filterByMood('${m.id}')">${m.label}</button>
      `).join('');'''

new_js = '''      const moodEl = document.getElementById('homeMoodChips');
      if (moodEl) {
        moodEl.innerHTML = MOOD_CHIPS.map(m => `
          <button class="pill-chip ${state.moodFilter === m.id ? 'active' : ''}" onclick="filterByMood('${m.id}')">${m.label}</button>
        `).join('');
      }'''

if old_js in text:
    text = text.replace(old_js, new_js, 1)
    print('Updated JS to safely guard homeMoodChips.')

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated index.html successfully.')
