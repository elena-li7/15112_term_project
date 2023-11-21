from cmu_graphics import *

class Character:
    def __init__(self, cx, cy):
        self.health = 100
        self.oxygen = 100
        self.powerups = set()
        self.cx = cx
        self.cy = cy
        self.arrows = []

    def draw(self):
        drawCircle(self.cx, self.cy, 10)

    def move(self, dx, dy):
        self.cx += dx
        self.cy += dy
    
class Arrow:
    def __init__(self, startX, startY, x, y):
        self.startX = startX
        self.startY = startY
        self.x = x
        self.y = y
        self.dx = None
        self.dy = None
    def draw(self):
        vecX, vecY = self.x - self.startX, self.y-self.startY
        mag = ((vecX)**2 + (vecY)**2)**0.5
        unitvecX, unitvecY = vecX/mag, vecY/mag
        unitvecX *= 25
        unitvecY *= 25
        self.dx, self.dy = unitvecX, unitvecY
        drawLine(self.startX, self.startY, self.startX+unitvecX, self.startY+unitvecY)
    def move(self):
        self.startX += self.dx
        self.startY += self.dy


class Enemy:
    def __init__(self, enemyType, name):
        self.enemyType = physical
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []


def onAppStart(app):
    app.mc = Character(app.width/2, app.height/2)
    app.arrows = []

def onStep(app):
    for arrow in app.arrows:
        arrow.move()

def onKeyHold(app, keys):
    if 'up' in keys or 'w' in keys:
        app.mc.move(0, -5)
    if 'down' in keys or 's' in keys: 
        app.mc.move(0, 5)
    if 'right' in keys or 'd' in keys:
        app.mc.move(5, 0)
    if 'left' in keys or 'a' in keys:
        app.mc.move(-5, 0)

def onMousePress(app, mx, my):
    newArrow = Arrow(app.mc.cx, app.mc.cy, mx, my)
    app.arrows.append(newArrow)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='gray')
    app.mc.draw()
    for arrow in app.arrows:
        arrow.draw()

def main():
    runApp(width = 640, height = 480)

main()