#-*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, url_for, redirect, Blueprint, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc, asc
from time import time, mktime
from models import *
from forms import *
import config
from . import loginmanager, db_session, app

frontend = Blueprint('frontend', __name__)
loginmanager.login_view = 'frontend.login'

@frontend.route("/fonts/roboto/<path:path>")
def getfont(path):
    return send_from_directory("static/font/roboto", path)

@app.errorhandler(404)
def error404(err):
    return render_template("404.html"), 404

@loginmanager.user_loader
def load_user(userid):
    return User.query.get(userid) or abort(500)

@frontend.route("/", methods=['GET', 'POST'])
def main():
    start = mktime(config.game_start.timetuple()) - time()
    if start > 0:
        return render_template("count.html", left = start, notices = Notice.query.order_by(desc(Notice.id)).limit(5).all())

    problems = Problem.query.filter_by(open = True).filter_by(hot = True).all()

    left = mktime(config.game_end.timetuple()) - time()
    return render_template('main.html', pr = problems, left = left, notices = Notice.query.order_by(desc(Notice.id)).limit(5).all(), users = User.query.filter(User.admin != True).order_by(desc(User.score), asc(User.last_auth_success)).limit(10).all())

@frontend.route("/rank/", defaults={'restrict': 'all'})
@frontend.route("/rank/<string:restrict>")
@login_required
def rank(restrict):
    users = None
    if restrict != 'all':
        users = User.query.filter_by(admin = False).filter_by(_type = int(restrict) - 13).order_by(desc(User.score), asc(User.last_auth_success)).all()
    else:
        users = User.query.filter_by(admin = False).order_by(desc(User.score), asc(User.last_auth_success)).all()
        
    return render_template('rank.html', users = users, cur = restrict) 

@frontend.route("/notice")
def notice():
    return render_template("notice.html", notices = Notice.query.order_by(desc(Notice.id)).all())

@frontend.route("/rule")
def rule():
    return render_template("rule.html", rules = Rule.query.all())

@frontend.route("/prob_admin")
@login_required
def prob_admin():
    if not current_user.admin: abort(404)
    problems = Problem.query.all()
    prs = {}
    for key in config.category:
        prs[key] = []

    for i in problems:
        prs[i.category].append(i)

    return render_template("prob_admin.html", pr = prs, categories = config.category)


@frontend.route("/prob")
@login_required
def prob():
    start = mktime(config.game_start.timetuple()) - time()
    if start > 0 and not current_user.admin and False:
        return render_template("count.html", left = start, notices = Notice.query.order_by(desc(Notice.id)).limit(5).all())
    problems = Problem.query.all()
    prs = {}
    for key in config.category:
        prs[key] = []

    for i in problems:
        prs[i.category].append(i)

    U13 = User.query.filter_by(_type = 0).filter_by(admin = False).order_by(desc(User.score), asc(User.last_auth_success)).limit(5).all()
    U14 = User.query.filter_by(_type = 1).filter_by(admin = False).order_by(desc(User.score), asc(User.last_auth_success)).limit(5).all()
    U15 = User.query.filter_by(_type = 2).filter_by(admin = False).order_by(desc(User.score), asc(User.last_auth_success)).limit(5).all()
    U16 = User.query.filter_by(_type = 3).filter_by(admin = False).order_by(desc(User.score), asc(User.last_auth_success)).limit(5).all()
    return render_template("prob.html", pr = prs, categories = config.category, notices = Notice.query.order_by(desc(Notice.id)).limit(5).all(), U13 = U13, U14 = U14, U15 = U15, U16 = U16)

@frontend.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    next = request.args.get('next') or url_for('frontend.main')
    msg = None
    if request.method == "POST" and form.validate():
        msg = 'Login fail'
        user = User.query.filter_by(userid=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(next)
    return render_template("login.html", msg = msg, form=form)

@frontend.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("frontend.main"))

@frontend.route("/signup", methods=["GET", "POST"])
def signup():
    form = registerForm(request.form)
    msg = None

    if request.method == "POST" and form.validate():
        if not form.entrance_year.data in map(lambda x: x[0], config.entrance_type):
            msg = "Entrance year - Invalid value"
        elif not all(map(lambda x: x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_', form.username.data)):
            msg = "Username - Invalid character"
        else:
            if config.registkey == form.registerkey.data or config.admin_registkey == form.registerkey.data:
                chk = User.query.filter_by(userid = form.username.data).first()
                if chk:
                    msg = "Username - Duplicated username"
                else:
                    user = User(form.username.data, form.password.data, form.name.data, form.entrance_year.data)
                    if config.admin_registkey == form.registerkey.data:
                        user.admin = True
                    db_session.add(user)
                    db_session.commit()
                    map(lambda x: x.set_score(update_score(x.solver)), Problem.query.all())
                    db_session.commit()
                    map(lambda x: x.rebuild_score(), User.query.all())
                    return redirect(url_for("frontend.login"))
            else:
                msg = "Regist key - Invalid"

    return render_template("signup.html", msg = msg, form = form)

@frontend.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
    if not current_user.admin:
        abort(404)
    msg = None
    try:
        cur = request.args['t']
    except:
        cur = "notice"
    try:
        target = request.args['target']
    except:
        target = None

    if request.method == "POST":
        if cur == 'notice':
            if target == '0':
                notice = Notice(request.form["notice"])
                db_session.add(notice)
                db_session.commit()
                msg = "notice added"
            else:
                notice = Notice.query.filter_by(id=target).first() or abort(404)
                notice.body = request.form['notice']
                db_session.add(notice)
                db_session.commit()
                msg = "notice changed"
        elif cur == 'rule':
            if target == '0':
                rule = Rule(request.form["rule"])
                db_session.add(rule)
                db_session.commit()
                msg = "rule added"
            else:
                rule = Rule.query.filter_by(id=target).first() or abort(404)
                rule.body = request.form['rule']
                db_session.add(rule)
                db_session.commit()
                msg = "rule changed"
        elif cur == 'user':
            pw = request.form['pw']
            pwchk = request.form['pwchk']
            name = request.form['name']
            eyear = request.form['eyear']
            openable = request.form['open']
            user = User.query.get(target) or abort(404)
            
            if not eyear in ["0", "1"]:
                msg = "no Troll"
            else:
                user._type = int(eyear)

            if pw:
                if pw == pwchk:
                    user.set_password(pw)
                else:
                    msg = "password and password check is differ"

            if name:
                user.name = name
            user.openable = int(openable)

            db_session.commit()
            return redirect(url_for("frontend.admin", t="user"))

        elif cur == 'problem':
            name = request.form['name']
            desc = request.form['description']
            flag = request.form['flag']
            cate = request.form['category']
            try:
                hot = True if request.form['ishot']=="on" else False
            except:
                hot = False
            try:
                opened = True if request.form['opened']=="on" else False
            except:
                opened = False
            if target == "0":
                problem = Problem.query.filter_by(name = name).first()
                if not problem and name and desc and flag and cate and cate in config.category:
                    problem = Problem(name, desc, cate, flag)
                    problem.hot = hot
                    db_session.add(problem)
                    db_session.commit()
                    if opened:
                        problem.openprob()
                    return redirect(url_for("frontend.admin", t="problem", msg="added"))
                else:
                    return redirect(url_for("frontend.admin", t="problem", msg="failed"))
            else:
                problem = Problem.query.get(target) or abort(404)

            if name:
                problem.name = name
            if desc:
                problem.description = desc
            if flag:
                problem.flag = flag
            if cate and cate in config.category:
                problem.category = cate
            problem.hot = hot
            if not problem.open and opened:
                problem.openprob()

            problem.open = opened

            db_session.commit()
            return redirect(url_for("frontend.admin", t="problem"))

        else:
            cur = "notice"

    if not cur in ['notice', 'rule', 'user', 'problem']:
        cur = "notice"
    
    if cur == 'user':
        if target:
            user = User.query.filter_by(id = target).first()
            return render_template("admin.html", msg = msg, cur = cur, users = user, target = target)
        else:
            user = User.query.filter(User.admin != True).all()
            return render_template("admin.html", msg = msg, cur = cur, users = user, target = target)
    elif cur == 'problem':
        if target:
            problem = Problem.query.filter_by(id = target).first()
            return render_template("admin.html", msg = msg, cur = cur, problems = problem, target = target, categories = config.category)
        else:
            problem = Problem.query.all()
            return render_template("admin.html", msg = msg, cur = cur, problems = problem, target = None)
    elif cur == 'notice':
        if target:
            notice = Notice.query.filter_by(id = target).first()
            return render_template("admin.html", msg = msg, cur = cur, notices = notice, target = target)
        else:
            notice = Notice.query.all()
            return render_template("admin.html", msg = msg, cur = cur, notices = notice, target = target)
    elif cur == 'rule':
        if target:
            rule = Rule.query.filter_by(id = target).first()
            return render_template("admin.html", msg = msg, cur = cur, rules = rule, target = target)
        else:
            rule = Rule.query.all()
            return render_template("admin.html", msg = msg, cur = cur, rules = rule, target = target)


    return render_template("admin.html", msg = msg, cur = cur)

@frontend.route("/mypage", methods=["POST", "GET"])
@login_required
def mypage():
    form = MypageForm(request.form)
    msg = None
    if request.method == "POST":
        if current_user.check_password(form.cpassword.data):
            msg = ""
            if form.password.data:
                if len(form.password.data) < 4:
                    msg = "password - Field must be at least 4 characters long."
                    return render_template("mypage.html", msg = msg, form = form, entrance_type = config.entrance_type)
                elif form.password.data == form.confirm.data:
                    msg += "password "
                    current_user.set_password(form.password.data)
                else:
                    msg = "Passwords must match"
                    return render_template("mypage.html", msg = msg, form = form, entrance_type = config.entrance_type)
            if form.name.data and form.name.data != current_user.name:
                msg += "name "
            if msg:
                msg += "changed successfully"
            db_session.commit()
        else:
            msg = "wrong current password"

    return render_template("mypage.html", msg = msg, form = form, entrance_type = config.entrance_type)

@frontend.route("/user/<int:_id>")
@login_required
def show_user(_id):
    user = User.query.filter_by(admin = False).filter_by(id = _id).first() or abort(404)
    return render_template('show_user.html', user = user, rank = user.get_rank())

@frontend.route("/show/<int:_id>", methods=["GET", "POST"])
@login_required
def show(_id):
    cur = time()
    start = mktime(config.game_start.timetuple()) - cur
    if start > 0 and not current_user.admin:
        return redirect(url_for("frontend.prob"))

    msg = None
    if current_user.admin:
        problem = Problem.query.filter_by().filter_by(id = _id).first() or abort(404)
    else:
        problem = Problem.query.filter_by(open = True).filter_by(id = _id).first() or abort(404)

    if request.method == "POST" and 'flag' in request.form.keys():

        wait = 60 - cur + mktime(current_user.last_auth_failed.timetuple()) if current_user.last_auth_failed else 0
        if mktime(config.game_end.timetuple()) - cur <= 0:
            msg = "Sorry. Game is Ended..."
        elif wait > 0:
            msg = "Wait %d Seconds.." % int(wait)
        elif problem.check_flag(request.form['flag']):
            msg = problem.add_solver(current_user)
        else:
            current_user.last_auth_failed = datetime.datetime.now()
            msg = "Ddang~"

    return render_template("show_prob.html", problem = problem, msg = msg)

@frontend.route("/open/<int:_id>")
@login_required
def open(_id):
    problem = Problem.query.filter_by(open = False).filter_by(id = _id).first() or abort(404)

    if problem.openprob(current_user):
        return redirect(url_for("frontend.prob"))
    else:
        abort(404)
