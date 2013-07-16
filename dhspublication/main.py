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
import webapp2

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
	date = db.DateTimeProperty(auto_now_add=True)
	writer = db.StringProperty()
	title = db.StringProperty()
	category = db.StringProperty()
	content = db.TextProperty()
	
class User(db.Model):
	username = db.UserProperty()
	nickname = db.StringProperty()

# pages -----------------------------------------------------------------------------------------------------------------
class MainPage(MainHandler):
    def get(self):
		params = {}
		self.render('index.html', **params)
		
# Page Assigns ----------------------------------------------------------------------------------------------------------
app = webapp2.WSGIApplication([('/', MainPage)], debug=True)