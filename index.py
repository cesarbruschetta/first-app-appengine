#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from os import sys, path

# Add lib as primary libraries directory, with fallback to lib/dist
# and optionally to lib/dist.zip, loaded using zipimport.
lib_path = path.dirname(__file__)
sys.path[0:0] = [
    lib_path,
    path.join(lib_path, 'lib'),
]


from util.sessions import Session

from models import *

import os
import logging
import wsgiref.handlers

def doRender(handler, tname='index.html', values={}):
    temp = os.path.join(os.path.dirname(__file__),'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    # Make a copy of the dictionary and add the path
    newval = dict(values)
    newval['path'] = handler.request.path
    if 'username' in handler.session:
        newval['username'] = handler.session['username']
   
    outstr = template.render(temp, newval)
    handler.response.out.write(unicode(outstr))
    return True

class LoginHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        doRender(self, 'loginscreen.html')

    def post(self):
        self.session = Session()
        acct = self.request.get('account')
        pw = self.request.get('password')
        #logging.info('Checking account='+acct+' pw='+pw)
        
        self.session.delete_item('username')
        self.session.delete_item('userkey')
        
        if pw == '' or acct == '':
            doRender(self, 'loginscreen.html', {'error' : 'Please specify Acct and PW'} )
            return
        
        # Check to see if our data is correct
        que = db.Query(User)
        que = que.filter('account =',acct)
        que = que.filter('password = ',pw)
        results = que.fetch(limit=1)
        if len(results) > 0 :
            user = results[0]
            self.session['userkey'] = user.key()
            self.session['username'] = acct
            doRender(self,'index.html',{ } )
        else:
            doRender(self,'loginscreen.html',{'error' : 'Incorrect password'} )

            
class LogoutHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        if 'username' in self.session:
            del self.session['username']
        self.session.delete_item('username')
        self.session.delete_item('userkey')
        doRender(self, '/index.html')
            
class ApplyHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        doRender(self, 'applyscreen.html')

    def post(self):
        self.session = Session()
        name = self.request.get('name')
        acct = self.request.get('account')
        pw = self.request.get('password')
        logging.info('Adding account='+acct)
        
        if pw == '' or acct == '' or name == '':
            doRender(self,'applyscreen.html',{'error' : 'Please fill in all fields'})
            return
        
        # Check whether the user already exists
        que = db.Query(User)
        que = que.filter('account =',acct)
        results = que.fetch(limit=1)
        if len(results) > 0 :
            doRender(self,'applyscreen.html',{'error' : 'Account Already Exists'})
            return
    
        # Create the User object and log the user in
        newuser = User(name=name, account=acct, password=pw);
        pkey = newuser.put();
        self.session['username'] = acct
        self.session['userkey'] = pkey
        doRender(self,'index.html',{ })

class MembersHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        que = db.Query(User)
        user_list = que.fetch(limit=100)
        doRender(self, 'memberscreen.html',{'user_list': user_list})

class ChatHandler(webapp.RequestHandler):
    # Retrieve the messages
    def get(self):
        self.session = Session()
        que = db.Query(ChatMessage).order('-created');
        chat_list = que.fetch(limit=10)
        doRender(self,'chatscreen.html',{ 'chat_list': chat_list })
        
    def post(self):
        self.session = Session()
        if not 'userkey' in self.session:
            doRender(self,'chatscreen.html',{'error' : 'Must be logged in'} )
            return
        
        msg = self.request.get('message')
        if msg == '':
            doRender(self,'chatscreen.html', {'error' : 'Blank message ignored'} )
            return
        
        newchat = ChatMessage(user=self.session['userkey'], text=msg)
        newchat.put()
        self.get()
        

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.session = Session()
        path = self.request.path
        if doRender(self,path) :
            return
        doRender(self,'index.html',{'stguess':'', 'msq':'',})
        
    def post(self):
        self.session = Session()
        path = self.request.path
        stguess = self.request.get('guess')
        try:
            guess = int(stguess)
        except:
            guess = -1
        answer = 42
            
        if guess == answer:
            msg = 'Congratulations'
        elif guess < 0 :
            msg = 'Please provide a number guess'
        elif guess < answer:
            msg = 'Your guess is too low'
        else:
            msg = 'Your guess is too high'

        doRender(self,'index.html',{'stguess':stguess,'msq':msg,'path':path })
       
        
        
def main():
    import appengine_admin
    application = webapp.WSGIApplication([('/login', LoginHandler),
                                          ('/logout', LogoutHandler),
                                          ('/apply', ApplyHandler),
                                          ('/members', MembersHandler),
                                          ('/chat', ChatHandler),
                                          ('/.*', MainHandler)],debug=True)
    
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
    main()
