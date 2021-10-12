from enum import Enum
# Read about enums https://docs.python.org/3/library/enum.html

class FN_STATE(Enum):
  HOME = "Home",
  INPUT = "Input",
  GUESS = "Guess",
  END = "End",
  GAMEOVER = "GG"
