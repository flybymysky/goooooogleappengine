import webapp2	# web application framework
import jinja2	# template engine
import os		# access file system
import datetime # format date time
import cgi
import urllib
from google.appengine.ext.db import GqlQuery
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore
from google.appengine.api import mail	# send email

# initialize template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Greeting(db.Model):
	"""Models an individual Guestbook entry with an author, content, and date."""
	author = db.StringProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
	
class User(db.Model):
	user = db.UserProperty()
	nickname = db.StringProperty()
	
def guestbook_key(guestbook_name=None):
	"""Constructs a Datastore key for a Guestbook entity with guestbook_name."""
	return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp2.RequestHandler):
	def get(self):
		msg = 0
		guestbook_name=self.request.get('guestbook_name')
		greetings_query = Greeting.all().ancestor(
			guestbook_key(guestbook_name)).order('-date')
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
			useR=users.get_current_user()
			U = GqlQuery("SELECT * FROM User WHERE user= :1", useR).get()
			if not U:
				msg = 1
				User.user = users.get_current_user()
				User.nickname = users.get_current_user().nickname()
			name= users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			
		else:
			name = 'guest'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'greetings': greetings,
			'url': url,
			'url_linktext': url_linktext,
			'name': name,
			'msg': msg,
		}

		template = jinja_environment.get_template('index.html')
		self.response.out.write(template.render(template_values))

class Guestbook(webapp2.RequestHandler):
	def post(self):
		# We set the same parent key on the 'Greeting' to ensure each greeting is in
		# the same entity group. Queries across the single entity group will be
		# consistent. However, the write rate to a single entity group should
		# be limited to ~1/second.
		guestbook_name = self.request.get('guestbook_name')
		greeting = Greeting(parent=guestbook_key(guestbook_name))

		if users.get_current_user():
			greeting.author = users.get_current_user().nickname()
			comment= self.request.get('content')
			if len(comment)>0:
				greeting.content = comment
				greeting.put()
				self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))
			else:
				self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))
		else:
			self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))
			
class Profile(webapp2.RequestHandler):
	def get(self, username):
		pass
			# main
app = webapp2.WSGIApplication([('/', MainPage), ('/sign', Guestbook),('/profile/(.*)',Profile),],
                              debug=True)