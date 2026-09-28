"""Rebuild the static homepage using Python's standard library."""
import html
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
esc = html.escape


def import_publications():
    blocks = (ROOT / 'publications-source.md').read_text().split('\n## ')[1:]
    venues = ['TVCG', 'ICLR', 'CVPR', 'ACL', 'ECCV', 'ECCV', 'TMLR', 'NeurIPS', 'NeurIPS', 'NeurIPS']
    urls = {
        0: ('https://arxiv.org/abs/2511.09361', 'Paper'),
        1: ('https://proceedings.iclr.cc/paper_files/paper/2026/hash/43b3b23fd3bc9c6e3fe8366f71e51c5b-Abstract-Conference.html', 'Paper'),
        3: ('https://arxiv.org/abs/2602.14337', 'Preprint'),
        4: ('https://arxiv.org/abs/2511.21256', 'Paper'),
        5: ('https://arxiv.org/abs/2512.16300', 'Paper'),
        6: ('https://arxiv.org/abs/2503.06542', 'Preprint'),
    }
    previous_path = ROOT / 'publications.json'
    previous = {p['id']: p for p in json.loads(previous_path.read_text())} if previous_path.exists() else {}
    papers = []
    for i, block in enumerate(blocks):
        lines = [re.sub(r'\\([()|\-])', r'\1', x).strip() for x in block.splitlines() if x.strip()]
        authors = [a.strip() for a in re.split('[;,]', lines[1].replace('**', ''))]
        paper = dict(previous.get(f'paper-{i+1}', {}))
        paper.update(dict(id=f'paper-{i+1}', title=lines[0], authors=authors,
                           venue=venues[i], year=2026,
                           track='Findings' if 'Findings' in lines[2] else ('Journal' if venues[i] in ['TVCG', 'TMLR'] else 'Main Conference'),
                           publicationStatus='forthcoming' if venues[i] == 'NeurIPS' else 'published',
                           url=paper.get('url') or urls.get(i, ('', ''))[0], linkLabel=paper.get('linkLabel') or urls.get(i, ('', ''))[1]))
        papers.append(paper)
    (ROOT / 'publications.json').write_text(json.dumps(papers, indent=2, ensure_ascii=False) + '\n')


def build():
    papers = json.loads((ROOT / 'publications.json').read_text())
    news = json.loads((ROOT / 'news.json').read_text())
    news.sort(key=lambda item: item['date'], reverse=True)
    news_by_id = {item['id']: item for item in news}
    # Both sections use the same event date; publication dates are separate metadata.
    for p in papers:
        event = news_by_id[p['newsKey']]
        p['eventDate'] = event['date']
        p['eventKind'] = event.get('kind', 'accepted')
        month = datetime.strptime(event['date'], '%Y-%m').strftime('%b %Y')
        p['dateLabel'] = f'{p["eventKind"].capitalize()} {month}'
    papers.sort(key=lambda p: p['eventDate'], reverse=True)
    rows = []
    for i, p in enumerate(papers, 1):
        authors = ', '.join(f'<strong>{esc(a)}</strong>' if a == 'Sizhuo Zhou' else esc(a) for a in p['authors'])
        status = '<span class="forthcoming">Accepted · publication forthcoming</span>' if p.get('publicationStatus') == 'forthcoming' else ''
        if p.get('image'):
            if not (ROOT / p['image']).is_file():
                raise FileNotFoundError(p['image'])
            # Crop the preview in CSS, keeping the original accessible on click.
            iw, ih = p['imageSize']
            x, y, w, h = p.get('imageCrop', [0, 0, iw, ih])
            if not (0 <= x < iw and 0 <= y < ih and w > 0 and h > 0 and x + w <= iw and y + h <= ih):
                raise ValueError(f'Invalid image crop: {p["id"]}')
            crop_style = f'--figure-ratio:{w}/{h};--image-width:{iw/w*100:.5f}%;--image-height:{ih/h*100:.5f}%;--image-left:{-x/w*100:.5f}%;--image-top:{-y/h*100:.5f}%'
            figure = f'<a class="paper-figure" style="{crop_style}" href="{esc(p["image"])}" target="_blank" rel="noopener" aria-label="View full figure: {esc(p["title"])}"><img src="{esc(p["image"])}" alt="{esc(p["imageAlt"])}" width="{iw}" height="{ih}" loading="lazy" decoding="async"></a>'
        else:
            figure = '<div class="figure-placeholder" aria-label="Paper figure placeholder"><span>FIGURE FORTHCOMING</span></div>'
        date_label = f'<time class="paper-date" datetime="{p["eventDate"]}">{esc(p["dateLabel"])}</time>'
        venue_label = esc(p.get('venueLabel', f'{p["venue"]} {p["year"]}'))
        resource = (f'<a class="paper-link" href="{esc(p["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(p["linkLabel"] + ": " + p["title"])}">{esc(p["linkLabel"])} <span aria-hidden="true">↗</span></a>'
                    if p['url'] else ('' if status else '<span class="link-pending">Link forthcoming</span>'))
        rows.append(f'''<article class="publication" id="{p['id']}" data-venue="{esc(p['venue'])}">
          <span class="paper-number" aria-hidden="true">{i:02d}</span>
          {figure}
          <div class="paper-main"><div class="paper-meta"><span class="venue">{venue_label}</span><span class="track">{esc(p['track'])}</span>{date_label}</div>
          <h3>{esc(p['title'])}</h3><p class="authors">{authors}</p>{status}{resource}</div>
          <span class="paper-mark" aria-hidden="true">↗</span>
        </article>''')
    template = (ROOT / 'template.html').read_text()
    # Refresh cached assets whenever their contents change.
    for name, filename in [('STYLE_VERSION', 'style.css'), ('SCRIPT_VERSION', 'script.js')]:
        version = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()[:12]
        template = template.replace('{{' + name + '}}', version)
    updates = []
    for item in news:
        venue = esc(item['venue'])
        count = item['count']
        subject = f'<strong>{count} {"paper" if count == 1 else "papers"}</strong>'
        verb = 'has' if count == 1 else 'have'
        if item.get('kind') == 'published':
            sentence = f'{subject} {verb} been published in <strong>{venue}</strong>.'
        else:
            sentence = f'{subject} {verb} been accepted to <strong>{venue}</strong>.'
        updates.append(f'<li class="news-item"><time datetime="{esc(item["date"])}">{esc(item["date"].replace("-", "."))}</time><p><span class="news-celebration" aria-hidden="true">🎉🎉</span> {sentence}</p></li>')
    years = sorted({p['eventDate'][:4] for p in papers})
    date_range = years[0] if len(years) == 1 else f'{years[0]}–{years[-1]}'
    date_range_short = years[0] if len(years) == 1 else f'{years[0]}–{years[-1][2:]}'
    (ROOT / 'index.html').write_text(template.replace('<!-- PUBLICATIONS -->', '\n'.join(rows)).replace('<!-- NEWS -->', '\n'.join(updates)).replace('{{COUNT}}', str(len(papers))).replace('{{DATE_RANGE}}', date_range).replace('{{DATE_RANGE_SHORT}}', date_range_short))
    print(f'Built index.html: {len(papers)} papers and {len(news)} news items, newest first.')


def export_site(destination):
    """Copy only public website assets, never source PDFs or temporary files."""
    output = (ROOT / destination).resolve()
    if output != ROOT / '_site':
        raise ValueError('The deployment output must be _site')
    if output.exists():
        shutil.rmtree(output)
    papers = json.loads((ROOT / 'publications.json').read_text())
    paths = {'index.html', 'style.css', 'script.js', '.nojekyll',
             'assets/favicon.svg', 'assets/portrait.jpg'}
    paths.update(p['image'] for p in papers if p.get('image'))
    for name in sorted(paths):
        source = (ROOT / name).resolve()
        source.relative_to(ROOT)
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print(f'Exported {len(paths)} public files to {output}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import', dest='import_source', action='store_true')
    parser.add_argument('--output', choices=['_site'], help='Export the deployment bundle')
    args = parser.parse_args()
    if args.import_source:
        import_publications()
    build()
    if args.output:
        export_site(args.output)
