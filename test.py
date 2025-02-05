import pygame
import sys

WIDTH = 800
HEIGHT = 600
BACKGROUND = 'black'


class Sprite(pygame.sprite.Sprite):  # Всё для спрайтов
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Sprite):  # Для персонажа
    def __init__(self, startx, starty):
        super().__init__("Froggo/Animation/frog.png", startx, starty)
        self.stand_image = self.image

        self.walk_cycle = [pygame.image.load(f"Froggo/Animation/walk_animation{i}.png") for i in range(1, 9)]
        self.animation_index = 0
        self.facing_left = False

        self.speed = 4
        self.jump_speed = 20
        self.vsp = 0  # Вертикальная скорость
        self.gravity = 1

    def update(self, boxes):
        hsp = 0  # Горизонтальная скорость
        on_ground = pygame.sprite.spritecollideany(self, boxes)

        # Проверка нажатия кнопки
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.facing_left = False
            self.walk_animation()
            hsp = -self.speed
        elif key[pygame.K_RIGHT]:
            self.facing_left = True
            self.walk_animation()
            hsp = self.speed
        else:
            self.image = self.stand_image

        if key[pygame.K_UP] and on_ground:
            self.vsp = -self.jump_speed

        # Гравитация
        if self.vsp < 10 and not on_ground:
            self.vsp += self.gravity

        if self.vsp > 0 and on_ground:
            self.vsp = 0

        self.move(hsp, self.vsp)

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle) - 1:
            self.animation_index += 1
        else:
            self.animation_index = 0


class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("Sprites/brick_1.png", startx, starty)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player(100, 200)

    boxes = pygame.sprite.Group()
    for bx in range(0, 800, 32):
        boxes.add(Box(bx, 600))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

        pygame.event.pump()
        player.update(boxes)

        # Рисуем
        screen.fill(BACKGROUND)
        player.draw(screen)
        boxes.draw(screen)

        # Обновляем
        pygame.display.flip()




if __name__ == "__main__":
    main()