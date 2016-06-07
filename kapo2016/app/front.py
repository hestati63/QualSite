#-*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, session, flash, url_for, redirect, Blueprint
from flask.ext.session import Session
import models
import databases
import config
from datetime import datetime
from time import time, mktime
import string

frontend = Blueprint('frontend', __name__)
debug = True

@frontend.route("/", methods=['GET', 'POST'])
def main():
    start = mktime(datetime(2016, 9, 1, 0, 0).timetuple()) - time()
    if not debug and  start > 0:
        return render_template("count.html", left = start)

    if 'uid' in session.keys():
        problems = models.Problem.query.filter_by(is_open = True).filter_by(solver = 0).all()
        return render_template('logined_main.html', pr = problems)
    else:
        return render_template('base.html')

@frontend.route("/rule")
def rule():
    return render_template("rule.html")

@frontend.route("/prob")
def prob():
    problems = models.Problem.query.all()
    map(lambda x: x.score(), problems)
    return render_template("prob.html", pr = problems)

@frontend.route("/score")
def score():
    pass

@frontend.route("/login")
def login():
    pass

@frontend.route("/mypage")
def mypage():
    pass

@frontend.route("/show/<int:_id>")
def show(_id):
    return "!!"

@frontend.route("/open/<int:_id>")
def open(_id):
    return "!!"
