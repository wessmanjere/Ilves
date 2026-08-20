import json, urllib.request, urllib.error
from datetime import datetime, timezone

TEAM = '35186299'
ACCEPT_KEY = 'json/n9tnjq45uuccbe8nbfy6q7ggmreqntvs'
REF = 'https://tulospalvelu.palloliitto.fi/'
ORI = 'https://tulospalvelu.palloliitto.fi'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'

def base(u): return u.format(TEAM)

variants = [
  ('1 .net accept-only', base('https://spl.torneopal.net/taso/rest/getMatches?team_id={}'),
     {'Accept': ACCEPT_KEY}),
  ('2 .net accept+ref+origin', base('https://spl.torneopal.net/taso/rest/getMatches?team_id={}'),
     {'Accept': ACCEPT_KEY, 'Referer': REF, 'Origin': ORI, 'User-Agent': UA}),
  ('3 .fi accept+ref+origin', base('https://spl.torneopal.fi/taso/rest/getMatches?team_id={}'),
     {'Accept': ACCEPT_KEY, 'Referer': REF, 'Origin': ORI, 'User-Agent': UA}),
  ('4 palloliitto same-origin', base('https://tulospalvelu.palloliitto.fi/taso/rest/getMatches?team_id={}'),
     {'Accept': ACCEPT_KEY, 'Referer': REF, 'Origin': ORI, 'User-Agent': UA}),
  ('5 .net accept-json std', base('https://spl.torneopal.net/taso/rest/getMatches?team_id={}'),
     {'Accept': 'application/json', 'Referer': REF, 'Origin': ORI, 'User-Agent': UA}),
  ('6 .net +xrw', base('https://spl.torneopal.net/taso/rest/getMatches?team_id={}'),
     {'Accept': ACCEPT_KEY, 'Referer': REF, 'Origin': ORI, 'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest'}),
]

out = {}
for name, url, headers in variants:
    rec = {'url': url}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode('utf-8', 'replace')
            rec['http'] = r.status
            rec['body_head'] = body[:180]
            try:
                d = json.loads(body)
                rec['json_keys'] = list(d.keys())
                m = d.get('matches', [])
                rec['match_count'] = len(m)
                if m:
                    rec['first_match_keys'] = list(m[0].keys())
                    rec['first_match_scores'] = {k: m[0].get(k) for k in ('date','time','fs_A','fs_B','status','team_A_name','team_B_name')}
            except Exception as e:
                rec['json'] = 'not json: ' + str(e)[:80]
    except urllib.error.HTTPError as e:
        rec['http'] = e.code
        try: rec['body_head'] = e.read().decode('utf-8','replace')[:180]
        except Exception: rec['body_head'] = ''
    except Exception as e:
        rec['error'] = type(e).__name__ + ': ' + str(e)[:120]
    out[name] = rec

with open('results.json','w',encoding='utf-8') as f:
    json.dump({'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'results': {}, '_probe': out}, f, ensure_ascii=False, indent=2)
print('probe done')
