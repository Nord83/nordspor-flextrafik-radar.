#!/usr/bin/env python3
"""Conservative public-page change monitor. No claim of tender status without review."""
import json, re, hashlib, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
SOURCES=[
 ('midttrafik','Midttrafik – igangværende','https://midttrafik.dk/udbud/udbud-flextrafik-og-specialkoersel/igangvaerende-udbud/'),
 ('midttrafik_all','Midttrafik – Flextrafik','https://midttrafik.dk/udbud/udbud-flextrafik-og-specialkoersel/'),
 ('sydtrafik','Sydtrafik','https://sydtrafik.dk/'),
 ('fynbus','FynBus','https://fynbus.dk/'),
 ('nt','NT','https://www.ntrejse.dk/'),
 ('movia','Movia','https://www.moviatrafik.dk/'),
 ('udbud','Udbud.dk','https://udbud.dk/'),
 ('ted','TED','https://ted.europa.eu/da/'),
 ('fstyr','Færdselsstyrelsen','https://www.fstyr.dk/'),
 ('indeks','Trafikselskaberne – omkostningsindeks','https://www.trafikselskaberne.dk/flex-2025-omkostningsindeks/'),
]
KEYWORDS=re.compile(r'flextrafik|flexvariabel|flexgaranti|flexspeciel|fv10|fg10|persontransport|udbud|tilbudsfrist|omkostningsindeks|chauffør|køretøj|taxi|ethics',re.I)
STRONG=re.compile(r'flextrafik|flexvariabel|flexgaranti|flexspeciel|fv10|fg10|tilbudsfrist|omkostningsindeks',re.I)
UA='NordsporPublicTenderMonitor/1.0 (public pages; once hourly)'

def norm(s):return ' '.join(s.split()).strip()
def load(path, default):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except (OSError,ValueError):return default

def main():
 DATA.mkdir(exist_ok=True)
 old=load(DATA/'radar.json',{})
 previous={x['id']:x for x in old.get('sources',[])}
 events=load(DATA/'events.json',[])
 now=datetime.now(timezone.utc).isoformat(timespec='seconds')
 output=[]; newevents=[]
 for sid,name,url in SOURCES:
  prev=previous.get(sid,{})
  record={'id':sid,'name':name,'url':url,'checked_at':now,'status':'error','items':prev.get('items',[]),'last_success':prev.get('last_success')}
  try:
   r=requests.get(url,headers={'User-Agent':UA,'Accept-Language':'da,en;q=0.8'},timeout=22)
   r.raise_for_status()
   if 'html' not in r.headers.get('content-type','').lower():raise ValueError('Svar er ikke HTML')
   soup=BeautifulSoup(r.text,'html.parser')
   for tag in soup(['script','style','nav','footer','header','noscript']):tag.decompose()
   candidates={}
   for a in soup.select('a[href]'):
    label=norm(a.get_text(' ',strip=True))[:180]
    href=urljoin(r.url,a['href']).split('#')[0]
    if not href.startswith('https://') and not href.startswith('http://'):continue
    if len(label)<8 or not KEYWORDS.search(label+' '+href):continue
    # Keep link records, not unverified tender claims.
    key=hashlib.sha256((sid+'|'+href).encode()).hexdigest()[:16]
    candidates[key]={'id':key,'title':label,'url':href}
   items=sorted(candidates.values(),key=lambda x:x['id'])[:150]
   if not items and sid in ('midttrafik','midttrafik_all'):raise ValueError('Ingen relevante links fundet; mulig sideændring')
   record.update(status='ok',items=items,last_success=now,error=None)
   olditems={i['id']:i for i in prev.get('items',[])}
   if prev.get('last_success'):
    for item in items:
     if item['id'] not in olditems and STRONG.search(item['title']):
      event={'id':hashlib.sha256((sid+item['id']).encode()).hexdigest()[:20],'detected_at':now,'source':name,'title':item['title'],'url':item['url'],'type':'new_link','verification':'Kræver manuel kontrol af udbud, status og frist'}
      if not any(e['id']==event['id'] for e in events):newevents.append(event)
   print(sid,'OK',len(items))
  except (requests.RequestException,ValueError) as exc:
   record['error']=str(exc)[:220]
   print(sid,'ERROR',record['error'])
  output.append(record)
 events=(newevents+events)[:300]
 (DATA/'radar.json').write_text(json.dumps({'updated_at':now,'monitoring':'periodisk, ikke realtid','sources':output},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (DATA/'events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('New candidate links:',len(newevents))

if __name__=='__main__':main()
