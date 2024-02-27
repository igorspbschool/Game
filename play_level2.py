import pygame
import os
import sys
from random import randrange
from game_over import main  as game_over_main
from victory_final import main as victory_final_main

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
FPS = 12
MAPS_DIR = "maps"
TILE_SIZE = 50
ENEMY_EVENT_TYPE = pygame.USEREVENT + 5
ENEMY_SPAWN_INTERVAL = 1000


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


class Labyrinth:
    def __init__(self, filename, free_tile, finish_tile):
        self.map = []
        with open(f"{MAPS_DIR}/{filename}") as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        # print(self.map)
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.tile_size = TILE_SIZE
        self.free_tiles = free_tile
        self.finish_tile = finish_tile
        self.tile_images = self.load_tile_images()

    def load_tile_images(self):
        return {
            0: load_image('pole.png'),
            1: load_image('box.png'),
            2: load_image('freze.png')
        }

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.get_tile_id((x, y))
                image = self.tile_images.get(tile_type)
                if image:
                    rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                       self.tile_size, self.tile_size)
                    screen.blit(image, rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        INF = 1080
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.height and self.is_free(
                        (next_x, next_y)) and \
                        distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy):
        super().__init__()
        self.fire = load_image("star.png")
        self.image = self.fire
        self.rect = self.image.get_rect()
        self.screen_rect = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.center = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 10

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(self.screen_rect):
            self.kill()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(
                    sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Hero(AnimatedSprite):
    def __init__(self, sheet_right, columns, rows, x, y):
        super().__init__(sheet_right, columns, rows, x, y)
        self.frames_right = self.frames.copy()
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in
                            self.frames_right]
        self.direction = "right"

    def update_position(self, position):
        prev_rect = self.rect.copy()
        self.rect.topleft = (position[0] * TILE_SIZE, position[1] * TILE_SIZE)

        # Провер направл движ и выбираем список кадров
        if self.rect.left < prev_rect.left:
            self.direction = "left"
        elif self.rect.left > prev_rect.left:
            self.direction = "right"

        # Обновл кадр в зависимости от направления
        if self.direction == "left":
            self.frames = self.frames_left
        else:
            self.frames = self.frames_right

        self.image = self.frames[self.cur_frame]


class Enemy(AnimatedSprite):
    def __init__(self, sheet_right, columns, rows, x, y):
        super().__init__(sheet_right, columns, rows, x, y)
        self.frames_right = self.frames.copy()
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in
                            self.frames_right]
        self.direction = "right"
        # self.frozen = False

    def update_position(self, position):
        # if not self.frozen:
        prev_rect = self.rect.copy()
        self.rect.topleft = (position[0] * TILE_SIZE, position[1] * TILE_SIZE)

        if self.rect.left < prev_rect.left:
            self.direction = "left"
        elif self.rect.left > prev_rect.left:
            self.direction = "right"

        if self.direction == "left":
            self.frames = self.frames_left
        else:
            self.frames = self.frames_right

        self.image = self.frames[self.cur_frame]


class Zoloto(AnimatedSprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(sheet, columns, rows, x, y)

    def update(self):
        super().update()
        # В планах добавить движ звезд если время будет


class Bomb(pygame.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y):
        super().__init__()
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (tile_x * TILE_SIZE, tile_y * TILE_SIZE)
        # Задержка перед исчезновением после столкновения
        self.collided_time = 0
        self.explosion_delay = 500

    def update(self):
        # Если прошло врем после столкн удалить бомбу
        if self.collided_time != 0 and pygame.time.get_ticks() - self.collided_time > self.explosion_delay:
            self.kill()
        else:
            self.rect = self.rect.move(randrange(3) - 1,
                                       randrange(3) - 1)
            if self.rect.x < self.tile_x * TILE_SIZE - 5:
                self.rect.x = self.tile_x * TILE_SIZE
            if self.rect.x + 50 > self.tile_x * TILE_SIZE + 55:
                self.rect.x = self.tile_x * TILE_SIZE
            if self.rect.y < self.tile_y * TILE_SIZE - 5:
                self.rect.y = self.tile_y * TILE_SIZE
            if self.rect.y + 50 > self.tile_y * TILE_SIZE + 55:
                self.rect.y = self.tile_y * TILE_SIZE

    def collide_with_enemy(self):
        # Вызыв при столкн с врагом
        self.collided_time = pygame.time.get_ticks()


class Game():
    def __init__(self, labyrinth, hero_group, enemy_group, zoloto_group, particle_group,
                 reiting):
        self.labyrinth = labyrinth
        self.hero_group = hero_group
        self.enemy_group = enemy_group
        self.zoloto_group = zoloto_group
        self.particle_group = particle_group
        self.hero = hero_group.sprites()[0]
        self.enemy_timer = 0
        self.last_enemy_update = pygame.time.get_ticks()
        self.reiting_level2 = 0
        self.amount_enemy = 0

        self.bomb_group = pygame.sprite.Group()

        self.bomb_boom = load_image("boom.png")
        self.reiting_final = reiting

        # Таймер для генер врагов
        pygame.time.set_timer(ENEMY_EVENT_TYPE, ENEMY_SPAWN_INTERVAL)

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero_group.draw(screen)
        self.zoloto_group.draw(screen)
        self.enemy_group.draw(screen)
        self.particle_group.draw(screen)

    def update_hero(self):
        next_x, next_y = self.hero.rect.topleft
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= TILE_SIZE
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += TILE_SIZE
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= TILE_SIZE
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += TILE_SIZE
        if self.labyrinth.is_free((next_x // TILE_SIZE, next_y // TILE_SIZE)):
            self.hero.update_position((next_x // TILE_SIZE, next_y // TILE_SIZE))

        collided_zoloto = pygame.sprite.spritecollide(self.hero, self.zoloto_group, True)
        if collided_zoloto:
            self.reiting_level2 += 1
            for zoloto in collided_zoloto:
                zoloto.kill()
                for _ in range(10):
                    particle = Particle(zoloto.rect.center, randrange(-10, 10),
                                        randrange(-10, 10))
                    self.particle_group.add(particle)
        # print(self.reiting)
        # Рейтинг в зависимости от затрат времени на уровень
        time_game = pygame.time.get_ticks() // 1000
        # print(time_game)
        if self.reiting_level2 == 30:
            itog_time_reitig = self.reiting_level2 + self.reiting_final
            if time_game < 60:
                itog_time_reitig += 20
            elif time_game > 60 and time_game < 80:
                itog_time_reitig += 10
            else:
                itog_time_reitig += 5
            pygame.quit()
            victory_final_main(itog_time_reitig)
            terminate()

    def spawn_enemy(self):
        # print(pygame.time.get_ticks() // 1000)
        # Генерю координаты врага по нужным тайлам и в пределах от игрока не более
        # врагов, потом по сложности расчитаю

        while True:
            # print(amount_enemy)
            y_enemy = randrange(len(self.labyrinth.map))
            x_enemy = randrange(len(self.labyrinth.map[y_enemy]))
            if self.labyrinth.map[y_enemy][x_enemy] == 0 and abs(
                    x_enemy * TILE_SIZE - self.hero.rect.topleft[0]) > 100 and abs(
                y_enemy * TILE_SIZE - self.hero.rect.topleft[1]) > 100:
                break

        # print(y_enemy, x_enemy)
        # print(abs(x_enemy * TILE_SIZE - self.hero.rect.topleft[0]) > 100, abs(y_enemy * TILE_SIZE - self.hero.rect.topleft[1]))

        # Враги с определенным количеством
        if pygame.time.get_ticks() // 1000 > 15 and self.amount_enemy < 15:
            enemy_sprite = Enemy(load_image('enemy.png'), columns=5, rows=2,
                                 x=x_enemy * TILE_SIZE, y=y_enemy * TILE_SIZE)
            self.enemy_group.add(enemy_sprite)
            self.amount_enemy += 1

    def move_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_update > 4000 // FPS:
            # Провер где герой на клетке с изображением отдыха
            hero_position = (self.hero.rect.topleft[0] // TILE_SIZE,
                             self.hero.rect.topleft[1] // TILE_SIZE)
            if self.labyrinth.get_tile_id(hero_position) == 2:
                return  # Если герой на клетке отдыха тормоз для врагов
            for enemy in self.enemy_group:
                next_position = self.labyrinth.find_path_step(
                    (enemy.rect.topleft[0] // TILE_SIZE,
                     enemy.rect.topleft[1] // TILE_SIZE),
                    (self.hero.rect.topleft[0] // TILE_SIZE,
                     self.hero.rect.topleft[1] // TILE_SIZE))
                collided_enemies = pygame.sprite.spritecollide(self.hero,
                                                               self.enemy_group, False)
                if collided_enemies:
                    pygame.quit()
                    game_over_main()
                    terminate()
                else:
                    enemy.update_position(next_position)
                for bomb in self.bomb_group:
                    if pygame.sprite.collide_rect(enemy, bomb):
                        enemy.kill()
                        bomb.image = self.bomb_boom
                        bomb.collide_with_enemy()
            self.last_enemy_update = current_time

    def handle_events(self, event):
        if event.type == ENEMY_EVENT_TYPE:
            self.spawn_enemy()


def main(reiting):
    # Время для расст бомб
    start_post_bomb = 15

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)

    labyrinth = Labyrinth("map1.txt", [0, 2], 2)
    hero_sprite = Hero(load_image('12.png'), columns=6, rows=2,
                       x=300, y=300)

    hero_group = pygame.sprite.Group(hero_sprite)
    enemy_group = pygame.sprite.Group()
    particle_group = pygame.sprite.Group()

    # Генерация 30 звезд в правильных координатах!!!!!! ТЯЖКО ДАЛАСЬ ЗАПОМНИТЬ НА БУДУЩЕЕ
    proverka_koord_zolot = []
    zoloto_group = pygame.sprite.Group()
    with open(f"{MAPS_DIR}/map1.txt") as input_file:
        map_for_zoloto = []
        for line in input_file:
            map_for_zoloto.append(list(map(int, line.split())))
    for _ in range(30):
        while True:
            while True:
                y_zolot = randrange(0, len(map_for_zoloto))
                if map_for_zoloto[y_zolot].count(0) > 0:
                    break
            while True:
                x_zolot = randrange(0, len(map_for_zoloto[y_zolot]))
                if map_for_zoloto[y_zolot][x_zolot] == 0:
                    break
            if (x_zolot, y_zolot) not in proverka_koord_zolot:
                proverka_koord_zolot.append((x_zolot, y_zolot))
                break
        zoloto_sprite = Zoloto(load_image('zoloto.png'),
                               columns=7, rows=1, x=x_zolot * TILE_SIZE,
                               y=y_zolot * TILE_SIZE)
        zoloto_group.add(zoloto_sprite)
    # print(len(proverka_koord_zolot), len(set(proverka_koord_zolot)))
    game = Game(labyrinth, hero_group, enemy_group, zoloto_group, particle_group, reiting)

    # количество бомб
    amount_bomb = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and amount_bomb:
                mouse_pos = pygame.mouse.get_pos()
                tile_x = mouse_pos[0] // TILE_SIZE
                tile_y = mouse_pos[1] // TILE_SIZE
                bomb_sprite = Bomb(load_image('bomb.png'), tile_x, tile_y)
                game.bomb_group.add(bomb_sprite)
                if len(game.bomb_group) == 15:
                    amount_bomb = False

        game.move_enemy()
        if not amount_bomb:
            game.update_hero()
        enemy_group.update()
        hero_group.update()
        zoloto_group.update()
        particle_group.update()

        screen.fill((0, 0, 0))

        game.render(screen)
        game.bomb_group.draw(screen)
        particle_group.draw(screen)

        game.bomb_group.update()

        time_to_start_enemy = start_post_bomb - pygame.time.get_ticks() // 1000
        if time_to_start_enemy > 0:
            time_text = font.render(
                f"Минируйте поле, враги на подходе: {time_to_start_enemy}", True,
                (255, 255, 255))
            screen.blit(time_text, (10, 2))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
