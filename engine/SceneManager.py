import pygame
from resources.sounds import SoundsClass
from resources.fonts import FontClass
from UI.CharacterCreationUI import CharacterCreationUI
from UI.JoinGameUI import JoinGameUI
from UI.LobbyUI import LobbyUI
from UI.LeaderboardUI import LeaderboardUI
from UI.SettingsUI import SettingsUI
from UI.HubUI import HubUI
from UI.GameSelectionUI import GameSelectionUI

from games.ButtonGame.ButtonGame import ButtonGame
from games.FakeNews.FakeNews import FakeNews
from games.DefenseGame.DefenseGame import DefenseGame
from resources.hubColours import ColoursClass

from STATE import STATE
from pathlib import Path
# IDEA:
# Have object handler manage all the objects inside UIs
class SceneManager():
    
    def __init__(self, STATE, hub, width, height):
        self.hub = hub
        self.color = ColoursClass("alt")


        self.width = width
        self.height = height
        self.fullScreen = False
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF)  #Main display
        self.background = pygame.Surface((self.width, self.height)).convert()  # Main background
        self.background.fill(self.color.getColour(7)) # fill background colour.

        # Have all the states here
        self.initSound()
        self.initFonts()
        self.initGames()
        self.initUI()
        self.initObjects()
        self.state = STATE
        self.prevState = STATE
        self.setScene(STATE) # Set default (Home)
        self.soundController.startMenuMusic()

    # Init scene manager objects
    def initObjects(self):
        # IMAGES
        self.backgroundImg2 = pygame.transform.smoothscale(pygame.image.load(str(Path("resources/Images/gug2.png"))), (int(self.width / 3.9), int(self.height / 1.5)))
        self.backgroundImg = pygame.transform.smoothscale(pygame.image.load(str(Path("resources/Images/gug.png"))), (int(self.width / 3.5), int(self.height / 1.5)))
        
        self.background = pygame.Surface((self.width, self.height)).convert()  # Main background
        self.background.fill(self.color.getColour(7)) # fill background colour.
    
    # Sound
    def initSound(self):
        self.soundController = SoundsClass()
    # Fonts
    def initFonts(self):
        self.fontController = FontClass()
    # Ui
    def initUI(self):
        self.HubUI = HubUI(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.GameSelectionUI = GameSelectionUI(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.CharacterCreationUI = CharacterCreationUI(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.JoinGameUI = JoinGameUI(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.LobbyUI = LobbyUI(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.SettingsUI = SettingsUI(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.LeaderboardUI = LeaderboardUI(self.hub, self.width, self.height, self.soundController, self.fontController)
    # Games
    def initGames(self):
        self.ButtonGame = ButtonGame(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.FakeNews = FakeNews(self.hub, self.width, self.height, self.soundController, self.fontController)
        self.DefenseGame = DefenseGame(self.hub, self.width, self.height, self.soundController, self.fontController)
    
    def update(self):
        self.UI.update()
    
    def draw(self):   # draw
        if self.state != STATE.ButtonGame or self.state != STATE.FakeNews or self.state != STATE.DefenseGame: # Don't draw background if in game
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.backgroundImg2, (40,  self.height -  self.backgroundImg2.get_height() - 40))
            self.screen.blit(self.backgroundImg, (self.width - self.backgroundImg.get_width() - 40, self.height -  self.backgroundImg.get_height() - 40))
            
        
        self.UI.draw(self.screen) # Render UI or games
        pygame.display.flip()


    def handle_events(self, events):   # Handle events
        self.UI.handle_events(events)
    # TODO
    # Change to switch statments to have O(1)
    def changeScene(self):  #Changes the current scene (UI or Game)
        print("GOING FROM: ", self.prevState, " TO ", self.state)
        if self.state == STATE.Home:
            self.UI = self.HubUI
        if self.state == STATE.Lobby:
            self.UI = self.LobbyUI
        if self.state == STATE.SelectGame:
            self.UI = self.GameSelectionUI
        if self.state == STATE.JoinGame:
            if self.prevState == STATE.Home:
                if self.hub.isConnected:
                    self.setScene(STATE.CharacterCreation)
                else:
                    self.UI = self.JoinGameUI
            elif self.prevState == STATE.CharacterCreation:
                if self.hub.isConnected:

                    self.setScene(STATE.Home)
                else:
                    self.UI = self.JoinGameUI
        if self.state == STATE.CharacterCreation:
            if self.prevState == STATE.JoinGame: # If prev state was join game, go to lobby
                if self.hub.characterExists:
                    self.setScene(STATE.Lobby)
                else:
                    self.UI = self.CharacterCreationUI
            elif self.prevState == STATE.Lobby: # If prev state was lobby, go to join game
                if self.hub.characterExists:
                    self.setScene(STATE.JoinGame)
                else:
                    self.UI = self.CharacterCreationUI
            elif self.prevState == STATE.Home:  # If coming from home, means we skipped join game screen, go to lobby
                if self.hub.characterExists:
                    self.setScene(STATE.Lobby)
                else:
                    self.UI = self.CharacterCreationUI
            else:
                self.UI = self.CharacterCreationUI
        if self.state == STATE.Settings:
            self.UI = self.SettingsUI
        if self.state == STATE.Leaderboard:
            self.UI = self.LeaderboardUI
        if self.state == STATE.ButtonGame:
            self.UI = self.ButtonGame
        if self.state == STATE.FakeNews:
            self.UI = self.FakeNews
        if self.state == STATE.DefenseGame:
            self.UI = self.DefenseGame

    def setScene(self, STATE):    # Sets the current scene
        self.prevState = self.state
        self.state = STATE
        self.changeScene()


    def setFullScreen(self, fullScreen):
        if fullScreen:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF)
            self.initUI()
            self.initGames()
            self.initObjects()
            self.changeScene() # Reset current scene

        else:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.HWSURFACE)
            self.initUI()
            self.initGames()
            self.initObjects()
            self.changeScene() # Reset current scene

        self.fullScreen = fullScreen
        print("Fullscreen: ", self.fullScreen)


    def changeResolution(self, width, height):  # Changes resolution
        print("TRYING TO CHANGE RESOLUTION")
        self.width = width  
        self.height = height

        try:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE | pygame.HWSURFACE) # Make display resizable until resolution is changed
        except:
            print("COULD NOT CHANGE RESOLUTION")

        print("NEW SIZE: ", self.screen.get_size())
        # Reinitialize UI and games

        # Make display not resizable
        if self.fullScreen:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.HWSURFACE)
        

        
        self.initUI()
        self.initGames()
        self.initObjects()
        self.changeScene() # Reset current scene
