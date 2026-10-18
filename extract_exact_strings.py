# -*- coding: utf-8 -*-
with open('mobile/web_preview/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

def p(label, s):
    print(f"=== {label} ===")
    print(s.encode('ascii', 'replace').decode('ascii'))

# 1. Era bar exact
idx_era = text.find('<!-- Era Switcher Segmented Bar')
end_era = text.find('</div>\n\n        <!-- ==================== 4-PILLAR', idx_era)
p("ERA BAR", text[idx_era:end_era+6])

# 2. Heritage exact
idx_her = text.find('<!-- ==================== 4-PILLAR KANNADA MUSIC HERITAGE')
end_her = text.find('</div>\n        </div>\n\n        <!-- Section 1:', idx_her)
p("HERITAGE", text[idx_her:end_her+15])

# 3. Rail menu exact
idx_rail = text.find('<div class="rail-menu">')
end_rail = text.find('</nav>', idx_rail)
p("RAIL MENU", text[idx_rail:end_rail])

# 4. Search bar exact
idx_s = text.find('<!-- Big Rounded Pill Search Bar -->')
end_s = text.find('<!-- Search Result Filter Tabs -->', idx_s)
p("SEARCH BAR", text[idx_s:end_s])

# 5. azBrowserBox exact
idx_az = text.find('<!-- Collapsible A-to-Z Kannada Varnamale')
end_az = text.find('<!-- Trending Kannada Music Videos Row -->', idx_az)
p("AZ BOX", text[idx_az:end_az])
