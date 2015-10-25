__author__ = 'Robin'

from struct import *
from agarioUtil import event, boundevent
import websocket
import select

import ssl
import binascii

class AgarIO:
    """ Main AgarIO class, implements the connection to the server and parses the packets """
    def __init__(self, server, token):
        self.blobs = {}
        self.mineblobs = []
        self.ws = websocket.WebSocket()
        self.ws.settimeout(1)
        self.ws.connect(server, origin='http://agar.io')
        self.sendInit()
        self.spawned = False
        self.server_token = token
        if self.server_token is not None:
            self.token(self.server_token)

    def run(self):
        while  self.ws.connected:
            r, w, e = select.select((self.ws.sock, ), (), ())
            if r:
               self.parse(self.ws.recv())
               if(self.spawned == False):
                   self.spawned = True

    # Events
    @event
    def onUpdate(self, io):
        """Update event"""

    def smartUnPack(self, fmt, buf, offset):
        size = calcsize(fmt)
        data = unpack_from(fmt,buf,offset)[0]
        offset = offset + size
        return [data, offset]

    def smartReadString(self, buf, offset):
        datar = ''
        while True:
            wchar, offset = self.smartUnPack('<H',buf,offset)
            datar += unichr(wchar)
            if wchar == 0:
                break
        return [datar, offset]

    """ Server to client """
    def parse(self, buf):
        opcode, offset = self.smartUnPack('<B',buf,0)

        if opcode == 16:
            self.parseNodeUpdate(buf, offset)
            self.onUpdate(self)
        elif opcode == 20:
            self.parseReset(buf,offset)
        elif opcode == 32:
            self.parseOwnBlob(buf,offset)
        elif opcode == 64:
            self.parseGameSize(buf,offset)

    def parseReset(self, buf, offset):
        return

    def parseOwnBlob(self,buf,offset):
        mineblob, offset = self.smartUnPack('<L',buf,offset)
        self.mineblobs.append(mineblob)
        return
    def parseGameSize(self, buf, offset):
        return


    def parseNodeUpdate(self, buf, offset):
        eatCnt, offset = self.smartUnPack('<H',buf,offset)

        # Eat events
        for x in xrange(0, eatCnt):
            killer, offset = self.smartUnPack('<L',buf,offset)
            killee, offset = self.smartUnPack('<L',buf,offset)
            if killee in self.blobs.keys():
                del self.blobs[killee]
                self.removeAll(self.mineblobs, killee);
        # Update events
        while True:
            blob = {}
            blob['id'], offset = self.smartUnPack('<L',buf,offset)

            if(blob['id'] == 0):
                break

            blob['x'], offset = self.smartUnPack('<i',buf,offset)
            blob['y'], offset = self.smartUnPack('<i',buf,offset)
            blob['size'], offset = self.smartUnPack('<H',buf,offset)
            blob['r'], offset = self.smartUnPack('<B',buf,offset)
            blob['g'], offset = self.smartUnPack('<B',buf,offset)
            blob['b'], offset = self.smartUnPack('<B',buf,offset)
            blob['flags'], offset = self.smartUnPack('<B',buf,offset)
            blob['virus'] = blob['flags'] & 1;
            blob['agitated'] = blob['flags'] & 16;

            if(blob['flags'] & 2):
                offset = offset + 4
            elif(blob['flags'] & 4):
                offset = offset + 8
            elif(blob['flags'] & 8):
                offset = offset + 16

            blob['name'], offset = self.smartReadString(buf,offset)
            self.blobs[blob['id']] = blob

        removeCnt, offset = self.smartUnPack('<L',buf,offset)
        for x in xrange(0, removeCnt):
            removeId, offset = self.smartUnPack('<L',buf,offset)
            if removeId in self.blobs.keys():
                del self.blobs[removeId]
                self.removeAll(self.mineblobs, removeId);

    """ Client to server """
    def removeAll(self, L, x):
        while L.count(x) > 0:
            L.remove(x)
    def sendInit(self):
        self.ws.send_binary(pack('<BI',254,5))
        self.ws.send_binary(pack('<BI',255,2200049715))

    def respawn(self, nick):
        self.ws.send_binary(pack('<B%iH' % len(nick), 0, *map(ord, nick)))

    def token(self, token):
        self.ws.send_binary(pack('<B%iB' % len(token), 80, *map(ord, token)))

    def move(self, x, y):
        if(x<-10000):
            x = 0
        if(y<-10000):
            y = 0
        if(x>10000):
            x = 10000
        if(y>10000):
            y = 10000
        self.ws.send_binary(pack('<BiiI', 16, int(x), int(y), 0))

    def split(self):
        self.ws.send_binary(pack('<B', 17))

    def eject(self):
        self.ws.send_binary(pack('<B', 21))

