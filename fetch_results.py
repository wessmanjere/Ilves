"""
Hakee Ilves P2017-joukkueiden ottelutulokset Palloliiton tulospalvelusta.
KÃ¤yttÃ¤Ã¤ Playwrightia Cloudflaren ohittamiseksi.
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
    '35213619': 'Ilves / KeltavihreÃ¤ A',
    '35213621': 'Ilves / KeltavihreÃ¤ B',
    '35186300': 'Ilves VihreÃ¤ A',
    '35186298': 'Ilves VihreÃ¤ B',
}

BASE_URL = 'https://spl.torneopal.net/taso/rest/getMatches?team_id='

async def fetch_team(page, team_id, team_name):
    """Hakee yhden joukkueen tulokset API:sta selain-headereiden kanssa."""
    url = BASE_URL + team_id
    try:
        # KÃ¤ytetÃ¤Ã¤n sivun fetch-funktiota, jolloin selain lisÃ¤Ã¤ oikeat headerit
        result = await page.evaluate(f"""
            async () => {{
                const resp = await fetch({json.dumps(url)}, {{
                    headers: {{
                        'Accept': 'application/json, text/plain, */*',
                        'Referer': 'https://tulospalvelu.palloliitto.fi/',
                    }}
                }});
                if (!resp.ok) return {{ error: resp.status }};
                return await resp.json();
            }}
        """)

        if isinstance(result, dict) and 'error' in result:
            print(f'  VIRHE {team_name}: HTTP {result["error"]}')
            return []

        matches = result.get('matches', []) if isinstance(result, dict) else []

        # Debug ensimmÃ¤iselle joukkueelle
        if team_id == '35186299' and matches:
            statuses = list({m.get('status') for m in matches})
            seasons = list({m.get('season_id') for m in matches})
            print(f'  DEBUG {team_name}: {len(matches)} ottelua, statukset={statuses}, kaudet={seasons}')
            print(f'  DEBUG esimerkki: {json.dumps(matches[0])}')

        # HyvÃ¤ksy ottelu jos sillÃ¤ on tulos
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

    except Exception as e:
        print(f'  VIRHE {team_name}: {type(e).__name__}: {e}')
        return []


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
        page = await context.new_page()

        # KÃ¤ydÃ¤Ã¤n ensin palloliitossa jotta evÃ¤steet asettuvat
        try:
            await page.goto('https://tulospalvelu.palloliitto.fi/', timeout=20000, wait_until='domcontentloaded')
            print('  Palloliitto-sivu ladattu (evÃ¤steet asetettu)')
        except Exception as e:
            print(f'  Huom: etusivu ei latautunut ({e}), jatketaan silti...')

        for team_id, team_name in TEAMS.items():
            results[team_id] = await fetch_team(page, team_id, team_name)

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
