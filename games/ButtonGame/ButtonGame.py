import pygame
from PodSixNet.Connection import connection, ConnectionListener
from objects.Button import Button
from time import sleep
from STATE import STATE
import sys, os
from objects.Text import Text
from resources.hubColours import ColoursClass

class ButtonGame(ConnectionListener):
    def __init__(self, hub, width, height, soundController, fontController, fps=60):
        #Hub
        self.hub = hub
       
        #COLOURS
        self.color = ColoursClass("buttonGame")

        #SOUNDS
        self.soundController = soundController

        #SCREEN
        self.width = width
        self.height = height
        self.background = pygame.Surface((self.width, self.height)).convert()  
        self.background.fill(self.color.colourSix) # fill background white

        #INFO
        self.fps = fps
        self.playtime = 0.0
        self.winner = "..."
        self.winnerColor = "..."

        #FONTS
        self.fontController = fontController
        
        #STATE
        # All player related stuff is stored in the HUB.
        # TODO:
        # Player class
        self.isRunning = True

        self.timeLeft = "Waiting for players..."
        self.isReady = False
        self.isRoundEnd = False

        self.clock = pygame.time.Clock()

        #OBJECTS
        #self.handler = ObjectHandler()
                          #Only used for state management
        self.on_init()

    #Initialize game objects
    def on_init(self):
        self.gameButtonOne = Button(500, 100, self.color.colourFour, text="CLICK ME", font = self.fontController.medium)        # Init button
        self.gameButtonOne.setPosCenter(self.width, 125)
        self.gameButtonTwo = Button(500, 100, self.color.colourFour, text="CLICK ME", font = self.fontController.medium)        # Init button
        self.gameButtonTwo.setPosCenter(self.width, 275)
        self.gameButtonThree = Button(500, 100, self.color.colourFour, text="CLICK ME", font = self.fontController.medium)        # Init button
        self.gameButtonThree.setPosCenter(self.width, 425)

        self.readyButton = Button(400, 100, self.color.colourFour, text='IM READY', font=self.fontController.medium, textColor=self.color.colourOne)
        self.readyButton.setPosCenter(self.width, 500)
        
        self.winnerText = Text(self.winner + "(" + self.winnerColor +  ") WINS!", self.color.getColour(8), font = self.fontController.large)
        self.winnerText.setPosCenter(self.width, 400)

        self.timerText = Text(self.timeLeft, self.color.getColour(8), font=self.fontController.large)
        self.timerText.setPosCenter(self.width, 50)
        #self.handler.add(button) # Add button to object handler

        self.maxClicks = 6
        self.clicksLeft = self.maxClicks

    # Draws on screen
    def draw(self, screen):                               # Update all objects (through object handler)                                            # This will update the contents of the entire display
        screen.blit(self.background, (0, 0))
        self.drawInfoText("Color: " + self.hub.playerColorName, 10, 10, self.fontController.tiny, screen)
        self.drawInfoText("Player Count: " + str(self.hub.getInGamePlayerCount()), 10, 20, self.fontController.tiny, screen)
        self.drawInfoText("FPS: " + str(round(self.getFPS(), 2)), 10, 30, self.fontController.tiny, screen)
        self.drawInfoText("Network Status: " + self.hub.statusLabel, 10, 40, self.fontController.tiny, screen)

        #To show player colour
        if (self.width == 1280):
            colRectX = self.width-(self.width/10)
            colTextX = 1165
        else:
            colRectX = self.width-(self.width/8)
            colTextX = self.width - (self.width/8)+3

        pygame.draw.rect(screen,self.hub.playerColor,pygame.Rect(colRectX,50,150,50))
        self.drawInfoText("Your colour", colTextX,30,self.fontController.small,screen)
        #sleep(0.2)
        #print("IS Ready: ", self.isReady)

        if(self.isReady):
            self.gameButtonOne.draw(screen)
            self.gameButtonTwo.draw(screen)
            self.gameButtonThree.draw(screen)
            self.timerText.draw(screen)
            self.drawInfoText("Remaining Clicks:", self.width/2-75,550, self.fontController.small,screen)
            self.drawInfoText(self.clicksLeft, self.width/2-10, 585, self.fontController.medium, screen)
        else:
            self.readyButton.draw(screen)
        
        if(self.isRoundEnd):
            self.readyButton.draw(screen)
            self.winnerText.draw(screen)



    # Looks for events
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT: 
                self.exitGame(event)
                self.hub.setState(STATE.Home)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exitGame(event)
                    self.hub.setState(STATE.SelectGame)
                    self.soundController.playButtonClick()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:          # Mouse first button
                    if(self.isReady):
                        if self.gameButtonOne.get_rect().collidepoint(pygame.mouse.get_pos()):
                            if self.clicksLeft > 0:
                                self.ButtonClick(event, 1)    # send current color to the server
                        elif self.gameButtonTwo.get_rect().collidepoint(pygame.mouse.get_pos()):
                            if self.clicksLeft > 0:
                                self.ButtonClick(event, 2)    # send current color to the server
                        elif self.gameButtonThree.get_rect().collidepoint(pygame.mouse.get_pos()):
                            if self.clicksLeft > 0:
                                self.ButtonClick(event, 3)    # send current color to the server

                    if(not self.isReady or self.isRoundEnd):
                        if self.readyButton.get_rect().collidepoint(pygame.mouse.get_pos()):
                            self.isReady = True
                            self.isRoundEnd = False
                            #self.clicksLeft = self.maxClicks
                            self.sendReady(event)
                            self.soundController.playButtonClick()

    # Update stuff (loop)
    def update(self):
        self.Pump()                 # Connection
        connection.Pump()           # Connection

    # returns FPS
    def getFPS(self):
        self.clock.tick(self.fps)
        return  self.clock.get_fps()

    # Helper for quickly drawing on screen
    def drawInfoText(self, text, x, y, font, screen):
        surface = font.render(str(text), 1, self.color.getColour(8))
        screen.blit(surface, (x, y))
    
    # Exits the game to home
    def exitGame(self, e):
        self.soundController.stopSoundEffects()
        connection.Send({"action":"exitGame", "isInGame": False})
        self.hub.isInGame = False
        self.resetGame()
    
    def resetGame(self):
        self.timeLeft = "Waiting for players..."
        self.timerText.setText(self.timeLeft)
        self.timerText.setPosCenter(self.width, 50)
        self.isReady = False
        self.isRoundEnd = False
        self.isRunning = False

    ######### NETWORK METHODS ########
    ### SENDS TO SERVER ###

     # Sends current buttoon color to the server
    #  Can send this with one method by passing additional variable specifying which button was clicked
    def ButtonClick(self, e, buttonNum):        
        if buttonNum == 1 and self.gameButtonOne.getColor() != self.hub.playerColor:
            self.clicksLeft-=1
            self.soundController.playButtonClick()
            connection.Send({"action": "buttonGame_buttonOneClick", "colorOne": self.hub.playerColor})
        elif buttonNum == 2 and self.gameButtonTwo.getColor() != self.hub.playerColor:
            self.clicksLeft-=1
            self.soundController.playButtonClick()
            connection.Send({"action": "buttonGame_buttonTwoClick", "colorTwo": self.hub.playerColor})
        elif buttonNum == 3 and self.gameButtonThree.getColor() != self.hub.playerColor:
            self.clicksLeft-=1
            self.soundController.playButtonClick()
            connection.Send({"action": "buttonGame_buttonThreeClick", "colorThree": self.hub.playerColor})

    # Tell server that client is ready
    def sendReady(self, e):
        print("TELLING THE SERVER I'M READY")
        connection.Send({"action": "buttonGame_ready", "isReady": self.isReady})

    ### RECEIVES FROM SERVER ###

    # Catches buttonClick events coming from the server (other clients)
    #  Can receive this with one method by passing additional variable specifying which button was clicked
    def Network_buttonGame_buttonOneClick(self, data):
        print("BUTTONGAME: ", data)
        self.gameButtonOne.setBgColor(data['colorOne'])

    def Network_buttonGame_buttonTwoClick(self, data):
        print("BUTTONGAME: ", data)
        self.gameButtonTwo.setBgColor(data['colorTwo'])

    def Network_buttonGame_buttonThreeClick(self, data):
        print("BUTTONGAME: ", data)
        self.gameButtonThree.setBgColor(data['colorThree'])

    # Catches network events and updates timer
    def Network_timer(self, data):
        self.timeLeft = data['time']
        self.timerText.setText(data['time'])
        self.timerText.setPosCenter(self.hub.width, 50)
        if self.timeLeft == 5:
            self.soundController.playCountdown()
        #print("TICK: ", self.timeLeft)
    
    # Catches endround events (when the timer ends server fires one)
    def Network_endRound(self, data):
        self.isReady = False
        self.isRoundEnd = True
        print("WINNER: ", data['winnerName'])
        self.winner = data['winnerName']
        self.winnerColor = data['winnerColor']
        #Update winnertext
        self.winnerText.setText(data['winnerName'] + "(" + data['winnerColor'] +  ") WINS!")
        self.winnerText.setPosCenter(self.width, 400)

        self.timeLeft = "Waiting for players..."
        self.timerText.setText(self.timeLeft)
        self.timerText.setPosCenter(self.hub.width, 50)

        self.clicksLeft = self.maxClicks
        # self.resetGame()

    # Used when player joins in the middle to know the state of the game
    def Network_currentState(self, data):
        print("WOOP! Looks the game already started... Setting")
        # self.gameButtonOne.setBgColor(data['currentColorOne'])
        # self.gameButtonTwo.setBgColor(data['currentColorTwo'])
        # self.gameButtonThree.setBgColor(data['currentColorThree'])
        self.timeLeft = data['timeLeft']
        
        self.timerText.setText(self.timeLeft)
        self.timerText.setPosCenter(self.width, 50)
    

    # Sets initial/current state of the game once client joins to the server
    def Network_initial(self, data):
        print("BUTTONGAME: I've just connected! Initial data: ", data)
        self.playerColor = data['playerColor']                            # Set player color
        self.playerColorName = data['playerColorName']                    # Set player color name
        self.isConnected = True
        self.gameButtonOne.setBgColor(data['currentColorOne'])            # Set current button color
        self.gameButtonTwo.setBgColor(data['currentColorTwo'])
        self.gameButtonThree.setBgColor(data['currentColorThree'])

    # Catches player join events and udates current player list
    def Network_players(self, data):
        self.hub.players = data['players']  # Send players to the hub
        print("BUTTONGAME: New player joined!", self.hub.players)

    # Receives all messages from the server
    def Network(self, data):
        #print("RECEIVED FROM SERVER: ", data)      # Uncomment if you want to print them                            # Uncomment if you want to see all the events from server
        pass

    # On connect
    def Network_connected(self, data):
        self.statusLabel = "Connected"
    
    # On error
    def Network_error(self, data):
        print(data)
        import traceback
        traceback.print_exc()
        #self.statusLabel = data['error'][1]
        connection.Close()
    # On disconnect
    
    def Network_disconnected(self, data):
        print("Disconnected...", data)
        self.statusLabel = "Disconnected"    

