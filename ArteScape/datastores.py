from google.appengine.ext import db


class Post(db.Model):
	"""Models an individual Guestbook entry with an author, content, and date."""
	author = db.StringProperty()
	content = db.TextProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	
class User(db.Model):
	username = db.UserProperty()
	nickname = db.StringProperty()