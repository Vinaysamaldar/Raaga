# Python script to apply full UI spec to mobile/web_preview/index.html
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS tokens
content = content.replace("--surface-elevated: #212D2A;", "--surface-elevated: #222C29;")
content = content.replace("font-size: 24px;\n      font-weight: 800;", "font-size: 28px;\n      font-weight: 700;")

# 2. Add chart-card, video-poster-card sizing, lib-tile, az-tile-56, np-sec-btn, etc.
extra_css = """
    /* Specific Dimensions from High-Fidelity Design Tokens */
    .chart-card {
      width: 160px;
      flex-shrink: 0;
      cursor: pointer;
      transition: transform 0.15s ease;
    }
    .chart-card:active { transform: scale(0.97); }
    .chart-art {
      width: 160px;
      height: 160px;
      border-radius: var(--card-radius);
      background: var(--surface);
      padding: 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
      border: 1px solid var(--border);
    }

    .video-poster-card {
      width: 180px !important;
      height: 260px !important;
      border-radius: var(--card-radius);
      flex-shrink: 0;
      position: relative;
      overflow: hidden;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 14px;
      border: 1px solid var(--border);
    }

    .lib-tile {
      height: 56px !important;
      background: var(--surface);
      border-radius: 16px;
      padding: 0 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      border: 1px solid var(--border);
      transition: all 0.15s ease;
    }
    .lib-tile:active { transform: scale(0.97); }
    .lib-tile-icon {
      font-size: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .lib-tile-label {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .az-tile-56 {
      height: 56px;
      border-radius: 16px;
      background: var(--surface);
      color: var(--text-primary);
      font-size: 19px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      border: 1px solid var(--border);
      transition: all 0.15s ease;
    }
    .az-tile-56:active { transform: scale(0.94); }
    .az-tile-56.active {
      background: var(--saffron);
      color: #0B1110;
      border-color: var(--saffron);
      box-shadow: 0 4px 14px rgba(242, 169, 0, 0.4);
    }

    .np-big-play {
      width: 72px !important;
      height: 72px !important;
      font-size: 28px !important;
    }

    .mini-mint-play {
      width: 56px !important;
      height: 56px !important;
      font-size: 20px !important;
    }

    .floating-fab {
      width: 56px !important;
      height: 56px !important;
      font-size: 28px !important;
    }

    .np-sec-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      font-size: 18px;
      padding: 6px 10px;
      border-radius: var(--pill-radius);
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .np-sec-btn:hover, .np-sec-btn:active {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-primary);
    }
    .np-sec-btn.active {
      color: var(--saffron);
    }

    .lyrics-line {
      padding: 6px 8px;
      border-radius: 8px;
      transition: all 0.2s ease;
    }
    .lyrics-line.active {
      background: rgba(242, 169, 0, 0.15);
      border-left: 3px solid var(--saffron);
    }
    .lyrics-line.active .lyrics-kn {
      color: var(--saffron);
      font-weight: 700;
    }
    .lyrics-line.active .lyrics-en {
      color: var(--text-primary);
      font-weight: 600;
    }
"""

if ".chart-card" not in content:
    content = content.replace("</style>", extra_css + "\n  </style>")

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated tokens and extra CSS.")
