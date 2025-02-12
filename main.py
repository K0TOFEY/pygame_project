import pygame
import sys
import pytmx
import random


# Вспомогательные функции
def contour(screen, rect, first_file, second_file):  # Наводка на кнопку
    if rect.collidepoint(pygame.mouse.get_pos()):
        btn = pygame.image.load(f"{first_file}")
        screen.blit(btn, rect)
    else:
        btn = pygame.image.load(f"{second_file}")
        screen.blit(btn, rect)

def play_random_music():  # Проигрыш музыки в меню
    global current_music
    next_music = random.choice(MENU_MUSIC)
    if next_music != current_music:
        pygame.mixer.music.load(next_music)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.5)
        current_music = next_music


# Класс любого спрайта
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)  # Загрузка изображения
        self.rect = self.image.get_rect()  # Rect этого изображения

        self.rect.center = [startx, starty]  # Центр rect размещаем на стартовых координатах

    def update(self):  # Пустая функция апдейта
        pass

    def draw(self, screen):  # Функция рисования спрайта
        screen.blit(self.image, self.rect)


# Класс персонажа
class Frog(Sprite):
    def __init__(self, startx, starty, brick_group):
        super().__init__("Froggo/Animation/frog.png", startx, starty)  # Наследование от класса Sprite
        self.stand_image = self.image  # Изображение персонажа
        self.jump_image = pygame.image.load('Froggo/Animation/jump.png')  # Изображение персонажа в прыжке

        # Анимация ходьбы
        self.walk_cycle = [pygame.image.load(f"Froggo/Animation/walk_animation{i}.png") for i in range(1, 9)]
        self.animation_index = 0

        self.facing_left = False  # Смотрит ли наш персонаж в левую сторону

        self.speed = 4  # Скорость игрока
        self.jump_speed = -20  # Скорость игрока в прыжке
        self.vsp = 0  # Вертикальная скорость
        self.gravity = 1  # Уменьшили гравитацию

        self.onground = False  # Проверка на наличие земли под ногами

        self.prev_key = pygame.key.get_pressed()  # Какую кнопку нажал
        self.map = None  # Добавлено поле для хранения ссылки на карту
        self.brick_group = brick_group  # Спрайт группа кирпичей

    def update(self):
        hsp = 0  # Горизонтальная скорость

        # Проверка нажатия кнопки
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:  # Если стрелочка влево
            self.facing_left = False
            self.walk_animation()
            hsp = -self.speed
        elif key[pygame.K_RIGHT]:  # Если стрелочка вправо
            self.facing_left = True
            self.walk_animation()
            hsp = self.speed
        else:  # Просто стоит
            self.image = self.stand_image

        # Прыжок
        if key[pygame.K_UP] and self.onground:  # Прыгаем, только если на земле
            self.vsp = self.jump_speed
            self.onground = False

        # Проигрывание анимации прыжка
        if self.vsp < 10 and not self.onground:
            self.jump_animation()

        # Гравитация
        self.vsp += self.gravity

        # Ограничение скорости падения
        if self.vsp > 10:
            self.vsp = 10

        # Движение
        self.move(hsp, self.vsp)

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

    def walk_animation(self):  # Анимация ходьбы
        self.image = self.walk_cycle[self.animation_index]  # Присваиваем персонажу картинку из цикла анимации ходьбы
        if self.facing_left:  # Проверяем поворот налево
            self.image = pygame.transform.flip(self.image, True, False)  # Зеркалим

        if self.animation_index < len(self.walk_cycle) - 1:  # Меняем индекс картинки с анимацией
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):  # Анимация прыжка
        self.image = self.jump_image   # Присваиваем персонажу картинку персонажа в прыжке
        if self.facing_left:  # Проверяем поворот налево
            self.image = pygame.transform.flip(self.image, True, False)  # Зеркалим

    def on_ground(self):  # Проверка на нахождение на земле
        return self.onground


# Класс блока
class Brick(pygame.sprite.Sprite):  # Класс для кирпичей
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/brick_1.png')  # Загружаем текстуру
        self.image = pygame.transform.scale(self.image, (width, height))  # Меняем размер текстуры
        self.rect = self.image.get_rect()  # Получаем rect текстуры
        self.rect.x = x  # Указываем х rect
        self.rect.y = y  # Указываем y rect


# Класс уровней
class Map():
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename)  # Загружаем карту
        self.tile_width = self.tmx_data.tilewidth  # Получаем длину тайла
        self.tile_height = self.tmx_data.tileheight  # Получаем высоту тайла
        self.width = self.tmx_data.width  # Получаем длину карты в тайлах
        self.height = self.tmx_data.height  # Получаем высоту карты в тайлах
        self.layers = self.tmx_data.layers  # Получаем слои карты
        self.brick_group = pygame.sprite.Group()  # Группа спрайтов для кирпичей
        self.collision_layer = self.tmx_data.get_layer_by_name('Tiles')  # Имя слоя, где происходит столкновение игрока с блоками
        self.map_image = self.make_map()  # Создаем единое изображение карты
        self.rect = self.map_image.get_rect()  # Получаем rect карты
        self.rect.width = self.width * self.tile_width  # Получаем длину rect карты в пикселях
        self.rect.height = self.height * self.tile_height  # Получаем высоту rect карты в пикселях
        self.Player = None  # Игрок
        self.all_sprites = pygame.sprite.Group()  # Все спрайты

    def make_map(self):  # Выведение карты на экран
        temp_surface = pygame.Surface((self.width * self.tile_width, self.height * self.tile_height))  # Создаём новую поверхность
        for layer in self.layers:  # Перебираем слои
            if isinstance(layer, pytmx.TiledTileLayer):  # Является ли этот слой слоем с тайлами
                for x, y, image in layer.tiles():  # Получаем x, y, картинку тайла
                    temp_surface.blit(image, (x * self.tile_width, y * self.tile_height))  # Рисуем

        # Создаем спрайты кирпичей
        for obj in self.tmx_data.objects:  # Перебираем объекты
            if obj.name == "Wall":  # Если объект называется Wall
                brick = Brick(obj.x, obj.y, obj.width, obj.height)  # Передаём данные в класс блока
                self.brick_group.add(brick)  # Добавляем кирпич в группу

        return temp_surface

    def render(self, surface):  # Рисуем кирпичики
        surface.blit(self.map_image, (0, 0))
        for brick in self.brick_group:  # Перебираем кирпичики
            surface.blit(brick.image, brick.rect)  # Рисуем

    def get_collision(self):  # Проверяем столкновение
        return self.collision_layer

    def view_player(self):  # Отображаем игрока
        for obj in self.tmx_data.objects:  # Перебираем объекты
            if obj.name == "Player":  # Если объект называется Player
                self.Player = Frog(obj.x, obj.y, self.brick_group)  # Передаём данные в класс персонажа
                self.Player.map = self  # Присваиваем ссылку на карту игроку
                self.all_sprites.add(self.Player)  # Добавляем в группу всех спрайтов
                break


# Функция главного меню
def main_menu(screen):
    global current_music
    clock = pygame.time.Clock()
    st_btn = pygame.image.load("Buttons/start_btn.png")
    qt_btn = pygame.image.load("Buttons/quit_btn.png")

    # Фон
    bg = pygame.image.load(BACKGROUND_FOR_MENU)
    bg = pygame.transform.flip(bg, True, False)
    screen.blit(bg, (0, 0))

    # Buttons
    st_btn_rect = st_btn.get_rect(topleft=(100, 250))
    qt_btn_rect = qt_btn.get_rect(topleft=(100, 350))

    # Работа над текстом
    font = pygame.font.Font(None, 52)  # Создаём шрифт
    text = font.render("Проклятие лягушачьего рыцаря", True, (255, 255, 255))
    text_x = 125
    text_y = 125

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
                    SOUND_ON_BUTTON.play()
                    lvl_page(screen)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if qt_btn_rect.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    pygame.quit()
                    sys.exit()

        # Наводка на кнопку
        contour(screen, st_btn_rect, 'Buttons/click_start_btn.png', 'Buttons/start_btn.png')  # кнопка старт

        contour(screen, qt_btn_rect, 'Buttons/click_qt_btn.png', 'Buttons/quit_btn.png')  # кнопка выйти

        pygame.display.update()

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
        if not pygame.mixer.music.get_busy():
            play_random_music()


# Функция окна с выбором уровня
def lvl_page(screen):
    global current_music
    bg = pygame.image.load(BACKGROUND_FOR_MENU)
    bg = pygame.transform.flip(bg, True, False)
    screen.blit(bg, (0, 0))

    # Кнопки уровней
    level_1 = pygame.image.load("Buttons/lvl1.png")
    level_2 = pygame.image.load("Buttons/lvl2.png")
    level_3 = pygame.image.load("Buttons/lvl3.png")
    back = pygame.image.load("Buttons/back.png")

    # Rect_of_levels
    rect_level_1 = level_1.get_rect(topleft=(175, 250))
    rect_level_2 = level_2.get_rect(topleft=(360, 250))
    rect_level_3 = level_3.get_rect(topleft=(550, 250))
    rect_back = back.get_rect(topleft=(10, 45))

    # Текст
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
                    SOUND_ON_BUTTON.play()
                    main_menu(screen)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_level_1.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    level1(screen)

        # Наводка на кнопки
        contour(screen, rect_level_1, 'Buttons/cl_lvl1.png', 'Buttons/lvl1.png')  # Кнопка уровня 1

        contour(screen, rect_level_2, 'Buttons/cl_lvl2.png', 'Buttons/lvl2.png')  # Кнопка уровня 2

        contour(screen, rect_level_3, 'Buttons/cl_lvl3.png', 'Buttons/lvl3.png')  # Кнопка уровня 3

        contour(screen, rect_back, 'Buttons/cl_back.png', 'Buttons/back.png')  # Кнопка назад

        pygame.display.update()

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
        if not pygame.mixer.music.get_busy():
            play_random_music()


# Функции уровней
# -------------- Функция уровня 1
def level1(screen):
    global level1_music
    global level1_music_playing
    level1_music_playing = True  # Флаг на то что уровень запущен и играет данная музыка

    pygame.mixer.music.load(MUSIC_ON_LEVEL)  # Загрузка музыки для уровня
    pygame.mixer.music.play(-1)  # Запуск музыки, -1 означает бесконечный повтор

    back = pygame.image.load("Buttons/back.png")
    rect_back = back.get_rect(topleft=(10, 25))

    game_map = Map("Tiledmap/tmx/test_map.tmx")
    game_map.view_player()  # Cоздаём игрока после загрузки карты

    player = game_map.Player  # Получаем ссылку на игрока из объекта карты

    while level1_music_playing: # Тоже самое, что while running, где running = True, но чтоб упростить сделаем так
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # если мы решим вдруг выйти
                if rect_back.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    pygame.mixer.music.stop()  # Останавливаем музыку уровня
                    level1_music_playing = False
                    lvl_page(screen)

        # Наводка на кнопку
        contour(screen, rect_back, 'Buttons/cl_back.png', 'Buttons/back.png')
        pygame.display.update()

        clock.tick(60)

        pygame.event.pump()
        player.update()

        # Рисуем
        screen.fill(BACKGROUND)
        game_map.render(screen)  # Отрисовываем карту и кирпичи
        screen.blit(back, rect_back)  # Кнопка назад
        player.draw(screen)  # Отрисовываем игрока
        # Обновляем
        pygame.display.flip()


# -------------- Последующие уровни


clock = pygame.time.Clock()

# Константы
WIDTH = 800  # Длина окна
HEIGHT = 600  # Высота окна
BACKGROUND = 'black'  # Чёрный цвет для заднего фона
BACKGROUND_FOR_MENU = 'Backgrounds/menu_bg.jpg'
MUSIC_ON_LEVEL = 'Sounds/dungeoun_music.mp3'

# Список музыки для меню
MENU_MUSIC = [
    'Sounds/menu_music1.mp3',
    'Sounds/menu_music2.mp3',
    'Sounds/menu_music3.mp3'
]

# Инициализация Pygame Mixer (звук)
pygame.mixer.init()
SOUND_ON_BUTTON = pygame.mixer.Sound("Sounds/click_on_button.mp3")  # Звук для нажатия кнопки
pygame.mixer.music.set_volume(1)  # Громкость трека 100%

# Создание окна
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Переменная для текущей музыки
# Запоминает текущий играющий трек, чтобы избежать повторного воспроизведения одного и того же трека подряд
current_music = None

# Запускаем первую музыку при запуске игры
play_random_music()

# Меню игры
main_menu(screen)

# завершение работы:
pygame.quit()