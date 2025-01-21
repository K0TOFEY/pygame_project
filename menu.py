import pygame
import sys

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
                    pass # Функция нужного окна

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if qt_btn_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # Наводка на кнопку
        if st_btn_rect.collidepoint(pygame.mouse.get_pos()):
            st_btn = pygame.image.load("click_start_btn.png")
            screen.blit(st_btn, st_btn_rect)
        else:
            st_btn = pygame.image.load("start_btn.png")
            screen.blit(st_btn, st_btn_rect)

        if qt_btn_rect.collidepoint(pygame.mouse.get_pos()):
            qt_btn = pygame.image.load("click_qt_btn.png")
            screen.blit(qt_btn, qt_btn_rect)
        else:
            qt_btn = pygame.image.load("quit_btn.png")
            screen.blit(qt_btn, qt_btn_rect)

        pygame.display.update()