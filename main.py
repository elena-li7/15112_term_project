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
        if self.cx <= 0: self.cx = 5
        if self.cx >= 640: self.cx = 635
        if self.cy <= 0: self.cy = 5
        if self.cy >= 480: self.cy = 475
    def drawHealthOxygen(self):
        drawRect(490, 0, 150, 100, fill='darkgray')
        drawLabel(f'♥   {self.health}', 550, 25, font='symbols', size=30, fill='darkred')
        drawLabel(f'○   {self.oxygen}', 550, 65, font='symbols', size=30, fill='blue')
    def loseOxygen(self, app):
        self.oxygen -= 5
        if self.oxygen <= 0:
            self.oxygen = 0
            app.gameOver = True
            print('you died!!!!!!')
    def gainOxygen(self):
        self.oxygen += 10
        if self.oxygen > 100:
            self.oxygen = 100
    
class Arrow:
    def __init__(self, startX, startY, x, y, entity):
        self.entity = entity
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


class EnemyPhysical:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.color = 'pink'
        self.health = 100
        self.powerups = set()
        self.speed = 10
        self.arrows = []
        self.hitbox = (self.cx-20, self.cy-20, 40, 40)
    def draw(self):
        drawRect(self.cx-20, self.cy-20, 40, 40, fill='white')
        drawCircle(self.cx, self.cy, 10, fill=self.color)
    def drawHealth(self):
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10, fill='limegreen')
    def attack(self, app):
        targetX = app.mc.cx
        targetY = app.mc.cy
        if targetX - self.cx > 0:
            self.cx += self.speed
        else:
            self.cx -= self.speed
        if targetY - self.cy > 0:
            self.cy += self.speed
        else:
            self.cy -= self.speed

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
        newArrow = Arrow(self.cx, self.cy, app.mc.cx, app.mc.cy, 'enemy')
        app.arrows.append(newArrow)
    
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
    app.enemyTypes = ['physical', 'ranged']
    app.gameOver = False
    app.win = False
    app.oxygen = []
    app.counter = 0
    app.mc = Character(app.width/2, app.height/2)
    app.enemyNumber = 3
    app.enemies = []
    app.arrows = []
    for i in range(app.enemyNumber):
        enemyType = random.randint(0, 1)
        if enemyType == 0:
            app.enemies.append(EnemyPhysical(random.randint(50, app.width - 200), random.randint(100, app.height - 50)))
        elif enemyType == 1:
            app.enemies.append(EnemyRanged(random.randint(50, app.width - 200), random.randint(100, app.height - 50)))
        # app.enemies.append(Enemy(random.randint(50, app.width - 200), random.randint(100, app.height - 50)))

def onStep(app):
    if app.enemyNumber == 0: 
        app.win = True
    if app.gameOver or app.win: return
    app.counter += 0.5
    if app.counter == 20:
        app.counter = 0
        app.mc.loseOxygen(app)
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
            if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2) and arrow.entity =='character':
                enemy.health -= 10
                if enemy.health <= 0:
                    app.enemies.remove(enemy)
                    app.enemyNumber -= 1
                app.arrows.remove(arrow)
            left2, top2, width2, height2 = app.mc.hitbox
            if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2) and arrow.entity =='enemy':
                app.mc.health -= 1
                if app.mc.health <= 0:
                    app.mc.health = 0
                    app.gameOver = True
                    print('you died!!!!')
                app.arrows.remove(arrow)

    for arrow in app.arrows:
        arrow.move()
        # deletes arrows that go off screen
        if arrow.startX < 0 or arrow.startX > 640 or arrow.startY < 0 or arrow.startY > 480:
            app.arrows.remove(arrow)
    for oxygen in app.oxygen:
        x, y = oxygen
        left1, top1, width1, height1 = app.mc.hitbox
        left2, top2, width2, height2 = x - 10, y - 10, 20, 20
        if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2):
            app.oxygen.remove(oxygen)
            app.mc.gainOxygen()

def onKeyHold(app, keys):
    if app.gameOver or app.win: return
    if 'up' in keys or 'w' in keys:
        app.mc.move(0, -5)
    if 'down' in keys or 's' in keys: 
        app.mc.move(0, 5)
    if 'right' in keys or 'd' in keys:
        app.mc.move(5, 0)
    if 'left' in keys or 'a' in keys:
        app.mc.move(-5, 0)

def onMousePress(app, mx, my):
    if app.gameOver or app.win: return
    newArrow = Arrow(app.mc.cx, app.mc.cy, mx, my, 'character')
    app.arrows.append(newArrow)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='gray')
    if app.win:
        drawLabel('YOU WONNNNNNN!!!!', app.width/2, app.height/2)
    elif app.gameOver:
        drawLabel('you died :(', app.width/2, app.height/2)
    else:
        app.mc.draw()
        app.mc.drawHealthOxygen()
        for enemy in app.enemies:
            enemy.draw()
            enemy.drawHealth()
            if app.counter == 10:
                enemy.attack(app)
        for arrow in app.arrows:
            arrow.draw()
        if app.counter == 10 and len(app.oxygen) <= 5:
            addOxygen(app)
        for oxygenX, oxygenY in app.oxygen:
            drawCircle(oxygenX, oxygenY, 10, fill='blue')

def addOxygen(app):
    newX = random.randint(50, app.width - 200)
    newY = random.randint(50, app.height - 50)
    app.oxygen.append((newX, newY))

def main():
    runApp(width = 640, height = 480)

main()

'''
notes
- must destroy arrows once they get off the page, too many objects
- fix the collisions so an enemy's arrows don't hurt themselves - may have to split up arrow class
- 50% success for enemy
'''
