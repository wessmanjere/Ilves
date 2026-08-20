"""
Hakee Ilves P2017 -joukkueiden ottelutulokset Palloliiton tulospalvelusta
(Torneopal REST). Kutsuu rajapintaa suoraan oikealla api_keylla seka
Referer/Origin-otsakkeilla, jotka Cloudflare vaatii. Ei selainta.
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
HEADERS = {
    'Accept': 'json/4h7dznqdxwtp3hsfdyf5r793uahfxy7x',
    'Referer': 'https://tulospalvelu.palloliitto.fi/',
    'Origin': 'https://tulospalvelu.palloliitto.fi',
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/120 Safari/537.36'),
}


def fetch_team(team_id, team_name):
    url = API_URL.format(team_id)
    req = urllib.request.Request(url, headers=HEADERS)
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
    print(f'\nValmis! {total} tulosta tallennettu.')


if __name__ == '__main__':
    main()
