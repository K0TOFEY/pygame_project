import pygame
import pytmx


class Level():
    pass


pygame.init()
size = width, height = 800, 608
screen = pygame.display.set_mode(size)


running = True
while running:
    # внутри игрового цикла ещё один цикл
    # приема и обработки сообщений
    for event in pygame.event.get():
        # при закрытии окна
        if event.type == pygame.QUIT:
            running = False

    # отрисовка и изменение свойств объектов
    # ...

    # обновление экрана
    pygame.display.flip()
pygame.quit()