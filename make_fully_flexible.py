# -*- coding: utf-8 -*-
"""
make_fully_flexible.py
Removes the prototype options (device-switcher-bar and prototype-guide-bar).
Makes the layout 100% fluid, edge-to-edge, and automatically responsive:
- Mobile (<600px): Fluid phone layout with floating mini-player & bottom nav pill
- Tablet (600-839px): Fluid tablet layout with left navigation rail & docked mini-player
- Desktop / Large Tablet (>=840px): Fluid 3-pane layout with navigation drawer, center grid, and persistent right player
"""

import os
import re

TARGET_FILE = os.path.join('mobile', 'web_preview', 'index.html')

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove device-switcher-bar and prototype-guide-bar
# Look for <div class="device-switcher-bar"> ... <div class="android-viewport
pattern_bars = re.compile(
    r'<!-- Responsive Device Viewport Switcher Toolbar.*?<div class="android-viewport',
    re.DOTALL
)

if pattern_bars.search(content):
    content = pattern_bars.sub('<div class="android-viewport', content)
    print('Removed device-switcher-bar and prototype-guide-bar.')
else:
    # Try finding each individually
    idx_dev = content.find('<div class="device-switcher-bar">')
    idx_guide = content.find('<div class="prototype-guide-bar">')
    idx_vp = content.find('<div class="android-viewport')
    if idx_dev != -1 and idx_vp != -1 and idx_dev < idx_vp:
        content = content[:idx_dev] + content[idx_vp:]
        print('Removed bars via index slicing.')

# 2. Update CSS for .preview-shell and .android-viewport to be 100% fluid and automatically flexible
OLD_PREVIEW_SHELL_CSS = '''    .preview-shell {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      min-height: 100vh;
      padding: 10px 8px;
      box-sizing: border-box;
      background: #050807;
    }'''

NEW_PREVIEW_SHELL_CSS = '''    html, body {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0;
      background: var(--bg);
      overflow: hidden;
    }

    .preview-shell {
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100%;
      min-height: 100vh;
      padding: 0;
      margin: 0;
      box-sizing: border-box;
      background: var(--bg);
      overflow: hidden;
    }'''

if OLD_PREVIEW_SHELL_CSS in content:
    content = content.replace(OLD_PREVIEW_SHELL_CSS, NEW_PREVIEW_SHELL_CSS, 1)
    print('Updated .preview-shell CSS.')

# Update .android-viewport CSS
OLD_VIEWPORT_CSS = '''.android-viewport {
      width: 100%;
      max-width: 390px;
      height: 844px;
      background: var(--bg);
      border-radius: 38px;
      border: 6px solid #1E2624;
      box-shadow: 0 28px 80px rgba(0, 0, 0, 0.85);
      display: flex;
      flex-direction: row; /* enables side rail & persistent now playing on tablet */
      position: relative;
      overflow: hidden;
      box-sizing: border-box;
      transition: max-width 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), border-radius 0.3s ease;
      container-type: inline-size;
      container-name: raagaApp;
    }'''

NEW_VIEWPORT_CSS = '''.android-viewport {
      width: 100%;
      max-width: 100%;
      height: 100vh;
      height: 100dvh;
      background: var(--bg);
      border-radius: 0;
      border: none;
      box-shadow: none;
      display: flex;
      flex-direction: row;
      position: relative;
      overflow: hidden;
      box-sizing: border-box;
      container-type: inline-size;
      container-name: raagaApp;
    }'''

if OLD_VIEWPORT_CSS in content:
    content = content.replace(OLD_VIEWPORT_CSS, NEW_VIEWPORT_CSS, 1)
    print('Updated .android-viewport CSS.')

# 3. Add Media Queries that automatically switch between Phone, Tablet and 3-Pane desktop based on viewport width
RESPONSIVE_MEDIA_QUERIES = '''
    /* ==================== AUTOMATIC FLUID RESPONSIVE MEDIA QUERIES ==================== */
    @media (max-width: 599px) {
      .tablet-nav-rail { display: none !important; }
      .tablet-persistent-player { display: none !important; }
      .floating-nav-pill { display: flex !important; }
      .floating-mini-player {
        display: flex !important;
        position: absolute !important;
        left: 16px !important;
        right: 16px !important;
        bottom: 84px !important;
        height: 68px !important;
        border-radius: var(--pill-radius) !important;
        border: 1px solid var(--border) !important;
      }
      .era-glass-bar { width: 100%; }
      .screens-wrapper { padding-bottom: 160px; }
      #homePillarGrid { grid-template-columns: 1fr 1fr !important; }
    }

    @media (min-width: 600px) and (max-width: 839px) {
      .tablet-nav-rail {
        display: flex !important;
        width: 88px !important;
        padding: 16px 8px !important;
      }
      .rail-logo-text { display: none !important; }
      .rail-btn-label { display: none !important; }
      .tablet-persistent-player { display: none !important; }
      .floating-nav-pill { display: none !important; }
      .floating-mini-player {
        display: flex !important;
        position: relative !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        height: 64px !important;
        border-radius: 0 !important;
        border: none !important;
        border-top: 1px solid var(--border) !important;
        width: 100% !important;
      }
      .screens-wrapper { padding-bottom: 24px; }
      #homePillarGrid { grid-template-columns: repeat(4, 1fr) !important; }
      .tablet-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)) !important;
        overflow-x: visible !important;
      }
    }

    @media (min-width: 840px) {
      .tablet-nav-rail {
        display: flex !important;
        width: 220px !important;
        padding: 20px 14px !important;
      }
      .rail-logo-text { display: block !important; }
      .rail-btn-label { display: inline !important; }
      .tablet-persistent-player {
        display: flex !important;
        width: 350px !important;
      }
      .floating-nav-pill { display: none !important; }
      .floating-mini-player { display: none !important; }
      .screens-wrapper { padding-bottom: 24px; }
      #homePillarGrid { grid-template-columns: repeat(4, 1fr) !important; }
      .tablet-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
        overflow-x: visible !important;
      }
    }
'''

if 'AUTOMATIC FLUID RESPONSIVE MEDIA QUERIES' not in content:
    # Insert right before </style>
    style_end = content.find('</style>')
    if style_end != -1:
        content = content[:style_end] + '\n' + RESPONSIVE_MEDIA_QUERIES + '\n' + content[style_end:]
        print('Added automatic fluid responsive media queries.')

# Add automatic window resize listener in JS
AUTO_RESIZE_JS = '''
    // Automatic Responsive Window Resize Listener
    window.addEventListener('resize', () => {
      updatePlayerSurfaces();
      renderAll();
    });
'''

if 'Automatic Responsive Window Resize Listener' not in content:
    script_end = content.rfind('</script>')
    if script_end != -1:
        content = content[:script_end] + '\n' + AUTO_RESIZE_JS + '\n' + content[script_end:]
        print('Added window resize listener.')

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated mobile/web_preview/index.html successfully.')
