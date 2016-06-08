#-*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, session, flash, url_for, redirect, Blueprint
from flask.ext.session import Session
from sqlalchemy import desc
import models
from databases import db_session
import config
from datetime import datetime
from time import time, mktime
import string

frontend = Blueprint('frontend', __name__)
debug = True

@frontend.route("/refill")
def refill():
    if session['user'].is_admin:
        session['user'].is_open_able += 1
    return redirect(url_for("frontend.prob"))

@frontend.route("/", methods=['GET', 'POST'])
def main():
    start = mktime(datetime(2016, 9, 1, 0, 0).timetuple()) - time()
    if not debug and  start > 0:
        return render_template("count.html", left = start)

    problems = models.Problem.query.filter_by(is_open = True).filter_by(solver = 0).all()

    left = mktime(datetime(2016, 9, 5, 0, 0).timetuple()) - time()

    return render_template('main.html', pr = problems, left = left, notices = models.Notice.query.order_by(desc(models.Notice.id)).limit(5).all())

@frontend.route("/Notice")
def notice():
    return render_template("notice.html", notices = models.Notice.query.order_by(desc(models.Notice.id)).all())

@frontend.route("/rule")
def rule():
    return render_template("rule.html", rules = models.Rule.query.all())

@frontend.route("/prob")
def prob():
    if not 'user' in session.keys() or not session['user']: return redirect(url_for("frontend.login"))
    problems = models.Problem.query.all()
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
        c_user = models.User.query.filter_by(userid=request.form['username']).first()
        if c_user and c_user.check_password(request.form['pw']):
            session['is_login'] = True
            session['user'] = c_user
            return redirect(url_for('frontend.main'))
        else:
            msg = 'Login fail'
    return render_template("login.html", msg = msg)

@frontend.route("/logout")
def logout():
    session['is_login'] = False
    session['user'] = None
    return redirect(url_for("frontend.main"))

@frontend.route("/mypage")
def mypage():
    pass

@frontend.route("/user/<int:_id>")
def show_user(_id):
    user = models.User.query.filter_by(id=_id).first()
    if not user:
        return redirect(url_for('frontend.main'))
    return render_template('show_user.html', user = user)

@frontend.route("/show/<int:_id>")
def show(_id):
    problem = models.Problem.query.filter_by(id=_id).first()
    if not problem.is_open:
        return redirect(url_for("frontend.prob"))
    problem.update_score()
    return render_template("show_prob.html", problem = problem)

@frontend.route("/open/<int:_id>")
def open(_id):
    problem = models.Problem.query.filter_by(id=_id).first()

    if not session['user'].is_admin and problem.is_open or session['user'].is_open_able <= 0:
        return redirect(url_for("frontend.prob"))

    problem.is_open = True
    session['user'].is_open_able -= 1

    if not session['user'].is_admin:
        notice = models.Notice("<a href=\"%s\">%s</a> open <a href=\"%s\"><b>[%s]</b>%s</a>!" %(url_for('frontend.show_user', _id=session['user'].id), session['user'].userid, url_for('frontend.show', _id = problem.id), problem.category, problem.name))
    else:
        notice = models.Notice("<a href=\"%s\"><b>[%s]</b>%s</a> open!" %(url_for('frontend.show', _id = problem.id), problem.category, problem.name))
    db_session.add(notice)
    db_session.commit()

    return redirect(url_for("frontend.prob"))
