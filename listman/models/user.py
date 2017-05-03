# -*- coding: utf-8 -*-

from flask_lastuser.sqlalchemy import UserBase2, ProfileBase
from . import db

__all__ = ['User']


class User(UserBase2, db.Model):
    __tablename__ = 'user'
    __uuid_primary_key__ = True


class Profile(ProfileBase, db.Model):
    __tablename__ = 'profile'
    __uuid_primary_key__ = True
