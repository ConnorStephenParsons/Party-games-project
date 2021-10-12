import pygame
import math
class Bullet(pygame.sprite.Sprite):
  def __init__(self, ownerId, x, y, width, height, velX, velY, bulleSprite):
      pygame.sprite.Sprite.__init__(self)
      self.ownerId = ownerId
      self.width = width
      self.height = height
      self.x = x
      self.y = y
      self.image = bulleSprite
      # self.rect = self.image.get_rect()
      self.pos = pygame.math.Vector2(pygame.Rect(self.x, self.y, self.width, self.height).center)
      self.rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
      self.vel = pygame.math.Vector2(velX, velY)
      self.willBeDeleted = False
      self.life = 100 # How long the bullet will live 1 = 1 tick
  # def draw(self, screen):
  #     pygame.draw.rect(screen, self.color, self.bullet)

  def update(self):
    # print(self.pos)
    self.rect.center = (int(self.pos[0]), int(self.pos[1]))
    self.pos = self.pos + self.vel
    self.life -= 1

    if self.life < 0:
      self.willBeDeleted = True

    if self.willBeDeleted:
      self.kill()

  def get_rect(self):
    return self.rect