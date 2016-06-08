#-*- coding: utf-8 -*-
from flask.ext.session import Session
from app import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

db = databases.engine.connect()
sess = Session(app)
