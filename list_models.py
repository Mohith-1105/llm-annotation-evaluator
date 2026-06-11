import requests, sys, re
src = open('step1_fetch_responses.py', encoding='utf-8').read()
m = re.search(r'GEMINI_API_KEY = "(.+?)"', src)
api_key = m.group(1) if m else ''
if not api_key or api_key == 'YOUR_GEMINI_API_KEY':
    print('Paste your API key in step1_fetch_responses.py first.')
    sys.exit(1)
url = 'https://generativelanguage.googleapis.com/v1beta/models?key=' + api_key
r = requests.get(url, timeout=15)
if r.status_code != 200:
    print('Error:', r.text[:300])
    sys.exit(1)
models = r.json().get('models', [])
print()
print(str(len(models)) + ' models available for your key:')
print()
for mo in models:
    name = mo.get('name', '').replace('models/', '')
    methods = mo.get('supportedGenerationMethods', [])
    if 'generateContent' in methods:
        print('  [OK]  ' + name)
    else:
        print('  [--]  ' + name + '  (no generateContent)')
