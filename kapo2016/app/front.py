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
    start = mktime(datetime(2016, 9, 1, 0, 0).timetuple()) - time()
    if not debug and start > 0:
        return render_template("count.html", left = start)

    problems = Problem.query.filter_by(is_open = True).filter_by(is_hot = True).all()

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

@frontend.route("/signup", methods=["GET", "POST"])
def signup():
    msg = ""
    try:
        if request.method == "POST":
            username = request.form['username']
            pw = request.form['pw']
            pwchk = request.form['pwchk']
            name = request.form['name']
            eyear = request.form['eyear']
            if not eyear in ["0", "1"]:
                msg = "no Troll"
            elif not all(map(lambda x: x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_', username)):
                msg = "Not allowed character in id"
            elif len(pw) < 5:
                msg = "password should be longer than 5 letters"
            elif pw == pwchk:
                if config.registkey == request.form['regkey']:
                    chk = User.query.filter_by(userid = username).first()
                    if chk:
                        msg = "user already exists"
                    else:
                        user = User(username, pw, name, eyear)
                        db_session.add(user)
                        db_session.commit()
                        return redirect(url_for("frontend.login"))
                else:
                    msg = "wrong regist key"
            else:
                msg = "password and password check is differ"
    except:
        msg = "empty field"

    return render_template("signup.html", msg = msg)

@frontend.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
    if not current_user.is_admin: return redirect(url_for("frontend.main"))
    msg = ""
    if request.method == "POST":
        notice = Notice(request.form["notice"])
        db_session.add(notice)
        db_session.commit()
        msg = "notice added"

    return render_template("admin.html", msg = msg)

@frontend.route("/mypage", methods=["POST", "GET"])
@login_required
def mypage():
    if current_user.is_admin:
        return redirect(url_for("frontend.admin"))
    else:
        msg = ""
        try:
            if request.method == "POST":
                cpw = request.form['cpw']
                pw = request.form['pw']
                pwchk = request.form['pwchk']
                name = request.form['name']
                if current_user.check_password(cpw):
                    if len(pw) < 5:
                        msg = "password should be longer than 5 letters"
                    elif pw == pwchk:
                        current_user.name = name
                        current_user.set_password(pw)
                        db_session.commit()
                        msg = "data successfully update"
                    else:
                        msg = "password and password check is differ"
                else:
                    msg = "wrong current password"
        except:
            msg = "something wrong"

        return render_template("mypage.html", msg = msg)

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
            msg = "Good!"
            if problem.solver == 0:
                notice = Notice("Wow! <a href=\"%s\">%s</a> <span class=\"red-text\">break</span> <a href=\"%s\"><b>[%s]</b>%s</a>!!!!" %(url_for('frontend.show_user', _id=current_user.id), current_user.userid, url_for('frontend.show', _id = problem.id), problem.category, problem.name))
                db_session.add(notice)
                db_session.commit()
                msg = "U got Breakthrough!!! Plz open new problem!!!"
            problem.add_solver(current_user)
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
