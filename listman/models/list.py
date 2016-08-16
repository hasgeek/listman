# -*- coding: utf-8 -*-

from coaster.utils import buid
from . import db, BaseNameMixin
from .user import User

__all__ = ['List']


class List(BaseNameMixin, db.Model):
    __tablename__ = 'list'
    __uuid_primary_key__ = True

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('lists', order_by=db.desc('list.updated_at')))
    _fields = db.Column('fields', db.UnicodeText, nullable=False, default=u'')
    default_country = db.Column(db.Unicode(2), nullable=False, default=u'IN')

    def __repr__(self):
        return '<List "%s">' % self.title

    @property
    def fields(self):
        flist = self._fields.split(u' ')
        while u'' in flist:
            flist.remove(u'')
        return tuple(flist)

    @fields.setter
    def fields(self, value):
        self._fields = u' '.join(sorted(set(value)))

    fields = db.synonym('_fields', descriptor=fields)

    def __init__(self, **kwargs):
        super(List, self).__init__(**kwargs)
        if 'name' not in kwargs:  # Use random name unless one was provided
            self.name = buid()

    def permissions(self, user, inherited=None):
        perms = super(List, self).permissions(user, inherited)
        if user is not None and user == self.user:
            perms.update([
                'edit',
                'delete',
                'new',
                ])
        return perms
