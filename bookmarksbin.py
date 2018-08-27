# -*- coding: utf-8 -*-
#http://bookmarksbin.appspot.com
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from google.appengine.api import users
from google.appengine.ext.webapp import RequestHandler

from datetime import date
import models
import os

#bookmarks = [models.Bookmark('teste', 'Search engine','http://www.google.com', 'Google'),
#             models.Bookmark('teste2', 'Cool reads','http://www.reddit.com', 'Reddit')]

class BookmarksBin(webapp.RequestHandler):
    def renderPage(self, fileName, values):
        #import dbg
        path = os.path.join(os.path.dirname(__file__),'templates/',fileName)
        self.response.out.write(template.render(path, values))

    def hasValidUser(self):
        self._user = users.get_current_user()
        if self._user:
            if self.isNewUser():
                self.__setUserPreferences()
                return True
        else:
            self.redirect(users.create_login_url(self.request.uri))
    
    def __displayBookmarksPage(self):
        x = {'bookmarks': '' }

        self.renderPage('bookmarksbin.html', x)
    
    def get(self):
        #if self.hasValidUser():
        self.__displayBookmarksPage()

def main():
    application = webapp.WSGIApplication([('/book', BookmarksBin)], debug=True)

    run_wsgi_app(application)

if __name__ == '__main__':
    main()