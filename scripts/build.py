#!/usr/bin/env python3
"""Generate portable GitHub Pages HTML using only the Python standard library."""
import argparse
import html
import json
import re
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
STYLE = '''body{margin:0;background:#f5f3ee;color:#232d27;font:18px/1.65 system-ui,sans-serif}main{max-width:900px;margin:auto;padding:48px 24px 64px}a{color:#205e43}h1{font-size:clamp(2.6rem,8vw,5rem);line-height:1.02;letter-spacing:-.045em}h2{line-height:1.25;letter-spacing:-.02em}nav a{margin-right:20px}.hero{padding:72px 0 48px}.eyebrow{color:#52725b;font-size:14px;font-weight:750;letter-spacing:.14em;text-transform:uppercase}.hero h1{max-width:760px;margin:14px 0 20px}.tagline{max-width:690px;color:#476251;font-size:clamp(1.25rem,3vw,1.7rem);line-height:1.45}.lead{max-width:720px}.feature-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,235px),1fr));gap:16px;margin:28px 0 52px}.feature-card,article{background:#fff;border:1px solid #deded4;border-radius:18px;padding:24px}.feature-card h3{margin:0 0 8px;font-size:1.16rem}.feature-card p,article p{margin:0;color:#59645b}.marketing-section{padding:32px 0;border-top:1px solid #d8d8ce}.steps{list-style:none;padding:0;counter-reset:step}.steps li{counter-increment:step;position:relative;padding:16px 16px 16px 64px;margin:12px 0;background:#ebece2;border-radius:14px}.steps li:before{content:counter(step);position:absolute;left:18px;top:15px;display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#41684f;color:white;font-weight:700}.note{padding:20px 24px;background:#e3eadb;border-radius:16px;color:#35533f}.app-links{padding:20px 0 4px}article{margin:24px 0}footer{margin-top:64px;border-top:1px solid #ccc;padding-top:24px;font-size:15px}p{overflow-wrap:anywhere}.language-switch{display:flex;gap:8px;margin:24px 0}.language-switch button{border:1px solid #205e43;border-radius:999px;background:white;color:#205e43;font:inherit;font-size:16px;padding:8px 16px;cursor:pointer}.language-switch button[aria-pressed="true"]{background:#205e43;color:white}:focus-visible{outline:3px solid #bf692c;outline-offset:4px}@media(max-width:560px){main{padding:28px 18px 48px}.hero{padding:48px 0 32px}.feature-card{padding:20px}}'''


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


def render_sections(sections):
    if not isinstance(sections, list) or not sections:
        raise ValueError('Policy language needs reviewed sections')
    text = ''
    for section in sections:
        if not isinstance(section, list) or len(section) < 2 or any(not isinstance(x, str) or not x.strip() for x in section):
            raise ValueError('Malformed policy section')
        text += '<section id="' + esc(anchor(section[0])) + '"><h2>' + esc(section[0]) + '</h2>' + ''.join('<p>' + esc(p) + '</p>' for p in section[1:]) + '</section>'
    return text


def render_policy(app, kind, policy):
    if not isinstance(policy, dict) or not isinstance(policy.get('updated'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', policy['updated']):
        raise ValueError(f"{app['id']}: {kind} requires updated YYYY-MM-DD")
    title = 'Privacy Policy' if kind == 'privacy' else 'Terms'
    body = f'<h1>{esc(app["name"])} — {title}</h1><p>Updated: {esc(policy["updated"])}</p>'

    languages = policy.get('languages')
    if languages is None:
        sections = policy.get('sections')
        body += render_sections(sections)
    else:
        if not isinstance(languages, dict) or 'en' not in languages:
            raise ValueError(f"{app['id']}: {kind}.languages must include English ('en')")
        codes = ['en'] + [code for code in languages if code != 'en']
        if any(not isinstance(code, str) or not re.fullmatch(r'[a-z]{2}', code) for code in codes):
            raise ValueError(f"{app['id']}: invalid {kind} language code")
        controls = ''
        content = ''
        for index, code in enumerate(codes):
            language = languages[code]
            if not isinstance(language, dict) or not isinstance(language.get('label'), str) or not language['label'].strip():
                raise ValueError(f"{app['id']}: {kind}.{code} requires a language label")
            selected = index == 0
            controls += f'<button type="button" data-language-choice="{esc(code)}" aria-pressed="{str(selected).lower()}">{esc(language["label"])}</button>'
            content += f'<div data-policy-language="{esc(code)}" lang="{esc(code)}"' + ('' if selected else ' hidden') + '>' + render_sections(language.get('sections')) + '</div>'
        body += '<div class="language-switch" role="group" aria-label="Policy language">' + controls + '</div>'
        body += '<div data-policy-languages>' + content + '</div>'
        body += '''<script>
document.querySelectorAll('[data-language-choice]').forEach(button => {
  button.addEventListener('click', () => {
    const selected = button.dataset.languageChoice;
    document.querySelectorAll('[data-language-choice]').forEach(option => {
      option.setAttribute('aria-pressed', String(option === button));
    });
    document.querySelectorAll('[data-policy-language]').forEach(content => {
      content.hidden = content.dataset.policyLanguage !== selected;
    });
    document.documentElement.lang = selected;
  });
});
</script>'''

    body += '<p><a href="../support/">Contact support</a></p>'
    return page(f"{app['name']} — {title}", body, '../../../')


def render_marketing(app):
    marketing = app.get('marketing')
    if marketing is None:
        links = '<a href="support/">Support</a>'
        for kind, title in (('privacy', 'Privacy Policy'), ('terms', 'Terms')):
            if app.get(kind) is not None:
                links += ' · <a href="' + kind + '/">' + title + '</a>'
        return f'<h1>{esc(app["name"])}</h1><p>{esc(app["platform"])}</p><p>{esc(app["summary"])}</p><nav aria-label="App pages">{links}</nav>'
    for key in ('eyebrow', 'tagline', 'intro', 'closing'):
        if not isinstance(marketing.get(key), str) or not marketing[key].strip():
            raise ValueError(f'{app["id"]}: marketing.{key} must be a nonempty string')
    highlights = marketing.get('highlights')
    steps = marketing.get('steps')
    if not isinstance(highlights, list) or not highlights or not isinstance(steps, list) or not steps:
        raise ValueError(f'{app["id"]}: marketing needs highlights and steps')
    if any(not isinstance(item, list) or len(item) != 2 or any(not isinstance(x, str) or not x.strip() for x in item) for item in highlights + steps):
        raise ValueError(f'{app["id"]}: malformed marketing highlight or step')

    body = '<header class="hero"><p class="eyebrow">' + esc(marketing['eyebrow']) + '</p>'
    body += '<h1>' + esc(app['name']) + '</h1><p class="tagline">' + esc(marketing['tagline']) + '</p>'
    body += '<p class="lead">' + esc(marketing['intro']) + '</p><p>' + esc(app['platform']) + '</p></header>'
    body += '<section aria-label="Game highlights" class="feature-grid">'
    for title, description in highlights:
        body += '<article class="feature-card"><h3>' + esc(title) + '</h3><p>' + esc(description) + '</p></article>'
    body += '</section><section class="marketing-section"><h2>' + esc(marketing.get('story_heading', 'About the game')) + '</h2>'
    body += '<p>' + esc(marketing['story']) + '</p></section>' if marketing.get('story') else ''
    body += '<section class="marketing-section"><h2>How to play</h2><ol class="steps">'
    for title, description in steps:
        body += '<li><strong>' + esc(title) + '</strong><br>' + esc(description) + '</li>'
    body += '</ol></section><p class="note">' + esc(marketing['closing']) + '</p>'
    body += '<nav aria-label="App pages" class="app-links"><a href="support/">Support</a>'
    for kind, title in (('privacy', 'Privacy Policy'), ('terms', 'Terms')):
        if app.get(kind) is not None:
            body += ' · <a href="' + kind + '/">' + title + '</a>'
    body += '</nav>'
    return body


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
            title = 'Privacy Policy' if kind == 'privacy' else 'Terms'
            files[f'apps/{app_id}/{kind}/index.html'] = render_policy(app, kind, policy)
            links += f' · <a href="{kind}/">{title}</a>'
        files[f'apps/{app_id}/index.html'] = page(app['name'], render_marketing(app), '../../')
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
