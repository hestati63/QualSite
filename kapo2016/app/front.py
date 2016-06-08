#-*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, session, flash, url_for, redirect, Blueprint
from flask.ext.session import Session
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
    session['user'].is_open_able += 1
    return redirect(url_for("frontend.main"))

@frontend.route("/", methods=['GET', 'POST'])
def main():
    start = mktime(datetime(2016, 9, 1, 0, 0).timetuple()) - time()
    if not debug and  start > 0:
        return render_template("count.html", left = start)

    problems = models.Problem.query.filter_by(is_open = True).filter_by(solver = 0).all()

    left = mktime(datetime(2016, 9, 5, 0, 0).timetuple()) - time()

    return render_template('main.html', pr = problems, left = left)

@frontend.route("/rule")
def rule():
    return render_template("rule.html")

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
    db_session.commit()
    return redirect(url_for("frontend.prob"))
