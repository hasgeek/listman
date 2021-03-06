# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from __future__ import absolute_import
from flask import Flask
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
from baseframe import baseframe, assets, Version
from flask_migrate import Migrate
import coaster.app
from ._version import __version__

version = Version(__version__)

# First, make an app

app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

# Second, import the models and views

from . import models, views  # NOQA
from .models import db

# Third, setup baseframe and assets

assets['listman.js'][version] = 'js/app.js'
assets['listman.css'][version] = 'css/app.css'


# Configure the app
coaster.app.init_app(app)
migrate = Migrate(app, db)
db.init_app(app)
db.app = app
baseframe.init_app(app, requires=['baseframe-bs3', 'listman'])
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))
