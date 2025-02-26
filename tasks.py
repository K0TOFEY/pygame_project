import pygame
import sys
import pytmx
import random
import time
import sqlite3

def contour(screen, rect, first_file, second_file):  # Наводка на кнопку
    """Делает эффект наводки на кнопку"""
    if rect.collidepoint(pygame.mouse.get_pos()):  # Проверяем, находится ли курсор мыши над кнопкой
        btn = pygame.image.load(f"{first_file}")  # Загружаем изображение для состояния "наведена мышь"
        screen.blit(btn, rect)  # Отображаем изображение на экране
    else:  # Если курсор мыши не над кнопкой
        btn = pygame.image.load(f"{second_file}")  # Загружаем изображение для обычного состояния
        screen.blit(btn, rect)  # Отображаем изображение на экране

def cursor(screen):
    pygame.mouse.set_visible(False)
    cursor_image = pygame.image.load('Sprites/cursor.png')
    cursor_rect = cursor_image.get_rect()
    if pygame.mouse.get_focused():
        cursor_rect.topleft = pygame.mouse.get_pos()  # Получаем позицию
        screen.blit(cursor_image, cursor_rect)

def play_random_music():  # Проигрыш музыки в меню
    """Воспроизводит случайную музыку из списка MENU_MUSIC в меню."""
    global current_music  # Используем глобальную переменную current_music, чтобы запоминать текущую музыку
    next_music = random.choice(MENU_MUSIC)  # Выбираем случайный трек из списка MENU_MUSIC
    if next_music != current_music:  # Проверяем, чтобы следующий трек не был таким же, как текущий
        pygame.mixer.music.load(next_music)  # Загружаем выбранный трек в проигрыватель
        pygame.mixer.music.play()  # Запускаем воспроизведение трека
        pygame.mixer.music.set_volume(0.02)  # Устанавливаем громкость трека на 50%
        current_music = next_music  # Обновляем значение current_music, чтобы запомнить, какой трек сейчас играет


def login(screen):
    global current_music  # Используем глобальную переменную для отслеживания текущей музыки
    global name

    def draw(screen):
        screen.blit(bg, (0, 0))
        screen.blit(back, rect_back)
        screen.blit(w, (w_x, w_y))

    bg = pygame.image.load(BACKGROUND_FOR_FINAL)  # Загружаем изображение фона для логина
    # текст
    w = FONT.render("Авторизация", True, pygame.Color('#71f0f0'))
    w_x = 400 - w.get_width() // 2
    w_y = 90

    back = pygame.image.load("Buttons/back.png")  # Загружаем изображение кнопки "Назад"
    rect_back = back.get_rect(topleft=(10, 45))

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
                    pass

        draw(screen)
        contour(screen, rect_back, 'Buttons/cl_back.png',
                'Buttons/back.png')  # Отображаем кнопку "Назад" с эффектом наведения
        cursor(screen)
        pygame.display.flip()

        # Проверяем, закончилась ли музыка, и если да, то включаем следующую
    if not pygame.mixer.music.get_busy():  # Если музыка не проигрывается
        play_random_music()  # Запускаем случайный трек из списка


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
login(screen)  # Запускаем главное меню игры

# Завершаем работу Pygame
pygame.quit()