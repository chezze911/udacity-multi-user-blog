"""
Handles likes post request and also error handlings of those cases
"""
from google.appengine.ext import db

from entities.entity import Post, User, Like
from handlers.auth import AuthHandler

from datetime import datetime



# class LikePage(BlogHandler):
#     def get(self, post_id):
#         # Get key from blog post.
#         key = db.Key.from_path('Post', int(post_id), parent=blog_key())
#         post = db.get(key)
#         likes = db.GqlQuery("select * from Like where post_id=" + post_id)

#         # if the post doesn't exist throw an error
#         if not post:
#             self.error(404)
#             return
#         error = self.request.get("error")

#         # Render the page and show blog content, comments, likes, etc.
#         self.render("permalink.html", post=post,
#                     numOfLikes=likes.count(), error=error)


#     def post(self, post_id):
#         # get all the necessary parameters
#         key = db.Key.from_path('Post', int(post_id), parent=blog_key())
#         post = db.get(key)
#         likes = db.GqlQuery("select * from Like where post_id = " + post_id)

#         # Check first if the post exists and throw an error if it doesn't
#         if not post:
#             self.error(404)
#             return

#         # Check if user is signed in.
#         if self.user:
#             # When like is clicked, like value increases by 1
#             if(self.request.get('like') and self.request.get('like') ==
#                "updateLike"):
#                 likes = db.GqlQuery("select * from Like where post_id =" + post_id + " and user_id = " + str(self.user.key().id()))
            
#             # Check if user is trying t olike his own post.
#             if self.user.key().id() == post.user_id:
#                 self.write("You can't like your own post & can only like a post once!")
#                 return

#             # add 1 to likes count if value is 0
#             elif likes.count() == 0:
#                 l = Like(parent=blog_key(), user_id=self.user.key().id(),
#                          post_id=int(post_id))
#                 l.put()

#             # Commenting on a post creates a new comment tuple.
#             if(self.request.get('comment')):
#                 c = Comment(parent=blog_key(), user_id=self.user.key().id(), post_id=int(post_id), comment=self.request.get('comment'))
#                 c.put()
#         else:
#             self.redirect('/loginError')
#             return

#         self.redirect('/blog/%s' % post_id)
     


class LoginError(BlogHandler):
    def get(self):
        self.write("Please login before commenting/editing/deleting/liking.")

