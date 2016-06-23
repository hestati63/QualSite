#-*- coding: utf-8 -*-
SECRET = '\x121\x11\xccRBv\x1e\xa1\xa7\xf36\xa5\x17Q\xfc \xc3\xf79\xa7\xa7\xa6Re\x93\xb9\x94<\xc7Vq' # should be change
db = 'sqlite:///tmp.db' # db for connection

entrance_type = [('0', '~13'), ('1', '14'), ('2', '15'), ('3', '16')]

category = ["Pwnable", "Reversing", "Webhacking", "Forensic", "Coding"] # exist categories
score_max = 600 # score when only 1 player solves

registkey = "a" # registration key for normal user
admin_registkey = "b" # registration key for admin

import datetime

game_start = datetime.datetime(2016, 9, 1, 0, 0)
game_end = datetime.datetime(2016, 9, 6, 0, 0)
