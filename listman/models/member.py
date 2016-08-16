# -*- coding: utf-8 -*-

import re
import phonenumbers
from coaster.utils import md5sum, LabeledEnum
from baseframe import __
from . import db, BaseMixin, JsonDict
from .list import List

__all__ = ['Member']

NAMESPLIT_RE = re.compile(r'[\W\.]+')
EMAIL_RE = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$', re.I)


class MEMBER_STATUS(LabeledEnum):
    UNKNOWN = (0, 'unknown', __("Unknown"))                 # Unclear how this member is on this list
    REQUESTED = (1, 'requested', __("Requested"))           # Someone asked for this member to be added to the list
    ADDED = (2, 'added', __("Added"))                       # Member was added with implicit confirmation
    SUBSCRIBED = (3, 'subscribed', __("Subscribed"))        # Member explicitly confirmed addition
    UNSUBSCRIBED = (4, 'unsubscribed', __("Unsubscribed"))  # Member chose to unsubscribe
    REMOVED = (5, 'removed', __("Removed"))                 # Member was removed by list owner
    BOUNCED = (6, 'bounced', __("Bounced"))                 # Member's email hard bounced or phone is invalid


class Member(BaseMixin, db.Model):
    __tablename__ = 'member'
    __uuid_primary_key__ = True

    # List this is a member of
    list_id = db.Column(None, db.ForeignKey('list.id'), nullable=False)

    status = db.Column(db.SmallInteger, nullable=False, default=MEMBER_STATUS.UNKNOWN, index=True)

    _fullname = db.Column('fullname', db.Unicode(80), nullable=True)
    _firstname = db.Column('firstname', db.Unicode(80), nullable=True)
    _lastname = db.Column('lastname', db.Unicode(80), nullable=True)
    _nickname = db.Column('nickname', db.Unicode(80), nullable=True)

    _email = db.Column('email', db.Unicode(254), nullable=True, index=True)
    md5sum = db.Column(db.String(32), nullable=True, index=True)

    _phone = db.Column('phone', db.Unicode(16), nullable=True, index=True)
    phone_valid = db.Column(db.Boolean, nullable=True)

    data = db.Column(JsonDict)

    list = db.relationship(List, backref=db.backref('members', lazy='dynamic',
        cascade='all, delete-orphan', order_by=(_fullname, _firstname, _lastname)))
    parent = db.synonym('list')

    __table_args__ = (
        db.UniqueConstraint('list_id', 'email'), db.UniqueConstraint('list_id', 'phone'),
        db.CheckConstraint('not (email is null and phone is null)', 'member_email_phone_check'))

    def __repr__(self):
        return '<Member %s %s of %s>' % (self.fullname, self.email, repr(self.list)[1:-1])

    @classmethod
    def get(cls, list, email=None, phone=None):
        if not list or ((not not email) + (not not phone) != 1):
            raise TypeError("List and one of email or phone must be provided")
        if email:
            return cls.query.filter_by(list=list, email=email).one_or_none()
        elif phone:
            return cls.query.filter_by(list=list, phone=phone).one_or_none()

    @property
    def fullname(self):
        """
        Recipient's fullname, constructed from first and last names if required.
        """
        if self._fullname:
            return self._fullname
        elif self._firstname:
            if self._lastname:
                # FIXME: Cultural assumption of <first> <space> <last> name.
                return u"{first} {last}".format(first=self._firstname, last=self._lastname)
            else:
                return self._firstname
        elif self._lastname:
            return self._lastname
        else:
            return None

    @fullname.setter
    def fullname(self, value):
        self._fullname = value

    @property
    def firstname(self):
        if self._firstname:
            return self._firstname
        elif self._fullname:
            return NAMESPLIT_RE.split(self._fullname)[0]
        else:
            return None

    @firstname.setter
    def firstname(self, value):
        self._firstname = value

    @property
    def lastname(self):
        if self._lastname:
            return self._lastname
        elif self._fullname:
            return NAMESPLIT_RE.split(self._fullname)[-1]
        else:
            return None

    @lastname.setter
    def lastname(self, value):
        self._lastname = value

    @property
    def nickname(self):
        return self._nickname or self.firstname

    @nickname.setter
    def nickname(self, value):
        self._nickname = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if value:
            self._email = value.lower()
            self.md5sum = md5sum(value)
        else:
            self._email = None
            self.md5sum = None

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        if value:
            try:
                phone_parsed = phonenumbers.parse(value, self.campaign.default_country)
                self._phone = phonenumbers.format_number(phone_parsed, phonenumbers.PhoneNumberFormat.E164)
                self.phone_valid = phonenumbers.is_valid_number(phone_parsed)
            except phonenumbers.NumberParseException:
                self._phone = value
                self.phone_valid = False
        else:
            self._phone = None
            self.phone_valid = None

    def phone_formatted(self):
        try:
            phone_parsed = phonenumbers.parse(self.phone)
            return phonenumbers.format_number(phone_parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except phonenumbers.NumberParseException:
            return self.phone

    fullname = db.synonym('_fullname', descriptor=fullname)
    firstname = db.synonym('_firstname', descriptor=firstname)
    lastname = db.synonym('_lastname', descriptor=lastname)
    nickname = db.synonym('_nickname', descriptor=nickname)
    email = db.synonym('_email', descriptor=email)
    phone = db.synonym('_phone', descriptor=phone)

    @property
    def email_valid(self):
        return EMAIL_RE.match(self.email) is not None

    @property
    def revision_id(self):
        return self.draft.revision_id if self.draft else None

    def is_latest_draft(self):
        if not self.draft:
            return True
        return self.draft == self.campaign.drafts[-1]

    def template_data(self):
        return dict([
            ('fullname', self.fullname),
            ('email', self.email),
            ('firstname', self.firstname),
            ('lastname', self.lastname),
            ('nickname', self.nickname),
            ('phone', self.phone),
            ('phone_formatted', self.phone_formatted),
            ] + (self.data.items() if self.data else []))


def members_iter(self):
    ids = [i.id for i in db.session.query(Member.id).filter(Member.list == self).order_by('id').all()]
    for rid in ids:
        yield Member.query.get(rid)

List.members_iter = members_iter
