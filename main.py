import pygame
import sys
import pytmx
import random
import time
import sqlite3

# Работа с БД
# База данных
DB_NAME = "frogger_knights.db"  # Имя файла базы данных SQLite


def cursor(screen):
    pygame.mouse.set_visible(False)
    cursor_image = pygame.image.load('Sprites/cursor.png')
    cursor_rect = cursor_image.get_rect()
    if pygame.mouse.get_focused():
        cursor_rect.topleft = pygame.mouse.get_pos()  # Получаем позицию
        screen.blit(cursor_image, cursor_rect)


def is_level_unlocked(level_number):
    """Проверяет, разблокирован ли уровень. Уровень считается разблокированным, если пройден предыдущий."""
    coins = update_bd(name, "how_coins", 0)
    if coins >= (level_number - 1) * 3:
        return True
    return False


def update_bd(name, s, n):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if s == "coin":
        k = cursor.execute("""SELECT coin FROM record WHERE name = ?""", (name,)).fetchone()
        if k:
            cursor.execute("""UPDATE record SET coin = ? WHERE name = ?""", (n, name))
        else:
            cursor.execute("""INSERT INTO record(coin, name) VALUES(?, ?)""", (n, name))
    elif s == "death":
        k = cursor.execute("""SELECT count FROM death WHERE name = ?""", (name,)).fetchone()[0]
        cursor.execute("""UPDATE death SET count = ? WHERE name = ?""", (k + 1, name))
    elif s == "death_0":
        k = cursor.execute("""SELECT count FROM death WHERE name = ?""", (name,)).fetchone()
        if k:
            cursor.execute("""UPDATE death SET count = 0 WHERE name = ?""", (name,))
        else:
            cursor.execute("""INSERT INTO death(name, count) VALUES(?, ?)""", (name, 0))
    elif s == "how_coins":
        k = cursor.execute("""SELECT coin FROM record WHERE name = ?""", (name,)).fetchone()
        if k:
            return k[0]
        return 0
    elif s == "record":
        k = cursor.execute("""SELECT name, level1, level2, level3, deaths FROM record 
        WHERE coin = 9 ORDER BY deaths""").fetchall()
        return k
    elif s == "how_death":
        old = cursor.execute(f"""SELECT {"level" + str(n)} FROM record WHERE name = ?""", (name,)).fetchone()
        now = cursor.execute("""SELECT count FROM death WHERE name = ?""", (name, )).fetchone()[0]
        if isinstance(old, tuple):
            old = old[0]
        if (old and (now < old)) or (not old and (n == 2 or n == 3)):
            cursor.execute(f"""UPDATE record SET {"level" + str(n)} = {now} 
            WHERE name = ?""", (name,))
        elif not old and (n == 1) and (old != 0):
            cursor.execute(f"""INSERT INTO record(name, {"level" + str(n)}) VALUES(?, {now})""", (name,))
        death = cursor.execute(f"""SELECT deaths FROM record WHERE name = ?""", (name,)).fetchall()
        if death:
            all_zn = cursor.execute("""SELECT level1, level2, level3 FROM record 
            WHERE name = ?""", (name,)).fetchone()
            all_death = 0
            for el in all_zn:
                if el:
                    all_death += el
            cursor.execute(f"""UPDATE record SET deaths = {all_death} WHERE name = ?""", (name,))
        else:
            cursor.execute(f"""UPDATE record SET deaths = {now} WHERE name = ?""", (name,))
    elif s == "users":
        k = cursor.execute("""SELECT name FROM record WHERE name = ?""", (name,)).fetchall()
        if k:
            return False
        return True
    conn.commit()
    conn.close()


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
        pygame.mixer.music.set_volume(0.02)  # Устанавливаем громкость трека на 50%
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
    def __init__(self, startx, starty, brick_group, spike_group, coin_group, door_group, level_num, fire_group):  # Принимаем coin_group
        super().__init__("Froggo/Animation/frog.png", startx, starty)
        self.stand_image = self.image  # Изображение лягушки в состоянии покоя
        self.jump_image = pygame.image.load('Froggo/Animation/jump.png')  # Изображение лягушки в прыжке

        self.walk_cycle = [pygame.image.load(f"Froggo/Animation/walk_animation{i}.png") for i in range(1, 9)]  # Список изображений для анимации ходьбы
        self.dead_cycle = [pygame.image.load(f"Froggo/Animation/dead_animation{i}.png") for i in range(1, 9)]  # Список изображений для анимации смерти
        self.animation_index = 0  # Текущий индекс анимации
        self.facing_left = False  # Направление взгляда (вправо/влево)

        self.speed = 4  # Скорость передвижения
        self.jump_speed = -20  # Изменили знак, чтобы прыжок был вверх # Скорость прыжка (отрицательная, т.к. ось Y направлена вниз)
        self.vsp = 0  # Вертикальная скорость
        self.gravity = 1  # Уменьшили гравитацию # Ускорение свободного падения

        self.onground = False  # Флаг, находится ли лягушка на земле

        self.min_jumpspeed = 3
        self.prev_key = pygame.key.get_pressed()
        self.map = None  # Ссылка на объект карты (уровня)
        self.brick_group = brick_group  # Группа спрайтов кирпичей
        self.spike_group = spike_group  # Группа спрайтов шипов
        self.coin_group = coin_group  # Группа спрайтов монет
        self.door_group = door_group
        self.fire_group = fire_group
        self.is_jumping = False
        self.dying = False  # Флаг, показывающий, что началась анимация смерти
        self.death_start_time = 0  # Время начала анимации смерти
        self.death_animation_index = 0  # Индекс текущего кадра анимации смерти
        self.death_frame_duration = DEATH_ANIMATION_DURATION / DEATH_FRAMES  # Длительность одного кадра анимации смерти
        self.last_death_frame_time = 0  # Время отображения последнего кадра анимации смерти
        self.coin_sound = pygame.mixer.Sound("Sounds/money_music.mp3")  # Загрузка звука при столкновении с монетой
        self.level_num = level_num

    def update(self):
        if self.dying:
            self.death_animation()
            return  # Прекращаем нормальное обновление, если лягушка находится в состоянии смерти

        hsp = 0  # Горизонтальная скорость, изначально равна 0

        # Проверка нажатия кнопки
        key = pygame.key.get_pressed()  # Получаем состояние всех клавиш

        if key[pygame.K_LEFT]:  # Если нажата клавиша "Влево"
            self.facing_left = False  # Лягушка смотрит влево
            self.walk_animation()  # Запускаем анимацию ходьбы
            hsp = -self.speed  # Устанавливаем горизонтальную скорость в отрицательное значение (движение влево)

        elif key[pygame.K_RIGHT]:  # Если нажата клавиша "Вправо"
            self.facing_left = True  # Лягушка смотрит вправо
            self.walk_animation()  # Запускаем анимацию ходьбы
            hsp = self.speed  # Устанавливаем горизонтальную скорость в положительное значение (движение вправо)

        else:  # Если никакие клавиши движения не нажаты
            self.image = self.stand_image  # Отображаем изображение лягушки в состоянии покоя

        # Прыжок
        if key[pygame.K_UP] and self.onground:  # Прыгаем, только если на земле
            self.vsp = self.jump_speed  # Устанавливаем вертикальную скорость для прыжка
            self.onground = False  # Сбрасываем флаг, так как игрок прыгнул

        if self.vsp < 10 and not self.onground:
            self.jump_animation()

        # Гравитация
        self.vsp += self.gravity  # Увеличиваем вертикальную скорость под воздействием гравитации (имитация падения)

        # Ограничение скорости падения
        if self.vsp > 10:
            self.vsp = 10  # Ограничиваем максимальную скорость падения

        # Движение
        self.move(hsp, self.vsp)  # Вызываем метод перемещения, передавая горизонтальную и вертикальную скорость

        # Анимация прыжка
        if self.is_jumping and not self.onground:  # Если прыгаем, то проигрываем анимацию падения
            self.jump_animation()  # Запускаем анимацию падения

    def move(self, x, y):
        # Горизонтальное движение
        self.rect.x += x  # Изменяем x-координату Rect лягушки на величину x (горизонтальное смещение)

        # Проверка столкновений по X с кирпичами
        for brick in self.brick_group:  # Перебираем все спрайты кирпичей из группы brick_group
            if self.rect.colliderect(brick.rect):  # Проверяем, столкнулся ли Rect лягушки с Rect текущего кирпича
                if x > 0:  # Движемся вправо
                    self.rect.right = brick.rect.left  # Если движемся вправо, устанавливаем правую границу Rect лягушки на левую границу Rect кирпича (останавливаем движение вправо)
                    x = 0  # Обнуляем x, чтобы предотвратить дальнейшее движение в этом направлении
                elif x < 0:  # Движемся влево
                    self.rect.left = brick.rect.right  # Если движемся влево, устанавливаем левую границу Rect лягушки на правую границу Rect кирпича (останавливаем движение влево)
                    x = 0  # Обнуляем x, чтобы предотвратить дальнейшее движение в этом направлении

        # Вертикальное движение
        self.rect.y += y  # Изменяем y-координату Rect лягушки на величину y (вертикальное смещение)

        # Проверка столкновений по Y с кирпичами
        self.onground = False  # Считаем, что не на земле, пока не докажем обратное
        for brick in self.brick_group:  # Перебираем все спрайты кирпичей из группы brick_group
            if self.rect.colliderect(brick.rect):  # Проверяем, столкнулся ли Rect лягушки с Rect текущего кирпича
                if y > 0:  # Падаем вниз
                    self.rect.bottom = brick.rect.top  # Если падаем вниз, устанавливаем нижнюю границу Rect лягушки на верхнюю границу Rect кирпича (останавливаем падение)
                    self.vsp = 0  # Обнуляем вертикальную скорость, чтобы предотвратить дальнейшее движение вниз
                    self.onground = True  # Устанавливаем флаг onground в True, т.к. теперь лягушка находится на земле
                elif y < 0:  # Прыгаем вверх
                    self.rect.top = brick.rect.bottom  # Если прыгаем вверх, устанавливаем верхнюю границу Rect лягушки на нижнюю границу Rect кирпича (останавливаем прыжок)
                    self.vsp = 0   # Обнуляем вертикальную скорость, чтобы предотвратить дальнейшее движение вверх
                    y = 0  # Обнуляем y, чтобы предотвратить дальнейшее движение в этом направлении

        # Проверка столкновений с шипами
        for spike in self.spike_group:  # Перебираем все спрайты шипов из группы spike_group
            if self.rect.colliderect(spike.rect):  # Проверяем, столкнулся ли Rect лягушки с Rect текущего шипа
                self.dead_collision()  # Вызываем метод spike_collision для обработки столкновения с шипом

        for fire in self.fire_group:
            if self.rect.colliderect(fire.rect):
                self.dead_collision()

        # Проверка столкновений с монетами
        for coin in self.coin_group:  # Перебираем монеты
            if self.rect.colliderect(coin.rect):  # Если игрок столкнулся с монетой
                self.coin_sound.play()  # Проигрываем звук
                coin.kill()  # Удаляем монету из всех групп

        if self.rect.y > 570:
            self.dead_collision()

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]  # Получаем текущий кадр анимации ходьбы из списка walk_cycle
        if self.facing_left:  # Если лягушка смотрит влево
            self.image = pygame.transform.flip(self.image, True, False)  # Отражаем изображение по горизонтали

        if self.animation_index < len(self.walk_cycle) - 1:  # Если текущий индекс не последний в списке
            self.animation_index += 1  # Переходим к следующему кадру
        else:  # Если текущий индекс последний
            self.animation_index = 0  # Возвращаемся к первому кадру (зацикливаем анимацию)

    def jump_animation(self):
        self.image = self.jump_image  # Устанавливаем текущее изображение лягушки на изображение для прыжка (self.jump_image)
        if self.facing_left:  # Если лягушка смотрит влево
            # Отражаем изображение по горизонтали, чтобы лягушка смотрела влево
            self.image = pygame.transform.flip(self.image, True, False)

    def death_animation(self):
        # Проверяем, прошло ли достаточно времени с момента отображения последнего кадра анимации смерти
        if time.time() - self.last_death_frame_time > self.death_frame_duration:
            self.last_death_frame_time = time.time()
            self.image = self.dead_cycle[self.death_animation_index]
            self.death_animation_index += 1
            if self.death_animation_index >= len(self.dead_cycle): # Если достигли конца анимации смерти
                self.death_animation_index = 0
                self.dying = False # Устанавливаем флаг dying в False, чтобы прекратить анимацию смерти
                update_bd(name, "death", self.level_num)
                self.reset()

    def on_ground(self):
        # Возвращает значение флага self.onground, который указывает, находится ли лягушка на земле
        return self.onground

    def dead_collision(self):
        if not self.dying:  # Если анимация смерти еще не началась (чтобы не прерывать ее, если она уже идет)
            self.dying = True  # Начинаем анимацию смерти (устанавливаем флаг self.dying в True)
            self.death_start_time = time.time()

    def reset(self):
        for obj in self.map.tmx_data.objects:  # Перебираем все объекты, определённые на карте (в Tiled Editor)
            if obj.name == "Player":  # Если имя текущего объекта "Player" (т.е. это объект, обозначающий стартовую позицию)
                self.rect.x = obj.x  # Устанавливаем x-координату Rect лягушки в x-координату объекта "Player"
                self.rect.y = obj.y  # Устанавливаем y-координату Rect лягушки в y-координату объекта "Player"
                break  # Прекращаем перебор объектов, т.к. нужная позиция найдена

        self.image = self.stand_image  # Устанавливаем изображение лягушки на изображение в состоянии покоя (self.stand_image)
        self.dying = False  # Устанавливаем флаг self.dying в False, чтобы прекратить анимацию смерти (если она шла)
        self.vsp = 0  # Обнуляем вертикальную скорость
        self.death_animation_index = 0  # Обнуляем индекс смерти


# Класс блока
class Brick(pygame.sprite.Sprite):  # Класс для кирпичей
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/brick_6.png')  # Загружаем текстуру
        self.image = pygame.transform.scale(self.image, (width, height))  # Меняем размер текстуры
        self.rect = self.image.get_rect()  # Получаем rect текстуры
        self.rect.x = x  # Указываем х rect
        self.rect.y = y  # Указываем y rect


class Spike(pygame.sprite.Sprite):  # Класс для шипов
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('Sprites/spike.png')  # Загружаем текстуру шипа
        self.image = pygame.transform.scale(self.image, (32, 32))  # Меняем размер текстуры
        self.rect = self.image.get_rect()  # Получаем rect текстуры
        self.rect.x = x  # Указываем х rect
        self.rect.y = y  # Указываем y rect


class Door(pygame.sprite.Sprite):  # Класс для двери
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('Sprites/door1.png')  # Загружаем текстуру двери
        self.image = pygame.transform.scale(self.image, (width, height))  # Меняем размер текстуры
        self.rect = self.image.get_rect()  # Получаем rect текстуры
        self.rect.x = x  # Указываем х rect
        self.rect.y = y  # Указываем y rect


class Money(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('Money/money_animation1.png')  # Загружаем текстуру Монеты
        self.rect = self.image.get_rect()  # Создаем Rect для монеты
        self.rect.x = x  # Устанавливаем x-координату Rect монеты
        self.rect.y = y  # Устанавливаем y-координату Rect монеты
        self.coin_cycle = [pygame.image.load(f"Money/money_animation{i}.png") for i in range(1, 6)]  # Создаем список кадров для анимации монеты
        self.animation_index = 0  # Указываем, какой сейчас кадр анимации
        self.last_update = pygame.time.get_ticks()  # Указываем, когда последний раз обновлялась анимация
        self.animation_cooldown = 100  # Указываем время между сменой кадров в анимации

    def update(self):
        now = pygame.time.get_ticks()  # Получаем текущее время в миллисекундах
        if now - self.last_update > self.animation_cooldown:  # Проверяем, прошло ли достаточно времени с момента последнего обновления
            self.last_update = now  # Обновляем время последнего обновления
            # Увеличиваем индекс текущего кадра анимации, зацикливая его (оператор %)
            self.animation_index = (self.animation_index + 1) % len(self.coin_cycle)
            # Устанавливаем текущий кадр анимации в качестве изображения спрайта
            self.image = self.coin_cycle[self.animation_index]


class Torch(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('Torch/torch_animation1.png')  # Загружаем текстуру Монеты
        self.rect = self.image.get_rect()  # Создаем Rect для монеты
        self.rect.x = x  # Устанавливаем x-координату Rect монеты
        self.rect.y = y  # Устанавливаем y-координату Rect монеты
        self.coin_cycle = [pygame.image.load(f"Torch/torch_animation{i}.png") for i in
                           range(1, 9)]  # Создаем список кадров для анимации монеты
        self.animation_index = 0  # Указываем, какой сейчас кадр анимации
        self.last_update = pygame.time.get_ticks()  # Указываем, когда последний раз обновлялась анимация
        self.animation_cooldown = 100  # Указываем время между сменой кадров в анимации

    def update(self):
        now = pygame.time.get_ticks()  # Получаем текущее время в миллисекундах
        if now - self.last_update > self.animation_cooldown:  # Проверяем, прошло ли достаточно времени с момента последнего обновления
            self.last_update = now  # Обновляем время последнего обновления
            # Увеличиваем индекс текущего кадра анимации, зацикливая его (оператор %)
            self.animation_index = (self.animation_index + 1) % len(self.coin_cycle)
            # Устанавливаем текущий кадр анимации в качестве изображения спрайта
            self.image = self.coin_cycle[self.animation_index]


class Fire(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('Fire/fire_animation1.png')  # Загружаем текстуру Огня
        self.rect = self.image.get_rect()  # Создаем Rect для Огня
        self.rect.x = x  # Устанавливаем x-координату Rect Огня
        self.rect.y = y  # Устанавливаем y-координату Rect Огня
        self.fire_cycle = [pygame.image.load(f"Fire/fire_animation{i}.png") for i in
                           range(1, 9)]  # Создаем список кадров для анимации Огня
        self.animation_index = 0  # Указываем, какой сейчас кадр анимации
        self.last_update = pygame.time.get_ticks()  # Указываем, когда последний раз обновлялась анимация
        self.animation_cooldown = 100  # Указываем время между сменой кадров в анимации

    def update(self):
        now = pygame.time.get_ticks()  # Получаем текущее время в миллисекундах
        if now - self.last_update > self.animation_cooldown:  # Проверяем, прошло ли достаточно времени с момента последнего обновления
            self.last_update = now  # Обновляем время последнего обновления
            # Увеличиваем индекс текущего кадра анимации, зацикливая его (оператор %)
            self.animation_index = (self.animation_index + 1) % len(self.fire_cycle)
            # Устанавливаем текущий кадр анимации в качестве изображения спрайта
            self.image = self.fire_cycle[self.animation_index]


# Класс уровней
class Map():
    def __init__(self, filename, level_num):
        self.tmx_data = pytmx.load_pygame(filename)  # Загружаем TMX-файл с использованием pytmx
        self.tile_width = self.tmx_data.tilewidth  # Получаем ширину тайла из данных TMX
        self.tile_height = self.tmx_data.tileheight  # Получаем высоту тайла из данных TMX
        self.width = self.tmx_data.width  # Получаем ширину карты в тайлах из данных TMX
        self.height = self.tmx_data.height  # Получаем высоту карты в тайлах из данных TMX
        self.layers = self.tmx_data.layers  # Получаем список слоев карты из данных TMX
        self.level_num = level_num
        self.brick_group = pygame.sprite.Group()  # Группа спрайтов для кирпичей
        self.spike_group = pygame.sprite.Group()  # Группа спрайтов для шипов
        self.coin_group = pygame.sprite.Group()  # Группа спрайтов для монет
        self.door_group = pygame.sprite.Group()  # Группа спрайтов для двери
        self.torch_group = pygame.sprite.Group()
        self.fire_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()  # Группа для всех спрайтов
        self.collision_layer = self.tmx_data.get_layer_by_name('Tiles')  # Получаем слой, содержащий информацию о коллизиях
        self.map_image = self.make_map()  # Создаем изображение карты, объединяя все слои в одну поверхность
        self.rect = self.map_image.get_rect()  # Создаем Rect для карты
        self.rect.width = self.width * self.tile_width  # Вычисляем ширину Rect карты в пикселях
        self.rect.height = self.height * self.tile_height  # Вычисляем высоту Rect карты в пикселях
        self.Player = None  # Переменная для хранения экземпляра игрока

    def make_map(self):
        # Создаем временную поверхность для хранения изображения карты
        temp_surface = pygame.Surface((self.width * self.tile_width, self.height * self.tile_height))
        for layer in self.layers:  # Перебираем все слои
            if isinstance(layer, pytmx.TiledTileLayer):  # Если текущий слой - это слой с тайлами
                for x, y, image in layer.tiles():  # Перебираем все тайлы на слое (x, y - координаты тайла, image - изображение тайла)
                    # Отображаем тайл на временной поверхности
                    temp_surface.blit(image, (x * self.tile_width, y * self.tile_height))

        # Создаем спрайты кирпичей и шипов
        for obj in self.tmx_data.objects:  # Перебираем все объекты, определенные в TMX-файле (в Tiled Editor)
            if obj.name == "Wall":  # Если имя объекта "Wall" (т.е. это кирпич)
                brick = Brick(obj.x, obj.y, obj.width, obj.height)  # Создаем объект Brick
                self.brick_group.add(brick)  # Добавляем кирпич в группу
            elif obj.name == "Spike":  # Если имя объекта "Spike" (т.е. это шип)
                spike = Spike(obj.x, obj.y)  # Создаем шип
                self.spike_group.add(spike)  # Добавляем шип в группу шипов
                self.all_sprites.add(spike)  # Добавляем шип в группу всех спрайтов
            elif obj.name == "Coin":  # Если имя объекта "Coin" (т.е. это монета)
                coin = Money(obj.x, obj.y)
                self.coin_group.add(coin)
                self.all_sprites.add(coin)
            elif obj.name == "Door":  # Если имя объекта "Door" (т.е. это дверь)
                door = Door(obj.x, obj.y, obj.width, obj.height)
                self.door_group.add(door)
                self.all_sprites.add(door)
            elif obj.name == "Torch":
                torch = Torch(obj.x, obj.y)
                self.torch_group.add(torch)
                self.all_sprites.add(torch)
            elif obj.name == "Fire":
                fire = Fire(obj.x, obj.y)
                self.fire_group.add(fire)
                self.all_sprites.add(fire)

        return temp_surface  # Возвращаем созданное изображение карты

    def render(self, surface):
        surface.blit(self.map_image, (0, 0))  # Отображаем изображение карты на поверхности
        # Отрисовываем все спрайты из соответствующих групп:
        for brick in self.brick_group:  # Отрисовываем кирпичи
            surface.blit(brick.image, brick.rect)  # Рисуем
        for spike in self.spike_group:  # Отрисовываем шипы
            surface.blit(spike.image, spike.rect)
        for coin in self.coin_group:  # Отрисовываем монеты
            surface.blit(coin.image, coin.rect)
        for door in self.door_group:  # Отрисовываем двери
            surface.blit(door.image, door.rect)
        for torch in self.torch_group:
            surface.blit(torch.image, torch.rect)
        for fire in self.fire_group:
            surface.blit(fire.image, fire.rect)

    def get_collision(self):
        return self.collision_layer  # Возвращает слой, который используется для определения столкновений

    def view_player(self):
        for obj in self.tmx_data.objects:  # Перебираем все объекты, определенные в TMX-файле
            if obj.name == "Player":  # Если имя объекта "Player" (т.е. это объект, обозначающий стартовую позицию)
                # Создаем объект Frog, передавая координаты объекта "Player" и группы спрайтов
                self.Player = Frog(obj.x, obj.y, self.brick_group, self.spike_group, self.coin_group,
                                   self.door_group, self.level_num, self.fire_group)  # Передаем группу с кирпичами и шипами
                self.Player.map = self  # Устанавливаем ссылку на текущую карту в объекте игрока (для доступа к данным карты из игрока)
                self.all_sprites.add(self.Player)  # Добавляем игрока в группу всех спрайтов
                break  # Прекращаем перебор объектов, т.к. игрок создан и добавлен


# Функция главного меню
def main_menu(screen):
    global current_music  # Используем глобальную переменную для отслеживания текущей музыки

    clock = pygame.time.Clock()  # Создаем объект Clock для управления частотой кадров

    st_btn = pygame.image.load("Buttons/start_btn.png")  # Загружаем изображение кнопки "Старт"
    qt_btn = pygame.image.load("Buttons/quit_btn.png")  # Загружаем изображение кнопки "Выход"
    login_btn = pygame.image.load("Buttons/login.png")  # Загружаем изображение кнопки "Пользователь"
    record_btn = pygame.image.load("Buttons/record.png")  # Загружаем изображение кнопки "Рекорд"

    # Фон
    bg = pygame.image.load(BACKGROUND_FOR_MENU)  # Загружаем изображение фона для меню
    bg = pygame.transform.flip(bg, True, False)  # Отражаем изображение фона по горизонтали

    # Buttons
    st_btn_rect = st_btn.get_rect(topleft=(100, 210))  # Создаем Rect для кнопки "Старт" и задаем её позицию
    qt_btn_rect = qt_btn.get_rect(topleft=(100, 300))  # Создаем Rect для кнопки "Выход" и задаем её позицию
    log_btn_rect = login_btn.get_rect(topleft=(110, 380))  # Создаем Rect для кнопки "Пользователь" и задаем её позицию
    rec_btn_rect = record_btn.get_rect(topleft=(210, 380))  # Создаем Rect для кнопки "Рекорд" и задаем её позицию

    # Работа над текстом  # Создаём шрифт
    text = FONT.render("Проклятие лягушачьего рыцаря", True, (255, 255, 255))  # Создаем текст
    text_x = 125  # X-координата текста
    text_y = 125  # Y-координата текста

    # смена (отрисовка) кадра:
    def draw(screen):
        screen.blit(bg, (0, 0))
        screen.blit(text, (text_x, text_y))  # Отображаем текст на экране
        screen.blit(st_btn, st_btn_rect)  # Отображаем кнопку "Старт" на экране
        screen.blit(qt_btn, qt_btn_rect)  # Отображаем кнопку "Выход" на экране
        screen.blit(login_btn, log_btn_rect)  # Отображаем кнопку "Пользователь" на экране
        screen.blit(record_btn, rec_btn_rect)  # Отображаем кнопку "Рекорд" на экране
    pygame.display.flip()  # Обновляем экран

    running = True  # Флаг, указывающий, активно ли меню
    while running:  # Главный цикл меню
        clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если пользователь закрыл окно
                pygame.quit()  # Завершаем работу Pygame
                sys.exit()  # Завершаем работу программы

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if st_btn_rect.collidepoint(event.pos) and name:  # Если клик пришелся на кнопку "Старт"
                    SOUND_ON_BUTTON.play()  # Проигрываем звук нажатия кнопки
                    lvl_page(screen)  # Открываем окно выбора уровня

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if qt_btn_rect.collidepoint(event.pos):  # Если клик пришелся на кнопку "Выход"
                    SOUND_ON_BUTTON.play()
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if rec_btn_rect.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    record(screen)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if log_btn_rect.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    login(screen)

        draw(screen)
        # Наводка на кнопку
        contour(screen, st_btn_rect, 'Buttons/click_start_btn.png', 'Buttons/start_btn.png')  # Отображаем кнопку "Старт" с эффектом наведения

        contour(screen, qt_btn_rect, 'Buttons/click_qt_btn.png', 'Buttons/quit_btn.png')  # Отображаем кнопку "Выход" с эффектом наведения

        contour(screen, log_btn_rect, 'Buttons/click_login.png', 'Buttons/login.png')  # Отображаем кнопку "Пользователь" с эффектом наведения

        contour(screen, rec_btn_rect, 'Buttons/click_record.png', 'Buttons/record.png')  # Отображаем кнопку "Рекорд" с эффектом наведения
        cursor(screen)
        pygame.display.update()  # Обновляем экран

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
        if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
            play_random_music()  # Запускаем случайный трек из списка


# Функция окна с выбором уровня
def lvl_page(screen):
    global current_music  # Используем глобальную переменную для отслеживания текущей музыки

    bg = pygame.image.load(BACKGROUND_FOR_MENU)  # Загружаем изображение фона для меню
    bg = pygame.transform.flip(bg, True, False)  # Отражаем изображение фона по горизонтали
    screen.blit(bg, (0, 0))  # Отображаем фон на экране

    # Кнопки уровней
    level_1 = pygame.image.load("Buttons/lvl1.png")  # Загружаем изображение кнопки уровня 1
    level_2 = pygame.image.load("Buttons/lvl2.png")  # Загружаем изображение кнопки уровня 2
    level_3 = pygame.image.load("Buttons/lvl3.png")  # Загружаем изображение кнопки уровня 3
    back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"

    # Rect_of_levels
    rect_level_1 = level_1.get_rect(topleft=(175, 250))  # Создаем Rect для кнопки уровня 1 и задаем её позицию
    rect_level_2 = level_2.get_rect(topleft=(360, 250))  # Создаем Rect для кнопки уровня 2 и задаем её позицию
    rect_level_3 = level_3.get_rect(topleft=(550, 250))  # Создаем Rect для кнопки уровня 3 и задаем её позицию
    rect_back = back.get_rect(topleft=(10, 45))  # Создаем Rect для кнопки "Назад" и задаем её позицию


    def draw(screen):
        screen.blit(bg, (0, 0))
        screen.blit(text, (text_x, text_y))  # Отображаем текст на экране
        screen.blit(level_1, rect_level_1)  # Отображаем кнопку уровня 1 на экране
        screen.blit(level_2, rect_level_2)  # Отображаем кнопку уровня 2 на экране
        screen.blit(level_3, rect_level_3)  # Отображаем кнопку уровня 3 на экране
        screen.blit(back, rect_back)  # Отображаем кнопку "Назад" на экране

    # Смена кадра
    pygame.display.flip()  # Обновляем экран
    fl_s = True
    # Цикл действий
    running = True  # Флаг, указывающий, активна ли страница выбора уровня
    while running:  # Главный цикл страницы выбора уровня
        clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если пользователь закрыл окно
                pygame.quit()  # Завершаем работу Pygame
                sys.exit()  # Завершаем работу программы

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if rect_back.collidepoint(event.pos):  # Если клик пришелся на кнопку "Назад"
                    SOUND_ON_BUTTON.play()  # Проигрываем звук нажатия кнопки
                    main_menu(screen)  # Возвращаемся в главное меню

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if rect_level_1.collidepoint(event.pos):  # Если клик пришелся на кнопку уровня 1
                    SOUND_ON_BUTTON.play()  # Проигрываем звук нажатия кнопки
                    start_level(screen, 1)  # Запускаем уровень 1

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_level_2.collidepoint(event.pos) and is_level_unlocked(2):  # Если клик пришелся на кнопку уровня 2
                    SOUND_ON_BUTTON.play()
                    start_level(screen, 2)
                elif rect_level_2.collidepoint(event.pos):
                    fl_s = False  # Выводим сообщение в консоль

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_level_3.collidepoint(event.pos) and is_level_unlocked(3):  # Если клик пришелся на кнопку уровня 3 и уровень разблокирован
                    SOUND_ON_BUTTON.play()
                    start_level(screen, 3)
                elif rect_level_3.collidepoint(event.pos):  # Если клик пришелся на кнопку уровня 3, но уровень заблокирован
                    fl_s = False

        # Текст
        if fl_s:
            s = "Выберите уровень"
        else:
            s = "Уровень заблокирован"
        text = FONT.render(s, True, pygame.Color('#71f0f0'))  # Создаем текст
        text_x = 400 - text.get_width() // 2  # X-координата текста
        text_y = 90  # Y-координата текста

        draw(screen)
        # Наводка на кнопки
        contour(screen, rect_level_1, 'Buttons/cl_lvl1.png', 'Buttons/lvl1.png')  # Отображаем кнопку уровня 1 с эффектом наведения

        contour(screen, rect_level_2, 'Buttons/cl_lvl2.png', 'Buttons/lvl2.png')  # Отображаем кнопку уровня 2 с эффектом наведения

        contour(screen, rect_level_3, 'Buttons/cl_lvl3.png', 'Buttons/lvl3.png')  # Отображаем кнопку уровня 3 с эффектом наведения

        contour(screen, rect_back, 'Buttons/cl_back.png', 'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
        cursor(screen)
        pygame.display.update()  # Обновляем экран

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
        if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
            play_random_music()  # Запускаем случайный трек из списка


# Функция старта уровня
def start_level(screen, level_number):
    global level1_music  # Используем глобальную переменную для музыки уровня 1 (если она есть)
    global level1_music_playing  # Используем глобальную переменную для отслеживания состояния проигрывания музыки уровня 1
    global name

    level1_music_playing = True  # Устанавливаем флаг проигрывания музыки уровня в True
    pygame.mouse.set_visible(True)
    pygame.mixer.music.load(MUSIC_ON_LEVEL)  # Загрузка музыки для уровня
    pygame.mixer.music.play(-1)  # Запуск музыки, -1 означает бесконечный повтор

    back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"
    rect_back = back.get_rect(topleft=(10, 25))  # Создаем Rect для кнопки "Назад" и задаем её позицию

    fl_coin = True

    coin = update_bd(name, "how_coins", 0)
    if coin >= level_number * 3:
        fl_coin = False
    level_map = Map(f"Tiledmap/tmx/test_map{level_number}.tmx", level_number)
    sprites = level_map.coin_group  # Получаем группу спрайтов монет из карты уровня
    level_map.view_player()  # Создаем объект игрока (Frog) на карте уровня

    player = level_map.Player  # Получаем ссылку на объект игрока из карты уровня

    update_bd(name, "death_0", 0)

    while level1_music_playing:  # Главный цикл игрового уровня (пока музыка уровня проигрывается)
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если пользователь закрыл окно
                pygame.quit()  # Завершаем работу Pygame
                sys.exit()  # Завершаем работу программы

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if rect_back.collidepoint(event.pos):  # Если клик пришелся на кнопку "Назад"
                    SOUND_ON_BUTTON.play()  # Проигрываем звук нажатия кнопки
                    pygame.mixer.music.stop()  # Останавливаем музыку уровня
                    level1_music_playing = False   # Устанавливаем флаг проигрывания музыки уровня в False
                    lvl_page(screen)  # Переходим на страницу выбора уровня

        # Переход на следующий уровень
        if player.rect.right >= WIDTH and not sprites:  # Если игрок достиг правой границы экрана и все монеты собраны
            update_bd(name, "how_death", n=level_number)
            if fl_coin:
                update_bd(name, "coin", n=level_number * 3)

            pygame.mixer.music.stop()
            level1_music_playing = False  # Устанавливаем флаг проигрывания музыки уровня в False
            if level_number < 3:
                # Если не последний уровень - запускаем следующий уровень
                start_level(screen, level_number + 1)
            else:  # Если последний уровень - возвращаемся в меню выбора уровня.
                final(screen)
            return
        elif player.rect.right >= WIDTH and sprites:
            player.reset()

        # Наводка на кнопку
        contour(screen, rect_back, 'Buttons/cl_back.png', 'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
        pygame.display.update()  # Обновляем экран

        clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS

        pygame.event.pump()  # Обрабатываем события Pygame
        player.update()  # Обновляем состояние игрока

        # Рисуем
        screen.fill(BACKGROUND)  # Заполняем экран цветом фона
        level_map.render(screen)  # Отрисовываем карту уровня
        screen.blit(back, rect_back)  # Кнопка назад # Отображаем кнопку "Назад" на экране
        player.draw(screen)  # Отрисовываем игрока на экране
        for coin in level_map.coin_group:  # Итерируем все монеты и вызываем функцию update для анимации
            coin.update()  # анимация монет

        for fire in level_map.fire_group:
            fire.update()

        for torch in level_map.torch_group:
            torch.update()

        # Обновляем
        pygame.display.flip()  # Обновляем экран


# Функция окна с рекорадми
def record(screen):
    global current_music  # Используем глобальную переменную для отслеживания текущей музыки

    bg = pygame.image.load(BACKGROUND_FOR_RECORD)

    back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"
    rect_back = back.get_rect(topleft=(10, 45))

    def draw(screen):
        screen.blit(bg, (0, 0))  # Отображаем фон на экране
        screen.blit(back, rect_back)  # Отображаем кнопку "Назад" на экране
        records = update_bd(True, "record", 0)
        # текст
        text = FONT.render("Рекорды", True, pygame.Color('#71f0f0'))
        text_x = 400 - text.get_width() // 2
        text_y = 70
        screen.blit(text, (text_x, text_y))
        column = FONT.render("name lvl1 lvl2 lv3 all", True, pygame.Color('#71f0f0'))
        column_x = 400 - column.get_width() // 2
        screen.blit(column, (column_x, 135))
        for i in range(5):
            if i < len(records):
                s = str(i + 1) + ") " + "  ".join([str(el) for el in records[i]])
                text_rec = FONT.render(s, True, pygame.Color('#71f0f0'))
                text_rec_x = 400 - text_rec.get_width() // 2
                text_rec_y = 200 + i * 75
                screen.blit(text_rec, (text_rec_x, text_rec_y))
            else:
                pass

    pygame.display.flip()  # Обновляем экран
    running = True
    while running:
        clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если пользователь закрыл окно
                pygame.quit()  # Завершаем работу Pygame
                sys.exit()  # Завершаем работу программы

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Если нажата левая кнопка мыши
                if rect_back.collidepoint(event.pos):  # Если клик пришелся на кнопку "Назад"
                    SOUND_ON_BUTTON.play()  # Проигрываем звук нажатия кнопки
                    main_menu(screen)  # Возвращаемся в главное меню

        draw(screen)
        contour(screen, rect_back, 'Buttons/cl_back.png',
                'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
        cursor(screen)
        pygame.display.update()

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
    if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
        play_random_music()  # Запускаем случайный трек из списка


def final(screen):
    global current_music  # Используем глобальную переменную для отслеживания текущей музыки
    global name

    def draw(screen):
        screen.blit(bg, (0, 0))
        screen.blit(back, rect_back)
        screen.blit(win, (win_x, win_y))

    bg = pygame.image.load(BACKGROUND_FOR_FINAL)

    back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"
    rect_back = back.get_rect(topleft=(10, 45))

    win = FONT.render("Поздравляем с победой!", True, pygame.Color('#2ca3b8'))
    win_x = 400 - win.get_width() // 2
    win_y = 270 - win.get_height() // 2

    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если пользователь закрыл окно
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_back.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    main_menu(screen)

        draw(screen)
        contour(screen, rect_back, 'Buttons/cl_back.png',
                'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
        cursor(screen)
        pygame.display.flip()

    if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
        play_random_music()  # Запускаем случайный трек из списка


def login(screen):
    global current_music  # Используем глобальную переменную для отслеживания текущей музыки
    global name

    def draw(screen):
        screen.blit(bg, (0, 0))
        screen.blit(back, rect_back)
        screen.blit(save, rect_save)
        screen.blit(avt, (avt_x, avt_y))
        screen.blit(message, (mes_x, mes_y))

    bg = pygame.image.load(BACKGROUND_FOR_LOGIN)  # Загружаем изображение фона для логина
    # текст
    avt = FONT.render("Авторизация", True, pygame.Color('#71f0f0'))
    avt_x = 400 - avt.get_width() // 2
    avt_y = 90

    back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"
    rect_back = back.get_rect(topleft=(10, 45))
    save = pygame.image.load("Buttons/save_btn.png")  # Загружаем изображение кнопки "Сохранить"
    rect_save = back.get_rect(topleft=(300, 360))

    fl = 1
    clock = pygame.time.Clock()
    input_box = pygame.Rect(200, 270, 407, 52)
    color_inactive = pygame.Color('black')
    color_active = pygame.Color('#71f0f0')
    color = color_inactive
    active = False
    text = ''

    running = True
    while running:
        clock.tick(60)  # Устанавливаем максимальную частоту кадров в 60 FPS
        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если пользователь закрыл окно
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_back.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    main_menu(screen)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_save.collidepoint(event.pos):
                    SOUND_ON_BUTTON.play()
                    if update_bd(text, "users", 0):
                        name = text
                        fl = 3
                    else:
                        fl = 2
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        print(text)
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 12:
                            text += event.unicode
        if fl == 1:
            s = "Введите имя:"
        elif fl == 2:
            s = "Имя уже занято"
        elif fl == 3:
            s = "Имя сохранено"
        message = FONT.render(s, True, pygame.Color('#71f0f0'))
        mes_x = 400 - message.get_width() // 2
        mes_y = 180

        draw(screen)

        txt_surface = FONT.render(text, True, color)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        contour(screen, rect_save, 'Buttons/click_save_btn.png',
                'Buttons/save_btn.png')  # Отображаем кнопку "Назад" с эффектом наведения

        contour(screen, rect_back, 'Buttons/cl_back.png',
                'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
        cursor(screen)
        pygame.display.flip()

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
    if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
        play_random_music()  # Запускаем случайный трек из списка


# -------------- Функция уровня 1
def level1(screen):
    start_level(screen, 1)


# -------------- Функция уровня 2
def level2(screen):
    start_level(screen, 2)


# -------------- Функция уровня 3
def level3(screen):
    start_level(screen, 3)


clock = pygame.time.Clock()  # Создаем объект Clock для управления частотой кадров
pygame.font.init()

# Константы
WIDTH = 800  # Длина окна
HEIGHT = 600  # Высота окна
BACKGROUND = 'black'  # Чёрный цвет для заднего фона
BACKGROUND_FOR_MENU = 'Backgrounds/menu_bg.jpg'  # Путь к изображению фона для меню
MUSIC_ON_LEVEL = 'Sounds/dungeoun_music.mp3'  # Путь к музыкальному файлу для уровня
BACKGROUND_FOR_RECORD = "Backgrounds/record_fon.jpg"
BACKGROUND_FOR_LOGIN = "Backgrounds/login.png"
BACKGROUND_FOR_FINAL = "Backgrounds/final.jpg"
DEATH_ANIMATION_DURATION = 1  # Длительность анимации смерти в секундах
DEATH_FRAMES = 8  # Кол-во кадров смерти
COIN_ANIMATION_SPEED = 0.2  # Скорость анимации монет
FONT = pygame.font.Font(None, 52)
name = ""

# Список музыки для меню
MENU_MUSIC = [
    'Sounds/menu_music1.mp3',
    'Sounds/menu_music2.mp3',
    'Sounds/menu_music3.mp3'
]  # Список путей к музыкальным файлам для меню

# Инициализация Pygame Mixer (звук)
pygame.mixer.init()  # Инициализируем модуль mixer для работы со звуком
SOUND_ON_BUTTON = pygame.mixer.Sound("Sounds/click_on_button.mp3")  # Загружаем звуковой эффект для нажатия кнопки
pygame.mixer.music.set_volume(1)  # Устанавливаем громкость музыки на 100%

# Создание окна
pygame.init()  # Инициализируем Pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Создаем окно

# Переменная для текущей музыки
# Запоменает текущий играющий трек, чтобы избежать повторного воспроизведения одного и того же трека подряд
current_music = None  # Инициализируем переменную для хранения текущего трека

# Запускаем первую музыку при запуске игры
play_random_music()  # Запускаем проигрывание случайного трека из списка

# Меню игры
main_menu(screen)  # Запускаем главное меню игры

# Завершаем работу Pygame
pygame.quit()