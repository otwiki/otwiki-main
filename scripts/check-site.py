#!/usr/bin/env python3
"""Check the rendered wiki and the migration errors that previously broke it."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.resources = path, set(), [], []
        self.main, self.proofs = False, []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'main':
            self.main = True
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                errors.append(f'{self.path.name}: duplicate ID {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag in ('ref', 'references', 'math'):
            errors.append(f'{self.path.name}: unsupported legacy <{tag}> element')
        if 'quarto-unresolved-ref' in attrs.get('class', '').split():
            errors.append(f'{self.path.name}: unresolved Quarto reference')
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('img', 'script', 'iframe') and 'src' in attrs:
            self.resources.append(attrs['src'])
        if tag == 'link' and 'href' in attrs:
            self.resources.append(attrs['href'])
        if self.main and tag == 'div':
            proof = 'proof' in attrs.get('class', '').split()
            if proof and any(self.proofs):
                errors.append(f'{self.path.name}: a proof is nested inside another proof')
            self.proofs.append(proof)

    def handle_endtag(self, tag):
        if tag == 'main':
            self.main = False
        if self.main and tag == 'div' and self.proofs:
            self.proofs.pop()

sources = sorted(ROOT.glob('*.qmd'))
for source in sources:
    text = source.read_text(encoding='utf-8')
    for label, pattern in {
        'legacy wiki tag': r'<(?:math|ref|references)\b',
        'retired wiki address': r'34\.106\.105\.83|https?://(?:www\.)?otwiki\.xyz/wiki/',
        'placeholder link': r'\]\(add_link\)',
        'escaped wiki link': r'\\\[\\\[',
        'escaped external link': r'\\\[https?://',
        'escaped heading': r'\\#{2,}',
        'citation hidden in comment': r'<!--\s*\[@citation\]',
        'raw LaTeX hyperlink or citation': r'\\(?:href|cite)\{',
    }.items():
        if re.search(pattern, text):
            errors.append(f'{source.name}: {label}')
    if not (SITE / (source.stem + '.html')).is_file():
        errors.append(f'{source.name}: rendered page is missing')

pages = {p.resolve(): Page(p) for p in SITE.rglob('*.html')}
for path, page in pages.items():
    for href in page.links + page.resources:
        url = urlsplit(urljoin('https://www.otwiki.xyz/' + path.relative_to(SITE).as_posix(), href))
        if url.scheme not in ('http', 'https') or url.netloc not in ('www.otwiki.xyz', 'otwiki.xyz'):
            continue
        target = SITE / unquote(url.path).lstrip('/')
        if target.is_dir():
            target /= 'index.html'
        elif not target.exists() and not target.suffix:
            target = target.with_suffix('.html')
        if not target.is_file():
            errors.append(f'{path.name}: missing local target {href}')
            continue
        fragment = unquote(url.fragment)
        if fragment and target.suffix == '.html' and not fragment.startswith('mjx-'):
            target_page = pages.get(target.resolve())
            if not target_page or fragment not in target_page.ids:
                errors.append(f'{path.name}: missing anchor {href}')

for filename, expected in [('CNAME', 'www.otwiki.xyz')]:
    if not (SITE / filename).is_file() or (SITE / filename).read_text().strip() != expected:
        errors.append(f'{filename}: rendered custom-domain configuration is missing or incorrect')
if not (SITE / '.nojekyll').is_file():
    errors.append('The rendered .nojekyll file is missing')
if errors:
    print('\n'.join(sorted(set(errors))), file=sys.stderr)
    sys.exit(1)
print(f'Passed: {len(sources)} pages, internal links, citations, resources, and source markup.')
