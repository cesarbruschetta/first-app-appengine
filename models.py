# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

#from owner import Owner

class UserPrefs(db.Model):
    tz_offset = db.IntegerProperty(default=0)
    user = db.UserProperty(auto_current_user_add=True)
    
    def cache_set(self):
        memcache.set(self.key().name(), self, namespace=self.key().kind())
    
    def put(self):
        self.cache_set()
        db.Model.put(self)
        
# A Model for a User
class User(db.Model):
    account = db.StringProperty()
    password = db.StringProperty()
    name = db.StringProperty()

# A Model for a Mensage
class ChatMessage(db.Model):
    user = db.ReferenceProperty()
    text = db.StringProperty()
    created = db.DateTimeProperty(auto_now=True)           
        
class Bookmark(db.Model):
  description = db.StringProperty()
  favIcon     = db.BlobProperty()
  locator     = db.LinkProperty()
  timeStamp   = db.DateTimeProperty(auto_now_add = True)
  title       = db.StringProperty()
  #owner       = db.ReferenceProperty(Owner, collection_name = 'bookmarks')

  '''
  @classmethod
  def getAll(self):
    return Bookmark.all().filter('owner = ',
        Owner.getCurrent()).order(
        'description').fetch(1000)


  @property
  def dateTimeText(self):
    return self.timeStamp.strftime("%Y.%m.%d")


  @property
  def id_or_name(self):
    return self.key().id_or_name()
  '''

def get_userprefs(user_id=None):
    if not user_id:
        user = users.get_current_user()
        if not user:
            return None
        user_id = user.user_id()
    
    userprefs = memcache.get(user_id, namespace='UserPrefs')
    if not userprefs:
        key = db.Key.from_path('UserPrefs', user_id)
        userprefs = db.get(key)
        if userprefs:
            userprefs.cache_set()
        else:
            userprefs = UserPrefs(key_name=user_id)
    
    return userprefs

import appengine_admin
class AdminPagina(appengine_admin.ModelAdmin):
    model = Bookmark
    #listFields = ('title', 'data_created', 'data_updated')
    #editFields = ('title', 'content')
    #readonlyFields = ('data_created', 'data_updated')



# Register to admin site
appengine_admin.register(AdminPagina)