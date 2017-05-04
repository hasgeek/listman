#!/usr/bin/env python

from coaster.manage import init_manager

import listman
import listman.models as models
import listman.forms as forms
import listman.views as views
from listman.models import db
from listman import app


if __name__ == '__main__':
    db.init_app(app)
    manager = init_manager(app, db, listman=listman, models=models, forms=forms, views=views)
    manager.run()
