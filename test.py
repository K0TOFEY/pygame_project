import pygame as pg


def main():
    screen = pg.display.set_mode((800, 600))
    font = pg.font.Font(None, 52)
    clock = pg.time.Clock()
    input_box = pg.Rect(200, 100, 140, 52)
    color_inactive = pg.Color('lightskyblue3') # неактивный
    color_active = pg.Color('dodgerblue2') # активный
    color = color_inactive
    active = False
    text = ''
    running = False

    while not running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = True
            if event.type == pg.MOUSEBUTTONDOWN: # Если пользователь нажал на прямоугольник input_box
                if input_box.collidepoint(event.pos): # Переключите активную переменную.
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive # Измените текущий цвет поля ввода.
            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        print(text)
                        text = ''
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        # Отобразите текущий текст.
        txt_surface = font.render(text, True, color)
        # Измените размер поля, если текст слишком длинный.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Увеличьте текст.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Выделите прямоугольник input_box.
        pg.draw.rect(screen, color, input_box, 2)

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()