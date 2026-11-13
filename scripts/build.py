#!/usr/bin/env python3
"""Generate portable GitHub Pages HTML using only the Python standard library."""
import argparse
import html
import json
import re
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
STYLE = '''body{margin:0;background:#f5f3ee;color:#232d27;font:18px/1.65 system-ui,sans-serif}main{max-width:900px;margin:auto;padding:64px 24px}a{color:#205e43}h1{font-size:clamp(2.4rem,8vw,4rem);line-height:1.1}h2{line-height:1.3}article{background:white;border:1px solid #deded4;border-radius:16px;padding:24px;margin:24px 0}nav a{margin-right:20px}footer{margin-top:64px;border-top:1px solid #ccc;padding-top:24px;font-size:15px}p{overflow-wrap:anywhere}:focus-visible{outline:3px solid #bf692c;outline-offset:4px}'''


def esc(value):
    return html.escape(value, quote=True)


def anchor(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')


def page(title, body, home):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · Lucky Studio</title><style>{STYLE}</style></head>
<body><main><nav aria-label="Main navigation"><a href="{home}">Lucky Studio</a></nav>{body}<footer>Lucky Studio · <a href="tel:+821083312512">+821083312512</a></footer></main></body></html>
'''


def render(apps):
    if not isinstance(apps, list):
        raise ValueError('content/apps.json must be an array')
    files = {'.nojekyll': ''}
    cards = []
    seen = set()
    for app in apps:
        app_id = app['id']
        if not isinstance(app_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', app_id) or app_id in seen:
            raise ValueError(f'Invalid or duplicate immutable app ID: {app_id!r}')
        seen.add(app_id)
        for key in ('name', 'summary', 'platform'):
            if not isinstance(app[key], str) or not app[key].strip():
                raise ValueError(f'{app_id}: {key} must be a nonempty string')
        name = esc(app['name'])
        links = '<a href="support/">Support</a>'
        for kind in ('privacy', 'terms'):
            policy = app.get(kind)
            if policy is None:
                continue
            if not isinstance(policy, dict) or not isinstance(policy.get('updated'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', policy['updated']):
                raise ValueError(f'{app_id}: {kind} requires updated YYYY-MM-DD')
            sections = policy['sections']
            if not isinstance(sections, list) or not sections:
                raise ValueError(f'{app_id}: {kind} needs reviewed sections')
            text = ''
            for section in sections:
                if not isinstance(section, list) or len(section) < 2 or any(not isinstance(x, str) or not x.strip() for x in section):
                    raise ValueError(f'{app_id}: malformed {kind} section')
                text += '<section id="' + esc(anchor(section[0])) + '"><h2>' + esc(section[0]) + '</h2>' + ''.join('<p>' + esc(p) + '</p>' for p in section[1:]) + '</section>'
            title = 'Privacy Policy' if kind == 'privacy' else 'Terms'
            files[f'apps/{app_id}/{kind}/index.html'] = page(f"{app['name']} — {title}", f'<h1>{name} — {title}</h1><p>Updated: {esc(policy["updated"])}</p>{text}<p><a href="../support/">Contact support</a></p>', '../../../')
            links += f' · <a href="{kind}/">{title}</a>'
        files[f'apps/{app_id}/index.html'] = page(app['name'], f'<h1>{name}</h1><p>{esc(app["platform"])}</p><p>{esc(app["summary"])}</p><nav aria-label="App pages">{links}</nav>', '../../')
        email = app.get('support_email')
        if email is not None and (not isinstance(email, str) or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email)):
            raise ValueError(f'{app_id}: support_email must be a valid email address')
        contact = '<a href="tel:+821083312512">+821083312512</a>'
        if email:
            contact += ' or <a href="mailto:' + esc(email) + '">' + esc(email) + '</a>'
        files[f'apps/{app_id}/support/index.html'] = page(f"{app['name']} support", f'<h1>{name} support</h1><p>Contact Lucky Studio at {contact}.</p><p>Please include the app version, device model, and a description of the issue.</p><p><a href="../">Back to {name}</a></p>', '../../../')
        cards.append(f'<article><h2><a href="apps/{app_id}/">{name}</a></h2><p>{esc(app["summary"])}</p><p>{esc(app["platform"])}</p></article>')
    catalog = ''.join(cards) if cards else '<p>App pages will appear here as they become available.</p>'
    files['index.html'] = page('Apps & games', '<p>APPS & GAMES</p><h1>Lucky Studio</h1><p>Official app information, support, and policies in one place.</p>' + catalog + '<p><a href="support/">Contact support</a></p>', './')
    files['support/index.html'] = page('Support', '<h1>How can we help?</h1><p>For app support, contact Lucky Studio at <a href="tel:+821083312512">+821083312512</a>.</p><p>Tell us the app name, version, device model, and what happened.</p>', '../')
    files['404.html'] = page('Page not found', '<h1>Page not found</h1><p>The page may have moved. <a href="/lucky-studio-pages/">Browse Lucky Studio apps</a>.</p>', '/lucky-studio-pages/')
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check generated output without writing')
    args = parser.parse_args()
    files = render(json.loads((ROOT / 'content/apps.json').read_text(encoding='utf-8')))
    target = ROOT / 'docs'
    actual = {str(p.relative_to(target)): p.read_text(encoding='utf-8') for p in target.rglob('*') if p.is_file()} if target.exists() else {}
    # Removing routes requires a deliberate migration, never silently delete URLs.
    removed = set(actual) - set(files)
    if removed:
        raise SystemExit('Existing routes would disappear; preserve them or plan redirects: ' + ', '.join(sorted(removed)))
    if args.check:
        if actual != files:
            raise SystemExit('Generated docs are out of date. Run python3 scripts/build.py')
        print(f'OK: {len(files)} generated files are current')
        return
    for name, body in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf-8')
    print(f'Built {len(files)} files in docs/')


if __name__ == '__main__':
    main()
