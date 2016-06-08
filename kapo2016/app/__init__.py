from flask import Flask
import config
app = Flask(__name__, static_url_path='')
app.secret_key = config.SECRET

import databases
import models


from front import *
app.register_blueprint(frontend, url_prefix='')
app.config['SESSION_TYPE'] = 'filesystem'

