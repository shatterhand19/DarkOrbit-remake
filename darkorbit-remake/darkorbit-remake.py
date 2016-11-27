import pygame, sys, random, time, math
from pygame.locals import *

#init global variables
pygame.init()
displaysurf = pygame.display.set_mode((1000, 700), RESIZABLE, 32)
mapx = 6000
mapy = 4000
pygame.display.set_caption("The Abis")
FPS = 50
fpsClock = pygame.time.Clock()

#init global functions
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def loadImg(name):
    img = pygame.image.load(name)
    return img

#global pictures

alien_small = loadImg("alien_small.png")
alien_small = pygame.transform.scale(alien_small, (85, 85))

alien_small_targeted = loadImg("alien_small_targeted.png")
alien_small_targeted = pygame.transform.scale(alien_small_targeted, (85, 85))


#colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)


#ship
class Ship:
    def __init__(self):
        self.Xpos = displaysurf.get_width()/2 - 150  #get the center of the screen
        self.Ypos = displaysurf.get_height()/2 - 150
        self.Xmap = 3000
        self.Ymap = 2000
        self.Xvel = 0  #velocity
        self.Yvel = 0
        self.times = 0  #iteration until the movement of the ship stops
        self.image = loadImg("player_ship.png")
        self.image = pygame.transform.scale(self.image, (300, 300))  #loads and transforms the ship base image
        self.rot_image = self.image  #image used to draw on surface
        self.rotationAngle = 0
        self.health = 1500
        self.pxHealthRatio = 10  #how much health is one pixel

        self.targetedAlien = 0

        self.lastLaserShot = 0

        self.laserShots = []
        self.shooting = False
        self.shootingInterval = 1000 #in ms

        self.points = 0
    
    def draw(self, displaysurf):
        
       
        displaysurf.blit(self.rot_image, (self.Xpos, self.Ypos))  #blits the rotated image in the center of the screen
        
        pygame.draw.rect(displaysurf, green, (self.Xpos + 75, self.Ypos + 40, self.health / self.pxHealthRatio, 5))  #draws the health bar on top
    
    def rotateAngleFind(self, x, y): 
        angle = math.atan2((y - (self.Ypos + self.image.get_height()/2)),(x - (self.Xpos + self.image.get_width()/2)))
        angle = math.degrees(angle)  #finds the angle to the mouse in degrees
        self.rot_image = self.image  #new copy of the image for better quality
        self.rot_image = rot_center(self.rot_image, - angle)  #rotate image
        self.rotationAngle = angle #save the rotation angle
    
    def moveTo(self, Xnew, Ynew):
        distance = math.sqrt((self.Ypos + self.image.get_height()/2 - Ynew)**2 + (self.Xpos + self.image.get_width()/2 - Xnew)**2) #find distance to click
                
        self.times = int(distance / 7) #speed 7 px per iteration
        if self.times: #if there is an actual diatnce to travel
            self.Xvel = int((Xnew - self.image.get_width()/2 - self.Xpos)/self.times)
            self.Yvel = int((Ynew - self.image.get_height()/2 - self.Ypos)/self.times)
                
    def move(self):
        if self.times > 0 and (self.Xmap + self.Xvel < mapx) and (self.Xmap + self.Xvel > 0) and (self.Ymap + self.Yvel < mapy) and (self.Ymap + self.Yvel > 0):
            #if the click was inside the map
            self.times -= 1
            self.Xmap += self.Xvel
            self.Ymap += self.Yvel
    def targetAlien(self, alien):
        self.targetedAlien = alien

    def shoot(self):
        if self.targetedAlien != 0 and self.shooting != 0: #if there is targeted alien and the ship is shooting
            if pygame.time.get_ticks() - self.lastLaserShot > self.shootingInterval: #set shooting intervals 
                laser = Laser() #new laser
                laser.rotateLaserAndFindDitance(self)
                self.laserShots.append(laser) #append to the array of active lasers
                self.lastLaserShot = pygame.time.get_ticks() #restart timer
        

class Laser:
    def __init__(self):
        self.image = loadImg("laser.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rot_image = self.image
        #load images
        self.rotationAngle = 0

        self.Xpos = displaysurf.get_width()/2 - self.image.get_width()/2
        self.Ypos = displaysurf.get_height()/2  - self.image.get_height()/2 #set postion in the center of the ship

        self.distance = 0
        self.times = 0

        self.Xvel = 0
        self.Yvel = 0

        self.target = 0

    def rotateLaserAndFindDitance(self, ship):
        self.target = ship.targetedAlien #if there is a targeted alien
        if self.target:
            angle = math.atan2((self.Ypos + self.image.get_height()/2 - self.target.Ypos - self.target.image.get_height()/2),(self.Xpos + self.image.get_width()/2 - self.target.Xpos - self.target.image.get_width()/2))
            angle = math.degrees(angle)
            #find angle to the alien
            self.rot_image = self.image
            self.rot_image = rot_center(self.rot_image,  -angle)
            self.rotationAngle = angle
            #rotate towards the targeted alien
            
            self.distance = math.sqrt((self.Xpos + self.image.get_width()/2 - self.target.Xpos - self.target.image.get_width()/2)**2+(self.Ypos + self.image.get_height()/2 - self.target.Ypos - self.target.image.get_height()/2)**2)
            self.times = int(self.distance/25)
            #find distance and set speed
            
            if self.times:
                self.Xvel = int((self.Xpos + self.image.get_width()/2 - self.target.Xpos - self.target.image.get_width()/2)/ self.times)
                self.Yvel = int((self.Ypos + self.image.get_height()/2 - self.target.Ypos - self.target.image.get_height()/2)/self.times)
                #determine velocity, it should be negative
        
    def moveAndDraw(self, ship, displaysurf):
        if self.times:
            self.Xpos -= self.Xvel
            self.Ypos -= self.Yvel
            self.times -= 1
            #move until there is some distance to the alien
        if self.times == 0 and ship.targetedAlien != 0:
            ship.laserShots.remove(self) #destroy laser
            ship.targetedAlien.dropHealth(100) #drop helth of targeted alien
        displaysurf.blit(self.rot_image, (self.Xpos, self.Ypos))  #blits the rotated image in the center of the screen
   
class Alien:
    def __init__(self):
        self.Xmap = random.randrange(100, mapx - 100)  
        self.Ymap = random.randrange(100, mapy - 100) #position at random coordinates
        self.Xpos = 0
        self.Ypos = 0
        self.distanceToShip = 0
        
        self.targeted = False
        self.inRange = False
        
        self.rotationAngle = 0
        
        self.Xvel = 0
        self.Yvel = 0
        self.times = 0 

        self.health = 0
        self.pxHealthRatio = 0

    def draw(self, ship, displaysurf):
        if self.distanceToShip < 800: #set visibility on minimap
            self.inRange = True
        else:
            self.inRange = False
        self.Xpos = (self.Xmap - (ship.Xmap - displaysurf.get_width()/2)) #set positions on the screen
        self.Ypos = (self.Ymap - (ship.Ymap - displaysurf.get_height()/2))
        self.distanceToShip = math.sqrt((self.Xpos + self.image.get_width()/2 - ship.Xpos - 150)**2 + (self.Ypos + self.image.get_height() - ship.Ypos - 150)**2)
        displaysurf.blit(self.rot_image, (self.Xpos, self.Ypos))
        #calculate new distance to ship and blit
        pygame.draw.rect(displaysurf, green, (self.Xpos + 10, self.Ypos + 5, self.health / self.pxHealthRatio, 5))
        

    def rotateToShip(self, ship):
        if self.distanceToShip < 500: #if distance <= 500
            angle = math.atan2((ship.Ypos + ship.image.get_height()/2 - (self.Ypos + self.image.get_height()/2)),(ship.Xpos + ship.image.get_width()/2 - (self.Xpos + self.image.get_width()/2)))
            angle = math.degrees(angle)
            if self.targeted == True:
                self.image = self.targetImg #if targeted rotate the target image
            else:
                self.image = self.alienImg #else the normal one
            self.rot_image = self.image  #copy the image for rotation
            self.rot_image = rot_center(self.rot_image, - angle)
            self.rotationAngle = angle;
        else:
            if self.targeted == True: #if distance > 500
                self.rot_image = self.targetImg
            else:
                self.rot_image = self.alienImg
            self.rot_image = rot_center(self.rot_image, - self.rotationAngle) #leave the alien rotated in the last direction

    def moveToShip(self, ship):
        if self.distanceToShip < 500 and self.distanceToShip > 200: 
            self.times = int(self.distanceToShip / 3) #3px per iteration 
            if self.times:
                self.Xvel = int((ship.Xpos + ship.image.get_width()/2 - self.Xpos - self.image.get_width()/2)/self.times)
                self.Yvel = int((ship.Ypos + ship.image.get_height()/2 - self.Ypos - self.image.get_height()/2)/self.times) 
            self.times = 1 #set times to be greater than 0
        if self.times > 0: #if the first if is ok
            self.times -= 1
            self.Xmap += self.Xvel
            self.Ymap += self.Yvel

    def dropHealth(self, dmg):
        self.health -= dmg

class smallAlien(Alien):
    def __init__ (self):
        Alien.__init__(self)
        self.image = alien_small
        
        self.alienImg = alien_small
        
        self.targetImg = alien_small_targeted
        
        #load images
        self.rot_image = self.image

        self.health = 600
        self.pxHealthRatio = 10

class Minimap():
    def __init__(self, ship, displaysurf):
        self.Xpos = displaysurf.get_width() - 310
        self.Ypos = displaysurf.get_height() - 210
        self.Xship = 0
        self.Yship = 0
        self.map = pygame.Surface([310, 210], 32) #create a surface to blit
    
    def shipCoord(self, ship):
        self.Xship = int(ship.Xmap / 20) + 5 #get the mapped coordinates of the ship on the minimap
        self.Yship = int(ship.Ymap / 20) + 5
        
    
    def draw(self, ship, aliens, displaysurf):
        self.shipCoord(ship)
        
        pygame.draw.rect(self.map, white, (0, 0, 310, 210)) #background

        pygame.draw.rect(self.map, black, (5, 5, 300, 200)) #map

        pygame.draw.line(self.map, red, (self.Xship, 5), (self.Xship, 205)) #lines for the ship

        pygame.draw.line(self.map, red, (5, self.Yship), (305, self.Yship))

        pygame.draw.circle(self.map, blue, (self.Xship, self.Yship), 2, 0) #ship dot

        for a in aliens:
            if a.inRange == True:
                pygame.draw.circle(self.map, red, (int(a.Xmap/20) + 5, int(a.Ymap/20) + 5), 2, 0)
        #if in range draw a red dot for aliens

        displaysurf.blit(self.map, (self.Xpos, self.Ypos))

    def onClick(self, X, Y):
        if X > self.Xpos and Y > self.Ypos:
            return True


    
      

def eventsHandler(ship, minimap, displaysurf):
    pressed = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type==VIDEORESIZE: #if resized update the globals
            screen=pygame.display.set_mode(event.dict['size'], RESIZABLE, 32)
            ship.Xpos = displaysurf.get_width()/2 - 150  #get the center of the screen
            ship.Ypos = displaysurf.get_height()/2 - 150
            minimap.Xpos = displaysurf.get_width() - 310
            minimap.Ypos = displaysurf.get_height() - 210
        if pygame.mouse.get_pressed()[0]:
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]
            ship.rotateAngleFind(x, y)
            moveToIt = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if minimap.onClick(x, y) == True:
                    moveToIt = False
                else:
                    for a in aliens:
                        if x > a.Xpos and x < a.Xpos + a.image.get_width() and y > a.Ypos and y < a.Ypos + a.image.get_height():
                            moveToIt = False
                            for b in aliens:
                                b.targeted = False
                            a.targeted = True
                            ship.targetAlien(a)
                            ship.shooting = False
                
            if (x < ship.Xpos and ship.Xmap - x < 0) or (x > ship.Xpos and ship.Xmap + x > mapx) or (y < ship.Ypos and ship.Ymap - y < 0) or (y > ship.Ypos and ship.Ymap + y > mapy):
                moveToIt = False

            if moveToIt == True:
                ship.moveTo(x, y)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                if ship.targetedAlien:
                    if ship.shooting:
                        ship.shooting = False
                    else:
                        ship.lastLaserShot = pygame.time.get_ticks()
                        ship.shooting = True
        



ship = Ship()

aliens = []

minimap = Minimap(ship, displaysurf)

for i in range(20):
    aliens.append(smallAlien())
    i += 1

while True:
    displaysurf.fill(black)
    #background.draw(ship, displaysurf)
    eventsHandler(ship, minimap, displaysurf)

    for l in ship.laserShots:
        l.rotateLaserAndFindDitance(ship)
        l.moveAndDraw(ship, displaysurf)

        

    for a in aliens:
        if a.health == 0:
            aliens.remove(a) #delete alien
            ship.points += 1
            ship.targetedAlien = 0 #no target
            ship.shooting = False #stop shooting after kill
        a.draw(ship, displaysurf)
        a.rotateToShip(ship)
        a.moveToShip(ship)
        

    ship.draw(displaysurf)
    ship.move()
    ship.shoot()

    

    minimap.draw(ship, aliens, displaysurf)

    pygame.display.flip()
    fpsClock.tick(FPS)
