from flask import Blueprint, render_template, request
from flask_paginate import Pagination, get_page_parameter
from recipe.adapters.memory_repo import MemoryRepository

browse_bp = Blueprint('browse', __name__)
repo = MemoryRepository()

@browse_bp.route('/browse')
def browse():
    all_recipes = repo.get_all_recipes()
    sort_by = request.args.get('sort', 'name')
    # if sort_by == 'name':
    #     all_recipes.sort(key=lambda r: r.name.lower())
    # elif sort_by =='cooking_time':
    #     all_recipes.sort(key=lambda r: r.created_date.)
    all_recipes.sort(key=lambda r: r.name.lower())
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    paginated_recipes = all_recipes[offset:offset + per_page]

    pagination = Pagination(page=page, total=len(all_recipes), per_page=per_page, css_framework='bootstrap5')
    return render_template('browse.html', recipes=paginated_recipes, pagination=pagination)

@browse_bp.route('/search')
def search():
    query = request.args.get('query', '')
    criteria = request.args.get('criteria', 'name')
    
    if criteria == 'name':
        results = repo.find_by_name(query)
    elif criteria == 'category':
        results = repo.find_by_category(query)
    elif criteria == 'author':
        results = repo.find_by_author(query)
    else:
        results = []
    
    back_url = '/browse'

    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    paginated_results = results[offset:offset + per_page]

    pagination = Pagination(page=page, total=len(results), per_page=per_page, css_framework='bootstrap5')
    return render_template('search_results.html', query=query, criteria=criteria, results=paginated_results, pagination=pagination, back_url=back_url)