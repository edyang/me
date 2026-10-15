"""Rebuild the reviewed 2013–2019 article corpus and its local SVG figures.

Authoring inputs and operational files stay under the excluded scripts directory.
The generator does not alter any existing article or deployment configuration.
"""
from pathlib import Path
from hashlib import sha256
from html import escape
from collections import Counter
import importlib.util
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NOTES = []
DOMAINS = {}


def domain(key, tags, since, environment, background, method, references):
    DOMAINS[key] = dict(tags=tags, since=since, environment=environment,
                        background=background, method=method, references=references)


def note(month, slug, title, domain_key, problem, reasoning, implementation,
         code, cases, boundary, nodes, since=None, references=None):
    """Cases: three (changed input, expected behavior, discriminating evidence)."""
    NOTES.append(dict(month=month, slug=slug, title=title, domain=domain_key,
                      problem=problem, reasoning=reasoning, implementation=implementation,
                      code=code, cases=cases, boundary=boundary, nodes=nodes,
                      since=since, references=references))


def figure(n, url):
    """Four-node relationship diagram, with explicit feedback and observation."""
    title = n['title']
    nodes = [x.split('|', 1) for x in n['nodes'].split('>')]
    assert len(nodes) == 4
    def label(s, x, y, size, color):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(s)}</text>'
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="660" viewBox="0 0 1120 660" role="img" aria-labelledby="title desc">',
         f'<title id="title">{escape(n["title"])}</title>',
         '<desc id="desc">'+escape('；'.join('：'.join(x) for x in nodes))+'</desc>',
         '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#3977b7"/></marker></defs>',
         '<rect width="1120" height="660" rx="18" fill="#f4f7fb"/>',
         '<g font-family="Noto Sans CJK SC,Microsoft YaHei,sans-serif">',
         label(title, 44, 58, 24, '#123555'),
         label('关系示意 · 箭头表示处理或依赖方向', 44, 91, 17, '#54718b')]
    positions = [(44, 132), (606, 132), (606, 332), (44, 332)]
    for i, ((head, detail), (x, y)) in enumerate(zip(nodes, positions)):
        assert len(head) <= 19 and len(detail) <= 25, (n['slug'], head, detail)
        s += [f'<rect x="{x}" y="{y}" width="470" height="142" rx="12" fill="white" stroke="#bdd0e2" stroke-width="2"/>',
              f'<circle cx="{x+30}" cy="{y+35}" r="15" fill="#2769a4"/>',
              label(str(i+1),x+25,y+41,17,'white'),
              label(head,x+57,y+43,22,'#143f64'),
              label(detail,x+24,y+91,17,'#3c5d7a')]
    s += ['<g fill="none" stroke="#3977b7" stroke-width="3" marker-end="url(#arrow)">',
          '<path d="M516 203 H600"/>', '<path d="M841 276 V326"/>',
          '<path d="M603 403 H520"/>', '<path d="M279 330 V280" stroke-dasharray="7 6"/>', '</g>',
          '<rect x="44" y="516" width="1032" height="106" rx="10" fill="#e5eef7"/>',
          label('观察点',64,546,19,'#174d78')]
    obs = n['cases'][0][2]
    lines = [obs[i:i+49] for i in range(0,len(obs),49)]
    for i, line in enumerate(lines[:2]):s.append(label(line,64,577+i*25,17,'#244e70'))
    s += ['</g></svg>']
    (ROOT/url.lstrip('/')).write_text('\n'.join(s)+'\n')


def article(n, d, day, url, series):
    env = n.get('environment') or d['environment']
    # The connective paragraphs describe this particular experiment; all technical
    # assertions, changed inputs and expected observations come from reviewed inputs.
    tests = []
    for i,(changed, expected, evidence) in enumerate(n['cases'],1):
        tests.append(f'### 对照 {i}：{changed}\n\n'
                     f'{expected}。观察时记录{evidence}。把这个条件与基准情形分开，'
                     '有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。')
    rows = '\n'.join(f'| {a} | {b} |' for a,b,_ in n['cases'])
    refs = n.get('references') or d['references']
    reftext = '\n'.join(f'{i}. [{label}]({link})' for i,(label,link) in enumerate(refs,1))
    neighbors = [r for r in series if r['slug']!=n['slug']]
    related = '\n'.join(f'- [{r["title"]}](/tech/{r["date"].replace("-","/")}/{r["slug"]}/)' for r in neighbors)
    return f'''{n['problem']}

本文使用{env}。{d['background']}

## 1. 从现象推到机制

{n['reasoning']}

![{n['title']}的处理、反馈与观察关系]({url})

图中的四个节点分别表示{ '、'.join(x.split('|')[0] for x in n['nodes'].split('>')) }。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

{n['implementation']}

{n['code']}

{d['method']}

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
{rows}

{chr(10).join(tests)}

## 4. 适用条件与取舍

{n['boundary']}

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“{n['cases'][-1][0]}”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

{related}

## 参考资料

{reftext}
'''


def main():
    for p in sorted(HERE.glob('year_*.py')):
        spec=importlib.util.spec_from_file_location(p.stem,p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        m.register(domain,note)
    counts=Counter(n['month'] for n in NOTES)
    expected={f'{y}-{m:02}' for y in range(2013,2020) for m in range(1,13)}
    assert set(counts)==expected and all(c==3 for c in counts.values()),counts
    for month in sorted(counts):
        group=[n for n in NOTES if n['month']==month]
        for n,day in zip(group,[5,15,25]):n['date']=f'{month}-{day:02}'
    registry=yaml.safe_load((ROOT/'_data/tech_notes.yml').read_text())
    historical_ids={n['slug'] for n in NOTES}
    registry=[r for r in registry if r['note_id'] not in historical_ids]
    report=[]
    for n in NOTES:
        d=DOMAINS[n['domain']];dt=n['date'];slug=n['slug']
        url=f'/img/tech-notes/{slug}.svg'
        path=f'_posts/{dt}-{slug}.md'
        group=[r for r in NOTES if r['month']==n['month']]
        body=article(n,d,dt,url,group)
        since=n['since'] or d['since']
        assert since<=dt,(slug,since,dt)
        meta=dict(layout='post',title=n['title'],subtitle=n['problem'].split('。')[0]+'。',
                  date=f'{dt} 08:00:00 +0800',author='edyang',
                  **{'header-style':'text'},catalog=True,tags=d['tags'],tech_note=True,
                  note_id=slug,permalink=f'/tech/{dt.replace("-","/")}/{slug}/',
                  excerpt=n['problem'].split('。')[0]+'。',privacy_reviewed=True,
                  content_revision=3,images=[url],technology_since=since)
        raw='---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False,width=110)+'---\n\n'+body
        (ROOT/path).write_text(raw)
        figure(n,url)
        record={k:meta[k] for k in ('note_id','title','date','permalink','tags','images','technology_since','privacy_reviewed','content_revision')}
        record.update(path=path,date=dt,sha256=sha256(raw.encode()).hexdigest())
        registry.append(record)
        report.append(dict(note_id=slug,date=dt,title=n['title'],path=path,
                           han=len(re.findall(r'[\u4e00-\u9fff]',body)),bytes=len(raw.encode())))
    registry.sort(key=lambda r:r['date'],reverse=True)
    (ROOT/'_data/tech_notes.yml').write_text(yaml.safe_dump(registry,allow_unicode=True,sort_keys=False,width=110))
    state_path=ROOT/'_data/tech_blog_state.yml'
    state=yaml.safe_load(state_path.read_text())
    state.update(article_count=len(registry),first_article_date='2013-01-05')
    state['historical_coverage']=dict(start='2013-01',end='2019-12',min_articles_per_month=3,article_count=252)
    state['topics']=[{k:r[k] for k in ('note_id','title','date','permalink')} for r in reversed(registry)]
    state_path.write_text(yaml.safe_dump(state,allow_unicode=True,sort_keys=False,width=110))
    (HERE/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(new_articles=len(report),total_articles=len(registry),
                          minimum_han=min(r['han'] for r in report),
                          short_articles=[(r['note_id'],r['han']) for r in report if r['han']<850]),ensure_ascii=False))


if __name__=='__main__':main()
