import sys
import pygame

from pytmx.util_pygame import load_pygame

pygame.init()
screen = pygame.display.set_mode((800, 608))

tmx_data = load_pygame('Tiledmap/tmx/test_map.tmx')
print(tmx_data)
print(tmx_data.layers)  # Все слои

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        screen.fill('black')
        pygame.display.update()

