# -*- coding: utf-8 -*-
with open('mobile/web_preview/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

def p(s):
    print(s.encode('ascii', 'replace').decode('ascii'))

idx1 = text.find('id="screen-search"')
if idx1 != -1:
    p("screen-search:\n" + text[idx1:idx1+1200])
