import pygame
import sys

from contour_guidance import contour

def main_menu(screen):
    clock = pygame.time.Clock()
    st_btn = pygame.image.load("start_btn.png")
    qt_btn = pygame.image.load("quit_btn.png")

    # Фон
    bg = pygame.image.load("Фон 800х600.jpg")
    screen.blit(bg, (0, 0))

    # Кнопки
    st_btn_rect = st_btn.get_rect(topleft=(275, 250))
    qt_btn_rect = qt_btn.get_rect(topleft=(275, 350))

    # Работа над текстом
    text_surf = pygame.Surface((350, 25))
    font = pygame.font.Font(None, 64)
    text = font.render("Название игры такое-то", True, (255, 0, 0))
    text_x = 125
    text_y = 50

    # рисование на холсте
    screen.blit(text, (text_x, text_y))
    screen.blit(st_btn, st_btn_rect)
    screen.blit(qt_btn, qt_btn_rect)
    # смена (отрисовка) кадра:
    pygame.display.flip()

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if st_btn_rect.collidepoint(event.pos):
                    lvl_page(screen)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if qt_btn_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # Наводка на кнопку
        contour(screen, st_btn_rect, 'click_start_btn.png', 'start_btn.png') # кнопка старт

        contour(screen, qt_btn_rect, 'click_qt_btn.png', 'quit_btn.png') # кнопка выйти

        pygame.display.update()

def lvl_page(screen):
    bg = pygame.image.load("Фон 800х600.jpg")
    screen.blit(bg, (0, 0))

    # Кнопки уровней
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
                    main_menu(screen)

        # Наводка на кнопки
        contour(screen, rect_level_1, 'cl_lvl1.png', 'lvl1.png') # Кнопка уровня 1

        contour(screen, rect_level_2, 'cl_lvl2.png', 'lvl2.png') # Кнопка уровня 2

        contour(screen, rect_level_3, 'cl_lvl3.png', 'lvl3.png') # Кнопка уровня 3

        contour(screen, rect_back, 'cl_back.png', 'back.png') # Кнопка назад

        pygame.display.update()

clock = pygame.time.Clock()

# Создание окна
pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)

# Меню игры
main_menu(screen)

# завершение работы:
pygame.quit()