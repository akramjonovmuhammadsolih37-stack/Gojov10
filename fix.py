f = open('userbot_panel.html', 'r')
content = f.read()
f.close()

dollar_func = 'function $(id) { return document.getElementById(id); }'

while dollar_func in content:
    content = content.replace(dollar_func, '')

content = content.replace('<script>', '<script>\n' + dollar_func, 1)

f = open('userbot_panel.html', 'w')
f.write(content)
f.close()
print('OK')
