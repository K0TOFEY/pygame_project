import pygame
import pytmx
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))


def level1(screen):
    screen.fill("black")

    tmx_data = pytmx.load_pygame('Map/level_1.tmx')

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

        pygame.display.flip()
#
#
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()
#
#     pygame.display.update()