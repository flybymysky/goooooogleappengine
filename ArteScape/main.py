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
from google.appengine.api import images

# initialize template ---------------------------------------------------------------------------------------------------
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                                             autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
#----------------------------------------------------------------------------------------------
class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# databases -----------------------------------------------------------------------------------
class Post(db.Model):
	"""Models an individual Guestbook entry with an author, content, and date."""
	author = db.StringProperty()
	title = db.StringProperty()
	content = db.TextProperty()
	mainimage = db.BlobProperty()
	thumbnail = db.BlobProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	
class User(db.Model):
	username = db.UserProperty()
	nickname = db.StringProperty()

	
	
	
# images ----------------------------------------------------------------------------------------------------------------	
class ThumbnailHandler(webapp2.RequestHandler):
	def get(self, post_id):
		post = Post.get(post_id)
		self.response.headers['Content-Type'] = 'image/jpeg'
		self.response.out.write(post.thumbnail)
		
class MainimageHandler(webapp2.RequestHandler):
	def get(self, post_id):
		post = Post.get(post_id)
		self.response.headers['Content-Type'] = 'image/jpeg'
		self.response.out.write(post.mainimage)
		
class PostHandler(MainHandler):
	def get(self, post_id):
		post = Post.get(post_id)
		params = {'post':post}
		self.render('postique.html', **params)
# pages -----------------------------------------------------------------------------------------------------------------
class MainPage(MainHandler):
    def get(self):
		post = db.GqlQuery('SELECT * FROM Post ORDER BY date DESC')
		
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
			'post':post, 
			'loginstatus':loginstatus, 
			'intromessage':intromessage,
		}
		self.render('index.html', **params)

#----------------------------------------------------------------------------------------------		
class Upload(MainHandler):
	def get(self):
		loginstatus = users.get_current_user()
		if users.get_current_user():
			name = users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			params = {
				'url':url, 
				'url_linktext':url_linktext, 
				'name':name,
				'loginstatus':loginstatus,
			}
			self.render('post.html', **params)
		else:
			self.redirect('/')
	def post(self):
		loginstatus = users.get_current_user()
		post = Post()
		message = 0

		name = users.get_current_user().nickname()
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		post.author = users.get_current_user().nickname()
		uploadC = self.request.get('content')
		uploadT = self.request.get('title')
		uploadM = self.request.get('mainimage')
		if uploadC != "<br>" and uploadT and uploadM:
			post.content = uploadC
			post.title = uploadT
			post.mainimage = db.Blob(uploadM)
			post.put()
			message=1
		
		else:
			message=2
		params = {
		'url':url, 
		'url_linktext':url_linktext, 
		'name':name, 
		'post':post, 
		'loginstatus':loginstatus, 
		'message':message,
		}
		self.render('post.html', **params)
		
class portfolio(MainHandler):
    def get(self):
		loginstatus = users.get_current_user()
		if users.get_current_user():
			name = users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			owner = users.get_current_user().nickname() #portfolio owner is user
		else:
			name = 'guest'
			url = users.create_login_url(self.request.uri)
		
		params = {
		'name':name,
		'url':url,
		'loginstatus':loginstatus,
		}
		self.render('portfolio.html', **params)		

class video(MainHandler):
    def get(self):
		params = {}
		self.render('tubular/index.html', **params)

class htmlvideo(MainHandler):
    def get(self):
		params = {}
		self.render('htmlvideo.html', **params)

class countdown(MainHandler):
    def get(self):
		params = {}
		self.render('timeclock.html', **params)			
#----------------------------------------------------------------------------------------------		
class Upload(MainHandler):
	def get(self):
		loginstatus = users.get_current_user()
		if users.get_current_user():
			name = users.get_current_user().nickname()
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			params = {
				'url':url, 
				'url_linktext':url_linktext, 
				'name':name,
				'loginstatus':loginstatus,
			}
			self.render('post.html', **params)
		else:
			self.redirect('/')
	def post(self):
		loginstatus = users.get_current_user()
		post = Post()
		message = 0

		name = users.get_current_user().nickname()
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		post.author = users.get_current_user().nickname()
		uploadC = self.request.get('content')
		uploadT = self.request.get('title')
		uploadM = self.request.get('mainimage')
		if uploadC != "<br>" and uploadT and uploadM:
			post.content = uploadC
			post.title = uploadT
			post.mainimage = db.Blob(uploadM)
			post.put()
			message=1
		
		else:
			message=2
		params = {
		'url':url, 
		'url_linktext':url_linktext, 
		'name':name, 
		'post':post, 
		'loginstatus':loginstatus, 
		'message':message,
		}
		self.render('post.html', **params)		
# Page Assigns ----------------------------------------------------------------------------------------------------------
app = webapp2.WSGIApplication([('/', MainPage),
								(r'/thumbnails/(.*)', ThumbnailHandler), (r'/mainimages/(.*)', MainimageHandler),
								(r'/posts/(.*)', PostHandler),('/post', Upload),('/folio/flybymysky', portfolio),('/countdown', countdown),('/video', video),('/video2', htmlvideo)], debug=True)
