import pygame
from PodSixNet.Connection import connection, ConnectionListener
from objects.Button import Button
from time import sleep
from STATE import STATE
import sys, os
from objects.Text import Text
from resources.hubColours import ColoursClass
from pathlib import Path
from objects.Bullet import Bullet
from games.DefenseGame.DG_STATE import DG_STATE
from Player import Player
import math
import base64

# https://pastebin.com/KPRHmHv8
class DefenseGame(ConnectionListener):
    def __init__(self, hub, width, height, soundController, fontController, fps=60):
        #Hub
        self.hub = hub
       
        #COLOURS
        self.color = ColoursClass("alt")

        #SOUNDS
        self.soundController = soundController

        #SCREEN
        self.width = width
        self.height = height
        self.background = pygame.Surface((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF).convert()  
        self.background.fill(self.color.getColour(7)) # fill background white

        #INFO
        self.fps = fps
        self.playtime = 0.0

        self.HP = 1000
        self.state = DG_STATE.Home

        self.frameCount = 0

        #FONTS
        self.fontController = fontController
        
        #STATE
        self.isRunning = True
        self.isShooting = False
        self.isBoostOn = False
        # Movement  
        self.moveLeft = False
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False
        self.lastDirection = "none"
        self.smoothAmount = 3.0

        # Object groups
        self.bullets = pygame.sprite.Group()
        self.players = pygame.sprite.Group()

        # Stats
        self.bulletSpeed = 10 # Should live elswhere (mb player class)
        self.shotingSpeed = 1 # Should live elswhere        
        self.playerSpeed = 5 # Should live elswhere
        self.playerBoost = 1
        self.playerBoostAmnt = 1.5
        # self.timeLeft = "Waiting for players..."
        self.clock = pygame.time.Clock()

        self.on_init()
        self.updateScore()
  
    # TODO:
    # USE CHARACTER IMAGES
    #Initialize game objects
    def on_init(self):
      self.hpTxt = Text("", self.color.getColour(8), 10, 60, self.fontController.medium, True)
      self.player = Player(self.hub.playerId, 0, self.height - 50, 50, 50, 1000, self.hub.playerColor)
      self.playerBulletSprite = pygame.image.load(str(Path("resources/Images/bullet.png"))).convert_alpha()
      # print("Created my player")
      self.readyButton = Button(200, 50,  self.color.getColour(4), text='IM READY', font=self.fontController.small)
      self.readyButton.setPosCenter(self.width, self.height - 100)

    # Checks if player exists and creates if no
    def createPlayer(self, data):
      willInsert = True
      isOwner = False
      #print("WANT TO CREATE PLAYER: ", data)
      # self.player = Player(self.hub.playerId,0, self.height - 50, 50, 50, 1000, self.hub.playerColor)
      for p in self.players:
        if p.id == data['id']:
          willInsert = False
      
      if willInsert:
        id = data['id']

        if id == self.hub.playerId:
          print("ADDED OWNER")
          isOwner = True

        # Just update the info if clients player exists
        if isOwner:
          print("OWNER: ", id)
          self.player.id = id
          self.player.pos[0] = data['x']
          self.player.pos[1] = data['y']
          #self.player.setPlayerColor(data['playerColor'])
          self.player.playerName = data['playerName']
          self.player.image = base64.b64decode( data['playerIMG'] )
          self.player.image = pygame.image.frombuffer(self.player.image, (200, 200), "RGB")
          self.player.image = pygame.transform.smoothscale(self.player.image, (50, 50))
          self.players.add(self.player)
        #self.player = Player(self.hub.playerId, 0, self.height - 50, 50, 50, 1000, self.hub.playerColor)
        else:
          print("Player created! ID: ", id)
          image = base64.b64decode( data['playerIMG'] )
          image = pygame.image.frombuffer(image, (200, 200), "RGB")
          image = pygame.transform.smoothscale(image, (50, 50))

          self.players.add(Player(id, data['x'],  data['y'], 50, 50,  data['hp'],  data['playerColor'], image=image, playerName=data['playerName']))

    def initRound(self):
      self.updateScore()

    # Draws on screen
    def draw(self, screen):                               # Update all objects (through object handler)                                            # This will update the contents of the entire display
        screen.blit(self.background, (0, 0))
        self.drawInfoText("Color: " + self.hub.playerColorName, 10, 10, self.fontController.tiny, screen)
        self.drawInfoText("Player Count: " + str(self.hub.getInGamePlayerCount()), 10, 20, self.fontController.tiny, screen)
        self.drawInfoText("FPS: " + str(round(self.getFPS(), 2)), 10, 30, self.fontController.tiny, screen)
        self.drawInfoText("Network Status: " + self.hub.statusLabel, 10, 40, self.fontController.tiny, screen)
        self.drawInfoText("Is Host: " + str(self.hub.isHost), 10, 50, self.fontController.tiny, screen)
        
        if self.state == DG_STATE.Home:
          self.readyButton.draw(screen)
        if self.state == DG_STATE.Play:
          self.hpTxt.draw(screen)
          self.bullets.draw(screen)
          self.players.draw(screen)
          self.frameCount = self.frameCount + 1

          

    # Sends player position to server
    def onMove(self):
      connection.Send({"action": "playerMove", 'x': self.player.pos[0] , 'y': self.player.pos[1], 'id': self.hub.playerId})

    # creates bullet object, puts it into array
    # determines the velocity needed to hit the target
    # launches it and notifies the server about it!
    def shoot(self):
      # https://stackoverflow.com/questions/55008954/calculate-x-and-y-velocity-to-hit-the-target-on-flat-2d-surface-in-pygame
      if self.frameCount%3 == 0:
        posX, posY = pygame.mouse.get_pos()

        traget = pygame.math.Vector2(posX, posY)
        start  = pygame.math.Vector2(self.player.pos[0], self.player.pos[1])

        delta = traget - start
        distance = delta.length() 
        try:
          direction = delta.normalize()
          vel = direction * self.bulletSpeed
          self.bullets.add(Bullet(self.hub.playerId,self.player.pos[0], self.player.pos[1], 10, 10, vel[0], vel[1], self.playerBulletSprite)) # add bullet to array
          self.sendShot(self.player.pos[0], self.player.pos[1], vel[0], vel[1])# Sends shot event to server
        except ValueError:
          print("Avoided divide by zero error when shooting.")


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
                if event.key == pygame.K_SPACE:
                  for p in self.players:
                    print("PLAYER: ", p)
                  print("self.player: ", self.player)
                  print("My id: ", self.hub.playerId)
                
                if event.key == pygame.K_LSHIFT:
                  self.isBoostOn = True
               
                # Move if key down
                if event.key == pygame.K_w:
                  self.lastDirection = "none"
                  self.moveUp = True
                if event.key == pygame.K_a:
                  self.lastDirection = "none"
                  self.moveLeft = True
                if event.key == pygame.K_s:
                  self.lastDirection = "none"
                  self.moveDown = True
                if event.key == pygame.K_d:
                  self.lastDirection = "none"
                  self.moveRight = True

            # Stop moving if not pressing WASD
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                  self.moveUp = False
                  self.lastDirection = "up"
                  self.smoothMove(events)
                if event.key == pygame.K_a:
                  self.moveLeft = False
                  self.lastDirection = "left"
                  self.smoothMove(events)
                if event.key == pygame.K_s:
                  self.moveDown = False
                  self.lastDirection = "down"
                  self.smoothMove(events)
                if event.key == pygame.K_d:
                  self.moveRight = False
                  self.lastDirection = "right"
                  self.smoothMove(events)

                #Boost
                if event.key == pygame.K_LSHIFT:
                  self.isBoostOn = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:          # Mouse first button
                  
                  if self.state == DG_STATE.Home:
                    if self.readyButton.get_rect().collidepoint(pygame.mouse.get_pos()):
                      self.initRound()
                      self.state = DG_STATE.Play
                      self.soundController.playButtonClick()

                  if self.state == DG_STATE.Play:
                    self.isShooting = True
            elif event.type == pygame.MOUSEBUTTONUP:
              if event.button == 1:
                self.isShooting = False

    def smoothMove(self, events):
      #maybe have a target destination and move slowly to it?
      if self.lastDirection == "up":
        self.lastDirection = "none"
      #   tempSmoothAmount = self.smoothAmount
      #   for i in range(1,100):
      #     for event in events:
      #       if event.type == pygame.KEYDOWN:
      #         break
      #     self.player.pos[1] -= tempSmoothAmount
      #     tempSmoothAmount = math.log(tempSmoothAmount)
      #     self.onMove()

    # Update stuff (loop)
    def update(self):
        self.Pump()                 # Connection
        connection.Pump()           # Connection
        self.bullets.update()
        self.players.update()

        if self.isShooting:
          self.shoot()

        self.detectCollisions(self.bullets, self.players) # looks for collisions with bullets and players
        
        if self.isBoostOn:
            self.playerBoost = self.playerBoostAmnt
        else:
          self.playerBoost = 1

        if self.moveLeft:
          self.player.pos[0] -= self.playerSpeed * self.playerBoost
          self.onMove()
        if self.moveRight:
          self.player.pos[0] += self.playerSpeed * self.playerBoost
          self.onMove()
        if self.moveUp:
          self.player.pos[1] -= self.playerSpeed * self.playerBoost
          self.onMove()
        if self.moveDown:
          self.player.pos[1] += self.playerSpeed * self.playerBoost
          self.onMove()

        # sleep(0.001)

    def resetGame(self):
        self.HP = 1000
        self.state = DG_STATE.Home
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False
        self.player.isInGame = True
        self.bullets = pygame.sprite.RenderUpdates()
        self.bulletSpeed = 10 # Should live elswhere
        self.shotingSpeed = 1 # Should live elswhere
        self.isShooting = False
        self.players = pygame.sprite.RenderUpdates()
        self.playerSpeed = 5 # Should live elswhere


    # Looks for collision between the players and bullets
    # If player hits himself, we do nothing
    # If player hit other player - destroy the bullet
    #   If that player who shot was THIS player - tell the server, so it lets know every other client
    def detectCollisions(self, bullets, players):
      if len(bullets) > 0:
        playersHit = pygame.sprite.groupcollide(bullets, players, False, False)
        for b in playersHit:  # b is the bullets that hit something
          for p in playersHit[b]: # p is the player who was hit
            if p.id == b.ownerId: # print("Hit self")
              pass
            else:  # print("Other was hit")
              b.kill()
              if b.ownerId == self.player.id:  # print("I HIT!")
                self.sendPlayerHit(p.id)


    # Updates the score
    def updateScore(self):
        scrTxt = ""
        self.hpTxt.setText(scrTxt)
        for p in self.players:
          scrTxt += str(p.playerName) + " HP: " + str(p.hp) + '\n'

        self.hpTxt.setText(scrTxt)

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
        connection.Send({"action":"defenseGame_exitGame", "isInGame": False, 'id': self.hub.playerId})
        self.resetGame()
        self.hub.isInGame = False

  
    ######### NETWORK METHODS ########
    ### SENDS TO SERVER ###

    # Send location and velocity of the bullet to the server
    # So it can be created in other clients
    def sendShot(self, x, y, velX, velY):
      # print("SENDING SHOT: ", x, y, velX, velY, color)
      connection.Send({"action":"defenseGame_shot", "id": self.hub.playerId, "x":x, "y":y, "velX":velX, "velY":velY})

    # Send to server which player was hit by the owner player
    def sendPlayerHit(self, otherId, dmg = 1):
      # print("SENDING PLAYER HIT")
      connection.Send({'action':'defenseGame_playerHit', 'id': self.hub.playerId, 'otherId': otherId, 'dmg': dmg})
    
    
    
    ### RECEIVES FROM SERVER ###

    # Substracts hp from player which was hit
    def Network_defenseGame_playerHit(self, data):
      print("Player was hit", data)
      # Decrement hp
      for p in self.players:
        if p.id == data['otherId']:
          p.hp -= data['dmg']
  
      self.updateScore()

    # Receives who launched the bullet, then creates one and sets velocity
    def Network_defenseGame_shot(self, data):
      # print("player shot: ", data)
      if data['id'] != self.hub.playerId:
        self.bullets.add(Bullet(data['id'], data['x'], data['y'], 10, 10, data['velX'], data['velY'], self.playerBulletSprite))

    # Update player position received from server
    def Network_playerMove(self, data):
      # print("PLAYER MOVE", data)
      for p in self.players:
        if p.id == data['id'] and self.hub.playerId != data['id']: # Check withs object has moved
          p.pos[0] = data['x']
          p.pos[1] = data['y']
          break

    # Catches player join events and udates current player list inside hub
    def Network_players(self, data):
      self.hub.players = data['players']  # Send players to the hub self.hub.players
      self.updateScore()

    # Deletes player from client (received from server)
    def Network_playerDelete(self, data):
      print("Deleting player: ", data)
      self.deletePlayer(data)
      self.updateScore()

    # Receives players from the server
    # Will update players on join
    def Network_defenseGamePlayers(self, data):
      #print("Players update: ", data)
      for p in self.players:
        for p2 in data['players']:
          if p2['id'] == p.id:
            # p.pos[0] = p2['x']
            # p.pos[1] = p2['y']
            p.hp = p2['hp']
            p.playerColor = p2['playerColor']
            p.playerName = p2['playerName']

      # Create new player if missing
      if len(data['players']) > len(self.players): # If there are more players on the server
        for p in data['players']:
          self.createPlayer(p)
      else:
        print("Player will be deleted")
         # it means that player will be deleted trough Network_playerDelete(self, data)
      self.updateScore()

    # Deletes player from player list
    def deletePlayer(self, data):
      willDelete = True
      print("Deleting PLAYER: ", data)
      
      # Search for player
      for p in self.players:
        if data['id'] == p.id and not data['isInGame']: # If player exists, dont delete
          print("Player deleted from client id: ", p.id)
          p.kill()
  
      # if willDelete:
      #   print("Player deleted from client id: ", p.id)
      #   p.kill()

      # willDelete = True        
      self.updateScore()

    # Catches network events and updates timer
    def Network_timer(self, data):
        pass
        # self.timeLeft = data['time']
        # self.timerText.setText(data['time'])
        # self.timerText.setPosCenter(self.hub.width, 50)
        # if self.timeLeft == 5:
        #     self.soundController.playCountdown()
        # #print("TICK: ", self.timeLeft)
    
    # Catches endround events (when the timer ends server fires one)
    def Network_endRound(self, data):
        pass
        # self.resetGame()

    # Used when player joins in the middle to know the state of the game
    def Network_currentState(self, data):
        pass

    # Sets initial/current state of the game once client joins to the server
    # def Network_initial(self, data):
    #     print("INITIAL:", data)
    #     self.hub.isInGame = True                    
    #     self.hub.isConnected = True
    #     self.hub.playerId = data['id']
    #     self.players[0]['id'] = data['id'] # Set self id to server asigned (player is already created)
    #     print("INITIAL PLAYERS: ", self.players)
    #     # self.gameButton.setBgColor(data['currentColor'])            # Set current button color



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

