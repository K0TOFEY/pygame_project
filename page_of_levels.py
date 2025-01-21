import pygame
import sys

def lvl_page(screen):
    clock = pygame.time.Clock()

    pygame.init()
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)

    # Фон
    bg = pygame.image.load("Фон 800х600.jpg")
    screen.blit(bg, (0, 0))

    # Buttons уровней
    level_1 = pygame.image.load("lvl1.png")
    level_2 = pygame.image.load("lvl2.png")
    level_3 = pygame.image.load("lvl3.png")
    back = pygame.image.load("back.png")

    # Rect_of_levels
    rect_level_1 = level_1.get_rect(topleft=(175, 250))
    rect_level_2 = level_2.get_rect(topleft=(360, 250))
    rect_level_3 = level_3.get_rect(topleft=(550, 250))
    rect_back = back.get_rect(topleft=(10, 45))

    # текст
    font = pygame.font.Font(None, 64)
    text = font.render("Выберите уровень", True, (255, 0, 0))
    text_x = 200
    text_y = 50

    # Рисование на холсте
    screen.blit(text, (text_x, text_y))
    screen.blit(level_1, rect_level_1)
    screen.blit(level_2, rect_level_2)
    screen.blit(level_3, rect_level_3)
    screen.blit(back, rect_back)

    # Смена кадра
    pygame.display.flip()

    # Цикл действий
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_back.collidepoint(event.pos):
                    pass # Функция нужного окна

        if rect_level_1.collidepoint(pygame.mouse.get_pos()):
            level_1 = pygame.image.load("cl_lvl1.png")
            screen.blit(level_1, rect_level_1)
        else:
            level_1 = pygame.image.load("lvl1.png")
            screen.blit(level_1, rect_level_1)

        if rect_level_2.collidepoint(pygame.mouse.get_pos()):
            level_2 = pygame.image.load("cl_lvl2.png")
            screen.blit(level_2, rect_level_2)
        else:
            level_2 = pygame.image.load("lvl2.png")
            screen.blit(level_2, rect_level_2)

        if rect_level_3.collidepoint(pygame.mouse.get_pos()):
            level_3 = pygame.image.load("cl_lvl3.png")
            screen.blit(level_3, rect_level_3)
        else:
            level_3 = pygame.image.load("lvl3.png")
            screen.blit(level_3, rect_level_3)

        if rect_back.collidepoint(pygame.mouse.get_pos()):
            back = pygame.image.load("cl_back.png")
            screen.blit(back, rect_back)
        else:
            back = pygame.image.load("back.png")
            screen.blit(back, rect_back)

        pygame.display.update()