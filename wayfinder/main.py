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
	content = db.TextProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	
class User(db.Model):
	username = db.UserProperty()
	nickname = db.StringProperty()

# comments ------------------------------------------------------------------------------------
def comments_key(comments_name=None):
	return db.Key.from_path('Comments', comments_name or 'default_comments')
	"""Constructs a Datastore key for a Guestbook entity with guestbook_name."""

class Comments(BaseHandler):
	def post(self):
		"""We set the same parent key on the 'Comments' to ensure each comment is in
		the same entity group. Queries across the single entity group will be
		consistent. However, the write rate to a single entity group should
		be limited to ~1/second. """
		comments_name = self.request.get('comments_name')
		greeting = Greeting(parent=comments_key(comments_name))
		
		if users.get_current_user():
			greeting.author = users.get_current_user().nickname()
			comment=self.request.get('content')
			if comment:
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
		comments_name = self.request.get('comments_name')
		greetings_query = Greeting.all().ancestor(
			comments_key(comments_name)).order('-date')
			
		greetings = greetings_query.fetch(10)
		
		loginstatus = users.get_current_user()
		intromessage = False
		
		#if logged in
		if users.get_current_user():
			name = users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			
			#check if user in database
			U = GqlQuery("SELECT * FROM User WHERE nickname= :1", name).get()
			
			#for first-time log-in
			if not U: 
				intromessage = True #display intro message
				user = User()
				user.username = users.get_current_user() #add username into database
				user.nickname = users.get_current_user().nickname() #add nickname into database
				user.put()
		#not logged in
		else:
			name = 'guest'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		params = {
			'url':url, 
			'url_linktext':url_linktext, 
			'name':name, 
			'greetings':greetings, 
			'loginstatus':loginstatus, 
			'intromessage':intromessage,
		}
		self.render('index.html', **params)

# Account Page ---------------------------------------------------------------------------------
class Account(BaseHandler):
	def get(self):
		comments_name = self.request.get('comments_name')
		greetings_query = Greeting.all().ancestor(
			comments_key(comments_name)).order('-date')	
		greetings = greetings_query.fetch(10)
		
		loginstatus = users.get_current_user()
		if loginstatus:
			name = users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			name = 'guest'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		params = {
			'url':url, 
			'url_linktext':url_linktext, 
			'name':name, 
			'loginstatus':loginstatus,
			'greetings':greetings, 
		}
		self.render('account.html', **params)
		
	def post(self):
		updatename = self.request.get('nickname')
		updatesuccess=False
		updateerror=False
		
		if updatename:
			updatesuccess=True
			user = User()
			user.username = users.get_current_user()
			user.nickname = updatename
			user.put()
		else:
			updateerror=True
			
# Profile Page (public) ------------------------------------------------------------------------			
class Profile(BaseHandler):
	def get(self, user):
		u=db.GqlQuery('SELECT * FROM User WHERE nickname = :1', user).get()
		currentuser = users.get_current_user()
		if not u:
			self.error(404)
			return
		if users.get_current_user():
			name= users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			name = 'guest'
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		params = {
			'url': url,
			'url_linktext': url_linktext,
			'name': name,
			'currentuser' :currentuser,
        }
		self.render('profile.html', **params)       
		
		

# Page Assigns ---------------------------------------------------------------------------------
app = webapp2.WSGIApplication([('/', MainPage), ('/sign', Comments),('/account', Account),(r'/profile/(.+)',Profile),],
                              debug=True)