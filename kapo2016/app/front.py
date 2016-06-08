#-*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, session, flash, url_for, redirect, Blueprint
from flask.ext.session import Session
from flask.ext.login import login_required, login_user, logout_user, current_user, LoginManager
from sqlalchemy import desc
from databases import db_session
from time import time, mktime
from models import *
import config, string
from . import app

frontend = Blueprint('frontend', __name__)
loginmanager = LoginManager(app)
loginmanager.login_view = 'frontend.login'

debug = True


from datetime import datetime
@loginmanager.user_loader
def load_user(userid):
        return User.query.get(userid)

@frontend.route("/refill")
def refill():
    if current_user.is_admin:
        current_user.is_open_able = 1
    return redirect(url_for("frontend.prob"))

@frontend.route("/", methods=['GET', 'POST'])
def main():
    datetime(2015, 9, 5, 0, 0)
    start = mktime(datetime(2016, 9, 1, 0, 0).timetuple()) - time()
    if not debug and  start > 0:
        return render_template("count.html", left = start)

    problems = Problem.query.filter_by(is_open = True).filter_by(solver = 0).all()

    left = mktime(datetime(2016, 9, 5, 0, 0).timetuple()) - time()
    return render_template('main.html', pr = problems, left = left, notices = Notice.query.order_by(desc(Notice.id)).limit(5).all())

@frontend.route("/Notice")
def notice():
    return render_template("notice.html", notices = Notice.query.order_by(desc(Notice.id)).all())

@frontend.route("/rule")
def rule():
    return render_template("rule.html", rules = Rule.query.all())

@frontend.route("/prob")
@login_required
def prob():
    problems = Problem.query.all()
    map(lambda x: x.update_score(), problems)
    prs = {}
    for key in config.category:
        prs[key] = []

    for i in problems:
        prs[i.category].append(i)

    return render_template("prob.html", pr = prs, categories = config.category)

@frontend.route("/score")
def score():
    pass

@frontend.route("/login", methods=["GET", "POST"])
def login():
    msg = None
    if request.method == "POST":
        c_user = User.query.filter_by(userid=request.form['username']).first()
        next = request.args.get('next') or url_for('frontend.main')
        if c_user and c_user.check_password(request.form['pw']):
            login_user(c_user)
            return redirect(next)
        else:
            msg = 'Login fail'
    return render_template("login.html", msg = msg)

@frontend.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("frontend.main"))

@frontend.route("/mypage")
@login_required
def mypage():
    pass

@frontend.route("/user/<int:_id>")
@login_required
def show_user(_id):
    user = User.query.filter_by(id=_id).first()
    if not user:
        return redirect(url_for('frontend.main'))
    return render_template('show_user.html', user = user)

@frontend.route("/show/<int:_id>", methods=["GET", "POST"])
@login_required
def show(_id):
    problem = Problem.query.filter_by(id=_id).first()
    msg = ""
    if request.method == "POST" and 'flag' in request.form.keys():
        if problem.check_flag(request.form['flag']):
            if problem.solver == 0:
                notice = Notice("Wow! <a href=\"%s\">%s</a> <span class=\"red-text\">break</span> <a href=\"%s\"><b>[%s]</b>%s</a>!!!!" %(url_for('frontend.show_user', _id=current_user.id), current_user.userid, url_for('frontend.show', _id = problem.id), problem.category, problem.name))
                db_session.add(notice)
                db_session.commit()
            problem.add_solver(current_user)
            msg = "Good!"
        else:
            msg = "Wrong!"

    if not problem.is_open:
        return redirect(url_for("frontend.prob"))
    problem.update_score()

    return render_template("show_prob.html", problem = problem, msg = msg)

@frontend.route("/unhot/<int:_id>")
@login_required
def unhot(_id):
    problem = Problem.query.filter_by(id=_id).first()

    if not problem.is_open or not current_user.is_admin:
        return redirect(url_for("frontend.prob"))

    problem.is_hot = False
    db_session.commit()
    return redirect(url_for("frontend.prob"))

@frontend.route("/open/<int:_id>")
@login_required
def open(_id):
    problem = Problem.query.filter_by(id=_id).first()

    if problem.is_open or current_user.is_open_able <= 0:
        return redirect(url_for("frontend.prob"))

    problem.open()
    current_user.is_open_able -= 1

    if not current_user.is_admin:
        notice = Notice("<a href=\"%s\">%s</a> open <a href=\"%s\"><b>[%s]</b>%s</a>!" %(url_for('frontend.show_user', _id=current_user.id), current_user.userid, url_for('frontend.show', _id = problem.id), problem.category, problem.name))
    else:
        problem.is_hot = False
        notice = Notice("<a href=\"%s\"><b>[%s]</b>%s</a> open!" %(url_for('frontend.show', _id = problem.id), problem.category, problem.name))
    db_session.add(notice)
    db_session.commit()

    return redirect(url_for("frontend.prob"))
