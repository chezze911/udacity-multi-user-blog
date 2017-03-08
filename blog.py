import re
import hmac
import webapp2
import os
import jinja2

from google.appengine.ext import db
from user import User
from post import Post
from comment import Comment

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'fart'

def jinja_render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Method to create secure cookie values.
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

# Method to check secure cookie values.
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        

    def render_str(self, template, **params):
        params['user'] = self.user
        return jinja_render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

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


##### blog stuff
# Get key from blog table.  
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

# Renders homepage with all posts
class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = db.GqlQuery("select * from Comment where post_id = " + post_id + " order by created desc")
        
        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post, comments=comments)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        
        
        if not post:
            self.error(404)
            return
              
        if(self.request.get('like') and self.request.get('like') == "update"):
            post.likes = post.likes + 1;
            post.put();
        
        if(self.user):
            if(self.request.get('comment')):
                c = Comment(parent=blog_key(), user_id=self.user.key().id(), post_id=int(post_id), comment = self.request.get('comment'))
                c.put()
        else:
            self.render("permalink.html", post=post, error="You need to login before commenting.!!")
            return
            
        comments = db.GqlQuery("select * from Comment where post_id = "+post_id+"order by created desc")
        self.render("permalink.html", post=post, comments=comments, new=self.request.get('comment'))

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content').replace('/n', '<br>')
        user_id = self.user.key().id()
       
        # If we have subject and content of post, add to database and redirect to post page
        if subject and content:
            print "user_id: %s" % user_id

            p = Post(parent=blog_key(), user_id=user_id, subject=subject, content=content, likes=0)
            
            print p.user_id
            
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "please fill in subject and content lines"
            self.render("newpost.html", subject=subject, content=content, error=error)

# Defines a valid username
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

# Defines a valid password
PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

# Defines a. valid email
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


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

        params = dict(username = self.username,
                      email = self.email)

        # Give an error if username isn't valid 
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        # Give an error if password isn't valid
        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        
        # Give an error if password and verify password don't match 
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        # Give an error if email isn't valid 
        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        # Go to signup-form if we have an error
        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        # Give an error if username already exists
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

    # Get user's input for username and password
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        # get the user account that associates with that username and pw
        u = User.login(username, password)
        if u:
            # login and redirect to blog page
            self.login(u)
            self.redirect('/')
        else:
            # Give an error if there's no associated user account
            msg ='Invalid login'
            self.render('login-form.html', error=msg)

class Logout(BlogHandler):
    def get(self):
        
        if self.user:
            
            self.logout()
            self.redirect('/')
        
        else:
            error ="You have to be logged in able to log out.  Please log in."
            self.render('/login', error=error)


app = webapp2.WSGIApplication([('/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
