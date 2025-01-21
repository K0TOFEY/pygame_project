import pygame


def contour(screen, rect, first_file, second_file):
    if rect.collidepoint(pygame.mouse.get_pos()):
        btn = pygame.image.load(f"{first_file}")
        screen.blit(btn, rect)
    else:
        btn = pygame.image.load(f"{second_file}")
        screen.blit(btn, rect)