"""
Hakee Ilves P2017-joukkueiden ottelutulokset Palloliiton tulospalvelusta.
Navigoi oikealle tiimisivulle ja kaappaa verkkoliikenne.
"""
import json
import asyncio
from datetime import datetime, timezone
from playwright.async_api import async_playwright

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

TEAM_PAGE = 'https://tulospalvelu.palloliitto.fi/team/{}/matches'
API_URL = 'https://spl.torneopal.net/taso/rest/getMatches?team_id={}'


async def fetch_team(context, team_id, team_name):
    """Navigoi tiimisivulle ja kaappaa API-vastaus verkkoliikenteestä."""
    page = await context.new_page()
    captured = {}

    async def handle_response(response):
        url = response.url
        if 'getMatches' in url and team_id in url:
            try:
                body = await response.json()
                captured['data'] = body
            except Exception:
                pass

    page.on('response', handle_response)

    try:
        url = TEAM_PAGE.format(team_id)
        await page.goto(url, timeout=30000, wait_until='networkidle')

        # Odota hetki lisää dataa varten
        await page.wait_for_timeout(2000)

    except Exception as e:
        print(f'  VIRHE {team_name}: {type(e).__name__}: {str(e)[:100]}')
    finally:
        await page.close()

    if not captured:
        print(f'  {team_name}: ei API-vastausta kaapattu')
        return []

    data = captured['data']
    matches = data.get('matches', [])

    # Debug ensimmäiselle joukkueelle
    if team_id == '35186299':
        statuses = list({m.get('status') for m in matches})
        seasons = list({m.get('season_id') for m in matches})
        print(f'  DEBUG {team_name}: {len(matches)} ottelua, statukset={statuses}, kaudet={seasons}')
        if matches:
            print(f'  DEBUG esimerkki: {json.dumps(matches[0])}')

    played = [
        m for m in matches
        if m.get('fs_A', '') != '' and m.get('fs_B', '') != ''
    ]
    print(f'  {team_name}: {len(played)} tulosta')
    return [
        {
            'date': m['date'],
            'time': m['time'][:5],
            'fs_A': m.get('fs_A', ''),
            'fs_B': m.get('fs_B', ''),
        }
        for m in played
    ]


async def main():
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'fi-FI,fi;q=0.9,en;q=0.8',
            }
        )

        for team_id, team_name in TEAMS.items():
            results[team_id] = await fetch_team(context, team_id, team_name)

        await browser.close()

    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'results': results,
    }

    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in results.values())
    print(f'\nValmis! {total} tulosta tallennettu results.json-tiedostoon.')


asyncio.run(main())
