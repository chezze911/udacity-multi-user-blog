
"""
Contains CRUD views of comments
"""
from google.appengine.ext import db

from entities.entity import Post, User, Comment
from handlers.auth import BlogHandler

from datetime import datetime
import copy



class NewComment(BlogHandler):

	def post(self, post_id):
        # get all the necessary parameters
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        c = ""
        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + " order by created desc")

        # Check first if the post exists and throw an error if it doesn't
        if not post:
            self.error(404)
            return

        # Check if user is signed in.
        if self.user:
            # Check if user is trying t olike his own post.
            if self.user.key().id() == post.user_id:
                self.write("You cannot comment on your own post!")
                return
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


        
class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
         """
        Shows edit comment page
        """
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
        if comment:
            # Get all the necessary parameters
            key = db.Key.from_path('Comment',
                                   int(comment_id),
                                   parent=blog_key())
            c = db.get(key)
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



class DeleteComment(BlogHandler):
    def get(self, post_id, comment_id):
        """
        Delete the comment it has been posted by the user asking to delete it
        """
        key = db.Key.from_path(
                               'Post',
                               int(post_id),
                               parent=blog_key()
                               )
        c = db.get(key)

        # Check first if the comment exists and throw an error if it doesn't
        if not c:
            self.error(404)
            return
        # Check if user is logged in.
        if self.user:
            self.render("deletecomment.html")
        # Otherwise throw an error
        else:
            self.redirect('/commentError')

    def post(self, post_id, comment_id):
        key = db.Key.from_path(
                           'Post',
                           int(post_id),
                           parent=blog_key()
                           )
        c = db.get(key)
        
        # Check first if the comment exists and throw an error if it doesn't
        if not c:
            self.error(404)
            return
        
        if not self.user:
            return self.redirect('/commentError')

        # Check if user is the author of this comment
        if c.user_id == self.user.key().id():
            c.delete()
        self.redirect('/blog/%s' % str(post_id))



class LoginError(BlogHandler):
    def get(self):
        self.write("Please login before commenting/editing/deleting/liking.")


class CommentError(BlogHandler):
    def get(self):
        """
        Handles error cases when unauthorized edit/delete is requested
        """
        self.write('You can only edit or delete comments you have created.')
