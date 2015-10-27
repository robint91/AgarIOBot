__author__ = 'Robin'

from math import *
from agarplot import *

class AgarBot:
    OPTIMAL_BLOB_SIZE = 100/0.75
    GROUP_NUM = 8

    def __init__(self, name):
        self.name = name
        self.target = None
        self.respawn_counter = 0
        self.regroup = False
        self.regroup_metric = 0
        self.avoid = False
        self.avoid_target = None
        self.oldTarget = None

        self.shoot = False
        self.oldShoot = False
        return

    def distance(self, a, b):
        return sqrt((a['x']-b['x'])**2 + (a['y']-b['y'])**2)

    def heading(self, a, b):
        xoff = a['x'] - b['x']
        yoff = a['y'] - b['y']
        return atan2(yoff,xoff)

    def vector(self, hdg, len):
        return (cos(hdg) * len, sin(hdg) * len)

    def select_me(self, blobs, minelist):
        minsize = 25000
        minsize_opt = 25000
        maxsize_opt = 0
        maxsize = 0;
        optBlob = None
        maxBlob = None
        minBlob = None
        if len(minelist) == 0:
            return [None, None, None]
        for id in minelist:
            if id in blobs.keys():
                target = blobs[id]
                if(target['size'] > self.OPTIMAL_BLOB_SIZE):
                    maxsize_opt = self.OPTIMAL_BLOB_SIZE
                if target['size'] < minsize and target['size'] > maxsize_opt:
                    minsize = target['size']
                    optBlob = target
                if target['size'] < minsize_opt:
                    minsize_opt = target['size']
                    minBlob = target
                if target['size'] > maxsize:
                    maxsize = target['size']
                    maxBlob = target

        return [optBlob, maxBlob, minBlob]

    def calculate_offset(self, blobs, minelist, me):
        x = 0
        y = 0
        n = 0

        for id in minelist:
            if id in blobs.keys():
                target = blobs[id]
                x += target['x']
                y += target['y']
                n += 1
        if(n>1):
            x /= float(n)
            y /= float(n)
        else:
            x = me['x']
            y = me['y']

        return [x, y]

    def findBestTarget(self, blobs, me, ignorelist, depth, size):
        target = None
        maxdist = 600000

        if depth == 0:
            return 0 , None


        for key, value in blobs.iteritems():
            if key not in ignorelist:
                d = self.distance(me, value)/6000 * float(me['size']) / (float(value['size'])*5)
                i = list(ignorelist)
                i.append(value['id'])
                dm , tg = self.findBestTarget(blobs, value, i, depth-1, size)
                d  += dm
                if d < maxdist and size*0.79 > value['size'] and  "rtheunis" not in value['name']:
                    maxdist = d
                    target = value

        return maxdist , target

    def planPath(self, blobs, minelist, me):
        ignorelist = minelist
        dm, target = self.findBestTarget(blobs,me,minelist,2, me['size'])
        return target


    def run(self, io, plot):
        goal = ""
        plot.start()
        blobs = io.blobs
        mineblobs = io.mineblobs

        me, maxopt, minopt = self.select_me(blobs,mineblobs)

        if me is not None:
            self.respawn_counter = 0


            ####################################################################
            #    Check for target/track
            ####################################################################
            maxdist = 6000
            track = False;
            #Presistant follow
            if self.target is not None:
                if self.target['id'] not in blobs.keys():
                    self.target = None
                    track = True
                    self.shoot = False
                    self.oldShoot = False

                else:
                    self.target = blobs[self.target['id']]
                    if(self.distance(self.target, me) > 600):
                        track = True
                        self.shoot = False
                        self.oldShoot = False
            else:
                track = True
                self.shoot = False
                self.oldShoot = False


            if track:
                self.target = self.planPath(blobs, mineblobs, me)

            if self.oldTarget is not None and self.target is not None:
                if(self.oldTarget['id'] == self.target['id']):
                    if(self.distance(self.target,self.oldTarget) > 0):
                        print "Moving"
                        if(self.distance(me,self.target) > self.distance(me,self.oldTarget)):
                            print "Going away"
                            if self.distance(me,self.target) < 300:
                                print "In range"
                                self.shoot = True
                            else:
                                self.shoot = False
                        else:
                            self.shoot = False


            self.oldTarget = self.target

                # Check moving target
                # Smaller as 2 times me
                # Within Range --> SHOOT


#                for key, value in blobs.iteritems():
#                    if key not in mineblobs:
#                        d = self.distance(me, value)/6000 * float(me['size']) / (float(value['size'])*5)
#                        if d < maxdist and me['size']*0.79 > value['size']:
#                            maxdist = d
#                            self.target = value
            ####################################################################
            #    Regroup
            ####################################################################
            if len(mineblobs) > self.GROUP_NUM and float(minopt['size'])/float(maxopt['size']) < 0.33 and not self.regroup:
                if self.regroup_metric < 800:
                    self.regroup_metric += 1
                else:
                    print 'regroup'
                    self.regroup = True
            else:
                if self.regroup_metric > 4:
                    self.regroup_metric -= 4
            if self.regroup:
                if len(mineblobs) == 1 or float(minopt['size'])/float(maxopt['size']) > 0.4:
                    self.regroup = False

            ####################################################################
            #    Split
            ####################################################################
            if not self.regroup:
                if minopt['size'] > 3*self.OPTIMAL_BLOB_SIZE  and len(mineblobs)<=8:
                    print 'split: ' + str(maxopt['size'])
                    io.split()

            ####################################################################
            #    Avoid
            ####################################################################
            dmin = 1000
            ax = 0
            ay = 0
            feed = False;
            feed_target = None
            for key, value in blobs.iteritems():
                if key not in mineblobs:
                    d = self.distance(me, value) - value['size'] - me['size']
                    if "rtheunis" in value['name'] and  "bot" not in value['name']:
                        print value['name']
                        if d < 300:
                            feed = True;
                            feed_target = value;
                    elif me['size']*0.79 < value['size'] and not value['virus']:
                        if d < 600:
                            plot.drawCircleEasy(me, value['x'], value['y'], value['size']+20, AgarPlot.PINK)
                            x,y = self.vector(self.heading(me, value),1)
                            ax += x
                            ay += y
                        if  dmin>d :
                            dmin = d;
                            self.avoid_target = value


            if self.avoid_target is not None:
                if dmin < 300:
                    self.avoid = True
                if dmin > 600:
                    self.avoid = False
                    self.avoid_target = None

            ####################################################################
            #    Movement
            ####################################################################
            if(feed):
                goal = "Feed"
                xoff = feed_target['x'] - me['x']
                yoff = feed_target['y'] - me['y']
                dirOff = atan2(yoff,xoff)
                xoff -= cos(dirOff) * 300
                yoff -= sin(dirOff) * 300
                io.move(feed_target['x']+xoff,feed_target['x']+yoff)
                plot.drawCircleEasy(me, feed_target['x']+xoff,feed_target['x']+yoff, feed_target['size']+20, AgarPlot.BLUE)

                io.eject()
            if self.avoid:
                goal = "avoid"
                ax,ay = self.vector(atan2(ay,ax),300)
                ax = me['x'] + ax
                ay = me['y'] + ay
                plot.drawCircleEasy(me, ax, ay, me['size'], AgarPlot.BLUE)
                io.move(ax,ay)
                if dmin < 150:
                    io.split()

            elif self.regroup:
                goal = "Regroup"
                io.move(me['x'],me['y'])
            elif self.target is not None:
                goal = "Track"
                if track:
                    print  "New Track: " + str(self.target['id'])
                xoff = self.target['x'] - me['x']
                yoff = self.target['y'] - me['y']
                dirOff = atan2(yoff,xoff)
                xoff += cos(dirOff) * me['size']
                yoff += sin(dirOff) * me['size']
                io.move(self.target['x']+xoff,self.target['y']+yoff)
                plot.drawCircleEasy(me, self.target['x'], self.target['y'], self.target['size']+20, AgarPlot.BLUE)
                plot.drawCircleEasy(me, self.target['x']+xoff, self.target['y']+yoff, self.target['size']+10, AgarPlot.WHITE)
                if self.shoot and not self.oldShoot and me['size']*2.5 > self.target['size'] and me['size'] > 90:
                    print "SHOOT!"
                    io.split()
                    self.oldShoot = self.shoot
            else:
                print "None"
                io.move(3000,3000)

            ####################################################################
            #    Update graphics
            ####################################################################
            mblobs = {}
            oblobs = {}
            for key, value in blobs.iteritems():
                if key in mineblobs:
                    mblobs[key] = value
                else:
                    oblobs[key] = value

            plot.drawCircleEasy(me, me['x'], me['y'], me['size']+20, AgarPlot.YELLOW)
            plot.drawBlobs(me, mblobs,AgarPlot.RED)
            plot.drawBlobs(me, oblobs,AgarPlot.GREEN)

            size = 0
            for id in mineblobs:
                if id in blobs.keys():
                    size += blobs[id]['size']

            plot.drawText(10,10,20,"Goal: "+ goal)
            plot.drawText(10,40,10,"Total size: "+ str(size))
            plot.drawText(10,55,10,"Max size: "+ str(maxopt['size']))
            plot.drawText(10,70,10,"Min size: "+ str(minopt['size']))

            plot.drawText(250,40,10,"Own blobs: "+ str(len(mineblobs)))
            plot.drawText(250,55,10,"Regroup metric: "+ str(self.regroup_metric))
            plot.drawText(250,70,10,"Min dist enemy: "+ str(dmin))

            plot.drawText(490,40,10,"Me pos: (" + str(me['x']) + "," + str(me['y']) + ")")
            if self.oldTarget is not None:
                plot.drawText(490,55,10,"Target rate: " + str(self.distance(me,self.target) - self.distance(me,self.oldTarget)) + "")
                plot.drawText(490,70,10,"Target speed: " + str(self.distance(self.target,self.oldTarget)) + "")


        else:
            if self.respawn_counter > 10:
                io.respawn(self.name)
                self.respawn_counter = 0
                self.target = None
                self.respawn_counter = 0
                self.regroup = False
                self.regroup_metric = 0
                self.avoid = False
                self.avoid_target = None
            else:
                self.respawn_counter += 1


        plot.update()