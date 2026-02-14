import pygame
import math
import random

pygame.init()
pygame.joystick.init()

WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Player Arena")

clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255,255,255)
BLACK = (20,20,25)
RED = (200,40,40)
GREEN = (40,200,40)
BLUE = (40,120,255)
GRAY = (80,80,80)
YELLOW = (255,220,50)

font = pygame.font.SysFont("Arial", 20)

# Controller
controller = None
if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()

# Weapon definitions
WEAPONS = {
    0: {"name": "SMG", "damage": 5, "delay": 120, "speed": 12},
    1: {"name": "Shotgun", "damage": 4, "delay": 500, "speed": 10},
    2: {"name": "Sniper", "damage": 20, "delay": 750, "speed": 18},
}

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 20
        self.hp = 70
        self.max_hp = 70
        self.weapon = 0
        self.last_shot = 0
        self.angle = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Aim line
        end_x = self.x + math.cos(self.angle) * 40
        end_y = self.y + math.sin(self.angle) * 40
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 3)

        # HP bar
        bar_width = 50
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x - 25, self.y - 40, bar_width, 6))
        pygame.draw.rect(screen, GREEN, (self.x - 25, self.y - 40, bar_width * ratio, 6))

class Bullet:
    def __init__(self, x, y, angle, speed, damage, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner = owner

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 5)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT


def draw_background():
    screen.fill(BLACK)
    for i in range(0, WIDTH, 50):
        pygame.draw.line(screen, (30,30,35), (i,0), (i,HEIGHT))
    for j in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (30,30,35), (0,j), (WIDTH,j))

def draw_weapon_ui(player, x_offset):
    for i in range(3):
        rect = pygame.Rect(x_offset + i*120, 10, 100, 30)
        pygame.draw.rect(screen, GRAY, rect)
        if i == player.weapon:
            pygame.draw.rect(screen, BLUE, rect, 3)
        text = font.render(WEAPONS[i]["name"], True, WHITE)
        screen.blit(text, (rect.x + 10, rect.y + 5))

player1 = Player(200, 350, BLUE)
player2 = Player(1000, 350, GREEN)
bullets = []

running = True
while running:
    clock.tick(FPS)
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard switching
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                player2.weapon = 0
            if event.key == pygame.K_2:
                player2.weapon = 1
            if event.key == pygame.K_3:
                player2.weapon = 2

    keys = pygame.key.get_pressed()

    # Player 2 Movement
    if keys[pygame.K_w]: player2.y -= 5
    if keys[pygame.K_s]: player2.y += 5
    if keys[pygame.K_a]: player2.x -= 5
    if keys[pygame.K_d]: player2.x += 5

    # Mouse Aim
    mx, my = pygame.mouse.get_pos()
    player2.angle = math.atan2(my - player2.y, mx - player2.x)

    # Shoot mouse
    if pygame.mouse.get_pressed()[0]:
        now = pygame.time.get_ticks()
        weapon = WEAPONS[player2.weapon]
        if now - player2.last_shot > weapon["delay"]:
            bullets.append(Bullet(player2.x, player2.y, player2.angle,
                                  weapon["speed"], weapon["damage"], player2))
            player2.last_shot = now

    # Controller Player 1
    if controller:
        lx = controller.get_axis(0)
        ly = controller.get_axis(1)
        rx = controller.get_axis(2)
        ry = controller.get_axis(3)

        player1.x += lx * 5
        player1.y += ly * 5

        if abs(rx) > 0.2 or abs(ry) > 0.2:
            player1.angle = math.atan2(ry, rx)

        # R2 shoot
        if controller.get_axis(5) > 0.5:
            now = pygame.time.get_ticks()
            weapon = WEAPONS[player1.weapon]
            if now - player1.last_shot > weapon["delay"]:
                bullets.append(Bullet(player1.x, player1.y, player1.angle,
                                      weapon["speed"], weapon["damage"], player1))
                player1.last_shot = now

        # L1 / R1 weapon switch
        if controller.get_button(4):
            player1.weapon = (player1.weapon - 1) % 3
        if controller.get_button(5):
            player1.weapon = (player1.weapon + 1) % 3

    # Bullet logic
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()

        target = player2 if bullet.owner == player1 else player1
        dist = math.hypot(bullet.x - target.x, bullet.y - target.y)

        if dist < target.radius:
            target.hp -= bullet.damage
            bullets.remove(bullet)
        elif bullet.off_screen():
            bullets.remove(bullet)

    player1.draw()
    player2.draw()

    draw_weapon_ui(player1, 100)
    draw_weapon_ui(player2, WIDTH - 460)

    pygame.display.flip()

pygame.quit()
