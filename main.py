import pygame
import sys
import pytmx
import random
import time
import sqlite3


# Работа с БД
# База данных
DB_NAME = "frogger_knights.db"  # Имя файла базы данных SQLite


def is_level_unlocked(level_number):
    """Проверяет, разблокирован ли уровень. Уровень считается разблокированным, если пройден предыдущий."""
    conn = sqlite3.connect(DB_NAME)  # Подключение к базе данных
    cursor = conn.cursor()  # Создание объекта курсора для выполнения SQL-запросов
    # Выполнение SQL-запроса, считающего количество записей в таблице level_progress для предыдущего уровня
    cursor.execute("SELECT COUNT(*) FROM level_progress WHERE level = ?", (level_number - 1,))
    count = cursor.fetchone()[0]  # Получение результата запроса (количество записей)
    conn.close()  # Закрытие соединения с базой данных
    # Возвращает True, если предыдущий уровень пройден (количество записей > 0) или это первый уровень (level_number == 1)
    return count > 0 or level_number == 1


def mark_level_complete(level_number):
    """Отмечает уровень как пройденный, добавляя запись в таблицу level_progress."""
    conn = sqlite3.connect(DB_NAME)  # Подключение к базе данных
    cursor = conn.cursor()  # Создание объекта курсора
    # Выполнение SQL-запроса, добавляющего запись в таблицу level_progress.  INSERT OR IGNORE предотвращает добавление дубликатов.
    cursor.execute("INSERT OR IGNORE INTO level_progress (level, completed_time) VALUES (?, ?)", (level_number, time.time()))
    conn.commit()  # Фиксация изменений в базе данных
    conn.close()  # Закрытие соединения


def create_level_progress_table():
    """Создает таблицу level_progress в базе данных, если она еще не существует."""
    conn = sqlite3.connect(DB_NAME)  # Подключение к базе данных
    cursor = conn.cursor()  # Создание объекта курсора
    # Выполнение SQL-запроса, создающего таблицу level_progress.  IF NOT EXISTS предотвращает попытку создания таблицы, если она уже существует.
    cursor.execute('''CREATE TABLE IF NOT EXISTS level_progress (level INTEGER PRIMARY KEY,completed_time REAL)''')
    conn.commit()  # Фиксация изменений
    conn.close()  # Закрытие соединения


create_level_progress_table()


# Вспомогательные функции
def contour(screen, rect, first_file, second_file):  # Наводка на кнопку
    """Делает эффект наводки на кнопку"""
    if rect.collidepoint(pygame.mouse.get_pos()):  # Проверяем, находится ли курсор мыши над кнопкой
        btn = pygame.image.load(f"{first_file}")  # Загружаем изображение для состояния "наведена мышь"
        screen.blit(btn, rect)  # Отображаем изображение на экране
    else:  # Если курсор мыши не над кнопкой
        btn = pygame.image.load(f"{second_file}")  # Загружаем изображение для обычного состояния
        screen.blit(btn, rect)  # Отображаем изображение на экране


def play_random_music():  # Проигрыш музыки в меню
    """Воспроизводит случайную музыку из списка MENU_MUSIC в меню."""
    global current_music  # Используем глобальную переменную current_music, чтобы запоминать текущую музыку
    next_music = random.choice(MENU_MUSIC)  # Выбираем случайный трек из списка MENU_MUSIC
    if next_music != current_music:  # Проверяем, чтобы следующий трек не был таким же, как текущий
        pygame.mixer.music.load(next_music)  # Загружаем выбранный трек в проигрыватель
        pygame.mixer.music.play()  # Запускаем воспроизведение трека
        pygame.mixer.music.set_volume(0.5)  # Устанавливаем громкость трека на 50%
        current_music = next_music  # Обновляем значение current_music, чтобы запомнить, какой трек сейчас играет


# Класс любого спрайта
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()  # Вызываем конструктор родительского класса pygame.sprite.Sprite
        self.image = pygame.image.load(image)  # Загрузка изображения спрайта из файла
        self.rect = self.image.get_rect()  # Создание объекта Rect на основе загруженного изображения. Rect используется для определения позиции и размеров спрайта.
        self.rect.center = [startx, starty]  # Установка центра Rect (а значит и спрайта) в указанные координаты

    def update(self):
        pass  # В базовом классе ничего не делает

    def draw(self, screen):
        screen.blit(self.image, self.rect)  # Отображает изображение спрайта на экране в позиции, определяемой Rect


# Класс персонажа
class Frog(Sprite):
    def __init__(self, startx, starty, brick_group, spike_group, coin_group, door_group):  # Принимаем coin_group
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
        self.coin_group = coin_group  # Сохраняем группу монет
        self.door_group = door_group
        self.is_jumping = False
        self.dying = False  # Флаг, показывающий, что началась анимация смерти
        self.death_start_time = 0  # Время начала анимации смерти
        self.death_animation_index = 0  # Индекс текущего кадра анимации смерти
        self.death_frame_duration = DEATH_ANIMATION_DURATION / DEATH_FRAMES  # Длительность одного кадра анимации смерти
        self.last_death_frame_time = 0  # Время отображения последнего кадра анимации смерти
        self.coin_sound = pygame.mixer.Sound("Sounds/money_music.mp3")  # Звук для монеты

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
        for coin in self.coin_group:  # Перебираем монеты
            if self.rect.colliderect(coin.rect):  # Если игрок столкнулся с монетой
                self.coin_sound.play() # Проигрываем звук
                coin.kill()  # Удаляем монету из всех групп

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
        if time.time() - self.last_death_frame_time > self.death_frame_duration:
            self.last_death_frame_time = time.time()
            self.image = self.dead_cycle[self.death_animation_index]
            self.death_animation_index += 1
            if self.death_animation_index >= len(self.dead_cycle):
                self.death_animation_index = 0
                self.dying = False
                self.reset()

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


# Класс блока
class Brick(pygame.sprite.Sprite):  # Класс для кирпичей
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/brick_4.png')  # Загружаем текстуру
        self.image = pygame.transform.scale(self.image, (width, height))  # Меняем размер текстуры
        self.rect = self.image.get_rect()  # Получаем rect текстуры
        self.rect.x = x  # Указываем х rect
        self.rect.y = y  # Указываем y rect


class Spike(pygame.sprite.Sprite):  # Класс для шипов
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/spike.png')  # Загружаем текстуру шипа
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Door(pygame.sprite.Sprite):  # Класс для двери
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/door1.png')  # Загружаем текстуру двери
        self.image = pygame.transform.scale(self.image, (width, height))
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
        self.animation_cooldown = 100  # 100 ms между кадрами

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_cooldown:
            self.last_update = now
            self.animation_index = (self.animation_index + 1) % len(self.coin_cycle)
            self.image = self.coin_cycle[self.animation_index]


# Класс уровней
class Map():
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.layers = self.tmx_data.layers
        self.brick_group = pygame.sprite.Group()  # Группа спрайтов для кирпичей
        self.spike_group = pygame.sprite.Group()  # Группа спрайтов для шипов
        self.coin_group = pygame.sprite.Group()  # Группа спрайтов для монет
        self.door_group = pygame.sprite.Group()  # Группа спрайтов для двери
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
                self.brick_group.add(brick)  # Добавляем кирпич в группу
            elif obj.name == "Spike":
                spike = Spike(obj.x, obj.y, obj.width, obj.height)  # Создаем шип
                self.spike_group.add(spike)  # Добавляем шип в группу шипов
                self.all_sprites.add(spike)  # Добавляем шип в группу всех спрайтов
            elif obj.name == "Coin":
                coin = Money(obj.x, obj.y)
                self.coin_group.add(coin)
                self.all_sprites.add(coin)
            elif obj.name == "Door":
                door = Door(obj.x, obj.y, obj.width, obj.height)
                self.all_sprites.add(door)

        return temp_surface

    def render(self, surface):
        surface.blit(self.map_image, (0, 0))
        for brick in self.brick_group:  # Отрисовываем кирпичи
            surface.blit(brick.image, brick.rect)  # Рисуем
        for spike in self.spike_group:  # Отрисовываем шипы
            surface.blit(spike.image, spike.rect)
        for coin in self.coin_group:
            surface.blit(coin.image, coin.rect) # Отрисовываем монеты
        for door in self.door_group:
            surface.blit(door.image, door.rect)

    def get_collision(self):
        return self.collision_layer

    def view_player(self):
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                self.Player = Frog(obj.x, obj.y, self.brick_group, self.spike_group, self.coin_group, self.door_group)  # Передаем группу с кирпичами и шипами
                self.Player.map = self  # Присваиваем ссылку на карту игроку
                self.all_sprites.add(self.Player)
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
                    start_level(screen, 1)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_level_2.collidepoint(event.pos) and is_level_unlocked(2):
                    SOUND_ON_BUTTON.play()
                    start_level(screen, 2)
                elif rect_level_2.collidepoint(event.pos):
                    print("Этот уровень заблокирован")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_level_3.collidepoint(event.pos) and is_level_unlocked(3):
                    SOUND_ON_BUTTON.play()
                    start_level(screen, 3)
                elif rect_level_3.collidepoint(event.pos):
                    print("Этот уровень заблокирован")

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
# Новая функция старта уровня
def start_level(screen, level_number):
    global level1_music
    global level1_music_playing
    level1_music_playing = True

    pygame.mixer.music.load(MUSIC_ON_LEVEL)  # Загрузка музыки для уровня
    pygame.mixer.music.play(-1)  # Запуск музыки, -1 означает бесконечный повтор

    back = pygame.image.load("Buttons/back.png")
    rect_back = back.get_rect(topleft=(10, 25))

    level_map = Map(f"Tiledmap/tmx/test_map{level_number}.tmx")
    sprites = level_map.coin_group
    level_map.view_player()

    player = level_map.Player

    while level1_music_playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_ESCAPE:
            #         pygame.mixer.music.stop()
            #         lvl_page(screen)  # Вернуться в меню выбора уровней
            #         return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # если мы решим вдруг выйти
                if rect_back.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    pygame.mixer.music.stop()  # Останавливаем музыку уровня
                    level1_music_playing = False
                    lvl_page(screen)

        # Переход на следующий уровень
        if player.rect.right >= WIDTH and not sprites:  # ToDo and coins < 3 to pass
            # Обновление бд
            mark_level_complete(level_number)  # Отмечаем прохождение уровня
            pygame.mixer.music.stop()  # останавливаем трек
            level1_music_playing = False  # переключаем флаг
            if level_number < 3:
                # Если не последний уровень - запускаем следующий уровень
                start_level(screen, level_number + 1)
            else:  # Если последний уровень - возвращаемся в меню выбора уровня.
                lvl_page(screen)
            return  # Иначе код не работает
        elif player.rect.right >= WIDTH and sprites:
            player.reset()

        # Наводка на кнопку
        contour(screen, rect_back, 'Buttons/cl_back.png', 'Buttons/back.png')
        pygame.display.update()

        clock.tick(60)

        pygame.event.pump()
        player.update()

        # Рисуем
        screen.fill(BACKGROUND)
        level_map.render(screen)
        screen.blit(back, rect_back)  # Кнопка назад
        player.draw(screen)
        for coin in level_map.coin_group:
            coin.update()  # анимация монет
        # Обновляем
        pygame.display.flip()

# -------------- Функция уровня 1
def level1(screen):
    start_level(screen, 1)


# -------------- Функция уровня 2
def level2(screen):
    start_level(screen, 2)


# -------------- Функция уровня 3
def level3(screen):
    start_level(screen, 3)


clock = pygame.time.Clock()

# Константы
WIDTH = 800  # Длина окна
HEIGHT = 600  # Высота окна
BACKGROUND = 'black'  # Чёрный цвет для заднего фона
BACKGROUND_FOR_MENU = 'Backgrounds/menu_bg.jpg'
MUSIC_ON_LEVEL = 'Sounds/dungeoun_music.mp3'
DEATH_ANIMATION_DURATION = 1  # Длительность анимации смерти в секундах
DEATH_FRAMES = 8  # Кол-во кадров смерти
COIN_ANIMATION_SPEED = 0.2  # Скорость анимации монет


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
# Запоменает текущий играющий трек, чтобы избежать повторного воспроизведения одного и того же трека подряд
current_music = None

# Запускаем первую музыку при запуске игры
play_random_music()

# Меню игры
main_menu(screen)

# завершение работы:
pygame.quit()