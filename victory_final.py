import pygame
import os
import sys
import random

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
FPS = 12


def terminate():
    pygame.quit()
    sys.exit()


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


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, all_sprites, pos, dx, dy, screen_rect):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 0.5
        self.screen_rect = screen_rect

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.screen_rect):
            self.kill()


def create_particles(all_sprites, position, screen_rect):
    particle = Particle(all_sprites, position, random.randrange(-5, 6),
                        random.randrange(-5, 0), screen_rect)
    all_sprites.add(particle)


def main(reiting):
    reiting = reiting
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen_rect = screen.get_rect()
    all_sprites = pygame.sprite.Group()
    background_image = load_image("kubok.png")
    background_rect = background_image.get_rect()
    background_rect.topleft = (300, 50)
    font = pygame.font.Font(None, 25)
    font1 = pygame.font.Font(None, 36)
    font2 = pygame.font.Font(None, 50)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        create_particles(all_sprites, pygame.mouse.get_pos(), screen_rect)
        create_particles(all_sprites, (WINDOW_WIDTH // 2 - 10, WINDOW_HEIGHT // 2 - 250),
                         screen_rect)

        all_sprites.update()
        screen.fill((0, 0, 0))
        screen.blit(background_image, background_rect)
        all_sprites.draw(screen)
        text = font.render("Ваш рейтинг", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2 - 10, 464))
        screen.blit(text, text_rect)
        text1 = font1.render(f"{reiting}", True, (255, 0, 0))
        text_rect1 = text1.get_rect(center=(WINDOW_WIDTH // 2 - 10, 483))
        screen.blit(text1, text_rect1)
        text2 = font2.render("УРААААА!!! ПОБЕДА!", True,
                             (0, 255, 255))
        text_rect2 = text2.get_rect(center=(WINDOW_WIDTH // 2 - 10, 300))
        screen.blit(text2, text_rect2)
        pygame.display.flip()
        clock.tick(50)

    pygame.quit()