import json, urllib.request, urllib.error, re
from datetime import datetime, timezone

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'

def get(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')

out = {}
try:
    st, html = get('https://tulospalvelu.palloliitto.fi/')
    out['root_http'] = st
    scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
    # inline hits in root html
    out['root_api_key_hits'] = re.findall(r'api_key["\'=:\s]{1,4}([A-Za-z0-9]{20,})', html)[:5]
    out['root_json_slash'] = re.findall(r'json/([A-Za-z0-9]{20,})', html)[:5]
    # normalize script urls
    js_urls = []
    for s in scripts:
        if s.startswith('http'): js_urls.append(s)
        elif s.startswith('/'): js_urls.append('https://tulospalvelu.palloliitto.fi'+s)
        else: js_urls.append('https://tulospalvelu.palloliitto.fi/'+s)
    out['script_count'] = len(js_urls)
    out['scripts'] = js_urls[:12]

    found_keys = set()
    found_jsonslash = set()
    checked = []
    for u in js_urls:
        try:
            _, js = get(u, timeout=40)
        except Exception as e:
            checked.append(u+' ERR '+type(e).__name__); continue
        checked.append(u+' ('+str(len(js))+'b)')
        for m in re.findall(r'api_key["\'=:\s]{1,6}["\']?([A-Za-z0-9]{20,})', js): found_keys.add(m)
        for m in re.findall(r'json/([A-Za-z0-9]{20,})', js): found_jsonslash.add(m)
        # also capture generic assignment like apiKey:"..."
        for m in re.findall(r'[aA]pi[_-]?[kK]ey["\']?\s*[:=]\s*["\']([A-Za-z0-9]{20,})', js): found_keys.add(m)
    out['checked'] = checked
    out['api_keys_found'] = list(found_keys)[:10]
    out['json_slash_found'] = list(found_jsonslash)[:10]
except Exception as e:
    out['fatal'] = type(e).__name__+': '+str(e)[:200]

with open('results.json','w',encoding='utf-8') as f:
    json.dump({'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'results': {}, '_probe2': out}, f, ensure_ascii=False, indent=2)
print('probe2 done')
