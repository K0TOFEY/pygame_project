import pygame


def main():
    screen = pygame.display.set_mode((640, 480))
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    input_box = pygame.Rect(100, 100, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        print(text)
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 10:
                            text += event.unicode

        screen.fill((30, 30, 30))
        # Render the current text.
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long.
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()




# def login(screen):
#     global current_music  # Используем глобальную переменную для отслеживания текущей музыки
#
#     bg = pygame.image.load(BACKGROUND_FOR_LOGIN)  # Загружаем изображение фона для логина
#     screen.blit(bg, (0, 0))  # Отображаем фон на экране
#
#     # Кнопка
#     back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"
#     rect_back = back.get_rect(topleft=(10, 45))
#     screen.blit(back, rect_back)  # Отображаем кнопку "Назад" на экране
#
#     # текст
#     font = pygame.font.Font(None, 52)
#     text = font.render("Авторизация", True, (255, 255, 255))
#     text_x = 400 - text.get_width() // 2
#     text_y = 70
#     screen.blit(text, (text_x, text_y))
#
#     running = True
#     while running:
#         clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS
#         for event in pygame.event.get():  # Обрабатываем события
#             if event.type == pygame.QUIT:  # Если пользователь закрыл окно
#                 pygame.quit()
#                 sys.exit()
#
#             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                 if rect_back.collidepoint(event.pos):
#                     SOUND_ON_BUTTON.play()
#                     main_menu(screen)
#
#         contour(screen, rect_back, 'Buttons/cl_back.png',
#                 'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
#
#         pygame.display.update()
#
#         # Проверяем, закончилась ли музыка, и если да, то включаем следующую
#     if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
#         play_random_music()  # Запускаем случайный трек из списка