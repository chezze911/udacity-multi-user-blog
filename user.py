import random
import hashlib

from string import letters
from google.appengine.ext import db


# user stuff
# Make salt to secure password.
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


# Make password hash containing name, pw, and a salt.
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


# Check that pw is valid by hashing and comparing it to existing hash pw.
def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


# Get key from user table.
def users_key(group='default'):
    return db.Key.from_path('users', group)


# Creates a database to store user information.
class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    # Get user by user id.
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    # Get user by name.
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    # Register by first hashing password .
    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    # Login by first checking password.
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
