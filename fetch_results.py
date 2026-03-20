"""
Hakee Ilves P2017-joukkueiden ottelutulokset Palloliitto-API:sta.
Ajetaan GitHub Actionsin kautta automaattisesti.
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
    '35213619': 'Ilves / Keltavihreä A',
    '35213621': 'Ilves / Keltavihreä B',
    '35186300': 'Ilves Vihreä A',
    '35186298': 'Ilves Vihreä B',
}

BASE_URL = 'https://spl.torneopal.net/taso/rest/getMatches?team_id='
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; results-fetcher)',
    'Referer': 'https://tulospalvelu.palloliitto.fi/',
    'Accept': 'application/json',
}

results = {}

for team_id, team_name in TEAMS.items():
    url = BASE_URL + team_id
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        played = [
            m for m in data.get('matches', [])
            if m.get('season_id') == '2026' and m.get('status') == 'Played'
        ]
        results[team_id] = [
            {
                'date': m['date'],
                'time': m['time'][:5],
                'fs_A': m.get('fs_A', ''),
                'fs_B': m.get('fs_B', ''),
            }
            for m in played
        ]
        print(f'  {team_name}: {len(results[team_id])} tulosta')
    except urllib.error.HTTPError as e:
        print(f'  VIRHE {team_name}: HTTP {e.code}')
        results[team_id] = []
    except Exception as e:
        print(f'  VIRHE {team_name}: {e}')
        results[team_id] = []

output = {
    'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'results': results,
}

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in results.values())
print(f'\nValmis! {total} tulosta tallennettu results.json-tiedostoon.')
