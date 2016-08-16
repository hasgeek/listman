# -*- coding: utf-8 -*-

from flask.ext.lastuser.sqlalchemy import UserBase2, ProfileBase
from . import db

__all__ = ['User']


class User(UserBase2, db.Model):
    __tablename__ = 'user'


class Profile(ProfileBase, db.Model):
    __tablename__ = 'profile'
