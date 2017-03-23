import re
import hmac
import webapp2
import os
import jinja2

from google.appengine.ext import db
from user import User
from post import Post
from comment import Comment
from like import Like

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

file = open('secret.txt', 'r')
secret = file.read()


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


# Renders homepage with all posts.
class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)


class PostPage(BlogHandler):
    def get(self, post_id):
        # Get key from blog post.
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + " order by created desc")
        likes = db.GqlQuery("select * from Like where post_id=" + post_id)

        # if the post doesn't exist throw an error
        if not post:
            self.error(404)
            return
        error = self.request.get("error")

        # Render the page and show blog content, comments, likes, etc.
        self.render("permalink.html", post=post, comments=comments,
                    numOfLikes=likes.count(), error=error)


    def post(self, post_id):
        # get all the necessary parameters
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        c = ""
        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + " order by created desc")
        likes = db.GqlQuery("select * from Like where post_id = " + post_id)

        # Check first if the post exists and throw an error if it doesn't
        if not post:
            self.error(404)
            return

        # Check if user is signed in.
        if(self.user):
            # When like is clicked, like value increases by 1
            if(self.request.get('like') and self.request.get('like') ==
               "updateLike"):
                likes = db.GqlQuery("select * from Like where post_id =" +
                                    post_id + " and user_id = " +
                                    str(self.user.key().id()))
            # Check if user is trying to like his own post.
            if self.user.key().id() == post.user_id:
                self.write("You cannot comment on your own post!")
                return
            # add 1 to likes count if value is 0
            elif likes.count() == 0:
                l = Like(parent=blog_key(), user_id=self.user.key().id(),
                         post_id=int(post_id))
                l.put()
            # Commenting on a post creates a new comment tuple.
            if(self.request.get('comment')):
                c = Comment(parent=blog_key(), user_id=self.user.key().id(),
                            post_id=int(post_id),
                            comment=self.request.get('comment'))
                c.put()
        else:
            self.redirect('/loginError')
            return

        self.redirect('/blog/%s' % post_id)
        

class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path(
                               'Post',
                               int(post_id),
                               parent=blog_key()
                               )
        post = db.get(key)
        # Check first if the post exists and throw an error if it doesn't
        if not post:
            self.error(404)
            return
        # Check if user is logged in.
        if self.user:
            # Check if user is the blog post author
            if post.user_id == self.user.key().id():
                self.render('editpost.html',
                            subject=post.subject,
                            content=post.content)
            else:
                self.redirect('/editDeleteError')
        else:
            self.redirect('/loginError')

    def post(self, post_id):
        key = db.Key.from_path(
                               'Post',
                               int(post_id),
                               parent=blog_key()
                               )
        post = db.get(key)
        # if the post doesn't exist throw an error
        if not post:
            self.error(404)
            return
        # Check if user is not logged in.
        if not self.user:
            self.redirect('/blog')
        
        # Check if user is logged in.
        if self.user:
            # Check if user is the blog post author
            if post.user_id == self.user.key().id():
                
                subject = self.request.get('subject')
                content = self.request.get('content')

                if subject and content:
                    post.subject = subject
                    post.content = content
                    post.put()

                    self.redirect('/blog/%s' % post_id)
                else:
                    error = 'Please provide subject and content!'
                    self.render('editpost.html',
                                subject=subject,
                                content=content,
                                error=error)
            else:
                self.redirect('/editDeleteError')   
        else:
            self.redirect('/loginError')


class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
        key = db.Key.from_path(
                               'Comment',
                               int(comment_id),
                               parent=blog_key()
                               )
        c = db.get(key)
        # Check first if the comment exists and throw an error if it doesn't
        if not c:
            self.error(404)
            return
        # Check if user is logged in.
        if self.user:
            # Check if user is the blog comment author
            if c.user_id == self.user.key().id():
                self.render('editcomment.html',
                            comment=c.comment)
            else:
                self.redirect('/editDeleteError')

        # Throw an error if user isn't signed in
        else:
            self.redirect('/loginError')

    def post(self, post_id, comment_id):
        key = db.Key.from_path(
                               'Comment',
                               int(comment_id),
                               parent=blog_key()
                               )
        c = db.get(key)
        comment = self.request.get('comment')
         # Check first if the comment exists and throw an error if it doesn't
        if not c:
            self.error(404)
            return
        # Check if user is not logged in.
        if not self.user:
            self.redirect('/blog')
            
        # Check if user is logged in.
        if self.user:
            # Check if user is the blog post author
            if c.user_id == self.user.key().id():
        
                if comment:
                    c.comment = comment
                    c.put()
                    self.redirect('/blog/%s' % post_id)

                # Throw an error if user didn't provide all info.
                else:
                    error = "Please provide subject and content!"
                    self.render('editpost.html',
                                subject=subject,
                                content=content,
                                error=error)
            else:
                self.redirect('/editDeleteError')   
        else:
            self.redirect('/loginError')


class DeleteComment(BlogHandler):
    def get(self, post_id, comment_id):
        key = db.Key.from_path('Comment', 
                                   int(comment_id),
                                   parent = blog_key())
        c = db.get(key)
        if self.user:
            if c.user_id == self.user.key().id():
                c.delete()
                self.redirect('/blog/%s' % str(post_id))
            else:    
                self.redirect('/editDeleteError')
        else:
            self.redirect('/commentError')


class DeletePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post',
                                int(post_id),
                                parent = blog_key())
        post = db.get(key)
        
        if not post:
            self.error(404)
            return
        
        if self.user:
            if post.user_id == self.user.key().id():
                post.delete()
                self.redirect('/')
            else:
                self.redirect('/editDeleteError')  
        else:
            self.redirect('/loginError')


class LoginError(BlogHandler):
    def get(self):
        self.write("Please login before commenting/editing/deleting/liking.")


class EditDeleteError(BlogHandler):
    def get(self):
        self.write('You can only edit or delete posts you have created.')


class CommentError(BlogHandler):
    def get(self):
        self.write('You can only edit or delete comments you have created.')


class NewPost(BlogHandler):
    def get(self):
        # Check if user is logged in.
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        # Check if user is not logged in.
        if not self.user:
            self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content').replace('/n', '<br>')
        user_id = self.user.key().id()

        # Add to database and redirect to post page.
        if subject and content:
            print "user_id: %s" % user_id

            p = Post(parent=blog_key(),
                     user_id=user_id,
                     subject=subject,
                     content=content,
                     likes=0)

            print p.user_id

            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "please fill in subject and content lines"
            self.render("newpost.html",
                        subject=subject,
                        content=content,
                        error=error)

# Defines a valid username
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)

# Defines a valid password
PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)

# Defines a valid email
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


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


app = webapp2.WSGIApplication([('/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/editDeleteError', EditDeleteError),
                               ('/commentError', CommentError),
                               ('/loginError', LoginError),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/deletepost/([0-9]+)', DeletePost),
                               ('/blog/editcomment/([0-9]+)/([0-9]+)',
                                EditComment),
                               ('/blog/deletecomment/([0-9]+)/([0-9]+)',
                                DeleteComment),
                               ],
                              debug=True)
