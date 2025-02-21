import pygame
import sys
import pytmx
import time

WIDTH = 800
HEIGHT = 608
BACKGROUND = 'black'
DEATH_ANIMATION_DURATION = 1  # Длительность анимации смерти в секундах
DEATH_FRAMES = 8  # Кол-во кадров смерти
COIN_ANIMATION_SPEED = 0.2  # Скорость анимации монет


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Frog(Sprite):
    def __init__(self, startx, starty, brick_group, spike_group, coin_group):  # Принимаем coin_group
        super().__init__("Froggo/Animation/frog.png", startx, starty)
        self.stand_image = self.image
        self.jump_image = pygame.image.load('Froggo/Animation/jump.png')

        self.walk_cycle = [pygame.image.load(f"Froggo/Animation/walk_animation{i}.png") for i in range(1, 9)]
        self.dead_cycle = [pygame.image.load(f"Froggo/Animation/dead_animation{i}.png") for i in range(1, 9)]
        self.animation_index = 0
        self.facing_left = False

        self.speed = 4
        self.jump_speed = -20  # Изменили знак, чтобы прыжок был вверх
        self.vsp = 0  # Вертикальная скорость
        self.gravity = 1  # Уменьшили гравитацию

        self.onground = False

        self.min_jumpspeed = 3
        self.prev_key = pygame.key.get_pressed()
        self.map = None  # Добавлено поле для хранения ссылки на карту
        self.brick_group = brick_group  # Спрайт группа кирпичей
        self.spike_group = spike_group  # Сохраняем ссылку на группу шипов
        self.coin_group = coin_group # Сохраняем группу монет
        self.is_jumping = False
        self.dying = False  # Флаг, показывающий, что началась анимация смерти
        self.death_start_time = 0  # Время начала анимации смерти
        self.death_animation_index = 0  # Индекс текущего кадра анимации смерти
        self.death_frame_duration = DEATH_ANIMATION_DURATION / DEATH_FRAMES  # Длительность одного кадра анимации смерти
        self.last_death_frame_time = 0  # Время отображения последнего кадра анимации смерти

    def update(self):
        if self.dying:
            self.death_animation()
            return  # Прекращаем нормальное обновление

        hsp = 0  # Горизонтальная скорость

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

        # Прыжок
        if key[pygame.K_UP] and self.onground:  # Прыгаем, только если на земле
            self.vsp = self.jump_speed
            self.onground = False  # Сбрасываем флаг, так как игрок прыгнул

        if self.vsp < 10 and not self.onground:
            self.jump_animation()
        # Гравитация
        self.vsp += self.gravity

        # Ограничение скорости падения
        if self.vsp > 10:
            self.vsp = 10
        # Движение
        self.move(hsp, self.vsp)

        # Анимация прыжка
        if self.is_jumping and not self.onground:  # Если прыгаем, то проигрываем анимацию падения
            self.jump_animation()

    def move(self, x, y):
        # Горизонтальное движение
        self.rect.x += x

        # Проверка столкновений по X с кирпичами
        for brick in self.brick_group:
            if self.rect.colliderect(brick.rect):
                if x > 0:  # Движемся вправо
                    self.rect.right = brick.rect.left  # Прижимаемся к левой стороне кирпича
                    x = 0  # убираем движение, если столкнулись
                elif x < 0:  # Движемся влево
                    self.rect.left = brick.rect.right  # Прижимаемся к правой стороне кирпича
                    x = 0  # убираем движение, если столкнулись

        # Вертикальное движение
        self.rect.y += y

        # Проверка столкновений по Y с кирпичами
        self.onground = False  # Считаем, что не на земле, пока не докажем обратное
        for brick in self.brick_group:
            if self.rect.colliderect(brick.rect):
                if y > 0:  # Падаем вниз
                    self.rect.bottom = brick.rect.top  # Прижимаемся к верхней стороне кирпича
                    self.vsp = 0  # Обнуляем вертикальную скорость
                    self.onground = True  # Мы на земле!
                elif y < 0:  # Прыгаем вверх
                    self.rect.top = brick.rect.bottom  # Прижимаемся к нижней стороне кирпича
                    self.vsp = 0  # Гасим скорость
                    y = 0  # Убираем движение, если столкнулись

        # Проверка столкновений с шипами
        for spike in self.spike_group:
            if self.rect.colliderect(spike.rect):
                self.spike_collision()  # Вызываем метод столкновения с шипами
    # Проверка столкновений с монетами

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle) - 1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def death_animation(self):
        if self.dying:
            current_time = time.time()
            time_since_death = current_time - self.death_start_time

            if time_since_death < DEATH_ANIMATION_DURATION:
                frame_duration = DEATH_ANIMATION_DURATION / 8  # 8 кадров в анимации
                frame_index = int(time_since_death / frame_duration)
                if frame_index < 8:
                    self.image = self.dead_cycle[frame_index] # Передаём кадр из dead_cycle
            else:
                self.dying = False # Окончили проигрывание
                self.reset() # Перезагружаем уровень

    def on_ground(self):
        return self.onground

    def spike_collision(self):
        if not self.dying:  # Если анимация смерти еще не началась
            self.dying = True  # Начинаем анимацию смерти
            self.death_start_time = time.time()  # Запоминаем время начала
            print("Персонаж умер!") # Выводим сообщение в консоль

    def reset(self):
        for obj in self.map.tmx_data.objects:
            if obj.name == "Player":
                self.rect.x = obj.x
                self.rect.y = obj.y
                break
        self.image = self.stand_image  # Возвращаем обычную картинку
        self.dying = False  # Сбрасываем флаг
        self.vsp = 0
        self.death_animation_index = 0


class Brick(pygame.sprite.Sprite): # Класс для кирпичей
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/brick_1.png')  # Загружаем текстуру
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Spike(pygame.sprite.Sprite):  # Класс для шипов
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/spike.png')  # Загружаем текстуру шипа
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Money(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('Money/money_animation1.png')  # Загружаем текстуру Монеты
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.coin_cycle = [pygame.image.load(f"Money/money_animation{i}.png") for i in range(1, 6)]
        self.animation_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 100 # 100 ms между кадрами

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_cooldown:
            self.last_update = now
            self.animation_index = (self.animation_index + 1) % len(self.coin_cycle)
            self.image = self.coin_cycle[self.animation_index]


class Map():
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.layers = self.tmx_data.layers
        self.brick_group = pygame.sprite.Group()  #  Группа спрайтов для кирпичей
        self.spike_group = pygame.sprite.Group()  #  Группа спрайтов для шипов
        self.coin_group = pygame.sprite.Group()  #  Группа спрайтов для монет
        self.all_sprites = pygame.sprite.Group()
        self.collision_layer = self.tmx_data.get_layer_by_name('Tiles')  # или другое имя слоя с коллизиями
        self.map_image = self.make_map()  # Создаем единое изображение карты
        self.rect = self.map_image.get_rect()
        self.rect.width = self.width * self.tile_width
        self.rect.height = self.height * self.tile_height
        self.Player = None

    def make_map(self):
        temp_surface = pygame.Surface((self.width * self.tile_width, self.height * self.tile_height))
        for layer in self.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():  # Используем image вместо tile
                    temp_surface.blit(image, (x * self.tile_width, y * self.tile_height))

        # Создаем спрайты кирпичей и шипов
        for obj in self.tmx_data.objects:
            if obj.name == "Wall":
                brick = Brick(obj.x, obj.y, obj.width, obj.height)
                self.brick_group.add(brick)  #  Добавляем кирпич в группу
            elif obj.name == "Spike":
                spike = Spike(obj.x, obj.y, obj.width, obj.height)  # Создаем шип
                self.spike_group.add(spike)  # Добавляем шип в группу шипов
                self.all_sprites.add(spike)  # Добавляем шип в группу всех спрайтов
            elif obj.name == "Coin":
                coin = Money(obj.x, obj.y)
                self.coin_group.add(coin)
                self.all_sprites.add(coin)

        return temp_surface

    def render(self, surface):
        surface.blit(self.map_image, (0, 0))
        for brick in self.brick_group: # Отрисовываем кирпичи
            surface.blit(brick.image, brick.rect)  # Рисуем
        for spike in self.spike_group:  # Отрисовываем шипы
            surface.blit(spike.image, spike.rect)
        for coin in self.coin_group:
            surface.blit(coin.image, coin.rect) # Отрисовываем монеты

    def get_collision(self):
        return self.collision_layer

    def view_player(self):
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                self.Player = Frog(obj.x, obj.y, self.brick_group, self.spike_group, self.coin_group)  # Передаем группу с кирпичами и шипами
                self.Player.map = self  # Присваиваем ссылку на карту игроку
                self.all_sprites.add(self.Player)
                break


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game_map = Map("Tiledmap/tmx/test_map1.tmx")
    game_map.view_player()  # Создаем игрока после загрузки карты

    player = game_map.Player  # Получаем ссылку на игрока из объекта карты

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

        pygame.event.pump()
        player.update()

        # Рисуем
        screen.fill(BACKGROUND)
        game_map.render(screen)  # Отрисовываем карту и кирпичи
        player.draw(screen)
        for coin in game_map.coin_group:
            coin.update() # анимация монет
        # Обновляем
        pygame.display.flip()


if __name__ == "__main__":
    main()