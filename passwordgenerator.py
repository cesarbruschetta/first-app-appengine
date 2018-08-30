#!/usr/bin/env python
import cgi
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class DDTHandler(webapp.RequestHandler):
    def __startDisplay(self):
        self.response.out.write("<!--\n")
    
    def __endDisplay(self):
        self.response.out.write("-->\n")

    def __showDictionaryItems(self, dictionary, title):
        if (len(dictionary) > 0):
            request = self.request
            out = self.response.out
            out.write("\n"+title+":\n")
            for key, value in dictionary.iteritems():
                out.write(key+" = "+value+"\n")

    def __showRequestMembers(self):
        request = self.request
        out = self.response.out
        out.write(request.url+"\n")
        out.write("Query = "+request.query_string+"\n")
        out.write("Remote = "+request.remote_addr+"\n")
        out.write("Path = "+request.path+"\n\n")
        out.write("Request payload:\n")
        if (len(request.arguments()) > 0):
            for argument in request.arguments():
                value = cgi.escape(request.get(argument))
                out.write(argument+" = "+value+"\n")
        else:
            out.write("Empty\n")
            self.__showDictionaryItems(request.headers, "Headers")
            self.__showDictionaryItems(request.cookies, "Cookies")

    def viewRequest(self):
        self.__startDisplay()
        self.__showRequestMembers()
        self.__endDisplay()
    
    def view(self, aString):
        self.__startDisplay()
        self.response.out.write(aString+"\n")
        self.__endDisplay()



# *** Symbolic Constants ***
BASE = ord('0')
def mainForm():
    return """
            <html>
                <head>
                    <title>GenPasswd Strong(ish) Password Generator</title>
                </head>
                <body>
                    <div align="center">
                        <h1>Strong(ish) Password Generator</h1>
                        <form method="POST" name="baseWordCapture" action="/passwordGenRequest">
                            <p>Base word (6 chars minimum):</p>
                            <input type="text" name="baseWord" cols="24" /> <br />
                            <input type="submit" value="Enviar"/>
                            <input type="reset" value="Limpar"/>
                           <p>Password:</p>
                           <p>n/a</p>
                        </form>
                    </div>
                </body>
            </html>
           """
class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write(mainForm())

class UserRequestHandler(webapp.RequestHandler):

    def post(self):
        output = self.response.out
        baseWord = cgi.escape(self.request.get('baseWord'))
        password = self.__process(baseWord)
        output.write(mainForm().replace("n/a", password))


class PasswordGenerator(DDTHandler):
    def __process(self, aWord):
        password = ""
        if (len(aWord) >= 6):
            for i in range(len(aWord)):
                if i in [1, 5, 8, 13, 21]:
                    password += chr(BASE+(ord(aWord[i])+i)%10)
                else:
                    password += aWord[i]
        return password
    
    def get(self):
        self.viewRequest()
        self.response.out.write(mainForm())
    
    def post(self):
        self.viewRequest()
        output = self.response.out 
        baseWord = cgi.escape(self.request.get('baseWord'))
        password = self.__process(baseWord)
        output.write(mainForm().replace("n/a", password))

def main():
    application = webapp.WSGIApplication([('/password', MainPage),
                                          ('/passwordGenRequest', PasswordGenerator) ], debug=True)

    run_wsgi_app(application)

if __name__ == '__main__':
    main()
