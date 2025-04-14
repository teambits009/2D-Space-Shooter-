import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Cosmic Courier Enhanced")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
NEON_GREEN = (50, 255, 50)
PURPLE = (200, 0, 200)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Player
PLAYER_SIZE = 30
player_x = WINDOW_WIDTH // 2
player_y = WINDOW_HEIGHT - 50
PLAYER_SPEED = 300
player = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)

# Ammo (energy bolts)
AMMO_SIZE = 8
AMMO_SPEED = 600
ammo_cooldown = 0.15  # Faster firing
ammo_timer = 0
ammo_list = []

# Bombs
BOMB_SIZE = 50
BOMB_SPEED = 400
bomb_ammo = 3  # Start with 3 bombs
bomb_cooldown = 0.5
bomb_timer = 0
bomb_list = []

# Enemy class
class Enemy:
    def __init__(self, x, y, width, height, type_):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type_  # "standard", "fast", "tough"
        self.wave_offset = random.uniform(0, 2 * math.pi) if type_ == "standard" else 0
        self.health = 2 if type_ == "tough" else 1
        self.speed = {"standard": 150, "fast": 250, "tough": 100}[type_]
        self.points = {"standard": 5, "fast": 10, "tough": 20}[type_]
        self.penalty = {"standard": 2, "fast": 5, "tough": 10}[type_]

# Enemies
ENEMY_SIZE = 20
enemy_spawn_rate = 0.8  # More frequent
enemy_timer = 0
enemies = []

# Packages
PACKAGE_SIZE = 15
package_spawn_rate = 2.0
package_timer = 0
packages = []

# Stars and grid
stars = [(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)) for _ in range(50)]
grid_spacing = 50
grid_alpha = 50

# Particles
particles = []

# Score and UI
score = 0
font = pygame.font.SysFont(None, 36)

# Screen shake
shake_duration = 0
shake_offset = (0, 0)

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    delta_time = clock.tick(60) / 1000.0

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= PLAYER_SPEED * delta_time
    if keys[pygame.K_RIGHT] and player.x < WINDOW_WIDTH - PLAYER_SIZE:
        player.x += PLAYER_SPEED * delta_time
    if keys[pygame.K_UP] and player.y > 0:
        player.y -= PLAYER_SPEED * delta_time
    if keys[pygame.K_DOWN] and player.y < WINDOW_HEIGHT - PLAYER_SIZE:
        player.y += PLAYER_SPEED * delta_time

    # Shooting (energy bolts)
    ammo_timer -= delta_time
    if keys[pygame.K_SPACE] and ammo_timer <= 0:
        ammo = pygame.Rect(player.centerx - AMMO_SIZE // 2, player.y, AMMO_SIZE, AMMO_SIZE)
        ammo_list.append(ammo)
        ammo_timer = ammo_cooldown

    # Bombs
    bomb_timer -= delta_time
    if keys[pygame.K_b] and bomb_ammo > 0 and bomb_timer <= 0:
        bomb = pygame.Rect(player.centerx - BOMB_SIZE // 2, player.y, BOMB_SIZE, BOMB_SIZE)
        bomb_list.append(bomb)
        bomb_ammo -= 1
        score -= 5  # Bomb cost
        bomb_timer = bomb_cooldown
        shake_duration = 0.2

    # Update ammo
    for ammo in ammo_list[:]:
        ammo.y -= AMMO_SPEED * delta_time
        if ammo.y < 0:
            ammo_list.remove(ammo)

    # Update bombs
    for bomb in bomb_list[:]:
        bomb.y -= BOMB_SPEED * delta_time
        if bomb.y < -BOMB_SIZE:
            bomb_list.remove(bomb)

    # Spawn enemies
    enemy_timer -= delta_time
    if enemy_timer <= 0:
        enemy_x = random.randint(0, WINDOW_WIDTH - ENEMY_SIZE)
        enemy_type = random.choices(
            ["standard", "fast", "tough"],
            weights=[50, 30, 20],
            k=1
        )[0]
        enemy = Enemy(enemy_x, 0, ENEMY_SIZE, ENEMY_SIZE, enemy_type)
        enemies.append(enemy)
        enemy_timer = enemy_spawn_rate

    # Update enemies
    for enemy in enemies[:]:
        enemy.rect.y += enemy.speed * delta_time
        if enemy.type == "standard":
            enemy.rect.x += math.sin(enemy.rect.y * 0.02 + enemy.wave_offset) * 100 * delta_time
        if (enemy.rect.y > WINDOW_HEIGHT or
            enemy.rect.x < 0 or
            enemy.rect.x > WINDOW_WIDTH - ENEMY_SIZE):
            enemies.remove(enemy)
            score -= enemy.penalty

    # Spawn packages
    package_timer -= delta_time
    if package_timer <= 0 and random.random() < 0.3:
        package_x = random.randint(0, WINDOW_WIDTH - PACKAGE_SIZE)
        package = pygame.Rect(package_x, 0, PACKAGE_SIZE, PACKAGE_SIZE)
        packages.append(package)
        package_timer = package_spawn_rate
        if random.random() < 0.2:  # 20% chance for bomb ammo
            bomb_ammo = min(bomb_ammo + 1, 5)  # Max 5 bombs

    # Update packages
    for package in packages[:]:
        package.y += 100 * delta_time
        if package.y > WINDOW_HEIGHT:
            packages.remove(package)

    # Collisions
    for ammo in ammo_list[:]:
        for enemy in enemies[:]:
            if ammo.colliderect(enemy.rect):
                ammo_list.remove(ammo)
                enemy.health -= 1
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += enemy.points
                    # Particles
                    for _ in range(5):
                        particles.append({
                            'x': enemy.rect.centerx,
                            'y': enemy.rect.centery,
                            'vx': random.uniform(-100, 100),
                            'vy': random.uniform(-100, 100),
                            'life': 0.5
                        })
                    shake_duration = 0.1
                break

    for bomb in bomb_list[:]:
        for enemy in enemies[:]:
            if math.hypot(bomb.centerx - enemy.rect.centerx, bomb.centery - enemy.rect.centery) < BOMB_SIZE:
                enemies.remove(enemy)
                score += enemy.points
                for _ in range(10):
                    particles.append({
                        'x': enemy.rect.centerx,
                        'y': enemy.rect.centery,
                        'vx': random.uniform(-150, 150),
                        'vy': random.uniform(-150, 150),
                        'life': 0.7
                    })

    for package in packages[:]:
        if player.colliderect(package):
            packages.remove(package)
            score += 15

    # Update particles
    for particle in particles[:]:
        particle['x'] += particle['vx'] * delta_time
        particle['y'] += particle['vy'] * delta_time
        particle['life'] -= delta_time
        if particle['life'] <= 0:
            particles.remove(particle)

    # Screen shake
    if shake_duration > 0:
        shake_duration -= delta_time
        shake_offset = (random.randint(-5, 5), random.randint(-5, 5))
    else:
        shake_offset = (0, 0)

    # Render
    screen.fill(BLACK)
    # Grid
    grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    for x in range(0, WINDOW_WIDTH, grid_spacing):
        pygame.draw.line(grid_surface, (CYAN[0], CYAN[1], CYAN[2], grid_alpha), (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, grid_spacing):
        pygame.draw.line(grid_surface, (CYAN[0], CYAN[1], CYAN[2], grid_alpha), (0, y), (WINDOW_WIDTH, y))
    screen.blit(grid_surface, (0, 0))
    # Stars
    for star in stars:
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, 255), star, 2)
    # Player
    player_points = [
        (player.centerx, player.y),
        (player.x, player.bottom),
        (player.right, player.bottom)
    ]
    pygame.draw.polygon(screen, BLUE, player_points)
    pygame.draw.polygon(screen, CYAN, player_points, 2)  # Glow outline
    # Ammo
    for ammo in ammo_list:
        pygame.draw.rect(screen, NEON_GREEN, ammo)
        pygame.draw.rect(screen, (0, 100, 0), (ammo.x, ammo.y + AMMO_SIZE, AMMO_SIZE, AMMO_SIZE // 2))
    # Bombs
    for bomb in bomb_list:
        # Gradient effect
        for r in range(BOMB_SIZE // 2, 0, -2):
            alpha = int(255 * (r / (BOMB_SIZE // 2)))
            color = (PURPLE[0], PURPLE[1], PURPLE[2], alpha)
            pygame.draw.circle(screen, color, bomb.center, r)
    # Enemies
    for enemy in enemies:
        if enemy.type == "standard":
            pygame.draw.circle(screen, RED, enemy.rect.center, ENEMY_SIZE // 2)
        elif enemy.type == "fast":
            points = [
                (enemy.rect.centerx, enemy.rect.top),
                (enemy.rect.left, enemy.rect.bottom),
                (enemy.rect.right, enemy.rect.bottom)
            ]
            pygame.draw.polygon(screen, ORANGE, points)
        elif enemy.type == "tough":
            pygame.draw.rect(screen, GRAY, enemy.rect)
            if enemy.health == 1:
                pygame.draw.rect(screen, (150, 150, 150), enemy.rect, 2)  # Damaged
    # Packages
    for package in packages:
        pygame.draw.rect(screen, YELLOW, package)
        pygame.draw.rect(screen, WHITE, package, 1)
    # Particles
    for particle in particles:
        pygame.draw.circle(screen, WHITE, (int(particle['x']), int(particle['y'])), 3)
    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    bomb_text = font.render(f"Bombs: {bomb_ammo}", True, PURPLE)
    screen.blit(score_text, (10, 10))
    screen.blit(bomb_text, (10, 40))
    # Shake
    if shake_offset != (0, 0):
        surface = pygame.display.get_surface()
        temp_surface = pygame.Surface(surface.get_size())
        temp_surface.blit(surface, shake_offset)
        screen.blit(temp_surface, (0, 0))
    pygame.display.flip()

# Cleanup
pygame.quit()