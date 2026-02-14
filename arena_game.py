import pygame
import math
import random

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.joystick.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("2 Player Arena")

clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255,255,255)
BLACK = (20,20,25)
RED = (200,40,40)
GREEN = (40,200,40)
BLUE = (40,120,255)
CYAN = (100,200,255)
GRAY = (80,80,80)
YELLOW = (255,220,50)
ORANGE = (255,140,50)
PURPLE = (200,100,255)

font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 32, bold=True)
title_font = pygame.font.SysFont("Arial", 80, bold=True)
menu_font = pygame.font.SysFont("Arial", 40, bold=True)

# Particle system
particles = []
camera_offset = [0, 0]  # For moving background effect

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.radius = 3

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.vy += 0.1  # Gravity
        self.radius = max(1, 3 * (self.lifetime / self.max_lifetime))

    def draw(self):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), max(1, int(self.radius)))

# Sound generation
def generate_sound(frequency, duration, volume=0.3):
    """Generate a simple sine wave sound without numpy using pygame mixer"""
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    import array
    arr = array.array('h')  # signed short integer
    for i in range(frames):
        # Generate sine wave
        sample = math.sin(2.0 * math.pi * frequency * i / sample_rate)
        sample = int(sample * 32767 * volume)
        arr.append(sample)
        arr.append(sample)  # stereo - same for both channels
    
    # Create sound from buffer
    try:
        sound = pygame.mixer.Sound(buffer=arr.tobytes())
        return sound
    except Exception as e:
        # If sound creation fails, return a dummy object
        class DummySound:
            def play(self):
                pass
        return DummySound()

# Pre-generate sound effects
shoot_sound = generate_sound(800, 0.1, 0.3)  # Pew sound
hit_sound = generate_sound(400, 0.15, 0.3)   # Impact sound
ui_sound = generate_sound(600, 0.08, 0.2)    # UI beep

def play_shoot_sound():
    try:
        shoot_sound.play()
    except:
        pass

def play_hit_sound():
    try:
        hit_sound.play()
    except:
        pass

def play_ui_sound():
    try:
        ui_sound.play()
    except:
        pass

# Controller
controller = None
if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()

def normalize_angle_diff(target, current):
    """Calculate shortest angle difference for smooth 360-degree rotation"""
    diff = target - current
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

# Weapon definitions
WEAPONS = {
    0: {"name": "SMG", "damage": 5, "delay": 120, "speed": 12, "color": YELLOW},
    1: {"name": "Shotgun", "damage": 4, "delay": 500, "speed": 10, "color": ORANGE},
    2: {"name": "Sniper", "damage": 20, "delay": 750, "speed": 18, "color": PURPLE},
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
        self.last_hit_time = 0
        self.last_weapon_switch = 0

    def draw(self):
        # Draw enhanced glow effect with multiple layers
        glow_color = (int(self.color[0]//3), int(self.color[1]//3), int(self.color[2]//3))
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), self.radius + 12)
        pygame.draw.circle(screen, (int(self.color[0]//2), int(self.color[1]//2), int(self.color[2]//2)), (int(self.x), int(self.y)), self.radius + 8)
        
        # Draw main circle with border
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw direction indicator (larger triangle pointing in aim direction)
        angle = self.angle
        front_x = self.x + math.cos(angle) * (self.radius + 12)
        front_y = self.y + math.sin(angle) * (self.radius + 12)
        left_x = self.x + math.cos(angle + 2.5) * self.radius * 0.8
        left_y = self.y + math.sin(angle + 2.5) * self.radius * 0.8
        right_x = self.x + math.cos(angle - 2.5) * self.radius * 0.8
        right_y = self.y + math.sin(angle - 2.5) * self.radius * 0.8
        pygame.draw.polygon(screen, WEAPONS[self.weapon]["color"], [(front_x, front_y), (left_x, left_y), (right_x, right_y)])
        pygame.draw.polygon(screen, WHITE, [(front_x, front_y), (left_x, left_y), (right_x, right_y)], 2)

        # Draw aim line (longer for sniper) with gradient effect
        if self.weapon == 2:  # Sniper
            aim_length = 300
        else:
            aim_length = 80
        
        end_x = self.x + math.cos(angle) * aim_length
        end_y = self.y + math.sin(angle) * aim_length
        
        # Draw aim line with weapon color
        weapon_color = WEAPONS[self.weapon]["color"]
        pygame.draw.line(screen, weapon_color, (self.x, self.y), (end_x, end_y), 3)
        # Add glow to aim line
        pygame.draw.line(screen, weapon_color, (self.x, self.y), (end_x, end_y), 1)

        # HP bar with enhanced styling
        bar_width = 60
        bar_height = 10
        ratio = self.hp / self.max_hp
        
        # Bar background
        pygame.draw.rect(screen, (30, 30, 30), (self.x - 30, self.y - 50, bar_width, bar_height))
        # Health fill (gradient color based on health)
        if ratio > 0.5:
            bar_color = (int(40 + 160 * (ratio - 0.5) * 2), 200, 40)  # Green to yellow
        else:
            bar_color = (200, int(40 + 160 * ratio * 2), 40)  # Red to yellow
        pygame.draw.rect(screen, bar_color, (self.x - 30, self.y - 50, bar_width * ratio, bar_height))
        # Bar border
        pygame.draw.rect(screen, WHITE, (self.x - 30, self.y - 50, bar_width, bar_height), 2)
        
        # Draw player name
        player_name = "P1" if self is player1 else "P2"
        name_text = font.render(player_name, True, WHITE)
        screen.blit(name_text, (self.x - 10, self.y + 35))

class Bullet:
    def __init__(self, x, y, angle, speed, damage, owner, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.color = color
        self.trail_points = []

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        # Store trail points for visual effect
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > 15:
            self.trail_points.pop(0)

    def draw(self):
        # Draw trail
        for i, point in enumerate(self.trail_points):
            alpha = int(255 * (i / max(1, len(self.trail_points))))
            size = max(1, int(5 * (i / max(1, len(self.trail_points)))))
            pygame.draw.circle(screen, self.color, (int(point[0]), int(point[1])), size)
        
        # Draw bullet with enhanced glow
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 7)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 5)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT


class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self):
        # Draw obstacle with glowing effect
        glow_rect = self.rect.inflate(8, 8)
        pygame.draw.rect(screen, (100, 50, 200), glow_rect)
        pygame.draw.rect(screen, (150, 100, 255), self.rect)
        pygame.draw.rect(screen, CYAN, self.rect, 3)
    
    def collides_with_circle(self, x, y, radius):
        """Check if obstacle collides with a circle (player)"""
        # Find closest point on rectangle to circle center
        closest_x = max(self.rect.left, min(x, self.rect.right))
        closest_y = max(self.rect.top, min(y, self.rect.bottom))
        
        # Calculate distance between circle center and closest point
        distance = math.hypot(x - closest_x, y - closest_y)
        return distance < radius
    
    def collides_with_point(self, x, y, radius=3):
        """Check if obstacle collides with a point (bullet)"""
        return self.rect.collidepoint(x, y)


def draw_background():
    global camera_offset
    
    screen.fill(BLACK)
    
    # Moving grid background based on camera offset
    grid_size = 50
    offset_x = int(camera_offset[0]) % grid_size
    offset_y = int(camera_offset[1]) % grid_size
    
    # Draw vertical lines
    for i in range(-1, WIDTH // grid_size + 2):
        x = i * grid_size - offset_x
        pygame.draw.line(screen, (30, 30, 35), (x, 0), (x, HEIGHT), 1)
    
    # Draw horizontal lines
    for j in range(-1, HEIGHT // grid_size + 2):
        y = j * grid_size - offset_y
        pygame.draw.line(screen, (30, 30, 35), (0, y), (WIDTH, y), 1)

def draw_weapon_ui(player, x_offset):
    for i in range(3):
        rect = pygame.Rect(x_offset + i*120, 10, 100, 30)
        pygame.draw.rect(screen, GRAY, rect)
        if i == player.weapon:
            pygame.draw.rect(screen, BLUE, rect, 3)
        text = font.render(WEAPONS[i]["name"], True, WHITE)
        screen.blit(text, (rect.x + 10, rect.y + 5))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False

    def draw(self):
        color = tuple(min(255, c + 50) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.text_color, self.rect, 3)
        text_surf = menu_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

def draw_menu():
    draw_background()
    
    # Title
    title = title_font.render("2 PLAYER ARENA", True, CYAN)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    pygame.draw.rect(screen, CYAN, title_rect.inflate(40, 40), 3)
    screen.blit(title, title_rect)
    
    # Instructions
    instructions = [
        "Player 1 (Controller): Left stick to move, Right stick to aim, R2 to shoot",
        "Player 2 (Keyboard): WASD to move, Mouse to aim, Click to shoot",
        "Press 1-3 to switch weapons (SMG, Shotgun, Sniper)"
    ]
    
    y_offset = HEIGHT // 2 - 20
    instr_font = pygame.font.SysFont("Arial", 24)
    for instruction in instructions:
        text = instr_font.render(instruction, True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 50
    
    return start_button

start_button = None  # Will be created in menu state

def show_menu():
    global start_button
    start_button = Button(WIDTH // 2 - 150, HEIGHT - 200, 300, 80, "START GAME", BLUE, CYAN)
    
    menu_running = True
    while menu_running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        start_button.update_hover(mouse_pos)
        
        draw_menu()
        start_button.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_clicked(mouse_pos):
                    play_ui_sound()
                    menu_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    play_ui_sound()
        pygame.display.flip()
    
    return True

def show_game_over(winner):
    # Winner text
    winner_color = BLUE if winner == "PLAYER 1" else GREEN
    winner_text = title_font.render(f"{winner} WINS!", True, winner_color)
    winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Display winner for 3 seconds then return to menu
    start_time = pygame.time.get_ticks()
    display_duration = 3000  # 3 seconds in milliseconds
    
    while True:
        clock.tick(FPS)
        elapsed = pygame.time.get_ticks() - start_time
        
        draw_background()
        pygame.draw.rect(screen, winner_color, winner_rect.inflate(60, 60), 3)
        screen.blit(winner_text, winner_rect)
        
        # Check for quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        pygame.display.flip()
        
        # Auto return to menu after duration
        if elapsed >= display_duration:
            return True

# Show menu first
if not show_menu():
    pygame.quit()
    exit()

while True:
    player1 = Player(200, 350, BLUE)
    player2 = Player(1000, 350, GREEN)
    bullets = []
    
    # Generate obstacles
    obstacles = []
    for i in range(8):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        w = random.randint(40, 100)
        h = random.randint(40, 100)
        obstacles.append(Obstacle(x, y, w, h))

    running = True
    game_over = False
    while running:
        clock.tick(FPS)
        
        # Update camera to follow average of both players
        camera_offset[0] += (((player1.x + player2.x) / 2) - camera_offset[0]) * 0.05
        camera_offset[1] += (((player1.y + player2.y) / 2) - camera_offset[1]) * 0.05
        
        draw_background()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_over = True

            # Keyboard switching
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player2.weapon = 0
                    play_ui_sound()
                if event.key == pygame.K_2:
                    player2.weapon = 1
                    play_ui_sound()
                if event.key == pygame.K_3:
                    player2.weapon = 2
                    play_ui_sound()

        keys = pygame.key.get_pressed()

        # Player 2 Movement - check collisions BEFORE moving
        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= 5
        if keys[pygame.K_s]: move_y += 5
        if keys[pygame.K_a]: move_x -= 5
        if keys[pygame.K_d]: move_x += 5
        
        # Only apply movement if it doesn't collide with obstacles
        new_x = max(5, min(WIDTH - 5, player2.x + move_x))
        new_y = max(5, min(HEIGHT - 5, player2.y + move_y))
        
        can_move = True
        for obstacle in obstacles:
            if obstacle.collides_with_circle(new_x, new_y, player2.radius):
                can_move = False
                break
        
        if can_move:
            player2.x = new_x
            player2.y = new_y

        # Mouse Aim
        mx, my = pygame.mouse.get_pos()
        player2.angle = math.atan2(my - player2.y, mx - player2.x)

        # Shoot mouse
        if pygame.mouse.get_pressed()[0]:
            now = pygame.time.get_ticks()
            weapon = WEAPONS[player2.weapon]
            if now - player2.last_shot > weapon["delay"]:
                bullets.append(Bullet(player2.x, player2.y, player2.angle,
                                      weapon["speed"], weapon["damage"], player2, weapon["color"]))
                play_shoot_sound()
                player2.last_shot = now

        # Controller Player 1
        if controller:
            lx = controller.get_axis(0)
            ly = controller.get_axis(1)
            rx = controller.get_axis(2)
            ry = controller.get_axis(3)

            # Player 1 Movement - check collisions BEFORE moving
            move_x = lx * 5
            move_y = ly * 5
            
            # Only apply movement if it doesn't collide with obstacles
            new_x = max(5, min(WIDTH - 5, player1.x + move_x))
            new_y = max(5, min(HEIGHT - 5, player1.y + move_y))
            
            can_move = True
            for obstacle in obstacles:
                if obstacle.collides_with_circle(new_x, new_y, player1.radius):
                    can_move = False
                    break
            
            if can_move:
                player1.x = new_x
                player1.y = new_y

            # Reduced aim sensitivity for finer angle control with proper 360 wrapping
            if abs(rx) > 0.2 or abs(ry) > 0.2:
                target_angle = math.atan2(ry, rx)
                # Use normalize_angle_diff for smooth 360-degree rotation
                angle_diff = normalize_angle_diff(target_angle, player1.angle)
                player1.angle += angle_diff * 0.15

            # R2 shoot
            if controller.get_axis(5) > 0.5:
                now = pygame.time.get_ticks()
                weapon = WEAPONS[player1.weapon]
                if now - player1.last_shot > weapon["delay"]:
                    bullets.append(Bullet(player1.x, player1.y, player1.angle,
                                          weapon["speed"], weapon["damage"], player1, weapon["color"]))
                    play_shoot_sound()
                    player1.last_shot = now

            # L1 / R1 weapon switch
            now = pygame.time.get_ticks()
            if now - player1.last_weapon_switch > 200:  # 200ms debounce
                if controller.get_button(4):
                    player1.weapon = (player1.weapon - 1) % 3
                    play_ui_sound()
                    player1.last_weapon_switch = now
                if controller.get_button(5):
                    player1.weapon = (player1.weapon + 1) % 3
                    play_ui_sound()
                    player1.last_weapon_switch = now

        # Bullet logic
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw()

            target = player2 if bullet.owner == player1 else player1
            dist = math.hypot(bullet.x - target.x, bullet.y - target.y)

            if dist < target.radius:
                target.hp -= bullet.damage
                play_hit_sound()
                bullets.remove(bullet)
            elif bullet.off_screen():
                bullets.remove(bullet)
            else:
                # Check collision with obstacles
                bullet_hit_obstacle = False
                for obstacle in obstacles:
                    if obstacle.collides_with_point(bullet.x, bullet.y):
                        bullet_hit_obstacle = True
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
                if bullet_hit_obstacle:
                    continue

        player1.draw()
        player2.draw()
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw()

        draw_weapon_ui(player1, 100)
        draw_weapon_ui(player2, WIDTH - 460)

        # Check for game end
        if player1.hp <= 0:
            if not show_game_over("PLAYER 2"):
                game_over = True
            running = False
        elif player2.hp <= 0:
            if not show_game_over("PLAYER 1"):
                game_over = True
            running = False

        pygame.display.flip()
    
    if game_over:
        break
    
    # Return to menu after game ends
    if not show_menu():
        break

pygame.quit()
