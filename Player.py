import pygame
import sys


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__()
        self.position = (x, y)
        self.speed = (speed_x, speed_y)
        self.change_x = 0

    def update(self):
        self.position = (self.position[0] + self.speed[0], self.position[1] + self.speed[1])

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), self.position, 10)

    def move_left(self):
        self.speed = (-0.01, self.speed[1])

    def move_right(self):
        self.speed = (0.01, self.speed[1])

    def move_up(self):
        self.speed = (self.speed[0], -0.01)

    def move_down(self):
        self.speed = (self.speed[0], 0.01)


# Инициализация pygame
pygame.init()

# Размер окна
size = (640, 480)

# Создания окна
screen = pygame.display.set_mode(size)

# Создание спрайта игрока
player = Player(320, 240, 0, 0)

# Цикл действий
running = True
while running:
    # Перебор ивентов
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:  # если нажата кнопка
            if event.key == pygame.K_LEFT:  # кнопка стрелки влево
                player.move_left()
            elif event.key == pygame.K_RIGHT:  # кнопка стрелки вправо
                player.move_right()
            elif event.key == pygame.K_UP:
                player.move_up()
            elif event.key == pygame.K_DOWN:
                player.move_down()

    # Обновить спрайт персонажа
    player.update()

    # Сделать окно белым
    screen.fill((255, 255, 255))

    # Нарисовать спрайт игрока
    player.draw(screen)

    # Обновить кадр
    pygame.display.update()