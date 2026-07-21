"""
Hakee Ilves P2017-joukkueiden ottelutulokset Palloliiton tulospalvelusta.
Kutsuu suoraan Torneopalin REST-rajapintaa (ei selainta, ei Playwrightia).
Vaatii Accept-otsakkeen, joka toimii rajapinnan julkisena avaimena.
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

API_URL = 'https://spl.torneopal.net/taso/rest/getMatches?team_id={}'
ACCEPT = 'json/n9tnjq45uuccbe8nbfy6q7ggmreqntvs'


def fetch_team(team_id, team_name):
    """Hae yhden joukkueen ottelut ja palauta pelatut tulokset."""
    url = API_URL.format(team_id)
    req = urllib.request.Request(url, headers={
        'Accept': ACCEPT,
        'Accept-Language': 'fi-FI,fi;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Ilves-tulosbotti)',
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f'  VIRHE {team_name}: HTTP {e.code}')
        return []
    except Exception as e:
        print(f'  VIRHE {team_name}: {type(e).__name__}: {str(e)[:100]}')
        return []

    matches = data.get('matches', [])

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

    print(f'  {team_name}: {len(matches)} ottelua, {len(played)} tulosta')
    return played


def main():
    results = {}
    for team_id, team_name in TEAMS.items():
        results[team_id] = fetch_team(team_id, team_name)

    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'results': results,
    }

    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in results.values())
    print(f'\nValmis! {total} tulosta tallennettu results.json-tiedostoon.')


if __name__ == '__main__':
    main()
