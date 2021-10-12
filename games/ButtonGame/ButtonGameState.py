# All Button game data
class ButtonGameState:
    def __init__(self):
        self.timeLeft = 10
        self.buttonOneColor = (0,0,0)
        self.buttonTwoColor = (0,0,0)
        self.buttonThreeColor = (0,0,0)
        self.buttonColorName = 'Black'
        self.isRoundRunning = False
        self.roundLength = 10 #TODO
        self.start = 0
        self.round = 0 #TODO

    def reset(self):
        self.timeLeft = 10
        self.isRunning = False
        self.start = 0
