__author__ = 'Robin'

import pygame

class AgarPlot():

    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    PINK = (0, 255, 255)

    def __init__(self, noplot):
        if not noplot:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 800))
            self.me = None;
        self.noplot = noplot
        return

    def drawBlobs(self, me, blobs, color):
        if not self.noplot:
            self.me = me;
            if len(blobs)==0:
                return
            for key, value in blobs.iteritems():
                target = value
                draw_x = target['x']/4-me['x']/4 + 400
                draw_y = target['y']/4-me['y']/4 + 400
                if draw_x > 0 and draw_x < 800 and draw_y > 0 and draw_y < 800:
                    self.drawCircle(draw_x,draw_y,target['size']/4,color)

    def drawCircleEasy(self, me, x, y, radius, color):
        if not self.noplot:
            blobp = {}
            blobp['x'] = int(x)
            blobp['y'] = int(y)
            blobp['size'] = radius
            b = {}
            b[1] = blobp
            self.drawBlobs(me,b,color)

    def drawCircle(self, x, y, radius, color):
        if not self.noplot:
            pygame.draw.circle(self.screen, color, (x,y), radius, 0)

    def drawText(self,x,y,size,text):
        if not self.noplot:
            self.myfont = pygame.font.SysFont("monospace", size)
            label = self.myfont.render(text, True, self.WHITE)
            self.screen.blit(label, (x, y))

    def start(self):
        if not self.noplot:
            self.screen.fill((0,0,0));

    def update(self):
        if not self.noplot:
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
