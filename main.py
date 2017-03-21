import webapp2
from handlers.auth import Register, Login, Logout
from handlers.blog import NewPost, EditPost, DeletePost, LoginError, EditDeleteError
from handlers.comment import NewComment, DeleteComment, CommentError, EditComment, LoginError, EditDeleteError
from handlers.likes import LikePage, LikeError, LoginError

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
                               ('/blog/like/([0-9]+)', LikePage),
                               # ('/blog/like/([0-9]+)', LikePost)
                               # ('/blog/newcomment/([0-9]+)', NewComment),
                               ],
                              debug=True)
