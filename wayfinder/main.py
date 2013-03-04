import webapp2	# web application framework
import jinja2	# template engine
import os		# access file system
import datetime # format date time
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore
from google.appengine.api import mail	# send email

# initialize template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		template_values = {}
		
		if user:
			template = jinja_environment.get_template('index.html')
		
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
		self.response.write(template.render(template_values))
			
# main
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)