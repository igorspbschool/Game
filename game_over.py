import pygame
import os
import sys
import random

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 576, 576
FPS = 15
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, text_coord):
    intro_text = [
        "Очень жаль, темные рыцари одержали победу в этой схватке!",
        "Совет добрых планет сообщил,",
        "   что можно вернуться с новой стратегией!",
        "Перезапустите выполнение миссии."
    ]

    fon = pygame.transform.scale(load_image('fon1.jpg'), (WINDOW_SIZE))
    screen.blit(fon, (0, 0))
    fon = pygame.transform.scale(load_image('game_over.png'), (WINDOW_SIZE))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 26)
    text_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    text_surface.fill((0, 0, 0, 100))

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height + 10
        text_surface.blit(string_rendered, intro_rect)
    screen.blit(text_surface, (0, 0))


def draw_stars(screen, number_of_stars):
    for _ in range(number_of_stars):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        brightness = random.randint(100, 255)
        pygame.draw.circle(screen, pygame.Color(brightness, brightness, brightness),
                           (x, y), 1)


def main():
    pygame.init()
    reiting = 0
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    running = True
    text_coord = 576
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        text_coord -= 1
        screen.fill((0, 0, 0))
        start_screen(screen, text_coord)
        draw_stars(screen, 5)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
