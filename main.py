import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
ENEMY_SPAWN_INTERVAL = 2000  # Milliseconds for level 1
COLLECTIBLE_SPAWN_INTERVAL = 5000  # Milliseconds for collectibles
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()

# Define classes
class Player:
    def __init__(self):
        self.x = 100
        self.y = 500
        self.width = 50
        self.height = 50
        self.health = 100
        self.lives = 3
        self.score = 0
        self.level = 1
        self.velocity = 5

    def move(self, dx, dy):
        self.x += dx * self.velocity
        self.y += dy * self.velocity
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def collect(self, collectible):
        if isinstance(collectible, HealthBoost):
            self.health += 20
            self.health = min(self.health, 100)  # Max health cap
        elif isinstance(collectible, ExtraLife):
            self.lives += 1
        self.score += 1

    def shoot(self):
        return Bullet(self.x + self.width // 2, self.y)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 5
        self.speed = 10
        self.damage = 10
        self.active = True

    def move(self):
        self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, waypoints):
        self.x = random.randint(200, SCREEN_WIDTH - 100)
        self.y = random.randint(0, SCREEN_HEIGHT - 100)
        self.width = 50
        self.height = 50
        self.health = 30
        self.waypoints = waypoints
        self.current_waypoint = 0
        self.speed = 2

    def move(self):
        target_x, target_y = self.waypoints[self.current_waypoint]
        if self.x < target_x:
            self.x += self.speed
        elif self.x > target_x:
            self.x -= self.speed
        if self.y < target_y:
            self.y += self.speed
        elif self.y > target_y:
            self.y -= self.speed
        
        if (self.x, self.y) == (target_x, target_y):
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))

    def take_damage(self, amount):
        self.health -= amount

class BossEnemy:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - 75
        self.y = SCREEN_HEIGHT // 2 - 75
        self.width = 150
        self.height = 150
        self.health = 500
        self.speed = 1

    def move(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH - self.width or self.x < 0:
            self.speed = -self.speed  # Reverse direction if hitting screen edge

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 255), (self.x, self.y, self.width, self.height))
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        health_bar_length = 100
        health_ratio = self.health / 100
        # Draw background for health bar
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, health_bar_length, 10))
        # Draw current health
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, health_bar_length * health_ratio, 10))

    def take_damage(self, amount):
        self.health -= amount

class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.active = True

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, self.width, self.height))

class HealthBoost(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y)

class ExtraLife(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y)

def opening_window(screen):
    font = pygame.font.Font(None, 74)
    title_text = font.render("My Game", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))

    font = pygame.font.Font(None, 36)
    instructions_text = font.render("Press SPACE to Start", True, WHITE)
    screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def level_transition(screen, level):
    font = pygame.font.Font(None, 74)
    transition_text = font.render(f"Level {level} Complete!", True, WHITE)
    screen.blit(transition_text, (SCREEN_WIDTH // 2 - transition_text.get_width() // 2, SCREEN_HEIGHT // 3))

    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds

def game_over_screen(screen):
    font = pygame.font.Font(None, 74)
    game_over_text = font.render("Game Over", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))

    font = pygame.font.Font(None, 36)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Show the opening window
    opening_window(screen)

    player = Player()

    waypoints = [
        (400, 100), 
        (600, 200), 
        (400, 300), 
        (200, 200), 
        (400, 100)
    ]

    enemies = []  
    bullets = []  
    collectibles = []  
    last_enemy_spawn_time = pygame.time.get_ticks()  
    last_collectible_spawn_time = pygame.time.get_ticks()  
    running = True
    game_over = False
    current_level = 1
    enemies_defeated = 0  
    level_score_threshold = 10  
    boss = None  

    global ENEMY_SPAWN_INTERVAL
    ENEMY_SPAWN_INTERVAL = 2000  

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not game_over:
            current_time = pygame.time.get_ticks()
            
            # Level 1 settings
            if current_level == 1:
                if current_time - last_enemy_spawn_time > ENEMY_SPAWN_INTERVAL:
                    enemies.append(Enemy(waypoints))
                    last_enemy_spawn_time = current_time
                if current_time - last_collectible_spawn_time > COLLECTIBLE_SPAWN_INTERVAL:
                    collectibles.append(random.choice([HealthBoost(random.randint(200, 600), random.randint(50, 500)),
                                                        ExtraLife(random.randint(200, 600), random.randint(50, 500))]))
                    last_collectible_spawn_time = current_time

            # Level 2 settings
            elif current_level == 2:
                if current_time - last_enemy_spawn_time > ENEMY_SPAWN_INTERVAL // 1.5:
                    enemies.append(Enemy(waypoints))
                    last_enemy_spawn_time = current_time
                if current_time - last_collectible_spawn_time > COLLECTIBLE_SPAWN_INTERVAL:
                    collectibles.append(random.choice([HealthBoost(random.randint(200, 600), random.randint(50, 500)),
                                                        ExtraLife(random.randint(200, 600), random.randint(50, 500))]))
                    last_collectible_spawn_time = current_time

            # Level 3 settings
            elif current_level == 3:
                if boss is None:
                    boss = BossEnemy()

                if current_time - last_enemy_spawn_time > ENEMY_SPAWN_INTERVAL // 2:
                    enemies.append(Enemy(waypoints))
                    last_enemy_spawn_time = current_time
            
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            if keys[pygame.K_LEFT]:
                dx = -1
            if keys[pygame.K_RIGHT]:
                dx = 1
            if keys[pygame.K_UP]:
                dy = -1
            if keys[pygame.K_DOWN]:
                dy = 1
            if keys[pygame.K_x]:  # Shoot key
                bullet = player.shoot()
                if bullet:
                    bullets.append(bullet)

            player.move(dx, dy)

            # Move bullets
            for bullet in bullets:
                bullet.move()
                if bullet.x > SCREEN_WIDTH:
                    bullet.active = False

            # Remove inactive bullets
            bullets = [b for b in bullets if b.active]

            # Move enemies
            for enemy in enemies[:]:
                enemy.move()

                # Check for collision with bullets
                for bullet in bullets:
                    if (enemy.x < bullet.x < enemy.x + enemy.width and
                        enemy.y < bullet.y < enemy.y + enemy.height):
                        enemy.take_damage(bullet.damage)
                        bullet.active = False

                # Check for enemy collision with player
                if (player.x < enemy.x + enemy.width and
                    player.x + player.width > enemy.x and
                    player.y < enemy.y + enemy.height and
                    player.y + player.height > enemy.y):
                    if player.take_damage(20):
                        game_over = True
                    enemies.remove(enemy)

            # Move boss if it exists
            if boss:
                boss.move()
                for bullet in bullets:
                    if (boss.x < bullet.x < boss.x + boss.width and
                        boss.y < bullet.y < boss.y + boss.height):
                        boss.take_damage(bullet.damage)
                        bullet.active = False
                if (player.x < boss.x + boss.width and
                    player.x + player.width > boss.x and
                    player.y < boss.y + boss.height and
                    player.y + player.height > boss.y):
                    if player.take_damage(20):
                        game_over = True

            # Remove defeated enemies and count them
            for enemy in enemies[:]:
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    enemies_defeated += 1

            # Check for level completion
            if enemies_defeated >= level_score_threshold and current_level < 3:
                current_level += 1
                player.score = 0
                level_transition(screen, current_level)
                ENEMY_SPAWN_INTERVAL = 1500  # Increase enemy spawn rate in level 2
                enemies_defeated = 0

            elif boss and boss.health <= 0:
                boss = None
                level_transition(screen, 4)  # Transition to victory screen
                running = False

            # Check for collectibles
            for collectible in collectibles:
                if (player.x < collectible.x + collectible.width and
                    player.x + player.width > collectible.x and
                    player.y < collectible.y + collectible.height and
                    player.y + player.height > collectible.y):
                    player.collect(collectible)
                    collectible.active = False

            collectibles = [c for c in collectibles if c.active]

        else:
            game_over_screen(screen)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:  # Restart game
                player = Player()
                enemies = []
                bullets = []
                collectibles = []
                last_enemy_spawn_time = pygame.time.get_ticks()
                last_collectible_spawn_time = pygame.time.get_ticks()
                game_over = False
                current_level = 1
                enemies_defeated = 0
                boss = None

        # Update screen
        screen.fill((0, 0, 0))
        
        if not game_over:
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            if boss:
                boss.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for collectible in collectibles:
                collectible.draw(screen)

            # Display health, level, and score
            health_text = f"Health: {player.health}"
            level_text = f"Level: {current_level}"
            score_text = f"Enemies Defeated: {enemies_defeated}"
            font = pygame.font.Font(None, 36)
            health_surface = font.render(health_text, True, WHITE)
            level_surface = font.render(level_text, True, WHITE)
            score_surface = font.render(score_text, True, WHITE)
            screen.blit(health_surface, (10, 10))
            screen.blit(level_surface, (10, 40))
            screen.blit(score_surface, (10, 70))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
