#Simple button class
# Very helpful: http://thepythongamebook.com/en:pygame:step003

import pygame, os
from objects.Button import Button

# TODO:
# Rename class

class Headings(pygame.Rect):
    def __init__(self, width, height, x, y, font, color, textColor, headings=[], bgColor = (255, 255, 255)):
        self.width = width
        self.height = height
        self.color = color
        self.textColor = textColor
        self.x = x
        self.y = y
        self.surface = pygame.Surface((self.width,self.height))  # create a surface for the button
        self.surface = self.surface.convert()
        self.surface.fill(bgColor)
        
        if(font == None):
            self.font = pygame.font.Font(os.path.join("resources", "Chicle.ttf"), 20,)
        else:
            self.font = font

        self.headings = headings
        self.headingsDisplay = self.createHeadings(self.headings)
        self.selectedHeading = None  # Currently selected heading

    # TODO
    # Ability to add only one heading
    def addHeadings(self, headings):
      self.headings = headings
      self.createHeadings(self.headings) # Recreate headings
  
    # Iterates tough headings and creates a new object with Heading and its size, position and returns it
    # Used to determine how to display the headings on surface (size of width and height)
    def createHeadings(self, headings = []):
        newDisplayHeadings = []
        X, Y = 0, 0
        if(len(headings) > 0):
          headingHeight = self.height / len(headings) - 10
          for h in headings:
            # Create heading 
            heading = Button(self.width, headingHeight, self.color, X, Y, h['heading'], font=self.font)
            # Create exactly the same object as self.headings, but with Heading object inside it
            tempHead = {'playerId': h['playerId'], 'headingId': h['headingId'], 'heading': heading}
            newDisplayHeadings.append(tempHead) # Append
            Y += headingHeight + 10 
        
        self.headingsDisplay = newDisplayHeadings
        return newDisplayHeadings

    # 
    def handle_events(self, events):
      for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1:
            pos = pygame.mouse.get_pos()
            self.resetHeadingColors()
            for h in self.headingsDisplay:
              if h['heading'].get_rect().collidepoint(pos[0] - self.x, pos[1] - self.y):
                h['heading'].setBgColor((0, 0, 0))  # Change its color once selected
                self.selectedHeading = h

    def setColor(self, color):
      self.color = color
    
    def resetHeadingColors(self):
      for h in self.headingsDisplay:
        h['heading'].setBgColor(self.color)

    def setHeadings(self, headings):
      self.headings = headings
      self.createHeadings(headings)

    def setPosCenter(self, screenWidth, y):
        self.x = screenWidth / 2 - self.surface.get_width() / 2
        self.y = y

    # Will return currently selected heading
    def getSelectedHeading(self):
      print("Selected: ", self.selectedHeading)
      # Since there are two headings objects, one for displaying and one with actual headings
      # Need to find actual heading and return it
      if self.selectedHeading != None: # If selected
        for h in self.headings:
          print("Heading: ", h)
          if(h['headingId'] == self.selectedHeading['headingId']):
            print("FOUND THE HEADING")
            return h
      else:
         return None

      print("HEADING NOT FOUND")
      raise Exception("NO SUCH HEADING! (this not suposed to happen)")
        
    def getColor(self):
        return self.color
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_middle_width(self):
        return self.width / 2

    def draw(self, screen):
        for h in self.headingsDisplay:
          h['heading'].draw(self.surface)
          screen.blit(self.surface, ( self.x, self.y))