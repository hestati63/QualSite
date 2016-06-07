#-*- coding: utf-8 -*-
from flask import Flask, render_template, abort, request, session, flash, url_for, redirect
from flask.ext.session import Session
from app import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__, static_url_path='')
app.secret_key = config.SECRET

app.register_blueprint(frontend, url_prefix='')
app.config['SESSION_TYPE'] = 'filesystem'
db = databases.engine.connect()
sess = Session(app)
