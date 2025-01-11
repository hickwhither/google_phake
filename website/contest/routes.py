from flask import *
from flask_login import current_user

from website import db
from website.models import *

from . import bp

from libgravatar import Gravatar
import markdown, markupsafe
import time
import math

current_user: User


@bp.route('/contests')
def contests():
    current_time: int = time.time()
    contests: list = Contest.query.all()
    active_contests = []
    upcoming_contests = []
    past_contests = []
    for i in contests:
        if current_time < i.start: upcoming_contests.append(i)
        elif current_time < i.start+i.length: active_contests.append(i)
        else: past_contests.append(i)
    
    
    return render_template("coding/contests.html", upcoming_contests=upcoming_contests,
                           past_contests=past_contests, active_contests=active_contests)

@bp.route('/c/<string:id>', methods=['GET', 'POST'])
def contest(id):
    current_time = time.time()
    contest: Contest = Contest.query.get(id)
    if not contest:
        flash("Contest not found.")
        return render_template("404.html")
    if request.method == 'POST':
        if not current_user.is_active: flash("You need to login first.")
        elif current_user.id in contest.participants: flash("You already in.")
        elif current_time >= contest.start+contest.length: flash("Register no longer avaiable")
        else:
            contest.participants['current_user.id'] = {
                'solved': [{'attemps': 0,'penalty': 0,'accept': False,} for i in range(len(contest.problems))],
                'penalty': 0,
            }
            db.session.commit()
            return redirect(url_for('coding.contest', id=id))
    
    return render_template('coding/contest.html', contest=contest, current_time = current_time,
                           description=markdown.markdown(markupsafe.escape(contest.description)))

@bp.route('/c/<string:id>/ranking', methods=['GET', 'POST'])
def ranking(id):
    contest: Contest = Contest.query.get(id)
    if not contest:
        flash("Contest not found.")
        return render_template("404.html")
    ranks = [[idx+1, User.query.get(i['id']), i['solved'], sum(1 if z['accept'] else 0 for z in i['solved']), i['penalty']] for idx, i in enumerate(contest.participants)]

    return render_template('coding/ranking.html', ranks=ranks, contest=contest)


@bp.route('/p/<string:id>', methods=['GET', 'POST'])
def participating(id, pid):
    current_time = time.time()
    contest: Contest = Contest.query.get(id)
    if not contest:
        flash("Contest not found.")
        return render_template("404.html")
    
    if current_time < contest.start:
        flash("Contest haven't start yet")
        return render_template("404.html")
    if current_time >= contest.start+contest.length:
        flash("Register no longer avaiable")
        return render_template("404.html")

    return render_template('coding/participating.html', contest=contest)
