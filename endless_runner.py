import pygame
from pygame.locals import *
import random
import math

pygame.init()

# Create the game window
game_width = 800
game_height = 400
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Runaway Rush ')

# Game variables
score = 0
speed = 3

# Define FSM states for the player
class PlayerStates:
    RUNNING = 'running'
    JUMPING = 'jumping'
    LANDING = 'landing'

class Player(pygame.sprite.Sprite):
    def __init__(self):  # Corrected __init__ method
        pygame.sprite.Sprite.__init__(self)  # Initialize the parent class
        self.height = 150
        self.x = 25
        self.y = game_height - self.height
        self.state = PlayerStates.RUNNING  # Initialize the state
        self.health = 3
        self.setup_sprites()
        self.rect = self.running_sprites[self.running_sprite_index].get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.invincibility_frame = 0

    def setup_sprites(self):
        self.running_sprites = [self.load_sprite('run', i) for i in range(10)]
        self.jumping_sprites = [self.load_sprite('jump', i) for i in range(10)]
        self.running_sprite_index = 0
        self.jumping_sprite_index = 0

    def load_sprite(self, action, index):
        sprite = pygame.image.load(f'images/{action}{index}.png').convert_alpha()
        scale = self.height / sprite.get_height()
        new_width = sprite.get_width() * scale
        new_height = sprite.get_height() * scale
        sprite = pygame.transform.scale(sprite, (new_width, new_height))
        return sprite

    def draw(self):
        if self.state == PlayerStates.RUNNING:
            sprite = self.running_sprites[int(self.running_sprite_index)]
        elif self.state in [PlayerStates.JUMPING, PlayerStates.LANDING]:
            sprite = self.jumping_sprites[int(self.jumping_sprite_index)]
        else:
            return
        if self.invincibility_frame > 0:
            self.invincibility_frame -= 1
        if self.invincibility_frame % 10 == 0:
            game.blit(sprite, (self.x, self.y))

    def update(self):
        if self.state == PlayerStates.RUNNING:
            self.running_sprite_index += 0.2
            if self.running_sprite_index >= len(self.running_sprites):
                self.running_sprite_index = 0
            self.rect = self.running_sprites[int(self.running_sprite_index)].get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
            self.mask = pygame.mask.from_surface(self.running_sprites[int(self.running_sprite_index)])
            
        elif self.state == PlayerStates.JUMPING or self.state == PlayerStates.LANDING:
            self.jumping_sprite_index += 0.2
            if self.jumping_sprite_index >= len(self.jumping_sprites):
                self.jumping_sprite_index = 0
            if self.state == PlayerStates.JUMPING:
                self.y -= 2
                if self.y <= game_height - self.height * 1.5:
                    self.state = PlayerStates.LANDING
            elif self.state == PlayerStates.LANDING:
                self.y += 2
                if self.y == game_height - self.height:
                    self.state = PlayerStates.RUNNING
            self.rect = self.jumping_sprites[int(self.jumping_sprite_index)].get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
            self.mask = pygame.mask.from_surface(self.jumping_sprites[int(self.jumping_sprite_index)])

    def jump(self):
        if self.state not in [PlayerStates.JUMPING, PlayerStates.LANDING]:
            self.state = PlayerStates.JUMPING


# Define FSM states for obstacles
class ObstacleStates:
    ACTIVE = 'active'
    RESETTING = 'resetting'

class Coin(pygame.sprite.Sprite):
    def _init_(self, x, y):
        pygame.sprite.Sprite._init_(self)
        self.image = pygame.image.load('images/coin.png').convert_alpha()
        scale = 30 / self.image.get_height()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed  # Coin moves with the same speed as obstacles

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -self.image.get_width():
            self.kill()  # Remove coin if it goes off-screen

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)



class AdaptiveObstacle(pygame.sprite.Sprite):
    def __init__(self, difficulty):
        super().__init__()
        
        self.difficulty = difficulty
        
        # Set initial x and y positions
        self.x = game_width  # Start off-screen to the right
        self.y = game_height - 50  # Position on the ground (adjust as needed)

        self.setup_images()
        self.set_obstacle_type()
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Initialize additional attributes
        self.state = ObstacleStates.ACTIVE
        self.timer = 0
        self.passed = False

        # Adjust obstacle behavior based on difficulty
        self.adjust_for_difficulty()  # Ensure this method exists and is defined below

    def setup_images(self):
        self.obstacle_images = []
        for image_name in ['rock1', 'rock2', 'rock3', 'spikes']:
            image = pygame.image.load(f'images/{image_name}.png').convert_alpha()
            scale = 50 / image.get_width()
            new_width = image.get_width() * scale
            new_height = image.get_height() * scale
            image = pygame.transform.scale(image, (new_width, new_height))
            self.obstacle_images.append(image)
        
    def set_obstacle_type(self):
        global score
        if score < 10:
            self.image = random.choice(self.obstacle_images[:2])
        elif score < 20:
            self.image = random.choice(self.obstacle_images[2:3])
        else:
            self.image = self.obstacle_images[-1]

    def adjust_for_difficulty(self):
        """Adjust the obstacle's speed or behavior based on difficulty."""
        # Example: Increase obstacle speed based on difficulty
        self.x -= self.difficulty * 2

    def draw(self):
        game.blit(self.image, (self.x, self.y))
        
    def update(self):
        global score
        if self.state == ObstacleStates.ACTIVE:
            self.x -= speed + self.difficulty
            self.timer += 1
            if self.timer % 500 == 0:
                self.difficulty = min(1 + score // 10, 5)
            if self.x < -self.image.get_width():
                self.state = ObstacleStates.RESETTING
        elif self.state == ObstacleStates.RESETTING:
            self.reset()

        if self.x < player.x and not self.passed:
            score += 1
            self.passed = True
            self.spawn_coin()  # Try to spawn a coin

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.mask = pygame.mask.from_surface(self.image)

    def reset(self):
        self.x = game_width
        self.y = game_height - self.image.get_height()
        self.set_obstacle_type()
        self.state = ObstacleStates.ACTIVE
        self.timer = 0
        self.passed = False

    def spawn_coin(self):
        if score >= 50 and score % 50 == 0:
            y_position = game_height - 200  # Coins hanging in the sky
            x_position = game_width + random.randint(0, 200)  # Random x position off-screen
            new_coin = Coin(x_position, y_position)
            coins_group.add(new_coin)





# Set the image for the sky
sky = pygame.image.load('images/sky.png').convert_alpha()
num_bg_tiles = math.ceil(game_width / sky.get_width()) + 1

# Set the images for the parallax background
bgs = []
bgs.append(pygame.image.load('images/mountains.png').convert_alpha())
bgs.append(pygame.image.load('images/trees.png').convert_alpha())
bgs.append(pygame.image.load('images/bushes.png').convert_alpha())

parallax = []
for x in range(len(bgs)):
    parallax.append(0)
    
player = Player()

# Create obstacles with an initial difficulty level
obstacles_group = pygame.sprite.Group()
obstacle = AdaptiveObstacle(difficulty=1)
obstacles_group.add(obstacle)

heart_sprites = []
heart_sprite_index = 0
for i in range(8):
    heart_sprite = pygame.image.load(f'images/heart{i}.png').convert_alpha()
    scale = 30 / heart_sprite.get_height()
    new_width = heart_sprite.get_width() * scale
    new_height = heart_sprite.get_height() * scale
    heart_sprite = pygame.transform.scale(heart_sprite, (new_width, new_height))
    heart_sprites.append(heart_sprite)

# Create groups for coins and obstacles
obstacles_group = pygame.sprite.Group()
obstacle = AdaptiveObstacle(difficulty=1)
obstacles_group.add(obstacle)

coins_group = pygame.sprite.Group()  # Group to hold coins

# Game loop
clock = pygame.time.Clock()
fps = 90
quit = False
while not quit:
    clock.tick(fps)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            quit = True
            
        if event.type == KEYDOWN and event.key == K_SPACE:
            player.jump()
        
    for i in range(num_bg_tiles):
        game.blit(sky, (i * sky.get_width(), 0))
        
    for i in range(len(bgs)):
        bg = bgs[i]
        for j in range(num_bg_tiles):
            game.blit(bg, (j * bg.get_width() + parallax[i], 0))
            
    for i in range(len(parallax)):
        parallax[i] -= i + 1
        if abs(parallax[i]) > bgs[i].get_width():
            parallax[i] = 0

    player.draw()
    player.update()
    
    obstacle.draw()
    obstacle.update()
    
    # Update and draw coins
    coins_group.update()
    for coin in coins_group:
        coin.draw(game)
    
    if pygame.sprite.spritecollide(player, obstacles_group, True, pygame.sprite.collide_mask):
        player.health -= 1
        player.invincibility_frame = 30
        
        obstacles_group.remove(obstacle)
        difficulty = min(1 + score // 2, 5)
        obstacle = AdaptiveObstacle(difficulty=difficulty)
        obstacles_group.add(obstacle)
        
    # Check for coin collisions
    if pygame.sprite.spritecollide(player, coins_group, True):
        score += 5  # Award extra score for collecting the coin
        if player.health < 3:  # Restore lives if possible
            player.health += 1
    
    for life in range(player.health):
        heart_sprite = heart_sprites[int(heart_sprite_index)]
        x_pos = 10 + life * (heart_sprite.get_width() + 10)
        y_pos = 10
        game.blit(heart_sprite, (x_pos, y_pos))
        
    heart_sprite_index += 0.1
    if heart_sprite_index >= len(heart_sprites):
        heart_sprite_index = 0
        
    black = (0, 0, 0)
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'Score: {score}', True, black)
    text_rect = text.get_rect()
    text_rect.center = (game_width - 50, 20)
    game.blit(text, text_rect)
            
    pygame.display.update()
    
    gameover = player.health == 0
    while gameover and not quit:
        red = (255, 0, 0)
        font = pygame.font.Font(pygame.font.get_default_font(), 50)
        text = font.render(f'Game Over! Score: {score}', True, red)
        text_rect = text.get_rect()
        text_rect.center = (game_width // 2, game_height // 2)
        game.blit(text, text_rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    quit = True
                if event.key == K_r:
                    score = 0
                    speed = 3
                    player.health = 3
                    player.x = 25
                    player.y = game_height - player.height
                    obstacle = AdaptiveObstacle(difficulty=1)
                    obstacles_group.add(obstacle)
                    gameover = False

pygame.quit()