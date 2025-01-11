from flask import *

from website import db
from website.models import *
from datetime import datetime

bp = Blueprint('views', __name__, url_prefix='/')

@bp.app_errorhandler(404)
def _404(e):
    return render_template("404.html", err='hello em')

@bp.route('/')
def home():
    return render_template('index.html')

def float_to_date(value:float):
    return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')

@bp.route('/search')
def search():
    words = request.args.get('q', '').upper().strip().split()
    if not words: return redirect(url_for('views.home'))
    page = request.args.get('p', 1, type=int)
    
    url_results = set()
    word_objs = Word.query.filter(Word.word.in_(words)).all()
    for word_obj in word_objs: url_results.update(word_obj.urls)

    filtered = Hyperlinks.query.filter(Hyperlinks.url.in_(url_results))
    total_results = filtered.count()
    results = filtered.order_by(Hyperlinks.rate.desc()).paginate(page=page, per_page=20, error_out=False)
    total_pages = (total_results + 19) // 20  # Calculate total pages based on per_page value
    
    return render_template('search.html', results=results, page=page, query=request.args.get('q', ''), total_pages=total_pages, float_to_date=float_to_date)

# @bp.route('/u/')
# @bp.route('/u/<string:username>')
# def user(username=None):
#     if username: user = User.query.filter_by(username=username).first()
#     else:
#         if not current_user.is_authenticated: return redirect('views.home')
#         user = current_user

#     avatar = libgravatar.Gravatar(user.email).get_image()
#     return render_template('user.html', user=user, avatar=avatar)
