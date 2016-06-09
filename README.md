# QualSite
CTF framework for 2016 kapo-qual in GoN.

There are two registeration keys in config.py which are for player and admin.

You should change the registeration keys and secret key for app in config.py.

Also, you can change maximum score for problem.

This CTF framework's system is based on defcon2016 qual system.
  - First solver for each problem can open new problem.
  - Score of each problem is based on numbers of solvers.

## init db
```sh
$ python run.py initdb
```

## run for test
```sh
$ python run.py run
```

## run for launch
```sh
$ uwsgi --ini uwsgi.ini
```
