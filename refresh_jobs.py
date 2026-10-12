#!/usr/bin/env python3
"""Public ATS internship feed collector. No keys required; rerun with GitHub Actions."""
import json, re, datetime, urllib.request, urllib.error, html, concurrent.futures
from pathlib import Path

ROOT=Path(__file__).resolve().parent
# Board identifiers are editable in sources.json; invalid/private boards are skipped.
SOURCES=json.loads((ROOT/'sources.json').read_text())
DESIGN=re.compile(r'(?i)(product\s+design|ux\b|ui\b|user experience|user interface|interaction design|experience design|design systems?|service design|visual design|digital design|design research|uxr\b|user research|human.centered design|design intern|design co.op)')
INTERNSHIP=re.compile(r'(?i)(intern(ship)?\b|co[ -]?op\b|university\s+(student|program)|summer\s+20(?:26|27|28))')
EXCLUDE=re.compile(r'(?i)(senior|staff|principal|lead|manager|director|head of|full.time|graduate internship only)')

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'OrbitInternshipTracker/1.1 (+public ATS listings)','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=12) as resp: return json.load(resp)

def clean(txt): return html.unescape(re.sub('<[^>]*>',' ',str(txt or ''))).strip()
def match(title): return bool(DESIGN.search(title) and INTERNSHIP.search(title) and not EXCLUDE.search(title))
def norm(company,source,extid,title,location,url,description='',comp=None,remote=False):
    desc=clean(description)
    if not match(title) or not url or not url.startswith('https://'):return None
    # Never parse deadlines, relocation, or salaries from free-text heuristics as verified fields.
    return dict(id=f'feed:{source}:{company.lower().replace(" ","-")}:{extid}',company=company,role=title,location=location or 'Not specified',workType='Remote' if remote else 'Not specified',pay=None,payUnit='hour',relocation='Unknown',housing='Unknown',due='',status='Saved',priority='Medium',deadlineCertainty='Unverified',url=url,nextAction='Review the official posting and verify deadline, pay and relocation',notes='Automatically discovered via public '+source+' employer board; verify Summer 2027 eligibility and details.',source=source,sourceDescription=desc[:500],compensationText=comp or '',discoveredAt=datetime.datetime.now(datetime.timezone.utc).isoformat())

def collect(entry):
    company=entry['company'];slug=entry['slug'];kind=entry['type'];out=[]
    try:
        if kind=='greenhouse':
            data=get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true')
            for j in data.get('jobs',[]):
                v=norm(company,'Greenhouse',j.get('id'),j.get('title',''),(j.get('location') or {}).get('name',''),j.get('absolute_url',''),j.get('content',''))
                if v:out.append(v)
        elif kind=='ashby':
            data=get(f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true')
            for j in data.get('jobs',[]):
                c=j.get('compensation') or {};ct=c.get('compensationTierSummary') if isinstance(c,dict) else ''
                v=norm(company,'Ashby',j.get('id') or j.get('jobUrl'),j.get('title',''),j.get('location',''),j.get('jobUrl') or j.get('applyUrl',''),j.get('descriptionHtml',''),ct,bool(j.get('isRemote')))
                if v:out.append(v)
        elif kind=='lever':
            data=get(f'https://api.lever.co/v0/postings/{slug}?mode=json')
            for j in data:
                v=norm(company,'Lever',j.get('id'),j.get('text',''),(j.get('categories') or {}).get('location',''),j.get('hostedUrl',''),j.get('descriptionPlain',''))
                if v:out.append(v)
        return (company,out,None)
    except Exception as exc: return (company,[],str(exc))

def main():
    results=[];failed=[];ok=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for company,jobs,error in pool.map(collect,SOURCES):
            if error:failed.append(company+': '+error[:100])
            else:ok+=1
            results.extend(jobs)
    unique={x['url'].split('?')[0]:x for x in results}
    payload={'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceBoardsChecked':ok,'sourceBoardsConfigured':len(SOURCES),'count':len(unique),'jobs':list(unique.values())}
    out=ROOT/'data'/'internships.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
    print(f'Found {len(unique)} matching design internships from {ok}/{len(SOURCES)} boards. Failures: {len(failed)}')
    for problem in failed:print('SKIP',problem)
    if ok==0:raise SystemExit('All sources failed; preserve previous feed and investigate')
if __name__=='__main__': main()
