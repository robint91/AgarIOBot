__author__ = 'Robin'


import requests
from agario import *
from agarbot import *
from agarplot import *

def getAgarIOToken():
    url = 'http://m.agar.io'
    r = requests.post(url, data='EU-London', allow_redirects=True)
    a = r.text.split('\n')
    host, port = a[0].split(':')
    token = a[1]
    return host, port, token


if __name__ == "__main__":
    plot = AgarPlot(True)
    io = AgarIO("ws://newbies.servebeer.com:443", None)
    #host, port, token = getAgarIOToken()
	#print "Connecting to " + "ws://"+str(host)+":"+str(port)
    #io = AgarIO("ws://"+str(host)+":"+str(port), token)
    bot = AgarBot("rtheunis_bot")
    io.onUpdate += lambda io: bot.run(io, plot)

    io.run()


