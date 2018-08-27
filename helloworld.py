# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Hello(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')



def main():
    application = webapp.WSGIApplication([('/hello', Hello)],debug=True)
    
    run_wsgi_app(application)

if __name__ == "__main__":
    main()