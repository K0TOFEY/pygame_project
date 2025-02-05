import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super.__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self):
        screen.blit