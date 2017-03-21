from .base import Handler
from entities.entity import User
import utils



class BlogHandler(webapp2.RequestHandler):
    """
    Adds common utility methods needed for authentication
    """

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # Sets a cookie when user logs in.
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    # Reset the cookie when user logs out.
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # Get the user from the secure cookie when page initializes
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)


class MainPage(BlogHandler):
    def get(self):
        self.write('Hello, Udacity!')


# Get key from blog table.
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)



class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    # get user input username, password, verify and email
    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username, email=self.email)
        # Give an error if username isn't valid.
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        # Give an error if password isn't valid.
        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        # Give an error if password and verify password don't match.
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True
        # Give an error if email isn't valid.
        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True
        # Go to signup-form if we have an error.
        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):

    def done(self):
        # Make sure the user doesn't already exist.
        u = User.by_name(self.username)
        # Give an error if username already exists.
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            # Add user and login and redirect to blog page
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    # Get user's input for username and password.
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        # Get the user account that associates with that username and pw.
        u = User.login(username, password)
        if u:
            # Login and redirect to blog page.
            self.login(u)
            self.redirect('/')
        else:
            # Give an error if there's no associated user account.
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')
