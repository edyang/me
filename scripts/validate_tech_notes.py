#!/usr/bin/env python3
import argparse, json, re, sys, yaml
from pathlib import Path
from datetime import date
from hashlib import sha256
from html import unescape
from collections import Counter
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path);args=ap.parse_args()
errors=[]
def error(path,msg):errors.append({'path':str(path),'error':msg})
def day(s):return date.fromisoformat(str(s)[:10])
registry=yaml.safe_load((ROOT/'_data/tech_notes.yml').read_text())
state=yaml.safe_load((ROOT/'_data/tech_blog_state.yml').read_text())
byid={r['note_id']:r for r in registry}
for key in ('note_id','path','date','permalink'):
    if any(v>1 for v in Counter(str(r[key]) for r in registry).values()):error('registry','duplicate '+key)
forbidden=re.compile(r'归档日期|交流日期|整理发布|模拟归档|归档.{0,30}（模拟）|\(模拟\)|生成日期|整理时间')
patterns={
 'private IPv4':r'(?<![\d.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])',
 'email':r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
 'mobile':r'(?<!\d)1[3-9]\d{9}(?!\d)',
 'private key':r'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----',
 'token':r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})',
 'personal path':r'(?:/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/|C:\\Users\\[A-Za-z0-9_.-]+\\)',
 'MAC':r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}'}
required=('layout','title','excerpt','tags','note_id','date','permalink','content_revision','images','technology_since','privacy_reviewed')
removed=('source_date','source_dates','archive_date','date_basis','published_at','updated_at')
notes=[]
for path in sorted((ROOT/'_posts').glob('*.md')):
    raw=path.read_text()
    if not raw.startswith('---\n'):continue
    try:front,body=raw[4:].split('\n---\n',1);m=yaml.safe_load(front)
    except (ValueError,yaml.YAMLError):error(path.name,'invalid front matter');continue
    if not m.get('tech_note'):continue
    rel=path.relative_to(ROOT).as_posix();notes.append((path,m,body))
    for k in required:
        if k not in m:error(rel,'missing '+k)
    for k in removed:
        if k in m:error(rel,'obsolete date field '+k)
    r=byid.get(m.get('note_id'))
    if not r:error(rel,'missing registry record');continue
    for k in ('title','permalink','tags','images','technology_since','content_revision','privacy_reviewed'):
        if m.get(k)!=r.get(k):error(rel,'registry mismatch '+k)
    if r['path']!=rel or r.get('sha256')!=sha256(raw.encode()).hexdigest():error(rel,'path or hash mismatch')
    if m['layout']!='post' or m['privacy_reviewed'] is not True:error(rel,'layout or privacy review invalid')
    if not isinstance(m['tags'],list) or not m['tags']:error(rel,'tags required')
    if m['content_revision']<3:error(rel,'old editorial revision')
    d=day(m['date'])
    if day(r['date'])!=d or not path.name.startswith(str(d)+'-'):error(rel,'date mismatch')
    if day(m['technology_since'])>d:error(rel,'technology later than article')
    if m['note_id']=='jetson-orin-super-memory' and d<date(2025,1,16):error(rel,'NX Super predates JetPack 6.2')
    if m['note_id']=='talking-video-avatar-voice-pipeline' and d<date(2026,1,22):error(rel,'Flash predates release')
    if len(re.findall(r'[\u4e00-\u9fff]',body))<850:error(rel,'insufficient technical prose')
    if body.count('```')%2:error(rel,'unclosed code fence')
    if '{{' in body or '{%' in body:error(rel,'Liquid in body')
    if forbidden.search(body):error(rel,'obsolete date labels in body')
    if not re.fullmatch(r'/tech/\d{4}/\d{2}/\d{2}/[a-z0-9-]+/',m['permalink']):error(rel,'invalid permalink')
    if not m['permalink'].startswith('/tech/'+str(d).replace('-','/')+'/'):error(rel,'permalink date mismatch')
    images=re.findall(r'!\[([^\]]+)\]\((/[^\s)]+)\)',body)
    if not images or m['images']!=[url for alt,url in images]:error(rel,'image registration or alt missing')
    for alt,url in images:
        if not (ROOT/url.lstrip('/')).is_file():error(rel,'image missing '+url)
    for label,pattern in patterns.items():
        if re.search(pattern,body.replace('git@github.com','GitHub SSH identity')):error(rel,'possible sensitive '+label)
    if '## 参考资料' not in body:error(rel,'references missing')
    if args.site:
        f=args.site/m['permalink'].strip('/')/'index.html'
        if not f.is_file():error(rel,'Jekyll page missing');continue
        h=f.read_text()
        if unescape(m['title']) not in unescape(h):error(rel,'rendered title missing')
        if str(d) not in h:error(rel,'ordinary date missing')
        if forbidden.search(h):error(rel,'obsolete rendered date labels')
        if 'article:modified_time' in h:error(rel,'processing timestamp exposed')
        if '{{' in h or '{%' in h:error(rel,'unrendered Liquid')
        if '<h2' not in h or '<table' not in h:error(rel,'article formatting missing')
        for alt,url in images:
            if url not in h or not (args.site/url.lstrip('/')).is_file():error(rel,'rendered image missing')
dates=sorted(day(m['date']) for p,m,b in notes)
if len(notes)!=len(registry) or state['article_count']!=len(notes):error('registry','count mismatch')
if not dates or dates[0]!=date(2020,1,5):error('registry','wrong first date')
if any(not 5<=(b-a).days<=10 for a,b in zip(dates,dates[1:])):error('registry','interval outside 5-10 days')
if dates and str(dates[-1])!=state['last_article_date']:error('state','last date mismatch')
if len(state['topics'])!=len(registry):error('state','topic count mismatch')
if not 5<=(day(state['next_article_date'])-day(state['last_article_date'])).days<=10:error('state','next date outside interval')
for svg in (ROOT/'img/tech-notes').glob('*.svg'):
    try:
        n=ET.parse(svg).getroot()
        if not n.tag.endswith('svg') or not n.get('viewBox'):error(svg.name,'SVG dimensions invalid')
        for e in n.iter():
            if e.tag.endswith(('script','foreignObject')):error(svg.name,'active SVG content')
    except ET.ParseError:error(svg.name,'SVG XML invalid')
if args.site:
    for name in ('index.html','tech-notes/index.html','archive/index.html'):
        f=args.site/name
        if not f.is_file():error(name,'page missing');continue
        h=f.read_text()
        if forbidden.search(h):error(name,'obsolete labels')
        if name=='tech-notes/index.html':
            for r in registry:
                if r['permalink'] not in h:error(name,'missing link '+r['note_id'])
    try:
        tree=ET.parse(args.site/'feed.xml')
        for item in tree.findall('./channel/item'):
            link=item.findtext('link') or ''
            for r in registry:
                if link.endswith(r['permalink']) and str(day(r['date']).year) not in (item.findtext('pubDate') or ''):error('RSS','wrong date')
    except (ET.ParseError,FileNotFoundError) as exc:error('RSS',str(exc))
    for private in ('AGENTS.md','TECH_BLOG_AGENT.md','scripts','_data','full-blog-rebuild'):
        if (args.site/private).exists():error(private,'operational file exposed')
print(json.dumps({'valid':not errors,'articles':len(notes),'diagrams':len(list((ROOT/'img/tech-notes').glob('*.svg'))),'first':str(dates[0]) if dates else None,'last':str(dates[-1]) if dates else None,'rendered_checked':bool(args.site),'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))

