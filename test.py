import pygame


pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Крест")
# формирование кадра:
# команды рисования на холсте
pygame.draw.rect(screen, (255, 0, 0), (0, 0, 100, 100))
# смена (отрисовка) кадра:
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
# завершение работы:
pygame.quit()