# -*- coding: utf-8 -*-
with open('mobile/web_preview/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="screen-search"')
print("Index:", idx)
if idx != -1:
    print(text[idx:idx+600])
