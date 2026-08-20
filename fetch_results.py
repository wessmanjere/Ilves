"""
DIAGNOSTIIKKAVERSIO. Hakee Ilves P2017 -tulokset Torneopalin REST-rajapinnasta
ja kirjoittaa lisaksi _debug-osion results.json-tiedostoon, jotta nahdaan
tarkalleen mika menee pieleen (HTTP-koodit, vastauksen rakenne, kenttanimet).
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

TEAMS = {
    '35186280': 'Ilves / P2017',
    '35186299': 'Ilves Keltainen A',
    '35186284': 'Ilves Keltainen B',
    '35186295': 'Ilves Keltainen C',
    '35213619': 'Ilves / Keltavihrea A',
    '35213621': 'Ilves / Keltavihrea B',
    '35186300': 'Ilves Vihrea A',
    '35186298': 'Ilves Vihrea B',
}

API_URL = 'https://spl.torneopal.net/taso/rest/getMatches?team_id={}'
ACCEPT = 'json/n9tnjq45uuccbe8nbfy6q7ggmreqntvs'


def fetch_team(team_id, team_name, debug, sample_holder):
    url = API_URL.format(team_id)
    req = urllib.request.Request(url, headers={
        'Accept': ACCEPT,
        'Accept-Language': 'fi-FI,fi;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Ilves-tulosbotti)',
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8')
            http = resp.status
    except urllib.error.HTTPError as e:
        body = ''
        try:
            body = e.read().decode('utf-8')[:300]
        except Exception:
            pass
        debug[team_id] = f'HTTP {e.code}: {body}'
        return []
    except Exception as e:
        debug[team_id] = f'{type(e).__name__}: {str(e)[:200]}'
        return []

    try:
        data = json.loads(raw)
    except Exception:
        debug[team_id] = f'JSON-virhe (HTTP {http}). Vastaus alkaa: {raw[:200]}'
        return []

    matches = data.get('matches', [])

    if sample_holder.get('done') is not True:
        first = matches[0] if matches else None
        sample_holder['done'] = True
        sample_holder['data'] = {
            'http': http,
            'top_level_keys': list(data.keys()),
            'match_count': len(matches),
            'first_match_keys': list(first.keys()) if isinstance(first, dict) else None,
            'first_match': first,
        }

    played = []
    for m in matches:
        a = str(m.get('fs_A', '') or '').strip()
        b = str(m.get('fs_B', '') or '').strip()
        if a == '' or b == '':
            continue
        played.append({
            'date': m.get('date', ''),
            'time': (m.get('time', '') or '')[:5],
            'fs_A': a,
            'fs_B': b,
        })

    debug[team_id] = f'HTTP {http}, {len(matches)} ottelua, {len(played)} tulosta'
    return played


def main():
    results = {}
    debug = {}
    sample_holder = {}
    for team_id, team_name in TEAMS.items():
        results[team_id] = fetch_team(team_id, team_name, debug, sample_holder)

    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'results': results,
        '_debug': {
            'per_team': debug,
            'sample': sample_holder.get('data'),
        },
    }

    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in results.values())
    print(f'Valmis. {total} tulosta. Debug kirjoitettu results.json-tiedostoon.')


if __name__ == '__main__':
    main()
