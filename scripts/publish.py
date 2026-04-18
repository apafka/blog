#!/usr/bin/env python3
import sys
import re
import os

def parse_post(filepath):
    with open(filepath) as f:
        content = f.read()
    fm = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not fm:
        raise ValueError(f"No frontmatter found in {filepath}")
    meta, body = fm.group(1), fm.group(2).strip()
    title = re.search(r'^title:\s*(.+)$', meta, re.MULTILINE).group(1).strip()
    date = re.search(r'^date:\s*(.+)$', meta, re.MULTILINE).group(1).strip()
    return title, date, body

def to_html_paragraphs(text, indent='        '):
    return '\n'.join(
        f'{indent}<p>{p.strip()}</p>'
        for p in text.split('\n\n') if p.strip()
    )

def slugify(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

def make_post_html(title, date, body_html, slug):
    return f"""<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/style.css">
  <title>{title} — Alan Pafka</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta charset="utf-8">
</head>
<body class="post">
  <header>
    <h1 style="text-align:center"><a href="/" style="text-decoration:none;color:inherit">ALAN PAFKA</a></h1>
    <p><a href="/">← Home</a></p>
  </header>
  <article>
    <div class="post-date">{date}</div>
    <h2>{title}</h2>
    <div class="post-body">
{body_html}
    </div>
  </article>
</body>
</html>"""

def update_index(title, date, slug, body_html):
    with open('index.html') as f:
        html = f.read()

    # Find current featured post's title and href to demote it
    old = re.search(
        r'<article>.*?<h2><a href="([^"]+)">([^<]+)</a></h2>.*?</article>',
        html, re.DOTALL
    )

    new_article = f"""    <article>
      <div class="post-date">{date}</div>
      <h2><a href="/posts/{slug}.html">{title}</a></h2>
      <div class="post-body">
{body_html}
      </div>
    </article>"""

    # Replace the article block
    html = re.sub(r'<article>.*?</article>', new_article, html, flags=re.DOTALL)

    # Prepend old post as first <li> in Previously list
    if old:
        old_href, old_title = old.group(1), old.group(2)
        new_li = f'        <li><a href="{old_href}">{old_title}</a></li>\n'
        html = html.replace('<ul>\n', f'<ul>\n{new_li}', 1)

    with open('index.html', 'w') as f:
        f.write(html)

def main():
    md_file = sys.argv[1]
    title, date, body = parse_post(md_file)
    slug = slugify(title)
    body_html = to_html_paragraphs(body)

    os.makedirs('posts', exist_ok=True)
    post_path = f'posts/{slug}.html'
    with open(post_path, 'w') as f:
        f.write(make_post_html(title, date, body_html, slug))

    update_index(title, date, slug, body_html)
    print(f"Published: {post_path}")

if __name__ == '__main__':
    main()
