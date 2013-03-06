import webapp2	# web application framework
import jinja2	# template engine
import os		# access file system
import datetime # format date time
import cgi
import urllib
from google.appengine.ext.db import GqlQuery
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import mail

# initialize template -------------------------------------------------------------------------
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                                             autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# databases -----------------------------------------------------------------------------------
class Greeting(db.Model):
	"""Models an individual Guestbook entry with an author, content, and date."""
	author = db.StringProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
	
class User(db.Model):
	username = db.UserProperty()
	nickname = db.StringProperty()

# comments ------------------------------------------------------------------------------------
def comments_key(comments_name=None):
	return db.Key.from_path('Comments', comments_name or 'default_comments')
	"""Constructs a Datastore key for a Guestbook entity with guestbook_name."""

class Comments(webapp2.RequestHandler):
	def post(self):
		"""We set the same parent key on the 'Greeting' to ensure each greeting is in
		the same entity group. Queries across the single entity group will be
		consistent. However, the write rate to a single entity group should
		be limited to ~1/second. """
		comments_name = self.request.get('comments_name')
		greeting = Greeting(parent=comments_key(comments_name))
		
		if users.get_current_user():
			greeting.author = users.get_current_user().nickname()
			comment= self.request.get('content')
			if len(comment)>0:
				greeting.content = comment
				greeting.put()
				self.redirect('/?' + urllib.urlencode({'comments_name': comments_name}))
			else:  #empty comment
				self.redirect('/?' + urllib.urlencode({'comments_name': comments_name}))
		else:
			self.redirect('/?' + urllib.urlencode({'comments_name': comments_name}))

# Main Page -----------------------------------------------------------------------------------
class MainPage(BaseHandler):
	def get(self):
		currentuser = users.get_current_user()
		msg = 0
		user = User()
		comments_name=self.request.get('comments_name')
		greetings_query = Greeting.all().ancestor(
			comments_key(comments_name)).order('-date')
		greetings = greetings_query.fetch(10)
		'''
		U = GqlQuery('select * from User where user=:1',USER)
		if not U:
		   msg = 1
		else:
			USER = users.get_current_user()
		    u = User(user=USER,nickname=USER.nickname())
		    u.put()
		U.user
		U.nickname
		'''
		if users.get_current_user():
			currentuser = users.get_current_user().nickname()
			U = GqlQuery("SELECT * FROM User WHERE nickname= :1", currentuser).get()
			if not U:
				msg = 1
				user.username = users.get_current_user()
				user.nickname = users.get_current_user().nickname()
				user.put()
			name= users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			
		else:
			name = 'guest'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
			
			
		A = GqlQuery("SELECT * FROM Greeting WHERE author= :1", currentuser).get()
		A.content = "some text"
		A.put()

		params = {
			'greetings': greetings,
			'url': url,
			'url_linktext': url_linktext,
			'name': name,
			'msg': msg,
			'currentuser' :currentuser,
		}

		self.render('index.html',**params)
		
# Profile Page (public) ------------------------------------------------------------------------			
class Profile(webapp2.RequestHandler):
	def get(self, username):
		pass

# Page Assigns ---------------------------------------------------------------------------------
app = webapp2.WSGIApplication([('/', MainPage), ('/sign', Comments),('/profile/(.*)',Profile),],
                              debug=True)