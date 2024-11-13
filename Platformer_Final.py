import pygame
from pygame.locals import *
import sys
import random
import time

# Инициализация Pygame
pygame.init()
vec = pygame.math.Vector2  # Вектор для двухмерных операций

# Параметры игры
HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60

FramePerSec = pygame.time.Clock()  # Создаем объект для контроля кадров в секунду

# Создаем окно дисплея
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

# Загрузка фона
background = pygame.image.load("background.png")


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Загрузка и масштабирование изображения игрока
        self.surf = pygame.image.load("player.png")
        self.surf = pygame.transform.scale(self.surf, (30, 30))  # Уменьшаем размер игрока
        self.rect = self.surf.get_rect()

        # Позиция, скорость и ускорение игрока
        self.pos = vec((10, 360))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jumping = False
        self.score = 0  # Счет игрока

    # Метод для передвижения игрока
    def move(self):
        self.acc = vec(0, 0.5)  # Гравитация

        # Получение нажатий клавиш
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC

        # Применение трения, ускорение и передвижение
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Выход за пределы экрана по горизонтали
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    # Метод прыжка
    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -15

    # Отмена прыжка
    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    # Метод обновления для проверки столкновений
    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if hits:
                if self.pos.y < hits[0].rect.bottom:
                    if hits[0].point == True:
                        hits[0].point = False
                        self.score += 1
                    self.pos.y = hits[0].rect.top + 1
                    self.vel.y = 0
                    self.jumping = False


# Класс платформ
class platform(pygame.sprite.Sprite):
    def __init__(self, width=0, height=18):
        super().__init__()

        if width == 0:
            width = random.randint(50, 120)

        # Загрузка изображения платформы и изменение размера
        self.image = pygame.image.load("platform.png")
        self.surf = pygame.transform.scale(self.image, (width, height))
        self.rect = self.surf.get_rect(center=(random.randint(0, WIDTH - 10),
                                               random.randint(0, HEIGHT - 30)))
        self.point = True
        self.moving = True
        self.speed = random.randint(-1, 1)

        if self.speed == 0:
            self.moving = False

    # Метод для передвижения платформы
    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving:
            self.rect.move_ip(self.speed, 0)
            if hits:
                P1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH


# Функция для генерации платформ
def plat_gen():
    while len(platforms) < 6:
        width = random.randrange(50, 100)
        p = None
        C = True

        while C:
            p = platform()
            p.rect.center = (random.randrange(0, WIDTH - width),
                             random.randrange(-50, 0))
            C = check(p, platforms)

        platforms.add(p)
        all_sprites.add(p)


# Проверка пересечений платформ
def check(platform, groupies):
    if pygame.sprite.spritecollideany(platform, groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (
                    abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
    return False


# Основной игровой цикл и создание объектов
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

PT1 = platform(450, 80)
PT1.rect = PT1.surf.get_rect(center=(WIDTH / 2, HEIGHT - 10))
PT1.moving = False
PT1.point = False

P1 = Player()

all_sprites.add(PT1)
all_sprites.add(P1)
platforms.add(PT1)

for x in range(random.randint(4, 5)):
    C = True
    pl = platform()
    while C:
        pl = platform()
        C = check(pl, platforms)

    platforms.add(pl)
    all_sprites.add(pl)

# Основной цикл игры
while True:
    P1.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                P1.cancel_jump()

    # Проверка выхода за пределы экрана по вертикали
    if P1.rect.top > HEIGHT:
        for entity in all_sprites:
            entity.kill()
            time.sleep(1)
            displaysurface.fill((255, 0, 0))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            sys.exit()

    # Перемещение платформ при достижении игроком верхней границы
    if P1.rect.top <= HEIGHT / 3:
        P1.pos.y += abs(P1.vel.y)
        for plat in platforms:
            plat.rect.y += abs(P1.vel.y)
            if plat.rect.top >= HEIGHT:
                plat.kill()

    plat_gen()
    displaysurface.blit(background, (0, 0))
    f = pygame.font.SysFont("Verdana", 20)
    g = f.render(str(P1.score), True, (123, 255, 0))
    displaysurface.blit(g, (WIDTH / 2, 10))

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()

    pygame.display.update()
    FramePerSec.tick(FPS)
