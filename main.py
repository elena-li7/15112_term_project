from cmu_graphics import *
import random
import math
from PIL import Image, ImageDraw
import os, pathlib

class Character:
    def __init__(self, cx, cy, app):
        self.sprite = app.spriteForward
        self.health = 100
        self.oxygen = 100
        self.powerups = set()
        self.cx = cx
        self.cy = cy
        self.arrows = []
        self.width, self.height = getImageSize(CMUImage(self.sprite))
        self.hitbox = (self.cx - self.width/2, self.cy - self.height/2, self.width, self.height)
        self.attackPower = 10
        self.direction = 'forward'
        self.scene = 'combat'
    def draw(self, app):
        if self.scene == 'combat':
            if self.direction == 'forward':
                self.sprite = app.spriteForward
            elif self.direction == 'backward':
                self.sprite = app.spriteBackward
            elif self.direction == 'right':
                self.sprite = app.spriteRight
            elif self.direction == 'left':
                self.sprite = app.spriteLeft
        elif self.scene == 'candle':
            if self.direction == 'forward':
                self.sprite = app.spriteForwardCandle
            elif self.direction == 'right':
                self.sprite = app.spriteRightCandle
            elif self.direction == 'left':
                self.sprite = app.spriteLeftCandle
        drawImage(CMUImage(self.sprite), self.cx-self.width/2, self.cy-self.height/2)
        self.width, self.height = getImageSize(CMUImage(self.sprite))
        self.hitbox = (self.cx - self.width/2, self.cy - self.height/2, self.width, self.height)
    def move(self, dx, dy):
        self.cx += dx
        self.cy += dy
        if dx > 0:
            self.direction = 'right'
        if dx < 0:
            self.direction = 'left'
        if dy > 0:
            self.direction = 'forward'
        if dy < 0 and self.scene != 'candle':
            self.direction = 'backward'
        self.hitbox = (self.cx - 10, self.cy - 10, 20, 20)
        if self.cx <= 0: self.cx = 5
        if self.cx >= 640: self.cx = 635
        if self.cy <= 0: self.cy = 5
        if self.cy >= 480: self.cy = 475
    def drawHealthOxygen(self, app):
        drawImage(CMUImage(app.heartImage), 520, 15)
        drawLabel(f'   {self.health}', 560, 25, font='symbols', 
            size=30, fill='darkred')
        drawImage(CMUImage(app.bubbleImage), 520, 55)
        drawLabel(f'   {self.oxygen}', 560, 65, font='symbols', 
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
    def draw(self, app):
        distX = self.x - self.startX
        distY = self.y - self.startY
        dist = distance(self.x, self.y, self.startX, self.startY)
        angle = math.asin(distY / dist)
        if distX > 0:
            angle = math.degrees(angle) + 120
        else:
            angle = -1 * math.degrees(angle) - 60
        drawImage(CMUImage(app.arrowImage), self.startX, self.startY, rotateAngle=angle)
    def move(self):
        self.startX += self.dx 
        self.startY += self.dy  
        self.hitbox = (self.startX - 10, self.startY-10, 50, 25)

class EnemyPhysical:
    def __init__(self, cx, cy, app):
        self.cx = cx
        self.cy = cy
        self.type = 'physical'
        self.health = 100
        self.powerups = set()
        self.speed = 20
        self.arrows = []
        self.width, self.height = getImageSize(CMUImage(app.greenGhostForward))
        self.hitbox = (self.cx-self.width/2, self.cy-self.height/2, self.width, self.height)
    def draw(self, app):
        if app.stage == 'combat':
            drawImage(CMUImage(app.greenGhostForward), self.cx - self.width/2, self.cy-self.height/2)
        elif app.stage == 'red':
            drawImage(CMUImage(app.darkRedGhostForward), self.cx - self.width/2, self.cy-self.height/2)
    def drawHealth(self):
        healthColor = 'limegreen'
        if 25 <= self.health <= 75:
            healthColor = 'gold'
        if self.health < 25:
            healthColor = 'darkred'
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10,
             fill=healthColor)
    def attack(self, app):
        targetX = app.mc.cx
        targetY = app.mc.cy
        if targetX - self.cx > 0:
            self.cx += self.speed
            if self.cx > app.width - 25:
                self.cx = app.width - 25
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            while not canMove(app, self.hitbox):
                self.cx -= self.speed
                self.cy += 50
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
        else:
            self.cx -= self.speed
            if self.cx < 25:
                self.cx = 25
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            while not canMove(app, self.hitbox):
                self.cx += self.speed
                self.cy -= 50
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
        if targetY - self.cy > 0:
            self.cy += self.speed
            if self.cy > app.height - 30:
                self.cy = app.height - 30
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            while not canMove(app, self.hitbox):
                self.cy -= self.speed
                self.cx -= 50
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
        else:
            self.cy -= self.speed
            if self.cy < 30:
                self.cy = 30
            self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
            while not canMove(app, self.hitbox):
                self.cy += self.speed
                self.cx += 50
                self.hitbox = (self.cx - 20, self.cy-20, 40, 40)
class EnemyRanged:
    def __init__(self, cx, cy, app):
        self.cx = cx
        self.cy = cy
        self.type = 'ranged'
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []
        self.width, self.height = getImageSize(CMUImage(app.ghostForward))
        self.hitbox = (self.cx-self.width/2, self.cy-self.height/2, self.width, self.height)
    def draw(self, app):
        if app.stage == 'combat':
            drawImage(CMUImage(app.ghostForward), self.cx - self.width/2, self.cy-self.height/2)
        elif app.stage == 'red':
            drawImage(CMUImage(app.redGhostForward), self.cx - self.width/2, self.cy-self.height/2)
    def drawHealth(self):
        healthColor = 'limegreen'
        if 25 <= self.health <= 75:
            healthColor = 'gold'
        if self.health <25:
            healthColor = 'darkred'
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10,
             fill=healthColor)
    def attack(self, app):
        newArrow = Arrow(self.cx, self.cy, app.mc.cx, app.mc.cy, 'enemy')
        app.arrows.append(newArrow)

class EnemyBoss:
    def __init__(self, cx, cy, app):
        self.cx = cx
        self.cy = cy
        self.type = 'boss'
        self.color = 'red'
        self.health = 100
        self.powerups = set()
        self.speed = 5
        self.arrows = []
        self.width, self.height = getImageSize(CMUImage(app.bossImage))
        self.hitbox = (self.cx-self.width/2, self.cy-self.height/2, self.width, self.height)
        self.attackPower = 5
    def draw(self, app):
        drawImage(CMUImage(app.bossImage), self.cx-self.width/2, self.cy-self.height/2)        
        drawCircle(self.cx, self.cy, 150, fill=None, border='gray', borderWidth=5)
    def drawHealth(self):
        healthColor = 'limegreen'
        if 25 <= self.health <= 75:
            healthColor = 'gold'
        if self.health <25:
            healthColor = 'darkred'
        drawRect(self.cx - 25, self.cy + 30, 50, 20, fill='dimgray')
        drawRect(self.cx - 20, self.cy + 35, self.health / 100 * 40, 10,
             fill=healthColor)
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
                drawCircle(targetX, targetY, 30, fill='purple', opacity=opacity)
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
    return (bottom1>=top2 and bottom2>=top1 and right1>=left2 and right2>=left1)
###############################################################################

def distance(x0, y0, x1, y1):
    return ( (x0-x1)**2 + (y0-y1)**2 ) **0.5

def onAppStart(app):
    app.tutorialImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                                'tutorial.png'))
    app.titleImage = Image.open(os.path.join(pathlib.Path(__file__).parent, 
                                             'titlescreen.png'))
    app.settingsImage = Image.open(os.path.join(pathlib.Path(__file__).parent, 
                                             'settings.png'))
    app.arrowImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                            'arrow.png'))
    app.spriteForward = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                            'spriteForward.png'))
    app.spriteBackward = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                            'spriteBackward.png'))
    app.spriteRight = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                            'spriteRight.png'))
    app.spriteLeft = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                            'spriteLeft.png'))
    app.ghostForward = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'ghostForward.png'))
    app.greenGhostForward = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'greenGhostForward.png'))
    app.bubbleImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'bubble.png'))
    app.combatImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'combat.png'))
    app.bossImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'boss.png'))
    app.heartImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'heart.png'))
    app.phaseOneWin = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'phaseOneWin.png'))
    app.phaseTwoWin = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'phaseTwoWin.png'))
    app.phaseThreeWin = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'phaseThreeWin.png'))
    app.redGhostForward = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'redGhostForward.png'))
    app.darkRedGhostForward = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'darkRedGhostForward.png'))
    app.combatRed = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'combatRed.png'))
    app.gameOverImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'gameOver.png'))
    app.victoryImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'victory.png'))
    app.spriteForwardCandle = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'spriteForwardCandle.png'))
    app.spriteRightCandle = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'spriteRightCandle.png'))
    app.spriteLeftCandle = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'spriteLeftCandle.png'))
    app.moonImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'moon.png'))
    app.moonCandleImage = Image.open(os.path.join(pathlib.Path(__file__).parent,
                                               'moonCandle.png'))
    app.stage = 'combat'
    app.phase = 1
    app.enemyNumber = 0
    app.numObstacles = 0
    app.isBoss = False
    app.boss = EnemyBoss(app.width/2, app.height/2, app)

    app.verticalWall = (0, 0, 20, 50)
    app.horizontalWall = (0, 0, 50, 20)
    app.squareWall = (0, 0, 30, 30)
    app.potentialObstacles=[app.verticalWall,app.horizontalWall,app.squareWall]

    # initialize game states
    app.gameOver = False
    app.win = False
    app.bossKilled = False

    # initiliaze empty entity lists
    app.oxygen = []
    app.enemies = []
    app.arrows = []
    app.obstacles = []

    app.characterSpeed = 5
    app.enemyStrength = 10

    app.enemyTypes = ['physical', 'ranged']
    app.counter = 0
    app.moonMC = Character(50, 375, app)
    app.moonMC.scene = 'candle'
    app.mc = Character(25, app.height-50, app)

    app.candleCounter = 50
    app.candleWarning = False

def initializeNewEnemy(app):
    enemyType = random.randint(0, 1)
    if enemyType == 0:
        (app.enemies.append(EnemyPhysical(random.randint(50, 550), 
            random.randint(100, app.height - 50), app)))
    elif enemyType == 1:
        (app.enemies.append(EnemyRanged(random.randint(50, app.width - 200),
                random.randint(100, app.height - 50), app)))

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
                app.mc.health -= app.enemyStrength
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
            if (rectanglesOverlap(left1, top1, width1, height1, 
                                  left2, top2, width2, height2)
                and arrow.entity =='character'):
                enemy.health -= app.mc.attackPower
                # check if enemy dies
                if enemy.health <= 0:
                    app.enemies.remove(enemy)
                    app.enemyNumber -= 1
                app.arrows.remove(arrow)
            left1, top1, width1, height1 = app.mc.hitbox
            # check if mc is hit
            if (rectanglesOverlap(left1, top1, width1, height1, 
                                  left2, top2, width2, height2)
                and arrow.entity =='enemy'):
                app.mc.health -= app.enemyStrength//2
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
                if (rectanglesOverlap(left1, top1, width1, height1, 
                                      left2, top2, width2, height2)
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
        if rectanglesOverlap(left1, top1, width1, height1, 
                             left2, top2, width2, height2):
            app.oxygen.remove(oxygen)
            app.mc.gainOxygen()

def combat_onKeyPress(app, key):
    if key == 'p':
        setActiveScreen('pause')

def combat_onKeyHold(app, keys):
    if app.gameOver or app.win: return
    # mc movement
    if 'up' in keys or 'w' in keys:
        app.mc.move(0, -1 * app.characterSpeed)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(0, app.characterSpeed)
    if 'down' in keys or 's' in keys: 
        app.mc.move(0, app.characterSpeed)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(0, -1 * app.characterSpeed)
    if 'right' in keys or 'd' in keys:
        app.mc.move(app.characterSpeed, 0)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(-1 * app.characterSpeed, 0)
    if 'left' in keys or 'a' in keys:
        app.mc.move(-1 * app.characterSpeed, 0)
        if not canMove(app, app.mc.hitbox):
            app.mc.move(app.characterSpeed, 0)

def canMove(app, entity):
    if app.phase != 'red' and app.phase != 'combat':
        return True
    left1, top1, width1, height1 = entity
    for obstacle in app.obstacles:
        left2, top2, width2, height2 = obstacle
        if rectanglesOverlap(left1, top1, width1, height1, 
                             left2, top2, width2, height2):
            return False
    return True
    
def combat_onMousePress(app, mx, my):
    if 10 <= mx <= 50 and 10 <= my <= 50:
        setActiveScreen('pause')
    if app.gameOver or app.win: return
    newArrow = Arrow(app.mc.cx, app.mc.cy, mx, my, 'character')
    app.arrows.append(newArrow)

def combat_redrawAll(app):
    if app.stage == 'combat':
        drawImage(CMUImage(app.combatImage), 0, 0)
    elif app.stage == 'red':
        drawImage(CMUImage(app.combatRed), 0, 0)
    if not app.gameOver and not app.win:
        for obstacle in app.obstacles:
            x, y, width, height = obstacle
            color = None
            if app.stage == 'combat':
                color = 'darkslategray'
            elif app.stage == 'red':
                color = 'sienna'
            drawRect(x, y, width, height, fill=color)
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
            app.boss.draw(app)
            app.boss.drawHealth()
        elif app.bossKilled:
            # boss explodes and deals a large amount of dmg              
            drawCircle(app.width/2, app.height/2, 100, fill='orange')
            if distance(app.width/2, app.height/2, app.mc.cx, app.mc.cy) <= 110:
                app.mc.health -= 1
        for enemy in app.enemies:
            enemy.draw(app)
            enemy.drawHealth()
            if app.counter == 10:
                enemy.attack(app)
        for arrow in app.arrows:
            arrow.draw(app)
        if app.counter == 10 and len(app.oxygen) <= 5:
            addOxygen(app)
        for oxygenX, oxygenY in app.oxygen:
            width, height = getImageSize(CMUImage(app.bubbleImage))
            drawImage(CMUImage(app.bubbleImage), oxygenX-width/2, oxygenY-height/2)
        app.mc.draw(app)
        app.mc.drawHealthOxygen(app)

def addOxygen(app):
    newX = random.randint(50, 450)
    newY = random.randint(70, app.height - 60)
    app.oxygen.append((newX, newY))

def generateObstacle(app):
    index = random.randint(0, 2)
    obstacle = app.potentialObstacles[index]
    startX, startY, width, height = obstacle
    x, y = random.randint(50, 550), random.randint(110, 430)
    return (x, y, width, height)

#--------------
def pause_onKeyPress(app, key):
    if key == 'p':
        setActiveScreen('combat')

def pause_redrawAll(app):
    drawRect(0, 0, app.width, app.height)
    drawLabel('PAUSED.', app.width/2, 100, fill=rgb(176, 120, 30), 
              bold=True, size=30)
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
    drawImage(CMUImage(app.titleImage), 0, 0)
    drawRect(app.width - 98, app.height - 98, 75, 75, borderWidth=5, border=rgb(176, 120, 30), fill=None)

def titleScreen_onMousePress(app, mx, my):
    if 115 <= mx <= 215 and app.height/2 - 40 <= my <= app.height/2+40:
        app.phase = 1
        setActiveScreen('phaseSelection')
    if 115 <= mx <= 215 and app.height/2 + 62 <= my <= app.height/2 + 142:
        setActiveScreen('tutorial')
    if app.width-98 <= mx <= app.width-23 and app.height-98 <= my <= app.height-23:
        setActiveScreen('settings')
#--------------
def settings_redrawAll(app):
    drawImage(CMUImage(app.settingsImage), 0, 0)
    drawRect(80, 350, 50, 50, fill=None, border=rgb(176, 120, 30), borderWidth=5)
    drawLabel('⌂', 105, 375, font='symbols', fill='moccasin', size=30, bold=True)
    drawLine(app.width/2 - 100, app.height/2, app.width/2+100, app.height/2, fill='saddleBrown', lineWidth=5)
    drawCircle(app.width/2-100 +20*app.characterSpeed, app.height/2, 7, fill=rgb(176, 120, 30))
    drawRect(app.width/2-150, app.height/2 - 12.5, 25, 25, fill='saddleBrown')
    drawRect(app.width/2+125, app.height/2 - 12.5, 25, 25, fill='saddleBrown')
    drawLabel(f'CHARACTER SPEED: {app.characterSpeed}', app.width/2, app.height/2 - 30, fill=rgb(176, 120, 30), size=17, bold=True)
    drawLabel('_', app.width/2-137.5, app.height/2-2.5, fill='white', size=20, bold=True)
    drawLabel('+', app.width/2+137.5, app.height/2, fill='white', size=20, bold=True)

def settings_onMousePress(app, mx, my):
    if 80 <= mx <= 130 and 350 <= my <= 400:
        setActiveScreen('titleScreen')
    if app.width/2-150 <= mx <= app.width/2-125 and app.height/2-12.5 <= my <= app.height/2+12.5:
        app.characterSpeed -= 1
        if app.characterSpeed < 1:
            app.characterSpeed = 1
    if app.width/2+125 <= mx <= app.width/2+150 and app.height/2-12.5 <= my <= app.height/2+12.5:
        app.characterSpeed += 1
        if app.characterSpeed > 10:
            app.characterSpeed = 10
#--------------
def tutorial_redrawAll(app):
    drawImage(CMUImage(app.tutorialImage), 0, 0)
    drawRect(80, 350, 50, 50, fill=None, border=rgb(176, 120, 30), borderWidth=5)
    drawLabel('⌂', 105, 375, font='symbols', fill='moccasin', size=30, bold=True)
    drawLabel('1. Use WASD or arrow keys to move.', 150, 200, fill='moccasin', 
              size=15, align='left', bold=True)
    drawLabel('2. Replenish oxygen by collecting oxygen particles.', 150, 250, 
              fill='moccasin', size=15, align='left', bold=True)
    drawLabel('3. Defeat enemies by shooting arrows (mouse press).', 150, 300, 
              fill='moccasin', size=15, align='left', bold=True)

def tutorial_onMousePress(app, mx, my):
    if 80 <= mx <= 130 and 350 <= my <= 400:
        setActiveScreen('titleScreen')
#--------------
def gameOver_redrawAll(app):
    drawImage(CMUImage(app.gameOverImage), 0, 0)
    drawRect(app.width/2 - 100, app.height/2 + 40, 200, 50, fill='darkred')
    drawRect(app.width/2 - 100, app.height/2 + 110, 200, 50, fill='darkred')
    drawLabel('TRY AGAIN', app.width/2, app.height/2 + 65, fill='mistyRose', size=20, bold=True)
    drawLabel('QUIT', app.width/2, app.height/2 + 135, fill='mistyRose', size=20, bold=True)

def gameOver_onMousePress(app, mx, my):
    if app.width/2-100 <= mx <= app.width/2+ 100:
        if app.height/2 + 40 <= my <= app.height/2 + 90:
            app.gameOver = False
            app.boss.health = 100
            app.mc.health = app.mc.oxygen = 100
            app.enemies = []
            setActiveScreen('phaseSelection')
        if app.height/2 + 110 <= my <= app.height/2 + 160:
            setActiveScreen('titleScreen')
#--------------
def win_redrawAll(app):
    drawRect(0, 0, 640, 480)
    if app.phase == 1:
        drawImage(CMUImage(app.phaseOneWin), 0, 0)
    if app.phase == 2:
        drawImage(CMUImage(app.phaseTwoWin), 0, 0)
    if app.phase == 3:
        drawImage(CMUImage(app.phaseThreeWin), 0, 0)

    drawLabel('NEXT PHASE', app.width/2, app.height/2 + 100, fill=rgb(176, 120, 30), size=25)
    if app.phase == 4:
        drawImage(CMUImage(app.victoryImage), 0, 0)
        drawRect(app.width/2 - 100, app.height/2 + 50, 200, 50, fill=rgb(176, 120, 30))
        drawLabel('RETURN HOME', app.width/2, app.height/2 +75, fill='darkblue', size=20, bold=True)
def win_onMousePress(app, mx, my):
    if app.width/2 - 40 <= mx <= app.width/2 + 40 and app.height/2 - 40 <= my <= app.height/2 + 40 and app.phase != 4:
        app.phase += 1
        app.win = False
        app.mc.health = app.mc.oxygen = 100
        setActiveScreen('phaseSelection')
    if app.width/2 - 100 <= mx <= app.width/2 + 100 and app.height/2+50 <= my <= app.height/2 + 100 and app.phase == 4:
        setActiveScreen('titleScreen')
#--------------
def phaseSelection_redrawAll(app):
    color1 = color2 = color3 = color4 = None
    if app.phase == 1:
        color1 = rgb(176, 120, 30)
        color2 = color3 = color4 = 'burlyWood'
    elif app.phase == 2:
        color2 = rgb(176, 120, 30)
        color1 = color3 = color4 = 'burlyWood'
    elif app.phase == 3:
        color3 = rgb(176, 120, 30)
        color1 = color2 = color4 = 'burlyWood'
    elif app.phase == 4:
        color4 = rgb(176, 120, 30)
        color1 = color2 = color3 = 'burlyWood'
    drawRect(0, 0, 640, 480)
    drawLabel('PHASE SELECTION', app.width/2, 50, fill=color1, size=30)
    drawRect(app.width/5 - 45, 100, 90, app.height-200, fill=color1)
    drawRect(app.width/5*2 - 45, 100, 90, app.height-200, fill=color2)
    drawRect(app.width/5*3 - 45, 100, 90, app.height-200, fill=color3)
    drawRect(app.width/5*4 - 45, 100, 90, app.height-200, fill=color4)
    drawLabel('I', app.width/5, 125, fill='moccasin', size=30, bold=True)
    drawLabel('II', app.width/5*2, 125, fill='moccasin', size=30, bold=True)
    drawLabel('III', app.width/5*3, 125, fill='moccasin', size=30, bold=True)
    drawLabel('IV', app.width/5*4, 125, fill='moccasin', size=30, bold=True)

def phaseSelection_onMousePress(app, mx, my):
    if 100 <= my <= app.height-100:
        if app.width/5 - 45 <= mx <= app.width/5 + 45 and app.phase == 1:
            app.moonMC.scene = 'candle'
            app.candleWarning = False
            app.candleCounter = 50
            app.moonMC.cx = 50
            app.enemyNumber = 3
            for i in range(app.enemyNumber):
                initializeNewEnemy(app)
            app.obstacles = []
            for i in range(app.numObstacles):
                newObstacle = generateObstacle(app)
                app.obstacles.append(newObstacle)
            setActiveScreen('candle')
        elif app.width/5*2 - 45 <= mx <= app.width/5*2 + 45 and app.phase == 2:
            app.moonMC.scene = 'candle'
            app.candleWarning = False
            app.candleCounter = 50
            app.moonMC.cx = 50
            app.enemyNumber = 4
            app.numObstacles = 5
            for i in range(app.enemyNumber):
                initializeNewEnemy(app)
            app.obstacles = []
            for i in range(app.numObstacles):
                newObstacle = generateObstacle(app)
                app.obstacles.append(newObstacle)
            setActiveScreen('candle')
        elif app.width/5*3 - 45 <= mx <= app.width/5*3 + 45 and app.phase == 3:
            app.moonMC.scene = 'candle'
            app.candleWarning = False
            app.candleCounter = 50
            app.moonMC.cx = 50
            chance = random.randint(0, 2)
            if chance == 1 or chance == 2:
                app.stage = 'red'
                app.enemyStrength = 15
            app.enemyNumber = 5
            app.numObstacles = 7
            for i in range(app.enemyNumber):
                initializeNewEnemy(app)
            app.obstacles = []
            for i in range(app.numObstacles):
                newObstacle = generateObstacle(app)
                app.obstacles.append(newObstacle)
            setActiveScreen('candle')
        elif app.width/5*4 - 45 <= mx <= app.width/5*4 + 45 and app.phase == 4:
            app.moonMC.scene = 'candle'
            app.candleWarning = False
            app.candleCounter = 50
            app.moonMC.cx = 50
            app.stage = 'combat'
            app.enemyStrength = 10
            app.enemyNumber = 4
            app.numObstacles = 7
            app.isBoss = True
            for i in range(app.enemyNumber):
                initializeNewEnemy(app)
            app.obstacles = []
            for i in range(app.numObstacles):
                newObstacle = generateObstacle(app)
                app.obstacles.append(newObstacle)
            setActiveScreen('candle')
#------------
def phaseOne_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('FIRST QUARTER', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill='white')
    drawArc(app.width/2, app.height/2, 190, 190, 90, 180, fill='black')
    drawRect(app.width/2-50, app.height-100, 100, 50, fill='white')
    drawLabel('BEGIN', app.width/2, app.height - 75, 
              fill=rgb(176, 120, 30), size=20)

def phaseOne_onMousePress(app, mx, my):
    if app.width/2-50 <= mx <= app.width/2+50 and \
    app.height-100 <= my <= app.height-50:
        app.phase = 1
        setActiveScreen('combat')
#------------
def phaseTwo_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('FULL MOON', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill='white')
    drawRect(app.width/2-50, app.height-100, 100, 50, fill='white')
    drawLabel('BEGIN', app.width/2, app.height - 75, fill=rgb(176, 120, 30), size=20)

def phaseTwo_onMousePress(app, mx, my):
    if app.width/2-50 <= mx <= app.width/2+50 and app.height-100 <= my <= app.height-50:
        app.phase = 2
        setActiveScreen('combat')
#------------
def phaseThree_redrawAll(app):
    drawRect(0, 0, 640, 480)
    if app.stage == 'red':
        color = 'red'
        label = 'RANDOM EVENT: BLOOD MOON'
    else:
        color = 'white'
        label = 'LAST QUARTER'
    drawLabel(label, app.width/2, 75, fill=color, bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill=None, border=color, borderWidth=5)
    drawArc(app.width/2, app.height/2, 200, 200, 90, 180, fill=color)
    drawRect(app.width/2-50, app.height-100, 100, 50, fill='white')
    drawLabel('BEGIN', app.width/2, app.height - 75, fill=rgb(176, 120, 30), size=20)

def phaseThree_onMousePress(app, mx, my):
    if app.width/2-50 <= mx <= app.width/2+50 and app.height-100 <= my <= app.height-50:
        app.phase = 3
        setActiveScreen('combat')
#------------
def phaseFour_redrawAll(app):
    drawRect(0, 0, 640, 480)
    drawLabel('NEW MOON', app.width/2, 75, fill='white', bold=True, size=30)
    drawCircle(app.width/2, app.height/2, 100, fill=None, border='white')
    drawRect(app.width/2-50, app.height-100, 100, 50, fill='white')
    drawLabel('BEGIN', app.width/2, app.height - 75, fill=rgb(176, 120, 30), size=20)

def phaseFour_onMousePress(app, mx, my):
    if app.width/2-50 <= mx <= app.width/2+50 and \
    app.height-100 <= my <= app.height-50:
        app.phase = 4
        setActiveScreen('combat')
#---------
def candle_onStep(app):
    if app.moonMC.scene == 'combat':
        app.candleWarning = True
        app.candleCounter -= 0.5
    if app.candleCounter <= 0:
        if app.phase == 1: phase = 'phaseOne'
        if app.phase == 2: phase = 'phaseTwo'
        if app.phase == 3: phase = 'phaseThree'
        if app.phase == 4: phase = 'phaseFour'
        setActiveScreen(phase)
def candle_redrawAll(app):
    if app.moonMC.scene == 'candle':
        drawImage(CMUImage(app.moonImage), 0, 0)
    else:
        drawImage(CMUImage(app.moonCandleImage), 0, 0)
    if 325 <= app.moonMC.cx <= 430 and app.moonMC.scene == 'candle':
        drawLabel('press F to place the candle.', app.width/2, 200, fill='white')
    app.moonMC.draw(app)
    if app.candleWarning and app.candleCounter >= 0:
        drawLabel('!! ALERT: ENEMIES APPROACHING !!', app.width/2, 200, fill='darkred', size=30, bold=True)
def candle_onKeyHold(app, keys):
    if 'right' in keys or 'd' in keys:
        app.moonMC.move(app.characterSpeed, 0)
        if not canMove(app, app.moonMC.hitbox):
            app.moonMC.move(-1 * app.characterSpeed, 0)
    if 'left' in keys or 'a' in keys:
        app.moonMC.move(-1 * app.characterSpeed, 0)
        if not canMove(app, app.moonMC.hitbox):
            app.moonMC.move(app.characterSpeed, 0)

def candle_onKeyPress(app, key):
    if 325 <= app.moonMC.cx <= 430 and key =='f':
        app.moonMC.scene = 'combat'
        


def main():
    runAppWithScreens(width=640, height=480, initialScreen='titleScreen')

main()

'''
notes:
lighting the candle!!
fix the change scenes things
'''
