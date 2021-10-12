# TODO:
# Have players representation in here so it is possible to count score
from games.FakeNews.FN_STATE import FN_STATE
from pathlib import Path
import json
import random
class FakeNewsState:
    def __init__(self):
        self.inputTimeLeft = 10
        self.guessTimeLeft = 5
        self.start = 0
        self.round = 1 #TODO
        self.state = FN_STATE.HOME #Default state
        self.headings = []
        self.headingId = 0 # For assigning id

        # True headings
        trueHeadingsJson = open( str(Path("resources/Game Data/FakeNews_TrueHeadings.json")), "r")
        trueHeadingsJson = trueHeadingsJson.read()
        self.trueHeadings = json.loads(trueHeadingsJson)

        self.trueHeading = random.choice(self.trueHeadings)
        self.trueHeadingTitle = self.trueHeading["Title"]
        
        self.trueHeadingCategory = self.trueHeading["Category"]
        self.trueHeadings.remove(self.trueHeading) # remove the heading from the list after its used
        self.addCorrectHeading(self.trueHeadingTitle) # Adds correct heading to the heading pool
        self.playerSelections = []
    
    def nextHeadingId(self):
        self.headingId+=1
        return self.headingId
    
    def nextRound(self):
        self.round += 1
        return self.round

    # Adds correct heading to the heading pool
    # -1 helps to determine which heading is correct
    # TODO
    # What if we add more correct headings?
    def addCorrectHeading(self, heading):
        self.headings.append({'playerId': -1, 'headingId': -1, 'heading': heading})

    def reset(self):
        self.headings = []
        self.headingId = 0 # For assigning id
        self.trueHeading = random.choice(self.trueHeadings)
        self.trueHeadingTitle = self.trueHeading["Title"]
        self.trueHeadingCategory = self.trueHeading["Category"]
        self.trueHeadings.remove(self.trueHeading) # remove the heading from the list after its used
        self.addCorrectHeading(self.trueHeadingTitle)
        self.playerSelections = []
        self.inputTimeLeft = 10
        self.guessTimeLeft = 5
        self.start = 0
        self.state = FN_STATE.HOME  


    def addPlayerSelection(self, selection):
        print('ADDING PLAYER SELECTION: ', selection)
        if(len(self.playerSelections)) > 0:
          for i in range(len(self.playerSelections)):
            if(self.playerSelections[i]['playerId'] == selection['playerId']):
              self.playerSelections[i] = selection
        else:
          self.playerSelections.append(selection)

    def addHeading(self, heading, playerId):
        newHeading = {"playerId": playerId, "headingId": self.nextHeadingId(), 'heading': heading}
        willInsert = True
        # If there is heading already...
        if len(self.headings) > 1:
          # Iterate trough them
          for i in range(len(self.headings)):
            # If new heading matches already existent one - REPLACE
            if self.headings[i]['playerId'] == playerId:
              print("Replacing heading")
              self.headings[i] = newHeading
              willInsert = False
        
        # Insert new one otherwise
        if willInsert:
          self.headings.append(newHeading)

    def getWinners(self):
        winners = []    # Array of player ids
        print("GETTING WINNERS: ", self.playerSelections)
        print("ps.values")
        for ps in self.playerSelections:
            # print('ps:', ps.values())
            if ps['heading']['headingId'] == -1:
                print(ps, "picked correctly")
                winners.append(ps['playerId'])
        return winners

    def setState(self, state):
        print("SETTING STATE FOR FN")
        self.state = state
        self.start = 0 # Reset the timer

