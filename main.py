# Import necessary modules
import pygame
import random
import math
import copy



# Initialize program elements
pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("The Physics of Star Wars")
done = False
clock = pygame.time.Clock()

# Define color codes
white = (255, 255, 255)
lightGray = (200, 200, 200)
gray = (125, 125, 125)
darkGray = (65, 65, 65)
black = (0, 0, 0)

space = (100, 125, 125)
sky = (200, 230, 230)

red = (175, 0, 0)
green = (0, 200, 0)
blue = (0, 0, 255)
yellow = (200, 200, 0)

# Define font codes
titleFont = pygame.font.SysFont('franklingothicmedium', 30)
font = pygame.font.SysFont('franklingothicmedium', 20)
smallFont = pygame.font.SysFont('franklingothicbook', 15)
vectorFont = pygame.font.SysFont('franklingothicbook', 13)
tinyFont = pygame.font.SysFont('franklingothicbook', 10)

# Define visuals
shipTop = pygame.image.load('textures/ship/top/shipTop.png')
shipTopL = pygame.image.load('textures/ship/top/left.png')
shipTopR = pygame.image.load('textures/ship/top/right.png')
shipTopMain = pygame.image.load('textures/ship/top/main.png')

shipSide = pygame.image.load('textures/ship/side/shipSide.png')
shipSideU = pygame.image.load('textures/ship/side/up.png')
shipSideD = pygame.image.load('textures/ship/side/down.png')
shipSideMain = pygame.image.load('textures/ship/side/main.png')

shipRear = pygame.image.load('textures/ship/rear/shipRear.png')
shipRearMain = pygame.image.load('textures/ship/rear/shipRearMain.png')

pauseButton = pygame.image.load('textures/buttons/pauseButton.png')
playButton = pygame.image.load('textures/buttons/playButton.png')
stopButton = pygame.image.load('textures/buttons/stopButton.png')



# -------Input Variables-------
keyW = False
keyS = False
keyA = False
keyD = False
keyRight = False
keyLeft = False
keySpace = False

mouseSelected = 0
selectedButton = 0
draftInput = ""



# -------Setting Variables-------
showComponentVectors = False
showResultantVector = False
showForceVectors = False
earth = False
paused = False
zoomFactor = 10.0 # In hundreds of meters per gridline
speedFactor = 1.0 # In 100%




# -------Ship Variables-------
gameState = "simulator" # Set the main menu at the beginning of the game

shipDimX = 40
shipDimY = 40
shipDimZ = 40

shipX = 0
shipY = 0
shipZ = 0

shipVelocityX = 0
shipVelocityY = 0
shipVelocityZ = 0
unitVector = (0,0,0)

shipYaw = 0
shipPitch = 0
shipRoll = 0

shipVelocityYaw = 0
shipVelocityPitch = 0
shipVelocityRoll = 0

shipMass = 10000
mainThrusterForce = 200000
maneuveringThrusterForce = 100000

gravitationalConstant = 6.67 * 10**-11
planetMass = 5.972 # Defaults for Earth
planetRadius = 6.371

dragCoefficient = 0.1
airDensity = 1.225

forceDrag = 0
forceLift = 0
forceGravity = 0

timeElapsed = 0



# -------Screen Variables-------
screen1Anchor = (75, 80) # Define anchor point of display for use in relative coordinates
screen1Dim = (500, 500)
screen1Center = (int(screen1Anchor[0]+screen1Dim[0]/2), int(screen1Anchor[1]+screen1Dim[1]/2))
screen2Anchor = (screen1Anchor[0]+screen1Dim[0]+70, screen1Anchor[1])
screen2Dim = (250, screen1Dim[1])
screen2Center = (int(screen2Anchor[0]+screen2Dim[0]/2), int(screen2Anchor[1]+screen2Dim[1]/2))
screen3Anchor = (screen2Anchor[0]+screen2Dim[0]+35, screen1Anchor[1])
screen3Dim = (300, 200)
screen3Center = (int(screen3Anchor[0]+screen3Dim[0]/2), int(screen3Anchor[1]+screen3Dim[1]/2))



# -------Button Class-------
class Button:
    def __init__(self, buttonID, buttonType, buttonX, buttonY, buttonHitboxX, buttonHitboxY, buttonLabel, buttonEarth):
        self.id = buttonID
        self.type = buttonType
        self.x = buttonX
        self.y = buttonY
        self.hitboxX = buttonHitboxX
        self.hitboxY = buttonHitboxY
        self.label = buttonLabel
        self.earth = buttonEarth
        self.selected = False
        
    def draw(self):
        if self.type == "button":
            currentTextLength = textLength(self.label, "small")
            screen.blit(smallFont.render(self.label, 1, black), (self.x+self.hitboxX/2-currentTextLength/2, self.y+self.hitboxY))
            if self.id == "pause":
                if not paused:
                    screen.blit(pygame.transform.scale(pauseButton, (self.hitboxX, self.hitboxY)), (self.x, self.y))
                if paused:
                    screen.blit(pygame.transform.scale(playButton, (self.hitboxX, self.hitboxY)), (self.x, self.y))
            if self.id == "stop":
                screen.blit(pygame.transform.scale(stopButton, (self.hitboxX, self.hitboxY)), (self.x, self.y))
            
        if self.type == "checkbox":
            pygame.draw.rect(screen, black, (self.x, self.y, self.hitboxX, self.hitboxY), 3)
            screen.blit(smallFont.render(self.label, 1, black), (self.x+self.hitboxX+5, self.y))
            if (self.id == "showComponentVectors" and showComponentVectors) or (self.id == "showResultantVector" and showResultantVector) or (self.id == "showForceVectors" and showForceVectors) or (self.id == "earth" and earth):
                pygame.draw.rect(screen, black, (self.x+5, self.y+5, self.hitboxX-10, self.hitboxY-10), 0) # Fill in box if enabled

        if self.type == "slider":
            pygame.draw.rect(screen, black, (self.x, self.y, self.hitboxX, self.hitboxY), 0)
            pygame.draw.rect(screen, black, (screen3Anchor[0], self.y, self.hitboxX*20, self.hitboxY), 3) # Draw a slider maximum anchored to screen 3, but length and y-properties based on the sliding knob
            if self.id == "zoomSlider":
                screen.blit(smallFont.render("Scale: "+str(int(zoomFactor*100))+" m/line", 1, black), (screen3Anchor[0]+self.hitboxX*20+10, self.y - 4))
            if self.id == "speedSlider":
                screen.blit(smallFont.render("Sim Speed: "+str(speedFactor), 1, black), (screen3Anchor[0]+self.hitboxX*20+10, self.y - 4))

        if self.type == "input" and ((not self.earth) or (self.earth and earth)):
            if not self.selected:
                pygame.draw.rect(screen, black, (self.x, self.y, self.hitboxX, self.hitboxY), 3)
                currentText = str(eval(self.id))
            if self.selected:
                pygame.draw.rect(screen, yellow, (self.x, self.y, self.hitboxX, self.hitboxY), 3)
                global draftInput
                if draftInput == "":
                    currentText = str(eval(self.id))
                else:
                    currentText = str(draftInput)
            currentTextLength = textLength(currentText, "small")
            screen.blit(smallFont.render(currentText, 1, gray), (self.x+self.hitboxX-currentTextLength - 10, self.y+1))
            screen.blit(smallFont.render(self.label, 1, black), (self.x+self.hitboxX+10, self.y+1))
            
    def pressed(self):
        global paused
        
        if self.id == "pause":
            if paused:
                paused = False
            else:
                paused = True
                
        if self.id == "stop":
            global shipX
            global shipY
            global shipZ
            global shipVelocityX
            global shipVelocityY
            global shipVelocityZ
            global shipYaw
            global shipPitch
            global shipRoll
            global shipVelocityYaw
            global shipVelocityPitch
            global shipVelocityRoll
            global timeElapsed
            shipX = 0
            shipY = 0
            shipZ = 0
            shipVelocityX = 0
            shipVelocityY = 0
            shipVelocityZ = 0
            shipYaw = 0
            shipPitch = 0
            shipRoll = 0
            shipVelocityYaw = 0
            shipVelocityPitch = 0
            shipVelocityRoll = 0
            timeElapsed = 0
            if not paused:
                paused = True
                
        if self.id == "showComponentVectors":
            global showComponentVectors
            if showComponentVectors:
                showComponentVectors = False
            else:
                showComponentVectors = True

        if self.id == "showResultantVector":
            global showResultantVector
            if showResultantVector:
                showResultantVector = False
            else:
                showResultantVector = True
        
        if self.id == "showForceVectors":
            global showForceVectors
            if showForceVectors:
                showForceVectors = False
            else:
                showForceVectors = True

        if self.id == "earth":
            global earth
            if earth:
                earth = False
            else:
                earth = True

        global mouseSelected
        if self.type == "slider":
            mouseSelected = self.id

        global selectedButton
        if self.type == "input" and ((not self.earth) or (self.earth and earth)):
            self.selected = True
            selectedButton = self

    def released(self):
        global mouseSelected
        mouseSelected = 0

    def setInput(self, newInput):
        if self.id == "shipMass":
            global shipMass
            shipMass = int(newInput)

        if self.id == "mainThrusterForce":
            global mainThrusterForce
            mainThrusterForce = int(newInput)
        
        if self.id == "maneuveringThrusterForce":
            global maneuveringThrusterForce
            maneuveringThrusterForce = int(newInput)
        
        if self.id == "planetMass":
            global planetMass
            planetMass = float(newInput)
        
        if self.id == "planetRadius":
            global planetRadius
            planetRadius = float(newInput)
        
        if self.id == "airDensity":
            global airDensity
            airDensity = float(newInput)
        
        
        
simulatorButtonList = [Button("pause", "button", screen2Anchor[0]+screen2Dim[0]-40, screen2Anchor[1]+screen2Dim[1]+20, 40, 40, "Pause", False),
                       Button("stop", "button", screen2Anchor[0]+screen2Dim[0]-40-10-40, screen2Anchor[1]+screen2Dim[1]+20, 40, 40, "Stop", False),
                       Button("showComponentVectors", "checkbox", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+60, 20, 20, "Show Component Vectors (Velocity)", False),
                       Button("showResultantVector", "checkbox", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+85, 20, 20, "Show Resultant Vector (Velocity)", False),
                       Button("showForceVectors", "checkbox", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+110, 20, 20, "Show Vectors (Forces)", False),
                       Button("earth", "checkbox", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+135, 20, 20, "Simulate Earth flight", False),
                       Button("zoomSlider", "slider", screen3Anchor[0]+10*9, screen3Anchor[1]+screen3Dim[1]+170, 10, 10, "", False), # Should actually be anchored at screen3Anchor[0]
                       Button("speedSlider", "slider", screen3Anchor[0]+10*8, screen3Anchor[1]+screen3Dim[1]+195, 10, 10, "", False), # Should actually be anchored at screen3Anchor[0]

                       Button("shipMass", "input", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+255, 80, 20, "Ship Mass (kg)", False),
                       Button("mainThrusterForce", "input", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+280, 80, 20, "Main Thruster Force (N)", False),
                       Button("maneuveringThrusterForce", "input", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+305, 80, 20, "Maneuvering Thruster Force (N)", False),
                       Button("planetMass", "input", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+330, 80, 20, "Planet Mass (10^24 kg)", True),
                       Button("planetRadius", "input", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+355, 80, 20, "Planet Radius (10^6 m)", True),
                       Button("airDensity", "input", screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+380, 80, 20, "Air Density (kg/m^3)", True)
                      ]

zoomSlider = simulatorButtonList[6]
speedSlider = simulatorButtonList[7]



# -------General Functions-------
def textLength(text, fontSize): # Calculate the approximate horizontal length of a text label to determine how far away to put its anchor point
    if fontSize == "small":
        return len(str(text))*8
    if fontSize == "vector":
        return len(str(text))*7
    if fontSize == "tiny":
        return len(str(text))*5

def cancelInput(): # Cancels the state of changing parameter variables
    global selectedButton
    selectedButton.selected = False
    selectedButton = 0
    global draftInput
    draftInput = ""

def blitRotateCenter(image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    screen.blit(rotated_image, new_rect)

def arrow(color, start, end, text):
    rad = math.pi/180
    pygame.draw.line(screen, color, start, end, 3)
    rotation = (math.atan2(start[1] - end[1], end[0] - start[0])) + math.pi/2
    pygame.draw.polygon(screen, color, ((end[0] + 5 * math.sin(rotation),
                                        end[1] + 5 * math.cos(rotation)),
                                       (end[0] + 5 * math.sin(rotation - 120*rad),
                                        end[1] + 5 * math.cos(rotation - 120*rad)),
                                       (end[0] + 5 * math.sin(rotation + 120*rad),
                                        end[1] + 5 * math.cos(rotation + 120*rad))))
    currentTextLength = textLength(text, "vector")
    if end[0]-start[0] < 0:
        textAnchorX = end[0]-currentTextLength+10
    else:
        textAnchorX = end[0]+10
    if end[1]-start[1] < 0 and abs(end[0]-start[0]) > 20:
        textAnchorY = end[1]-20
    else:
        textAnchorY = end[1]-10
    screen.blit(vectorFont.render(text, 1, color), (textAnchorX, textAnchorY))



# -------Main Program-------
while not done:
    
    # -------Controls-------
    mouseX,mouseY = pygame.mouse.get_pos() # Constantly retrieve mouse position
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Thanks for playing!")
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: # 
                keyW = True
            if event.key == pygame.K_s: # 
                keyS = True
            if event.key == pygame.K_a: # 
                keyA = True
            if event.key == pygame.K_d: # 
                keyD = True
            if event.key == pygame.K_RIGHT: # 
                keyRight = True
            if event.key == pygame.K_LEFT: # 
                keyLeft = True
            if event.key == pygame.K_SPACE: # Activate primary thruster
                keySpace = True
            if event.key == pygame.K_RETURN:
                if selectedButton != 0:
                    selectedButton.setInput(float(draftInput))
                cancelInput()
            if event.key == pygame.K_ESCAPE:
                cancelInput()
            if event.key == pygame.K_1:
                draftInput = draftInput+"1"
            if event.key == pygame.K_2:
                draftInput = draftInput+"2"
            if event.key == pygame.K_3:
                draftInput = draftInput+"3"
            if event.key == pygame.K_4:
                draftInput = draftInput+"4"
            if event.key == pygame.K_5:
                draftInput = draftInput+"5"
            if event.key == pygame.K_6:
                draftInput = draftInput+"6"
            if event.key == pygame.K_7:
                draftInput = draftInput+"7"
            if event.key == pygame.K_8:
                draftInput = draftInput+"8"
            if event.key == pygame.K_9:
                draftInput = draftInput+"9"
            if event.key == pygame.K_0:
                draftInput = draftInput+"0"
            if event.key == pygame.K_PERIOD:
                draftInput = draftInput+"."

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                keyW = False
            if event.key == pygame.K_s:
                keyS = False
            if event.key == pygame.K_a:
                keyA = False
            if event.key == pygame.K_d:
                keyD = False
            if event.key == pygame.K_RIGHT:
                keyRight = False
            if event.key == pygame.K_LEFT:
                keyLeft = False
            if event.key == pygame.K_SPACE:
                keySpace = False

        if event.type == pygame.MOUSEBUTTONDOWN: # Player clicks mouse; check for mouse position against all buttons
            if gameState == "simulator":
                if selectedButton != 0: # Cancel input if player clicks out of button hitbox
                    if mouseX not in range(selectedButton.x, selectedButton.x + selectedButton.hitboxX) or mouseY not in range(selectedButton.y, selectedButton.y + selectedButton.hitboxY):
                        cancelInput()
                for c in range(len(simulatorButtonList)):
                    currentButton = simulatorButtonList[c]
                    if mouseX in range(currentButton.x, currentButton.x + currentButton.hitboxX) and mouseY in range(currentButton.y, currentButton.y + currentButton.hitboxY):
                        currentButton.pressed()

        if event.type == pygame.MOUSEBUTTONUP: # Player releases mouse; check for mouse position against all buttons
            if gameState == "simulator":
                for c in range(len(simulatorButtonList)):
                    currentButton = simulatorButtonList[c]
                    if mouseSelected == currentButton.id:
                        currentButton.released()

    # -------Settings Input Actions-------
    if mouseSelected == "zoomSlider": # Active for as long as mouse has been pressed on the corresponding slider, and hasn't been released yet
        zoomSlider.x = mouseX
        if zoomSlider.x < screen3Anchor[0]: # Cannot exceed minimum and maximum endpoints of slider
            zoomSlider.x = screen3Anchor[0]
        if zoomSlider.x > screen3Anchor[0]+zoomSlider.hitboxX*20-zoomSlider.hitboxX: # Cannot exceed minimum and maximum endpoints of slider
            zoomSlider.x = screen3Anchor[0]+zoomSlider.hitboxX*20-zoomSlider.hitboxX
        zoomFactor = round((zoomSlider.x - screen3Anchor[0])/(zoomSlider.hitboxX*19)*10 + 5, 1) # Place knob in middle of slider by default
        
    if mouseSelected == "speedSlider":
        speedSlider.x = mouseX
        if speedSlider.x < screen3Anchor[0]:
            speedSlider.x = screen3Anchor[0]
        if speedSlider.x > screen3Anchor[0]+speedSlider.hitboxX*20-speedSlider.hitboxX:
            speedSlider.x = screen3Anchor[0]+speedSlider.hitboxX*20-speedSlider.hitboxX
        speedFactor = round((speedSlider.x - screen3Anchor[0])/(speedSlider.hitboxX*20)*2 + 0.1, 1)

    if not paused: # The following actions only occur if not paused
        # -------Controls Input Actions-------
        if keySpace:
            shipVelocityX -= (mainThrusterForce/shipMass)*(math.sin(math.radians(shipYaw)))*abs(math.cos(math.radians(shipPitch))) / (60/speedFactor)
            shipVelocityY += (mainThrusterForce/shipMass)*(math.cos(math.radians(shipYaw)))*abs(math.cos(math.radians(shipPitch))) / (60/speedFactor)
            shipVelocityZ += (mainThrusterForce/shipMass)*(math.sin(math.radians(shipPitch))) / (60/speedFactor)
        if keyA and not earth:
            shipVelocityYaw += ((maneuveringThrusterForce*15)/(shipMass*(shipDimY/2)**2)) / (60/speedFactor)
        if keyD and not earth:
            shipVelocityYaw += ((-maneuveringThrusterForce*15)/(shipMass*(shipDimY/2)**2)) / (60/speedFactor)
        if keyW and not earth:
            shipVelocityPitch += ((maneuveringThrusterForce*15)/(shipMass*(shipDimZ/2)**2)) / (60/speedFactor)
        if keyS and not earth:
            shipVelocityPitch += ((-maneuveringThrusterForce*15)/(shipMass*(shipDimZ/2)**2)) / (60/speedFactor)
        if earth:
            if keyLeft:
                shipRoll += 1.5 / (60/speedFactor)
            if keyRight:
                shipRoll -= 1.5 / (60/speedFactor)

        # -------Kinematics-------
        shipX += shipVelocityX / (60/speedFactor)
        shipY += (-shipVelocityY) / (60/speedFactor)
        shipZ += shipVelocityZ / (60/speedFactor)
        
        shipYaw = (shipYaw + (shipVelocityYaw / (60/speedFactor))) % 360
        shipPitch = (shipPitch + (shipVelocityPitch / (60/speedFactor))) % 360
        shipRoll = (shipRoll + (shipVelocityRoll / (60/speedFactor))) % 360

        # Calculate ship resultant velocity and unit vector of resultant velocity for use throughout code
        shipResultantVelocity = (shipVelocityX**2+shipVelocityY**2+shipVelocityZ**2)**0.5
        if shipResultantVelocity != 0:
            unitVector = (shipVelocityX/shipResultantVelocity, shipVelocityY/shipResultantVelocity, shipVelocityZ/shipResultantVelocity)

        # Gravity
        if earth:
            GPE = shipMass * 9.81 * shipZ
            forceGravity = gravitationalConstant * (planetMass*10**24) * shipMass / (planetRadius*10**6+shipZ)**2
            if shipZ > 0:
                shipVelocityZ -= (forceGravity/shipMass) / (60/speedFactor)

        # Drag
        if earth and shipResultantVelocity > 0:
            forceDrag = 0.5 * dragCoefficient * airDensity * shipResultantVelocity**2 * 22**2 # Assumes cross sectional dimensions of 22 meters squared, 1 meter per pixel
            # Deduct drag force from all velocity dimensions using unit vector
            shipVelocityX -= (forceDrag/shipMass)*unitVector[0] / (60/speedFactor)
            shipVelocityY -= (forceDrag/shipMass)*unitVector[1] / (60/speedFactor)
            shipVelocityZ -= (forceDrag/shipMass)*unitVector[2] / (60/speedFactor)

        # Lift
        if earth and shipResultantVelocity > 0:
            resultantAngle = -math.atan(shipVelocityX/shipVelocityY)
            angleDifference = math.radians(shipYaw) - resultantAngle
            forceLift = 0.5 * 0.55 * airDensity * ((shipVelocityX**2 + shipVelocityY**2)**0.5)**2 * 88*2 * math.cos(angleDifference)**2 # 0.55 comes from the attack angle-lift coefficient chart; assumes wing area of 88 m^2 per wing based on pixel
            shipVelocityZ += (forceLift/shipMass)*(math.cos(math.radians(shipRoll))) / (60/speedFactor)
            shipVelocityX += -(forceLift/shipMass)*(math.sin(math.radians(shipRoll))) / (60/speedFactor)

        # Normal force
        if earth:
            forceNormal = forceGravity - (forceLift)*(math.cos(math.radians(shipRoll)))

        if earth: # Contact with the ground
            if shipZ <= 0.1:
                shipZ = 0
                if shipVelocityZ <= 0:
                    shipVelocityZ = 0
            shipPitch = 0
            shipVelocityPitch = 0
            shipYaw = 0
            shipVelocityYaw = 0

        # -------Timer-------
        timeElapsed += 1/(60/speedFactor)

    # -------Drawing, Main Menu-------
    if gameState == "mainMenu":
        # Background
        screen.fill(white)

    # -------Drawing, Simulator-------
    if gameState == "simulator":
        # General
        screen.fill(white)
        screen.blit(titleFont.render("William's Spaceflight Simulator", 1, black), (screen1Anchor[0]-5, screen1Anchor[1]-75))

        # -------XY UI-------
        screen.blit(font.render("XY Position (\"Bird\'s Eye View\")", 1, black), (screen1Anchor[0], screen1Anchor[1]-40)) # Label
        pygame.draw.rect(screen, black, (screen1Anchor[0]-5, screen1Anchor[1]-5, screen1Dim[0]+10, screen1Dim[1]+10), 0) # Background and border
        if not earth:
            pygame.draw.rect(screen, space, (screen1Anchor[0], screen1Anchor[1], screen1Dim[0], screen1Dim[1]), 0)
        if earth:
            pygame.draw.rect(screen, sky, (screen1Anchor[0], screen1Anchor[1], screen1Dim[0], screen1Dim[1]), 0)
        
        # X-axis gridlines
        shipX /= 1 * zoomFactor # Set zoom factor and flip signs if needed
        nearestLine = round(shipX/100)*100 # Round ship's current x position to nearest multiple of 100 as the anchor line
        for i in range(-3,3 + 1): # Test for the next 2 grid lines on either side
            currentLine = nearestLine+(i*100)
            if currentLine in range(int(shipX-screen1Dim[0]/2),int(shipX+screen1Dim[0]/2) + 1): # If the tested grid line is within half the screen length of the ship's current position (i.e. it will fit on screen), draw the line
                pygame.draw.line(screen, lightGray, (int(screen1Center[0]+(currentLine-shipX)), screen1Anchor[1]+screen1Dim[1]), (int(screen1Center[0]+(currentLine-shipX)), screen1Anchor[1]), 2)
                currentText = str(round((currentLine/1000)*zoomFactor,1))+" km" # Set current text label; text displays an amount greater based on the zoomFactor
                currentTextLength = textLength(currentText, "tiny") # Find length of text to display to determine displacement from anchor point
                screen.blit(tinyFont.render(currentText, 1, gray), (int(screen1Center[0]+(currentLine-shipX)-currentTextLength/2), screen1Anchor[1]+screen1Dim[1]+5)) # Axis labels
        shipX *= 1 * zoomFactor

        # Y-axis gridlines
        shipY /= 1 * zoomFactor
        nearestLine = round(shipY/100)*100
        for i in range(-3,3 + 1):
            currentLine = nearestLine+(i*100)
            if currentLine in range(int(shipY-screen1Dim[1]/2),int(shipY+screen1Dim[1]/2) + 1):
                pygame.draw.line(screen, lightGray, (screen1Anchor[0], int(screen2Center[1]+(currentLine-shipY))), (screen1Anchor[0]+screen1Dim[0], int(screen2Center[1]+(currentLine-shipY))), 2)
                currentText = str(round((-currentLine/1000)*zoomFactor,1))+" km"
                currentTextLength = textLength(currentText, "tiny")
                screen.blit(tinyFont.render(currentText, 1, gray), (screen1Anchor[0]-currentTextLength - 10, int(screen2Center[1]+(currentLine-shipY) - 5)))
        shipY *= 1 * zoomFactor

        # Axis titles
        axisTitle1Anchor = (screen1Anchor[0]-20, screen1Anchor[1]+screen1Dim[1]+20)
        arrow(black, (axisTitle1Anchor[0], axisTitle1Anchor[1]), (axisTitle1Anchor[0]+20, axisTitle1Anchor[1]), "")
        arrow(black, (axisTitle1Anchor[0], axisTitle1Anchor[1]), (axisTitle1Anchor[0], axisTitle1Anchor[1]-20), "")
        screen.blit(tinyFont.render("X", 1, black), (axisTitle1Anchor[0]+30, axisTitle1Anchor[1]-6))
        screen.blit(tinyFont.render("Y", 1, black), (axisTitle1Anchor[0]-3, axisTitle1Anchor[1]-40))

        # Draw ship
        blitRotateCenter(shipTop, (screen1Anchor[0]+screen1Dim[0]/2-shipDimX/2, screen1Anchor[1]+screen1Dim[1]/2-shipDimY/2), shipYaw)
        if keySpace:
            blitRotateCenter(shipTopMain, (screen1Anchor[0]+screen1Dim[0]/2-shipDimX/2, screen1Anchor[1]+screen1Dim[1]/2-shipDimY/2), shipYaw)
        if keyA and not earth:
            blitRotateCenter(shipTopL, (screen1Anchor[0]+screen1Dim[0]/2-shipDimX/2, screen1Anchor[1]+screen1Dim[1]/2-shipDimY/2), shipYaw)
        if keyD and not earth:
            blitRotateCenter(shipTopR, (screen1Anchor[0]+screen1Dim[0]/2-shipDimX/2, screen1Anchor[1]+screen1Dim[1]/2-shipDimY/2), shipYaw)

        zoomFactor /= 3
        
        # Draw component vector arrows on ship
        if showComponentVectors:
            if shipVelocityX != 0:
                vectorLength = shipVelocityX/zoomFactor # Calculate length of vector to display
                pygame.draw.line(screen, red, (screen1Center[0], screen1Center[1]), (screen1Center[0]+vectorLength, screen1Center[1]), 3) # Draw line based on vector length
                pygame.draw.polygon(screen, red, ((screen1Center[0]+vectorLength, screen1Center[1]+5), (screen1Center[0]+vectorLength, screen1Center[1]-5), (screen1Center[0]+vectorLength+(5*vectorLength/abs(vectorLength)), screen1Center[1])), 0) # Draw triangle at end of vector; vectorLength/abs(vectorLength) finds the sign of the direction
                currentTextLength = textLength(str(round(shipVelocityX,1))+" m/s", "small")
                if vectorLength < 0 and abs(shipVelocityX) < 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityX,1))+" m/s", 1, red), (screen1Center[0]+vectorLength-currentTextLength - 15, screen1Center[1] - 7))
                if vectorLength < 0 and abs(shipVelocityX) >= 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityX/1000,1))+" km/s", 1, red), (screen1Center[0]+vectorLength-currentTextLength - 15, screen1Center[1] - 7))
                if vectorLength > 0 and abs(shipVelocityX) < 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityX,1))+" m/s", 1, red), (screen1Center[0]+vectorLength + 15, screen1Center[1] - 7))
                if vectorLength > 0 and abs(shipVelocityX) >= 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityX/1000,1))+" km/s", 1, red), (screen1Center[0]+vectorLength + 15, screen1Center[1] - 7))

            if abs(shipVelocityY) >= 0.0001:
                vectorLength = -shipVelocityY/zoomFactor
                pygame.draw.line(screen, green, (screen1Center[0], screen1Center[1]), (screen1Center[0], screen1Center[1]+vectorLength), 3)
                pygame.draw.polygon(screen, green, ((screen1Center[0]-5, screen1Center[1]+vectorLength), (screen1Center[0]+5, screen1Center[1]+vectorLength), (screen1Center[0], screen1Center[1]+vectorLength+(5*vectorLength/abs(vectorLength)))), 0)
                currentTextLength = textLength(str(round(shipVelocityY,1))+" m/s", "small")
                if vectorLength < 0 and abs(shipVelocityY) < 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY,1))+" m/s", 1, green), (screen1Center[0]-currentTextLength/2, screen1Center[1] + vectorLength - 30))
                if vectorLength < 0 and abs(shipVelocityY) >= 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY/1000,1))+" km/s", 1, green), (screen1Center[0]-currentTextLength/2, screen1Center[1] + vectorLength - 30))
                if vectorLength > 0 and abs(shipVelocityY) < 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY,1))+" m/s", 1, green), (screen1Center[0]-currentTextLength/2, screen1Center[1] + vectorLength + 30))
                if vectorLength > 0 and abs(shipVelocityY) >= 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY/1000,1))+" km/s", 1, green), (screen1Center[0]-currentTextLength/2, screen1Center[1] + vectorLength + 30))

        # Draw resultant vector arrow on ship
        if showResultantVector and shipResultantVelocity != 0:
            if abs(shipResultantVelocity) < 1000:
                currentText = str(round(shipResultantVelocity,2))+" m/s"
            else:
                currentText = str(round(shipResultantVelocity/1000,1))+" km/s"
            arrow(black, (screen1Center[0], screen1Center[1]), (screen1Center[0]+shipVelocityX/zoomFactor, screen1Center[1]-shipVelocityY/zoomFactor), currentText)
            currentTextLength = textLength(currentText, "small")

        zoomFactor *= 3

        # Draw force vector arrows on ship
        if showForceVectors:
            if keySpace:
                vectorX = -(mainThrusterForce)*(math.sin(math.radians(shipYaw)))*abs(math.cos(math.radians(shipPitch))) / (zoomFactor*300)
                vectorY = -(mainThrusterForce)*(math.cos(math.radians(shipYaw)))*abs(math.cos(math.radians(shipPitch))) / (zoomFactor*300)
                currentText = "Thrust: "+str(int(mainThrusterForce/1000))+" kN"
                arrow(darkGray, (screen1Center[0], screen1Center[1]), (screen1Center[0]+vectorX, screen1Center[1]+vectorY), currentText)
            if keyA and not earth:
                vectorX = -(maneuveringThrusterForce)*(math.sin(math.radians(shipYaw+90))) / (zoomFactor*200)
                vectorY = -(maneuveringThrusterForce)*(math.cos(math.radians(shipYaw+90))) / (zoomFactor*200)
                currentText = "Rot. Thrust: "+str(int(maneuveringThrusterForce/1000))+" kN"
                arrow(darkGray, (screen1Center[0], screen1Center[1]), (screen1Center[0]+vectorX, screen1Center[1]+vectorY), currentText)
            if keyD and not earth:
                vectorX = -(maneuveringThrusterForce)*(math.sin(math.radians(shipYaw-90))) / (zoomFactor*200)
                vectorY = -(maneuveringThrusterForce)*(math.cos(math.radians(shipYaw-90))) / (zoomFactor*200)
                currentText = "Rot. Thrust: "+str(int(maneuveringThrusterForce/1000))+" kN"
                arrow(darkGray, (screen1Center[0], screen1Center[1]), (screen1Center[0]+vectorX, screen1Center[1]+vectorY), currentText)
            if earth:
                if forceDrag > 100:
                    vectorX = -forceDrag * unitVector[0] / (zoomFactor*300)
                    vectorY = -(-forceDrag * unitVector[1] / (zoomFactor*300))
                    currentText = "Drag: "+str(int(forceDrag/1000))+" kN"
                    arrow(darkGray, (screen1Center[0], screen1Center[1]), (screen1Center[0]+vectorX, screen1Center[1]+vectorY), currentText)
                if abs(forceLift*(math.sin(math.radians(shipRoll)))) > 100:
                    vectorX = -forceLift*(math.sin(math.radians(shipRoll))) / (zoomFactor*200)
                    vectorY = 0
                    currentText = "Lift: "+str(int(forceLift/1000))+" kN"
                    arrow(darkGray, (screen1Center[0], screen1Center[1]), (screen1Center[0]+vectorX, screen1Center[1]+vectorY), currentText)

        # -------YZ UI-------
        screen.blit(font.render("YZ Position (\"Altitude\")", 1, black), (screen2Anchor[0], screen3Anchor[1]-40))
        pygame.draw.rect(screen, black, (screen2Anchor[0]-5, screen2Anchor[1]-5, screen2Dim[0]+10, screen2Dim[1]+10), 0)
        if not earth:
            pygame.draw.rect(screen, space, (screen2Anchor[0], screen2Anchor[1], screen2Dim[0], screen2Dim[1]), 0)
        if earth:
            pygame.draw.rect(screen, sky, (screen2Anchor[0], screen2Anchor[1], screen2Dim[0], screen2Dim[1]), 0)

        # Z-axis gridlines
        shipZ /= -1 * zoomFactor
        nearestLine = round(shipZ/100)*100
        for i in range(-3,3 + 1):
            currentLine = nearestLine+(i*100)
            if currentLine in range(int(shipZ-screen2Dim[1]/2),int(shipZ+screen2Dim[1]/2) + 1):
                if currentLine == 0 and earth: # Draw floor of Earth if necessary
                    spaceBelowZero = int(screen2Dim[1]/2+int(shipZ))
                    pygame.draw.line(screen, gray, (screen2Anchor[0], int(screen2Anchor[1]+screen2Dim[1]/2+(currentLine-shipZ)+spaceBelowZero/2)), (screen2Anchor[0]+screen2Dim[0], int(screen2Anchor[1]+screen2Dim[1]/2+(currentLine-shipZ)+spaceBelowZero/2)), spaceBelowZero)
                pygame.draw.line(screen, lightGray, (screen2Anchor[0], int(screen2Anchor[1]+screen2Dim[1]/2+(currentLine-shipZ))), (screen2Anchor[0]+screen2Dim[0], int(screen2Anchor[1]+screen2Dim[1]/2+(currentLine-shipZ))), 2)
                currentText = str(round((-currentLine/1000)*zoomFactor,1))+" km"
                currentTextLength = textLength(currentText, "tiny")
                screen.blit(tinyFont.render(currentText, 1, gray), (screen2Anchor[0]-currentTextLength - 10, int(screen2Center[1]+(currentLine-shipZ) - 5)))
        shipZ *= -1 * zoomFactor

        # Y-axis gridlines
        shipY /= -1 * zoomFactor
        nearestLine = round(shipY/100)*100
        for i in range(-3,3 + 1):
            currentLine = nearestLine+(i*100)
            if currentLine in range(int(shipY-screen2Dim[0]/2),int(shipY+screen2Dim[0]/2) + 1):
                pygame.draw.line(screen, lightGray, (int(screen2Center[0]+(currentLine-shipY)), screen2Anchor[1]+screen2Dim[1]), (int(screen2Center[0]+(currentLine-shipY)), screen2Anchor[1]), 2)
                currentText = str(round((currentLine/1000)*zoomFactor,1))+" km"
                currentTextLength = textLength(currentText, "tiny")
                screen.blit(tinyFont.render(currentText, 1, gray), (int(screen2Center[0]+(currentLine-shipY)-currentTextLength/2), screen2Anchor[1]+screen2Dim[1]+5))
        shipY *= -1 * zoomFactor

        # Axis titles
        axisTitle2Anchor = (screen2Anchor[0]-20, screen2Anchor[1]+screen2Dim[1]+20)
        arrow(black, (axisTitle2Anchor[0], axisTitle2Anchor[1]), (axisTitle2Anchor[0]+20, axisTitle2Anchor[1]), "")
        arrow(black, (axisTitle2Anchor[0], axisTitle2Anchor[1]), (axisTitle2Anchor[0], axisTitle2Anchor[1]-20), "")
        screen.blit(tinyFont.render("Y", 1, black), (axisTitle2Anchor[0]+30, axisTitle2Anchor[1]-6))
        screen.blit(tinyFont.render("Z", 1, black), (axisTitle2Anchor[0]-3, axisTitle2Anchor[1]-40))

        # Draw ship
        blitRotateCenter(shipSide, (screen2Anchor[0]+screen2Dim[0]/2-shipDimY/2, screen2Anchor[1]+screen2Dim[1]/2-shipDimZ/2), shipPitch)
        if keySpace:
            blitRotateCenter(shipSideMain, (screen2Anchor[0]+screen2Dim[0]/2-shipDimZ/2, screen2Anchor[1]+screen2Dim[1]/2-shipDimZ/2), shipPitch)
        if keyW and not earth:
            blitRotateCenter(shipSideU, (screen2Anchor[0]+screen2Dim[0]/2-shipDimZ/2, screen2Anchor[1]+screen2Dim[1]/2-shipDimZ/2), shipPitch)
        if keyS and not earth:
            blitRotateCenter(shipSideD, (screen2Anchor[0]+screen2Dim[0]/2-shipDimZ/2, screen2Anchor[1]+screen2Dim[1]/2-shipDimZ/2), shipPitch)

        # Draw component vector arrows on ship
        zoomFactor /= 3
        if showComponentVectors:
            if shipVelocityZ != 0:
                shipVelocityZ *= -1
                vectorLength = shipVelocityZ/zoomFactor
                pygame.draw.line(screen, blue, (screen2Center[0], screen2Center[1]), (screen2Center[0], screen2Center[1]+vectorLength), 3)
                pygame.draw.polygon(screen, blue,((screen2Center[0]-5, screen2Center[1]+vectorLength), (screen2Center[0]+5, screen2Center[1]+vectorLength), (screen2Center[0], screen2Center[1]+vectorLength+(5*vectorLength/abs(vectorLength)))), 0)
                currentTextLength = textLength(str(round(-shipVelocityZ,1))+" m/s", "small")
                if shipVelocityZ < 0 and abs(shipVelocityZ) < 1000:
                    screen.blit(smallFont.render(str(round(-shipVelocityZ,1))+" m/s", 1, blue), (screen2Center[0]-currentTextLength/2, screen2Center[1] + vectorLength - 30))
                if shipVelocityZ < 0 and abs(shipVelocityZ) >= 1000:
                    screen.blit(smallFont.render(str(round(-shipVelocityZ/1000,1))+" km/s", 1, blue), (screen2Center[0]-currentTextLength/2, screen2Center[1] + vectorLength - 30))                         
                if shipVelocityZ > 0 and abs(shipVelocityZ) < 1000:
                    screen.blit(smallFont.render(str(round(-shipVelocityZ,1))+" m/s", 1, blue), (screen2Center[0]-currentTextLength/2, screen2Center[1] + vectorLength + 30))
                if shipVelocityZ > 0 and abs(shipVelocityZ) >= 1000:
                    screen.blit(smallFont.render(str(round(-shipVelocityZ/1000,1))+" km/s", 1, blue), (screen2Center[0]-currentTextLength/2, screen2Center[1] + vectorLength + 30))
                shipVelocityZ *= -1

            if shipVelocityY != 0:
                vectorLength = shipVelocityY/zoomFactor
                pygame.draw.line(screen, green, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorLength, screen2Center[1]), 3)
                pygame.draw.polygon(screen, green, ((screen2Center[0]+vectorLength, screen2Center[1]+5), (screen2Center[0]+vectorLength, screen2Center[1]-5), (screen2Center[0]+vectorLength+(5*vectorLength/abs(vectorLength)), screen2Center[1])), 0)
                currentTextLength = textLength(str(round(shipVelocityY,1))+" m/s", "small")
                if vectorLength < 0 and abs(shipVelocityY) < 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY,1))+" m/s", 1, green), (screen2Center[0]+vectorLength-currentTextLength - 15, screen2Center[1] - 7))
                if vectorLength < 0 and abs(shipVelocityY) >= 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY/1000,1))+" km/s", 1, green), (screen2Center[0]+vectorLength-currentTextLength - 15, screen2Center[1] - 7))
                if vectorLength > 0 and abs(shipVelocityY) < 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY,1))+" m/s", 1, green), (screen2Center[0]+vectorLength + 15, screen2Center[1] - 7))
                if vectorLength > 0 and abs(shipVelocityY) >= 1000:
                    screen.blit(smallFont.render(str(round(shipVelocityY/1000,1))+" km/s", 1, green), (screen2Center[0]+vectorLength + 15, screen2Center[1] - 7))

        # Draw resultant vector arrow on ship
        if showResultantVector and (shipVelocityZ != 0 or shipVelocityY != 0):
            if abs(shipResultantVelocity) < 1000:
                currentText = str(round(shipResultantVelocity,2))+" m/s"
            else:
                currentText = str(round(shipResultantVelocity/1000,1))+" km/s"
            arrow(black, (screen2Center[0], screen2Center[1]), (screen2Center[0]+shipVelocityY/zoomFactor, screen2Center[1]-shipVelocityZ/zoomFactor), currentText)

        zoomFactor *= 3

        # Draw force vector arrows on ship
        if showForceVectors:
            if keySpace and (abs(shipVelocityY) > 0.0001 or abs(shipVelocityZ) > 0.0001):
                vectorX = (mainThrusterForce)*abs(math.cos(math.radians(shipYaw)))*(math.cos(math.radians(shipPitch))) / (zoomFactor*300)
                vectorY = -(mainThrusterForce)*(math.sin(math.radians(shipPitch))) / (zoomFactor*300)
                currentText = "Thrust: "+str(int(mainThrusterForce/1000))+" kN"
                arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)
            if keyW and not earth:
                vectorX = (maneuveringThrusterForce)*(math.cos(math.radians(shipPitch+90))) / (zoomFactor*200)
                vectorY = -(maneuveringThrusterForce)*(math.sin(math.radians(shipPitch+90))) / (zoomFactor*200)
                currentText = "Rot. Thrust: "+str(int(maneuveringThrusterForce/1000))+" kN"
                arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)
            if keyS and not earth:
                vectorX = (maneuveringThrusterForce)*(math.cos(math.radians(shipPitch-90))) / (zoomFactor*200)
                vectorY = -(maneuveringThrusterForce)*(math.sin(math.radians(shipPitch-90))) / (zoomFactor*200)
                currentText = "Rot. Thrust: "+str(int(maneuveringThrusterForce/1000))+" kN"
                arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)
            if earth:
                if forceGravity > 0:
                    vectorX = 0
                    vectorY = forceGravity / (zoomFactor*200)
                    currentText = "Gravity: "+str(int(forceGravity/1000))+" kN"
                    arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)
                if forceDrag > 100:
                    vectorX = -forceDrag * unitVector[1] / (zoomFactor*300)
                    vectorY = -(-forceDrag * unitVector[2] / (zoomFactor*300))
                    currentText = "Drag: "+str(int(forceDrag/1000))+" kN"
                    arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)
                if forceLift > 100:
                    vectorX = 0
                    vectorY = -forceLift*(math.cos(math.radians(shipRoll))) / (zoomFactor*200)
                    currentText = "Lift: "+str(int(forceLift/1000))+" kN"
                    arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)
                if forceNormal > 0 and abs(shipZ) < 0.1:
                    vectorX = 0
                    vectorY = -forceNormal / (zoomFactor*200)
                    currentText = "Normal: "+str(int(forceNormal/1000))+" kN"
                    arrow(darkGray, (screen2Center[0], screen2Center[1]), (screen2Center[0]+vectorX, screen2Center[1]+vectorY), currentText)

        # -------Roll Screen-------
        screen.blit(font.render("Wing Angle (Relative to XY Plane)", 1, black), (screen3Anchor[0], screen3Anchor[1]-40))
        pygame.draw.rect(screen, black, (screen3Anchor[0]-5, screen3Anchor[1]-5, screen3Dim[0]+10, screen3Dim[1]+10), 0)
        if not earth:
            pygame.draw.rect(screen, space, (screen3Anchor[0], screen3Anchor[1], screen3Dim[0], screen3Dim[1]), 0)
        if earth:
            pygame.draw.rect(screen, sky, (screen3Anchor[0], screen3Anchor[1], screen3Dim[0], screen3Dim[1]), 0)

        # Draw ship
        blitRotateCenter(shipRear, (screen3Anchor[0]+screen3Dim[0]/2-45, screen3Anchor[1]+screen3Dim[1]/2-24), shipRoll) # Hard coded center displacements based on texture size
        if keySpace:
            blitRotateCenter(shipRearMain, (screen3Anchor[0]+screen3Dim[0]/2-45, screen3Anchor[1]+screen3Dim[1]/2-24), shipRoll)

        # Draw force vector arrows on ship
        if showForceVectors:
            if earth:
                if forceGravity > 0:
                    vectorX = 0
                    vectorY = forceGravity / (zoomFactor*200)
                    currentText = "Gravity: "+str(int(forceGravity/1000))+" kN"
                    arrow(darkGray, (screen3Center[0], screen3Center[1]), (screen3Center[0]+vectorX, screen3Center[1]+vectorY), currentText)
                if forceLift > 0:
                    vectorX = -forceLift*(math.sin(math.radians(shipRoll))) / (zoomFactor*200)
                    vectorY = -forceLift*(math.cos(math.radians(shipRoll))) / (zoomFactor*200)
                    currentText = "Lift: "+str(int(forceLift/1000))+" kN"
                    arrow(darkGray, (screen3Center[0], screen3Center[1]), (screen3Center[0]+vectorX, screen3Center[1]+vectorY), currentText)
                if forceNormal > 0 and abs(shipZ) < 0.1:
                    vectorX = 0
                    vectorY = -forceNormal / (zoomFactor*200)
                    currentText = "Normal: "+str(int(forceNormal/1000))+" kN"
                    arrow(darkGray, (screen3Center[0], screen3Center[1]), (screen3Center[0]+vectorX, screen3Center[1]+vectorY), currentText)

        # -------Non-Changeable Properties UI-------
        if abs(shipX) < 1000: # Check whether to display m or km
            screen.blit(smallFont.render("X Position: "+str(round(shipX,2))+" m", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+30))
        if abs(shipX) >= 1000:
            screen.blit(smallFont.render("X Position: "+str(round(shipX/1000,2))+" km", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+30))
        if shipY == 0: # Special case for when the ship's y position = 0 due to weird display bug
            screen.blit(smallFont.render("Y Position: 0.0 m", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+45))
        if abs(shipY) < 1000 and not (shipY == 0):
            screen.blit(smallFont.render("Y Position: "+str(round(-shipY,2))+" m", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+45))
        if abs(shipY) >= 1000:
            screen.blit(smallFont.render("Y Position: "+str(round(-shipY/1000,2))+" km", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+45))
        if abs(shipZ) < 1000:
            screen.blit(smallFont.render("Z Position: "+str(round(shipZ,2))+" m", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+60))
        if abs(shipZ) >= 1000:
            screen.blit(smallFont.render("Z Position: "+str(round(shipZ/1000,2))+" km", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+60))

        if shipResultantVelocity < 1000:
            screen.blit(smallFont.render("Velocity: "+str(round(shipResultantVelocity,2))+" m/s", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+75))
        if shipResultantVelocity >= 1000:
            screen.blit(smallFont.render("Velocity: "+str(round(shipResultantVelocity/1000,2))+" km/s", 1, black), (screen1Anchor[0], screen1Anchor[1]+screen1Dim[1]+75))
            
        screen.blit(smallFont.render("Yaw: "+str(int(shipYaw))+"°", 1, black), (screen1Anchor[0]+160, screen1Anchor[1]+screen1Dim[1]+30))
        screen.blit(smallFont.render("Pitch: "+str(int(shipPitch))+"°", 1, black), (screen1Anchor[0]+160, screen1Anchor[1]+screen1Dim[1]+45))
        screen.blit(smallFont.render("Roll: "+str(int(shipRoll))+"°", 1, black), (screen1Anchor[0]+160, screen1Anchor[1]+screen1Dim[1]+60))
        screen.blit(smallFont.render("ω (Yaw): "+str(round(shipVelocityYaw,2))+"°/s", 1, black), (screen1Anchor[0]+160, screen1Anchor[1]+screen1Dim[1]+85))
        screen.blit(smallFont.render("ω (Pitch): "+str(round(shipVelocityPitch,2))+"°/s", 1, black), (screen1Anchor[0]+160, screen1Anchor[1]+screen1Dim[1]+100))
        screen.blit(smallFont.render("ω (Roll): "+str(round(shipVelocityRoll,2))+"°/s", 1, black), (screen1Anchor[0]+160, screen1Anchor[1]+screen1Dim[1]+115))

        screen.blit(smallFont.render("Accel. Main Thruster: "+str(round(mainThrusterForce/shipMass,2))+" m/s^2", 1, black), (screen1Anchor[0]+280, screen1Anchor[1]+screen1Dim[1]+30))
        screen.blit(smallFont.render("Accel. Side Thrusters: "+str(round(maneuveringThrusterForce/shipMass,2))+" m/s^2", 1, black), (screen1Anchor[0]+280, screen1Anchor[1]+screen1Dim[1]+45))
        if not earth:
            screen.blit(smallFont.render("Kinetic Energy: "+str(round(0.5*shipMass*shipResultantVelocity**2/1000000,2))+" MJ", 1, black), (screen1Anchor[0]+280, screen1Anchor[1]+screen1Dim[1]+70))
        if earth:
            screen.blit(smallFont.render("Accel. Gravity: "+str(round(forceGravity/shipMass,2))+" m/s^2", 1, black), (screen1Anchor[0]+280, screen1Anchor[1]+screen1Dim[1]+60))
            screen.blit(smallFont.render("Kinetic Energy: "+str(round(0.5*shipMass*shipResultantVelocity**2/1000000,2))+" MJ", 1, black), (screen1Anchor[0]+280, screen1Anchor[1]+screen1Dim[1]+85))
            screen.blit(smallFont.render("Grav. Potential Energy: "+str(round(GPE/1000000,2))+" MJ", 1, black), (screen1Anchor[0]+280, screen1Anchor[1]+screen1Dim[1]+100))
        
        if int(timeElapsed%60) < 10: # Change time display based on how many digits to display
            screen.blit(smallFont.render("Time: "+str(math.floor(timeElapsed/60))+":0"+str(round(timeElapsed%60,2)), 1, gray), (screen2Anchor[0], screen2Anchor[1]+screen2Dim[1]+30))
        if int(timeElapsed%60) >= 10:
            screen.blit(smallFont.render("Time: "+str(math.floor(timeElapsed/60))+":"+str(round(timeElapsed%60,2)), 1, gray), (screen2Anchor[0], screen2Anchor[1]+screen2Dim[1]+30))

        # -------Setting UI-------
        screen.blit(font.render("Settings", 1, black), (screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+30))
        for c in range(len(simulatorButtonList)):
            currentButton = simulatorButtonList[c]
            currentButton.draw()

        # -------Parameters UI-------
        screen.blit(font.render("Parameters", 1, black), (screen3Anchor[0], screen3Anchor[1]+screen3Dim[1]+225))

    # Update screen
    pygame.display.flip()

    # 60 fps
    clock.tick(60)



# Quit
pygame.quit()
