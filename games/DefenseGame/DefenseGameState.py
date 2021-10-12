import pygame
from Player import Player
from games.DefenseGame.DG_STATE import DG_STATE
import base64

class DefenseGameState():
  def __init__(self, *args, **kwargs):
    # pygame.init()
    self.players = []
    self.round = 0
    self.state = DG_STATE.Home


  # Looks for which player was hit and removes dmg from hp
  def playerHit(self, id, dmg):
    print("Player hit")
    for p in self.players:
      if p.id == id:
        p.hp -= dmg

  # Update player position
  # TODO
  # VERY SLOW!
  def playerMove(self, data):
    for p in self.players:
      if p.id == data['id']:
        p.pos[0] = data['x']
        p.pos[1] = data['x']
        break
  
  # Checks if player does not exist and
  # Initializes player
  def initPlayer(self, data):
    #print("Creating new player: ", data)
    willInsert = True
    for p in self.players:
      if p.id == data['id']:
        willInsert = False
        print("Just update the player")
        p.updateFromDict(p)
    if willInsert: 
      print("Will add it to the list...")

      self.players.append(Player(data['id'], 0, 0, 200, 200, 1000, data['playerColor'], data['playerName'], image=data['playerIMG']))

  # Returns all players
  def getPlayers(self):
    players = []
    for p in self.players:
      players.append(p.toDict())

    #print("Sending players: ", players)
    return players

  # Deletes player from player list
  def deletePlayer(self, id):
    self.players = [p for p in self.players if p.id != id]
    print("Players after deletion: ", self.players)
