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
    '35213619': 'Ilves / KeltavihreÃ¤ A',
    '35213621': 'Ilves / KeltavihreÃ¤ B',
    '35186300': 'Ilves VihreÃ¤ A',
    '35186298': 'Ilves VihreÃ¤ B',
}

BASE_URL = 'https://spl.torneopal.net/taso/rest/getMatches?team_id='
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://tulospalvelu.palloliitto.fi/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fi-FI,fi;q=0.9,en;q=0.8',
}

results = {}

for team_id, team_name in TEAMS.items():
    url = BASE_URL + team_id
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)

        matches = data.get('matches', [])

        # Debug: nÃ¤ytÃ¤ uniikit status- ja season-arvot ensimmÃ¤iseltÃ¤ joukkueelta
        if team_id == '35186299':
            statuses = list({m.get('status') for m in matches})
            seasons = list({m.get('season_id') for m in matches})
            print(f'  DEBUG {team_name}: {len(matches)} ottelua, statukset={statuses}, kaudet={seasons}')
            if matches:
                print(f'  DEBUG esimerkki: {json.dumps(matches[0])}')

        # HyvÃ¤ksy ottelu jos sillÃ¤ on tulos (fs_A ja fs_B eivÃ¤t ole tyhjiÃ¤)
        # Ei rajoiteta season_id:llÃ¤ koska arvo voi vaihdella
        played = [
            m for m in matches
            if m.get('fs_A', '') != '' and m.get('fs_B', '') != ''
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
        print(f'  VIRHE {team_name}: HTTP {e.code} - {e.reason}')
        results[team_id] = []
    except urllib.error.URLError as e:
        print(f'  VIRHE {team_name}: URL-virhe {e.reason}')
        results[team_id] = []
    except Exception as e:
        print(f'  VIRHE {team_name}: {type(e).__name__}: {e}')
        results[team_id] = []

output = {
    'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'results': results,
}

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in results.values())
print(f'\nValmis! {total} tulosta tallennettu results.json-tiedostoon.')
