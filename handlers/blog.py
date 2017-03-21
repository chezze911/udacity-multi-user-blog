"""
Contains CRUD views of blogs
"""
from google.appengine.ext import db

from entities.entity import Post, User
from handlers.auth import BlogHandler

from datetime import datetime



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
        
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            # Get all the necessary post parameters
            key = db.Key.from_path('Post',
                                   int(post_id),
                                   parent=blog_key())
            post = db.get(key)
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


class DeletePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post',
                                int(post_id),
                                parent = blog_key())
        post = db.get(key)
        
        if self.user:
            if post.user_id == self.user.key().id():
                post.delete()
                self.redirect('/')
            else:
                self.redirect('/editDeleteError')  
        else:
            self.redirect('/loginError')

