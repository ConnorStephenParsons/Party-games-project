import pygame
from PodSixNet.Connection import connection, ConnectionListener
from objects.Button import Button
from objects.TextBox import TextBox
from resources.hubColours import ColoursClass
from time import sleep
from STATE import STATE
import sys, os
from objects.Text import Text
from games.FakeNews.FN_STATE import FN_STATE
from games.FakeNews.objects.Headings import Headings

class FakeNews(ConnectionListener):
    def __init__(self, hub, width, height, soundController, fontController, fps=60):

        #Hub
        self.hub = hub 

        # RESOURCES
        self.soundController = soundController
        self.color = ColoursClass("fakeNewsGame")

        #SCREEN
        self.width = width
        self.height = height
        self.background = pygame.Surface((self.width, self.height)).convert()  
        self.background.fill(self.color.getColour(7)) # fill background white

        #INFO
        self.fps = fps
        self.playtime = 0.0

        self.heading = ''
        self.headings = []

        self.round = 0
        self.instructions = ("Fake News:\n"
                            "All players are given a category and have to come up\n"
                            "with a crazy news title based on the category. On the\n"
                            "next screen, the players are shown all of the news \n"
                            "titles that were entered by players as well as one real\n"
                            "news title hidden in the mix of fake news titles. The \n"
                            "player's goal is to try and choose the real news title and\n"
                            "to fool other players into choosing their fake title.\n\n"
                            "Points:\n"
                            "1 Point for choosing the real news title\n"
                            "1 Point for each player that chooses your fake title")

        self.didPlayerSubmit = False
        self.didPlayerSelect = False

        #FONTS
        self.fontController = fontController
        
        #STATE
        # All player related stuff is stored in the HUB.
        # TODO:
        # Player class
        self.state = FN_STATE.HOME
        self.isRunning = True
        self.selectedHeading = ''
        self.timeLeft = "Waiting for players..."
        self.isReady = False
        self.clock = pygame.time.Clock()

        # Objects
        self.on_init()

    #Initialize game objects
    def on_init(self):
        self.instructionsText = Text(self.instructions, self.color.getColour(8), 10, 70, font = self.fontController.medium, multiLine=True) 

        self.readyButton = Button(200, 50,  self.color.getColour(4), text='IM READY', font=self.fontController.small)
        self.readyButton.setPosCenter(self.width, self.height - 100)

        self.againButton = Button(200, 50,  self.color.getColour(4), text='Again', font=self.fontController.small)
        self.againButton.setPosCenter(self.width, self.height - 100)
        
        self.winnerText = Text("", self.color.getColour(8), font = self.fontController.medium)
        self.winnerText.setPosCenter(self.width, self.height / 2)

        self.timerText = Text(self.timeLeft, self.color.getColour(8), font=self.fontController.medium)
        self.timerText.setPosCenter(self.width, 50)
        
        self.headingInput = TextBox(400, 45)
        self.headingInput.setPosCenter(self.width, self.height/2)

        self.submitHeadingBtn = Button(200, 50,  self.color.getColour(4), text="Submit")
        self.submitHeadingBtn.setPosCenter(self.width, self.height - 100)

        self.headingDisplayScreen = Headings(self.width, self.height / 2, 0, 200, self.fontController.medium, self.color.getColour(4), (255, 255, 255), self.headings, bgColor=self.color.getColour(7))
        #self.handler.add(button) # Add button to object handler

        self.selectHeadingBtn = Button(200, 50,  self.color.getColour(4), text="Select")
        self.selectHeadingBtn.setPosCenter(self.width, self.height - 100)

        self.category = Text("", self.color.getColour(8), font = self.fontController.medium)
        self.category.setPosCenter(self.width, self.height - 200)
        
        self.correctHeading = Text("", self.color.getColour(8), font = self.fontController.medium)
        self.correctHeading.setPosCenter(self.width, self.height / 3)

        self.leaderboard = Text("", self.color.getColour(8), font = self.fontController.medium)
        self.leaderboard.setPosCenter(self.width, self.height - 700)
        
        self.backToLobbyBtn = Button(300, 50, self.color.getColour(4), text="Return to Lobby", font=self.fontController.small)
        self.backToLobbyBtn.setPosCenter(self.width, self.height - 100)
    
    # Draws on screen
    def draw(self, screen):                               # Update all objects (through object handler)                                            # This will update the contents of the entire display
        screen.blit(self.background, (0, 0))
        self.drawInfoText("Player Count: " + str(self.hub.getInGamePlayerCount()), 10, 20, self.fontController.tiny, screen)
        self.drawInfoText("FPS: " + str(round(self.getFPS(), 2)), 10, 30, self.fontController.tiny, screen)
        self.drawInfoText("Network Status: " + self.hub.statusLabel, 10, 40, self.fontController.tiny, screen)
        self.drawInfoText("Round: " + str(self.round), 10, 50, self.fontController.tiny, screen)

        if(self.state == FN_STATE.HOME):
            self.readyButton.draw(screen)
            if self.round==0:
                self.instructionsText.draw(screen)
        elif (self.state == FN_STATE.INPUT):
            self.timerText.draw(screen)
            self.headingInput.draw(screen)
            self.category.draw(screen)
            self.submitHeadingBtn.draw(screen)
        elif (self.state == FN_STATE.GUESS):
            self.timerText.draw(screen)
            self.headingDisplayScreen.draw(screen)
            self.selectHeadingBtn.draw(screen)
        elif (self.state == FN_STATE.END):
            self.timerText.draw(screen)
            self.correctHeading.draw(screen)
            self.winnerText.draw(screen)
            self.againButton.draw(screen)
        elif (self.state == FN_STATE.GAMEOVER):
            # draw the leaderboard for this session, show who scored the most points
            self.leaderboard.draw(screen)
            self.backToLobbyBtn.draw(screen)



    # Looks for events
    def handle_events(self, events):
        self.headingInput.handle_events(events)
        self.headingDisplayScreen.handle_events(events)
        
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
                    # If mouse button pressed...
                    if(self.state == FN_STATE.HOME):
                        if self.readyButton.get_rect().collidepoint(pygame.mouse.get_pos()):
                            self.isReady = True
                            self.state = FN_STATE.INPUT
                            self.sendReady(event)
                            self.soundController.playButtonClick()
        
                    elif (self.state == FN_STATE.INPUT):
                        if self.submitHeadingBtn.get_rect().collidepoint(pygame.mouse.get_pos()):
                            self.heading = self.headingInput.getText()
                            if(len(self.heading) > 0):
                                self.sendHeading(self.heading)
                                self.soundController.playButtonClick()
        
                    elif (self.state == FN_STATE.GUESS):
                        if self.selectHeadingBtn.get_rect().collidepoint(pygame.mouse.get_pos()):
                            self.selectedHeading = self.headingDisplayScreen.getSelectedHeading()
                            if(self.selectedHeading != None):
                                self.sendSelectedHeading(self.selectedHeading)
                                self.soundController.playButtonClick()

                    elif (self.state == FN_STATE.END):
                        if self.againButton.get_rect().collidepoint(pygame.mouse.get_pos()):
                            print("Again")
                            self.resetGame()
                            self.soundController.playButtonClick()
                    elif (self.state == FN_STATE.GAMEOVER):
                        if self.backToLobbyBtn.get_rect().collidepoint(pygame.mouse.get_pos()):
                            print("Returning to lobby")
                            self.exitGame(event)
                            self.hub.setState(STATE.Lobby)
                            self.state = FN_STATE.HOME
                            self.round = 0
                            # NEED TO SET ROUND IN FakeNewsState to 0
                            self.soundController.playButtonClick()

    # Update stuff (loop)
    def update(self):
        self.Pump()                 # Connection
        connection.Pump()           # Connection

        # if self.round == 2:
            
    
    # returns FPS
    def getFPS(self):
        self.clock.tick(self.fps)
        return self.clock.get_fps()

    # Helper for quickly drawing on screen
    def drawInfoText(self, text, x, y, font, screen):
        surface = font.render(str(text), 1, self.color.getColour(8))
        screen.blit(surface, (x, y))
    
    # Exits the game to home
    def exitGame(self, e):
        connection.Send({"action":"exitGame", "isInGame": False})
        self.hub.isInGame = False
        self.resetGame()
    
    def resetGame(self):
        print("Resetting the game")
        self.timerText.setPosCenter(self.width, 50)
        self.isReady = False
        self.heading = ''
        self.headings = []
        self.headingDisplayScreen = Headings(self.width, self.height / 2, 0, 200, self.fontController.medium, self.color.getColour(4), (255, 255, 255), self.headings, bgColor=self.color.getColour(7)) # Reset headings
        self.state = FN_STATE.HOME
        self.didPlayerSubmit = False
        self.didPlayerSelect = False
        # if self.round==1:
            # self.Network_fakeNews_GameOver()


    def resetRoundOnServer(self):
        print("RESETTING ROUND ON SERVER")
        connection.Send({"action":"fakeNews_resetRound"})

    ######### NETWORK ########

    ### SENDS TO SERVER ###

    # Tell server that client is ready
    def sendReady(self, e):
        print("TELLING THE SERVER I'M READY")
        connection.Send({"action": "fakeNews_ready", "isReady": self.isReady})
    
    # Send heading to the server
    def sendHeading(self, heading):
        print("SENDING HEADING TO SERVER: ", heading)
        connection.Send({'action':'fakeNews_receiveHeading', 'heading': heading})
    
    # Send selected heading to the server
    def sendSelectedHeading(self, heading):
        print("SENDING SELECTED HEADING TO SERVER", heading)
        #sendHeading = {'playerId': heading['playerId'], 'headingId': heading['headingId']} # Because you can't send raw objects
        connection.Send({"action": "fakeNews_receiveHeadingSelection", 'heading': heading})
   
    ### RECEIVES FROM SERVER ###
    
    # Change state to whatever the server told
    def Network_fakeNews_newState(self, data):
        print("GOT NEW STATE!: ", FN_STATE(data['state']))
        self.state = FN_STATE(data['state'])

        if FN_STATE(data["state"]) == FN_STATE.GAMEOVER:
            self.resetRoundOnServer()

    # Receives headings, to be able to display them
    def Network_headings(self, data):
        print('Ive received headings: ', data['headings'])
        self.headings = data['headings']
        self.headingDisplayScreen.addHeadings(self.headings)

    # Catches network events and updates timer
    def Network_timer(self, data):
        self.timeLeft = data['time']
        self.timerText.setText(data['time'])
        self.timerText.setPosCenter(self.width, 50)
        print("TICK: ", self.timeLeft)

    # def Netowrk_round(self, data):
    #     print("ROUND: ", data['round'])
    #     self.round = data['round']
    
    # Catches endround events (when the timer ends server fires one)
    def Network_fakeNews_roundEnd(self, data):
        self.isReady = False
        winnerText = "Guessed correctly: "
        correctHeading = data['correctHeading']
        # self.round = data['nextRound']

        # Makes string of all winner names
        for w in data['winners']:
            winnerText += w['playerName'] +  ", "
        
        self.winnerText.setText(winnerText)
        self.winnerText.setPosCenter(self.width, 400)

        self.correctHeading.setText("True: " + correctHeading)
        self.correctHeading.setPosCenter(self.width, self.height / 3)

        # Makes timer to display that is waiting for players
        self.timeLeft = "Waiting for players..."
        self.timerText.setText(self.timeLeft)
        self.timerText.setPosCenter(self.width, 50)

    # Initial data about the game once round starts
    def Network_fakeNews_StartRound(self, data):
        print("STARTING!, category: ", data['category'], data['round'])
        category = data['category']

        # Set current round
        self.round = data['round']

        # Set current category
        self.category.setText("Category: " + category)
        self.category.setPosCenter(self.width, self.height - 200)

    def Network_fakeNews_GameOver(self):
        self.state = FN_STATE.GAMEOVER
        print("Game ending!")
        self.leaderboard.setText("Leaderboard:")


    # Catches player join events and udates current player list
    def Network_players(self, data):
        self.hub.players = data['players']  # Send players to the hub
        print("Fakenews: New player joined!", self.hub.players)

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
        print("NETWORK ERROR:", data['error'][1])
        #self.statusLabel = data['error'][1]
        connection.Close()
    # On disconnect
    
    def Network_disconnected(self, data):
        print("Disconnected...", data)
        self.statusLabel = "Disconnected"    

