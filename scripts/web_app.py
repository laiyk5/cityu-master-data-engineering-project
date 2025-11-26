"""
Simple Flask web app to display articles read from PostgreSQL via src/db_utils.DatabaseReader

Run:
  python scripts/web_app.py

Open http://127.0.0.1:5000/articles
"""
from flask import Flask, render_template, request, jsonify
import os
import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # project root
from psycopg2.extras import RealDictCursor

from typing import List, Dict

from atss.db_utils import ArticleStorage

# Serve templates from project-level templates/ and static assets from project-level static/
app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static')),
)

from atss import logger


@app.route('/')
def index():
    return "Go to /articles to view the articles UI"


@app.route('/articles')
def articles_page():
    q = request.args.get('q', '').strip()
    # pagination params
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', request.args.get('limit', 5))
    sort_by = request.args.get('sort_by', 'published_date')
    sort_dir = request.args.get('sort_dir', 'desc')
    try:
        page = int(page)
    except:
        page = 1

    try:
        per_page = int(per_page)
    except:
        per_page = 25

    # normalize
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 25

    reader = ArticleStorage()
    try:
        offset = (page - 1) * per_page
        if q:
            total = reader.get_article_count_by_query(q)
            articles = reader.get_articles_by_query_with_sort(q, limit=per_page, offset=offset, sort_by=sort_by, sort_dir=sort_dir)
        else:
            total = reader.get_article_count()
            articles = reader.get_all_articles_with_sort_and_offset(limit=per_page, offset=offset, sort_by=sort_by, sort_dir=sort_dir)
    finally:
        reader.close()

    total_pages = max(1, (total + per_page - 1) // per_page)

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
    }

    # pass pagination/sort state back to the template so headers can toggle
    return render_template('articles.html', articles=articles, q=q, per_page=per_page, page=page, sort_by=sort_by, sort_dir=sort_dir, pagination=pagination)


@app.route('/api/articles')
def api_articles():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', request.args.get('limit', 25))
    sort_by = request.args.get('sort_by', 'published_date')
    sort_dir = request.args.get('sort_dir', 'desc')
    try:
        page = int(page)
    except:
        page = 1

    try:
        per_page = int(per_page)
    except:
        per_page = 25

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 25

    storage = ArticleStorage()
    try:
        offset = (page - 1) * per_page
        if q:
            total = storage.get_article_count_by_query(q)
            articles = storage.get_articles_by_query_with_sort(q, limit=per_page, offset=offset, sort_by=sort_by, sort_dir=sort_dir)
        else:
            total = storage.get_article_count()
            articles = storage.get_all_articles_with_sort_and_offset(limit=per_page, offset=offset, sort_by=sort_by, sort_dir=sort_dir)
    finally:
        storage.close()

    total_pages = max(1, (total + per_page - 1) // per_page)

    return jsonify({
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
        },
        'data': articles,
    })


if __name__ == '__main__':
    # Allow host and port from env
    host = os.getenv('WEB_HOST', '127.0.0.1')
    port = int(os.getenv('WEB_PORT', '5000'))
    debug = os.getenv('WEB_DEBUG', '1') != '0'
    app.run(host=host, port=port, debug=debug)
