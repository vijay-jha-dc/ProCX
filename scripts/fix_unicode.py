import sys
with open('tests/test_step8_comprehensive.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('\u2713', '[OK]').replace('\u2717', '[X]').replace('\U0001F389', '[SUCCESS]')
with open('tests/test_step8_comprehensive.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed Unicode characters in test file')
