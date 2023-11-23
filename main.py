from cmu_graphics import *
import random

class Character:
    def __init__(self, cx, cy):
        self.health = 100
        self.oxygen = 100
        self.powerups = set()
        self.cx = cx
        self.cy = cy
        self.arrows = []
        self.hitbox = (self.cx - 10, self.cy - 10, 20, 20)
    def draw(self):
        drawRect(self.cx - 10, self.cy - 10, 20, 20, fill='white')
        drawCircle(self.cx, self.cy, 10)
    def move(self, dx, dy):
        self.cx += dx
        self.cy += dy
        self.hitbox = (self.cx - 10, self.cy - 10, 20, 20)
    def drawHealthOxygen(self):
        drawRect(490, 0, 150, 100, fill='darkgray')
        drawLabel(f'♥   {self.health}', 550, 25, font='symbols', size=30, fill='darkred')
        drawLabel(f'○   {self.oxygen}', 550, 65, font='symbols', size=30, fill='blue')

    
class Arrow:
    def __init__(self, startX, startY, x, y):
        self.startX = startX
        self.startY = startY
        self.dx = None
        self.dy = None
        self.hitbox = (self.startX - 10, self.startY-10, 50, 25)
        self.x = x
        self.y = y
        vecX, vecY = self.x - self.startX, self.y-self.startY
        mag = ((vecX)**2 + (vecY)**2)**0.5
        unitvecX, unitvecY = vecX/mag, vecY/mag
        unitvecX *= 5
        unitvecY *= 5
        self.dx, self.dy = unitvecX, unitvecY
    def draw(self):
        vecX, vecY = self.x - self.startX, self.y-self.startY
        mag = ((vecX)**2 + (vecY)**2)**0.5
        unitvecX, unitvecY = vecX/mag, vecY/mag
        unitvecX *= 25
        unitvecY *= 25
        drawLine(self.startX, self.startY, self.startX+unitvecX, self.startY+unitvecY)
    def move(self):
        self.startX += self.dx 
        self.startY += self.dy  
        self.hitbox = (self.startX - 10, self.startY-10, 50, 25)


class Enemy:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.color = 'pink'
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []
        self.hitbox = (self.cx-20, self.cy-20, 40, 40)
    def draw(self):
        drawRect(self.cx-20, self.cy-20, 40, 40, fill='white')
        drawCircle(self.cx, self.cy, 10, fill=self.color)
    def drawHealth(self):
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10, fill='limegreen')

class EnemyRanged:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.color = 'saddleBrown'
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []
        self.hitbox = (self.cx-20, self.cy-20, 40, 40)
    def draw(self):
        drawRect(self.cx-20, self.cy-20, 40, 40, fill='white')
        drawCircle(self.cx, self.cy, 10, fill=self.color)
    def drawHealth(self):
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10, fill='limegreen')
    def attack(self, app):
        newArrow = Arrow(self.cx, self.cy, app.mc.cx, app.mc.cy)
        app.arrows.append(newArrow)
        # newArrow.draw()
    
# this code is from CS Academy's 1.4.10 rectanglesOverlap exercise
def rectanglesOverlap(left1, top1, width1, height1,
                      left2, top2, width2, height2):
    bottom1 = top1 + height1
    bottom2 = top2 + height2
    right1 = left1 + width1
    right2 = left2 + width2
    return (bottom1 >= top2 and bottom2 >= top1 and right1 >= left2 and right2 >= left1)
###############################################################################

def onAppStart(app):
    app.enemyCounter = 0
    app.mc = Character(app.width/2, app.height/2)
    app.enemyNumber = 1
    app.enemies = []
    app.arrows = []
    for i in range(app.enemyNumber):
        app.enemies.append(EnemyRanged(random.randint(50, app.width - 200), random.randint(100, app.height - 50)))
        # app.enemies.append(Enemy(random.randint(50, app.width - 200), random.randint(100, app.height - 50)))

def onStep(app):
    app.enemyCounter += 1
    if app.enemyCounter == 25:
        app.enemyCounter %= 25
    for enemy in app.enemies:
        left1, top1, width1, height1 = enemy.hitbox
        left2, top2, width2, height2 = app.mc.hitbox
        # if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2):
        #     enemy.color = 'red'
        # else:
        #     enemy.color = 'blue'
        for arrow in app.arrows:
            arrow.move()
            left1, top1, width1, height1 = arrow.hitbox
            left2, top2, width2, height2 = enemy.hitbox
            # if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2):
            #     enemy.health -= 10
            #     if enemy.health <= 0:
            #         app.enemies.remove(enemy)
            #     app.arrows.remove(arrow)
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
    app.mc.drawHealthOxygen()
    for enemy in app.enemies:
        enemy.draw()
        enemy.drawHealth()
        if app.enemyCounter == 2:
            enemy.attack(app)
    for arrow in app.arrows:
        arrow.draw()


def main():
    runApp(width = 640, height = 480)

main()
