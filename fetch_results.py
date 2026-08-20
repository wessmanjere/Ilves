import json, urllib.request, urllib.error
from datetime import datetime, timezone
TEAM='35186299'
REF='https://tulospalvelu.palloliitto.fi/'; ORI='https://tulospalvelu.palloliitto.fi'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
K1='df8e84j9xtdz269euy3h'; K2='4h7dznqdxwtp3hsfdyf5r793uahfxy7x'
base='https://spl.torneopal.net/taso/rest/getMatches?team_id={}'
def h(accept): return {'Accept':accept,'Referer':REF,'Origin':ORI,'User-Agent':UA}
variants=[
 ('A accept json/K1', base.format(TEAM), h('json/'+K1)),
 ('B accept json/K2', base.format(TEAM), h('json/'+K2)),
 ('C qs api_key=K1', base.format(TEAM)+'&api_key='+K1, h('json')),
 ('D qs api_key=K2', base.format(TEAM)+'&api_key='+K2, h('json')),
]
out={}
for name,url,headers in variants:
    rec={}
    try:
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=30) as r:
            body=r.read().decode('utf-8','replace'); rec['http']=r.status
            try:
                d=json.loads(body); m=d.get('matches',[])
                rec['match_count']=len(m)
                played=[x for x in m if str(x.get('fs_A','') or '').strip()!='' and str(x.get('fs_B','') or '').strip()!='']
                rec['played_count']=len(played)
                if m:
                    ex=played[0] if played else m[0]
                    rec['sample']={k:ex.get(k) for k in ('date','time','fs_A','fs_B','status','team_A_name','team_B_name','category_name','competition_name')}
            except Exception as e:
                rec['nonjson']=body[:150]
    except urllib.error.HTTPError as e:
        rec['http']=e.code
        try: rec['err_body']=e.read().decode('utf-8','replace')[:150]
        except Exception: pass
    except Exception as e:
        rec['error']=type(e).__name__+': '+str(e)[:120]
    out[name]=rec
with open('results.json','w',encoding='utf-8') as f:
    json.dump({'updated':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'results':{},'_probe3':out},f,ensure_ascii=False,indent=2)
print('probe3 done')
