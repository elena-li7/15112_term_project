from cmu_graphics import *
import random
import math

class Character:
    def __init__(self, cx, cy):
        self.health = 100
        self.oxygen = 100
        self.powerups = set()
        self.cx = cx
        self.cy = cy
        self.arrows = []
        self.hitbox = (self.cx - 10, self.cy - 10, 20, 20)
        self.attackPower = 10
    def draw(self):
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
        drawLabel(f'♥   {self.health}', 550, 25, font='symbols', 
            size=30, fill='darkred')
        drawLabel(f'○   {self.oxygen}', 550, 65, font='symbols', 
            size=30, fill='blue')
    def loseOxygen(self, app):
        self.oxygen -= 5
        if self.oxygen <= 0:
            self.oxygen = 0
            app.gameOver = True
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
        self.type = 'physical'
        self.color = 'pink'
        self.health = 100
        self.powerups = set()
        self.speed = 20
        self.arrows = []
        self.hitbox = (self.cx-20, self.cy-20, 40, 40)
    def draw(self):
        drawCircle(self.cx, self.cy, 10, fill=self.color)
    def drawHealth(self):
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10,
             fill='limegreen')
    def attack(self, app):
        targetX = app.mc.cx
        targetY = app.mc.cy
        if targetX - self.cx > 0:
            self.cx += self.speed
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            if not canMove(app, self.hitbox):
                self.cx -= self.speed
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
        else:
            self.cx -= self.speed
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            if not canMove(app, self.hitbox):
                self.cx += self.speed
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
        if targetY - self.cy > 0:
            self.cy += self.speed
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            if not canMove(app, self.hitbox):
                self.cy -= self.speed
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
        else:
            self.cy -= self.speed
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            if not canMove(app, self.hitbox):
                self.cy += self.speed
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)

class EnemyRanged:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.type = 'ranged'
        self.color = 'saddleBrown'
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []
        self.hitbox = (self.cx-20, self.cy-20, 40, 40)
    def draw(self):
        drawCircle(self.cx, self.cy, 10, fill=self.color)
    def drawHealth(self):
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10,
             fill='limegreen')
    def attack(self, app):
        newArrow = Arrow(self.cx, self.cy, app.mc.cx, app.mc.cy, 'enemy')
        app.arrows.append(newArrow)

class EnemyBoss:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.type = 'boss'
        self.color = 'red'
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []
        self.hitbox = (self.cx-20, self.cy-20, 40, 40)
        self.attackPower = 5
    def draw(self):
        drawCircle(self.cx, self.cy, 10, fill=self.color)
        drawCircle(self.cx, self.cy, 150, fill=None, border='black')
    def drawHealth(self):
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10,
             fill='limegreen')
    def laserAttack(self, app, state):
        hitChance = random.randint(0, 1)
        distX = app.mc.cx - self.cx
        distY = app.mc.cy - self.cy
        dist = distance(app.mc.cx, app.mc.cy, self.cx, self.cy)
        angle = math.asin(distY / dist)
        
        if distX > 0:
            angle = math.degrees(angle)
        else:
            angle = -1 * math.degrees(angle)
        if state == 'attack': 
            if hitChance == 1:
                # does not hit
                angle += 10
            else:
                # does hit
                app.mc.health -= self.attackPower
            opacity = 100
        elif state == 'warning':
            opacity = 20
        else:
            opacity = 0
        drawRect(self.cx, self.cy, 1000, 10, rotateAngle=angle, align ='center', 
                 opacity = opacity, fill='red')
    def quakeAttack(self, app, state):
        # cx, cy = random.randint(self.cx - 100, self.cx + 100), random.randint(self.cy - 100, self.cy + 100) 
        targetX, targetY = app.mc.cx, app.mc.cy
        hitChance = random.randint(0, 3)
        if state == 'attack':
            if hitChance == 0:
                # 25% chance of hitting
                opacity = 100
                drawCircle(targetX, targetY, 30, fill='purple', opacity = opacity)
                app.mc.health -= self.attackPower * 2
        elif state == 'warning':
            opacity = 20
            drawCircle(targetX, targetY, 30, fill='purple', opacity=opacity)

    def lastDitchAttack(self, app):
        self.color='gold'
        self.attackPower = 10

###############################################################################
# this code is from CS Academy's 1.4.10 rectanglesOverlap exercise
def rectanglesOverlap(left1, top1, width1, height1,
                      left2, top2, width2, height2):
    bottom1 = top1 + height1
    bottom2 = top2 + height2
    right1 = left1 + width1
    right2 = left2 + width2
    return (bottom1 >= top2 and bottom2 >= top1 and right1 >= left2 and right2 >= left1)
###############################################################################

def distance(x0, y0, x1, y1):
    return ( (x0-x1)**2 + (y0-y1)**2 ) **0.5

def onAppStart(app):
    verticalWall = (0, 0, 20, 50)
    horizontalWall = (0, 0, 50, 20)
    squareWall = (0, 0, 30, 30)
    app.potentialObstacles = [verticalWall, horizontalWall, squareWall]
    app.numObstacles = 5
    app.obstacles = []
    for i in range(app.numObstacles):
        newObstacle = generateObstacle(app)
        app.obstacles.append(newObstacle)

    # initialize game states
    app.gameOver = False
    app.win = False
    app.bossKilled = False

    # initiliaze empty entity lists
    app.oxygen = []
    app.enemies = []
    app.arrows = []

    app.enemyTypes = ['physical', 'ranged']
    app.counter = 0
    app.mc = Character(25, 25)
    app.enemyNumber = 2
    for i in range(app.enemyNumber):
        initializeNewEnemy(app)
    app.isBoss = True
    app.boss = EnemyBoss(app.width/2, app.height/2)

def initializeNewEnemy(app):
    enemyType = random.randint(0, 1)
    if enemyType == 0:
        (app.enemies.append(EnemyPhysical(random.randint(50, app.width - 200), 
            random.randint(100, app.height - 50))))
    elif enemyType == 1:
        (app.enemies.append(EnemyRanged(random.randint(50, app.width - 200),
                random.randint(100, app.height - 50))))

def combat_onStep(app):
    if app.mc.oxygen <= 0 or app.mc.health <= 0:
        app.gameOver = True
    if app.enemyNumber == 0 and app.isBoss == False: 
        app.win = True
    if app.gameOver or app.win: 
        return
    app.counter += 0.5
    if app.counter == 20:
        app.counter = 0
        app.mc.loseOxygen(app)
    for enemy in app.enemies:
        left1, top1, width1, height1 = enemy.hitbox
        left2, top2, width2, height2 = app.mc.hitbox
        # check for physical enemy attacks
        if (rectanglesOverlap(left1-10, top1-10, width1+20, height1+20, left2-10, 
            top2-10, width2+20, height2+20) and enemy.type == 'physical'
            and app.counter == 10):
            enemy.color = 'red'
            hitChance = random.randint(0, 1)
            if hitChance == 0:
                # mc is hit
                app.mc.health -= 10
                if app.mc.health <= 0:
                    app.mc.health = 0
                    app.gameOver = True
        elif enemy.type == 'physical':
            enemy.color = 'pink'
        for arrow in app.arrows:
            arrow.move()
            if not canMove(app, arrow.hitbox):
                app.arrows.remove(arrow)
                continue
            left1, top1, width1, height1 = enemy.hitbox
            left2, top2, width2, height2 = arrow.hitbox
            # check if mc hits an enemy
            if (rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2)
                and arrow.entity =='character'):
                enemy.health -= app.mc.attackPower
                # check if enemy dies
                if enemy.health <= 0:
                    app.enemies.remove(enemy)
                    app.enemyNumber -= 1
                app.arrows.remove(arrow)
            left1, top1, width1, height1 = app.mc.hitbox
            # check if mc is hit
            if (rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2)
                and arrow.entity =='enemy'):
                app.mc.health -= 5
                if app.mc.health <= 0:
                    app.mc.health = 0
                    app.gameOver = True
                app.arrows.remove(arrow)
    # check if mc hits boss
    for arrow in app.arrows:
            arrow.move()
            if not canMove(app, arrow.hitbox):
                app.arrows.remove(arrow)
                continue
            if app.isBoss:
                left1, top1, width1, height1 = arrow.hitbox
                left2, top2, width2, height2 = app.boss.hitbox
                if (rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2)
                and arrow.entity =='character'):
                    app.arrows.remove(arrow)
                    app.boss.health -= app.mc.attackPower / 2
                    if app.boss.health <= 0:
                        app.isBoss = False
                        app.bossKilled = True
    for arrow in app.arrows:
        arrow.move()
        if not canMove(app, arrow.hitbox):
            app.arrows.remove(arrow)
            continue
        # deletes arrows that go off screen
        if (arrow.startX < 0 or arrow.startX > 640
            or arrow.startY < 0 or arrow.startY > 480):
            app.arrows.remove(arrow)
    # draw oxygen
    for oxygen in app.oxygen:
        x, y = oxygen
        left1, top1, width1, height1 = app.mc.hitbox
        left2, top2, width2, height2 = x - 10, y - 10, 20, 20
        if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2):
            app.oxygen.remove(oxygen)
            app.mc.gainOxygen()

def combat_onKeyPress(app, key):
    if key == 'p':
        setActiveScreen('pause')

def combat_onKeyHold(app, keys):
    if app.gameOver or app.win: return
    # mc movement
    if 'up' in keys or 'w' in keys:
        app.mc.move(0, -5)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(0, 5)
    if 'down' in keys or 's' in keys: 
        app.mc.move(0, 5)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(0, -5)
    if 'right' in keys or 'd' in keys:
        app.mc.move(5, 0)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(-5, 0)
    if 'left' in keys or 'a' in keys:
        app.mc.move(-5, 0)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(5, 0)

def canMove(app, entity):
    left1, top1, width1, height1 = entity
    for obstacle in app.obstacles:
        left2, top2, width2, height2 = obstacle
        if rectanglesOverlap(left1, top1, width1, height1, left2, top2, width2, height2):
            return False
    return True
    
def combat_onMousePress(app, mx, my):
    if app.gameOver or app.win: return
    newArrow = Arrow(app.mc.cx, app.mc.cy, mx, my, 'character')
    app.arrows.append(newArrow)

def combat_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='gray')
    if not app.gameOver and not app.win:
        for obstacle in app.obstacles:
            x, y, width, height = obstacle
            drawRect(x, y, width, height, fill='darkslategray')
    if app.win:
        setActiveScreen('win')
    elif app.gameOver:
        setActiveScreen('gameOver')
    else:
        if app.isBoss:
            if app.boss.health <= 25 and app.boss.health > 0:
                app.boss.lastDitchAttack(app)
            if distance(app.boss.cx, app.boss.cy, app.mc.cx, app.mc.cy) <= 160:
                app.mc.attackPower = 20
                if 0 <= app.counter < 15:
                    app.boss.quakeAttack(app, 'warning')
                elif app.counter == 15:
                    app.boss.quakeAttack(app, 'attack')
            else:
                app.mc.attackPower = 10
                if 0 <= app.counter < 10:
                    app.boss.laserAttack(app, 'warning')
                elif app.counter == 10:
                    app.boss.laserAttack(app, 'attack')
            app.boss.draw()
            app.boss.drawHealth()
        elif app.bossKilled:
            # boss explodes and deals a large amount of dmg              
            drawCircle(app.width/2, app.height/2, 100, fill='orange')
            if distance(app.width/2, app.height/2, app.mc.cx, app.mc.cy) <= 110:
                app.mc.health -= 25
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
        app.mc.draw()
        app.mc.drawHealthOxygen()

def addOxygen(app):
    newX = random.randint(50, app.width - 200)
    newY = random.randint(50, app.height - 50)
    app.oxygen.append((newX, newY))

def generateObstacle(app):
    index = random.randint(0, 2)
    obstacle = app.potentialObstacles[index]
    startX, startY, width, height = obstacle
    x, y = random.randint(0, 590), random.randint(0, 430)
    return (startX+x, startY+y, width, height)

#--------------
def pause_onKeyPress(app, key):
    if key == 'p':
        setActiveScreen('combat')

def pause_redrawAll(app):
    drawRect(0, 0, app.width, app.height)
    drawLabel('PAUSED.', app.width/2, 100, fill=rgb(176, 120, 30), bold=True, size=30)
    drawRect(app.width/2 - 100, 200, 200, 50, fill='moccasin')
    drawRect(app.width/2 - 100, 275, 200, 50, fill='moccasin')
    drawLabel('resume', app.width/2, 225, fill=rgb(176, 120, 30), size=20)
    drawLabel('quit', app.width/2, 300, fill=rgb(176, 120, 30), size=20)

def pause_onMousePress(app, mx, my):
    if app.width/2-100 <= mx <= app.width/2+100 and 200 <= my <= 250:
        setActiveScreen('combat')
    if app.width/2-100 <= mx <= app.width/2+100 and 275 <= my <= 325:
        setActiveScreen('titleScreen')
#--------------
def titleScreen_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('MOONLIGHT ARCHER', app.width/2, 100, fill=rgb(176, 120, 30), size=25, bold=True)
    drawLabel('super cool logo', 450, app.height/2, fill='gold')
    drawRect(100, app.height/2 - 50, 150, 50, fill='papayaWhip', border='gold', borderWidth=5)
    drawRect(100, app.height/2 + 50, 150, 50, fill='papayaWhip', border='gold', borderWidth=5)
    drawLabel('START', 175, app.height/2 - 25, fill=rgb(176, 120, 30), size=20)
    drawLabel('TUTORIAL', 175, app.height/2 + 75, fill=rgb(176, 120, 30), size=20)

def titleScreen_onMousePress(app, mx, my):
    if 100 <= mx <= 250 and app.height/2 - 50 <= my <= app.height/2:
        setActiveScreen('phaseSelection')
    if 100 <= mx <= 250 and app.height/2 + 50 <= my <= app.height/2 + 100:
        setActiveScreen('tutorial')
#--------------
def tutorial_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawRect(50, 50, app.width-100, app.height-100, fill=None, border='moccasin', borderWidth=5)
    drawRect(app.width/2 - 75, 25, 150, 50)
    drawLabel('TUTORIAL', app.width/2, 50, fill=rgb(176, 120, 30), size=25, bold=True)
    drawRect(80, 350, 50, 50, fill=None, border=rgb(176, 120, 30), borderWidth=5)
    drawLabel('⌂', 105, 375, font='symbols', fill='moccasin', size=30, bold=True)

def tutorial_onMousePress(app, mx, my):
    if 80 <= mx <= 130 and 350 <= my <= 400:
        setActiveScreen('titleScreen')
#--------------
def gameOver_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('GAME', app.width/2, 100, fill='darkRed', size=50)
    drawLabel('OVER', app.width/2, 175, fill='darkRed', size=50)
#--------------
def win_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('you won!', app.width/2, app.height/2, fill=rgb(176, 120, 30), size=50)
#--------------
def phaseSelection_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('PHASE SELECTION', app.width/2, 50, fill=rgb(176, 120, 30), size=30)
    drawRect(app.width/5 - 45, 100, 90, app.height-200, fill=rgb(176, 120, 30))
    drawRect(app.width/5*2 - 45, 100, 90, app.height-200, fill=rgb(176, 120, 30))
    drawRect(app.width/5*3 - 45, 100, 90, app.height-200, fill=rgb(176, 120, 30))
    drawRect(app.width/5*4 - 45, 100, 90, app.height-200, fill=rgb(176, 120, 30))
    drawLabel('I', app.width/5, 125, fill='moccasin', size=30, bold=True)
    drawLabel('II', app.width/5*2, 125, fill='moccasin', size=30, bold=True)
    drawLabel('III', app.width/5*3, 125, fill='moccasin', size=30, bold=True)
    drawLabel('IV', app.width/5*4, 125, fill='moccasin', size=30, bold=True)

def phaseSelection_onMousePress(app, mx, my):
    if 100 <= my <= app.height-100:
        if app.width/5 - 45 <= mx <= app.width/5 + 45:
            setActiveScreen('phaseOne')
        elif app.width/5*2 - 45 <= mx <= app.width/5*2 + 45:
            setActiveScreen('phaseTwo')
        elif app.width/5*3 - 45 <= mx <= app.width/5*3 + 45:
            setActiveScreen('phaseThree')
        elif app.width/5*4 - 45 <= mx <= app.width/5*4 + 45:
            setActiveScreen('phaseFour')
#------------
def phaseOne_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('FIRST QUARTER', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill='white')
    drawArc(app.width/2, app.height/2, 190, 190, 90, 180, fill='black')
#------------
def phaseTwo_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('FULL MOON', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill='white')
#------------
def phaseThree_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('LAST QUARTER', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill=None, border='white', borderWidth=5)
    drawArc(app.width/2, app.height/2, 200, 200, 90, 180, fill='white')
#------------
def phaseFour_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('NEW MOON', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill=None, border='white')
def main():
    runAppWithScreens(width=640, height=480, initialScreen='phaseSelection')

main()
