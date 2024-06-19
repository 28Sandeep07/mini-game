# mini-game 
import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple 2D Game")

# Set up colors
BLUE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up player
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 20
player_speed = 10

# Set up obstacles
obstacle_width, obstacle_height = 50, 50
obstacle_speed = 10
obstacle_gap = 200
obstacles = []

def spawn_obstacle():
    x = random.randint(0, WIDTH - obstacle_width)
    y = -obstacle_height
    obstacles.append(pygame.Rect(x, y, obstacle_width, obstacle_height))

def draw_screen():
    screen.fill(BLUE)
    pygame.draw.rect(screen, BLACK, (player_x, player_y, player_width, player_height))
    for obstacle in obstacles:
        pygame.draw.rect(screen, BLACK, obstacle)
    pygame.display.update()

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Move and spawn obstacles
    for obstacle in obstacles:
        obstacle.y += obstacle_speed
        if obstacle.y > HEIGHT:
            obstacles.remove(obstacle)
    if len(obstacles) == 0 or obstacles[-1].y > obstacle_gap:
        spawn_obstacle()

    # Check collision
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle):
            running = False

    # Draw everything
    draw_screen()

pygame.quit()
