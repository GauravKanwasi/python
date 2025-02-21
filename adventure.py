import pygame
import sys
import json
import math
from dataclasses import dataclass, asdict
from typing import List, Optional
import os
import random
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.font.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
TILE_SIZE = 40
PLAYER_SIZE = 40
ENEMY_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)

# Setup display with better resolution
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("The Lost Treasure of Pythonia")
clock = pygame.time.Clock()

# Load and scale images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(f"assets/{name}.png").convert_alpha()
        if scale != 1:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except:
        # Create a colorful placeholder if image not found
        surf = pygame.Surface((32, 32))
        surf.fill(PURPLE)
        return surf

# Fonts with better styling
FONT_LARGE = pygame.font.Font(None, 72)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 32)

class TileType(Enum):
    FLOOR = 0
    WALL = 1
    DOOR = 2
    CHEST = 3
    ENEMY_SPAWN = 4

@dataclass
class Player:
    name: str
    class_type: str
    health: int
    max_health: int
    mana: int
    max_mana: int
    strength: int
    intelligence: int
    agility: int
    inventory: List[str]
    gold: int
    x: int = WINDOW_WIDTH // 2
    y: int = WINDOW_HEIGHT // 2
    speed: int = 5
    animation_frame: int = 0
    facing: str = 'right'
    current_room: Optional['Room'] = None
    special_cooldown: int = 0
    special_duration: int = 0

    @classmethod
    def create(cls, name: str, class_type: str) -> 'Player':
        base_stats = {
            "Warrior": {"health": 120, "mana": 40, "strength": 10, "intelligence": 4, "agility": 6},
            "Mage": {"health": 80, "mana": 120, "strength": 4, "intelligence": 10, "agility": 6},
            "Rogue": {"health": 100, "mana": 60, "strength": 6, "intelligence": 6, "agility": 10}
        }
        stats = base_stats[class_type]
        return cls(
            name=name,
            class_type=class_type,
            health=stats["health"],
            max_health=stats["health"],
            mana=stats["mana"],
            max_mana=stats["mana"],
            strength=stats["strength"],
            intelligence=stats["intelligence"],
            agility=stats["agility"],
            inventory=["Health Potion", "Mana Potion"],
            gold=100
        )

    def move(self, keys):
        if self.current_room is None:
            return
            
        max_x = (self.current_room.width * TILE_SIZE) - PLAYER_SIZE
        max_y = (self.current_room.height * TILE_SIZE) - PLAYER_SIZE
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
            self.facing = 'left'
        if keys[pygame.K_RIGHT] and self.x < max_x:
            self.x += self.speed
            self.facing = 'right'
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < max_y:
            self.y += self.speed

    def draw(self, screen):
        # Draw character with bob animation
        bob_offset = math.sin(self.animation_frame * 0.2) * 3
        player_color = {
            "Warrior": RED,
            "Mage": BLUE,
            "Rogue": GREEN
        }[self.class_type]
        
        # Draw character shadow
        shadow_rect = pygame.Rect(self.x, self.y + 35, 40, 20)
        pygame.draw.ellipse(screen, (0, 0, 0, 128), shadow_rect)
        
        # Draw character body
        player_rect = pygame.Rect(self.x, self.y + bob_offset, 40, 40)
        pygame.draw.rect(screen, player_color, player_rect)
        
        # Draw character details based on class
        if self.class_type == "Warrior":
            # Draw sword
            sword_points = [(self.x + 45, self.y + 20), (self.x + 60, self.y + 20)]
            pygame.draw.line(screen, GRAY, *sword_points, 4)
        elif self.class_type == "Mage":
            # Draw staff
            pygame.draw.line(screen, GOLD, (self.x + 20, self.y - 5), (self.x + 20, self.y + 40), 3)
        elif self.class_type == "Rogue":
            # Draw daggers
            pygame.draw.line(screen, GRAY, (self.x - 5, self.y + 20), (self.x + 5, self.y + 20), 2)
            pygame.draw.line(screen, GRAY, (self.x + 35, self.y + 20), (self.x + 45, self.y + 20), 2)

        # Draw UI elements
        self.draw_status_bars(screen)
        self.draw_stats(screen)

    def draw_status_bars(self, screen):
        # Health bar with fancy styling
        bar_width = 200
        bar_height = 25
        border = 2

        # Health bar background and border
        pygame.draw.rect(screen, WHITE, (10-border, 10-border, bar_width+2*border, bar_height+2*border))
        pygame.draw.rect(screen, RED, (10, 10, bar_width, bar_height))
        health_width = int(bar_width * (self.health/self.max_health))
        pygame.draw.rect(screen, GREEN, (10, 10, health_width, bar_height))

        # Mana bar background and border
        pygame.draw.rect(screen, WHITE, (10-border, 40-border, bar_width+2*border, bar_height+2*border))
        pygame.draw.rect(screen, GRAY, (10, 40, bar_width, bar_height))
        mana_width = int(bar_width * (self.mana/self.max_mana))
        pygame.draw.rect(screen, BLUE, (10, 40, mana_width, bar_height))

        # Add text overlays
        health_text = FONT_SMALL.render(f"{self.health}/{self.max_health}", True, WHITE)
        mana_text = FONT_SMALL.render(f"{self.mana}/{self.max_mana}", True, WHITE)
        screen.blit(health_text, (15, 12))
        screen.blit(mana_text, (15, 42))

    def draw_stats(self, screen):
        stats_bg = pygame.Surface((200, 100))
        stats_bg.set_alpha(128)
        stats_bg.fill(BLACK)
        screen.blit(stats_bg, (WINDOW_WIDTH - 210, 10))

        stats_text = [
            f"Class: {self.class_type}",
            f"STR: {self.strength}",
            f"INT: {self.intelligence}",
            f"AGI: {self.agility}",
            f"Gold: {self.gold}"
        ]

        for i, text in enumerate(stats_text):
            text_surface = FONT_SMALL.render(text, True, WHITE)
            screen.blit(text_surface, (WINDOW_WIDTH - 200, 15 + i * 20))

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        
    def attack(self, enemies):
        attack_range = 60
        attack_damage = self.strength * 5
        
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= attack_range:
                enemy.health -= attack_damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    self.gold += random.randint(10, 30)

class AnimatedButton:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.color = color
        self.is_hovered = False
        self.animation_progress = 0
        self.original_y = y

    def draw(self, screen):
        # Hover animation
        if self.is_hovered:
            self.animation_progress = min(1, self.animation_progress + 0.1)
        else:
            self.animation_progress = max(0, self.animation_progress - 0.1)

        # Calculate button position and size based on animation
        hover_offset = self.animation_progress * 5
        hover_scale = 1 + (self.animation_progress * 0.1)
        
        button_rect = pygame.Rect(
            self.rect.x - (self.rect.width * (hover_scale - 1) / 2),
            self.original_y - hover_offset,
            self.rect.width * hover_scale,
            self.rect.height * hover_scale
        )

        # Draw button with gradient
        color = self.get_gradient_color()
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=10)

        # Draw text
        text_surface = FONT_MEDIUM.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

    def get_gradient_color(self):
        base_r, base_g, base_b = self.base_color
        highlight_amount = 50 * self.animation_progress
        return (
            min(255, base_r + highlight_amount),
            min(255, base_g + highlight_amount),
            min(255, base_b + highlight_amount)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Particle:
    def __init__(self, x, y, color, velocity=(0, 0), lifetime=30, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen, camera_x, camera_y):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color[:3], alpha)
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (self.size//2, self.size//2), self.size//2)
        screen.blit(surf, (self.x - camera_x, self.y - camera_y))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color, velocity=(0, 0), lifetime=30, size=3):
        self.particles.append(Particle(x, y, color, velocity, lifetime, size))

    def add_hit_effect(self, x, y, color):
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.add_particle(x, y, color, (vx, vy), random.randint(20, 40))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen, camera_x, camera_y):
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = 100
        self.max_health = 100
        self.speed = 3
        self.damage = 20
        self.attack_cooldown = 0
        self.animation_frame = 0
        self.state = "idle"  # idle, chase, attack
        self.detection_range = 200
        self.attack_range = 50
        self.particles = ParticleSystem()
        self.hit_cooldown = 0
        self.knockback = 0
        self.knockback_dx = 0
        self.knockback_dy = 0
        
        # Set enemy-specific stats
        if enemy_type == "Skeleton":
            self.health = 80
            self.damage = 15
            self.speed = 4
        elif enemy_type == "Demon":
            self.health = 120
            self.damage = 25
            self.speed = 2
        elif enemy_type == "Ghost":
            self.health = 60
            self.damage = 10
            self.speed = 5

        # Add enemy-specific effects
        self.effects = {
            "Skeleton": self.skeleton_effect,
            "Demon": self.demon_effect,
            "Ghost": self.ghost_effect
        }

    def skeleton_effect(self):
        if random.random() < 0.02:
            self.particles.add_particle(
                self.x + random.randint(0, ENEMY_SIZE),
                self.y + ENEMY_SIZE,
                (200, 200, 200, 128),
                (0, -1),
                20
            )

    def demon_effect(self):
        if random.random() < 0.05:
            self.particles.add_particle(
                self.x + ENEMY_SIZE//2,
                self.y + ENEMY_SIZE//2,
                (255, 50, 0, 200),
                (random.uniform(-1, 1), random.uniform(-1, 1)),
                15
            )

    def ghost_effect(self):
        if random.random() < 0.1:
            self.particles.add_particle(
                self.x + random.randint(0, ENEMY_SIZE),
                self.y + random.randint(0, ENEMY_SIZE),
                (200, 200, 255, 100),
                (0, -0.5),
                40
            )

    def take_damage(self, amount, knockback_direction):
        self.health -= amount
        self.hit_cooldown = 10
        
        # Apply knockback
        self.knockback = 20
        self.knockback_dx, self.knockback_dy = knockback_direction
        
        # Add hit effect
        hit_colors = {
            "Skeleton": (200, 200, 200),
            "Demon": (255, 100, 100),
            "Ghost": (200, 200, 255)
        }
        self.particles.add_hit_effect(
            self.x + ENEMY_SIZE//2,
            self.y + ENEMY_SIZE//2,
            hit_colors[self.enemy_type]
        )

    def update(self, player, current_time):
        # Apply enemy-specific effects
        self.effects[self.enemy_type]()
        
        # Update particles
        self.particles.update()
        
        # Handle knockback
        if self.knockback > 0:
            self.x += self.knockback_dx * 2
            self.y += self.knockback_dy * 2
            self.knockback -= 1
            return

        # Update hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        dist_to_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        
        # Update state based on distance to player
        if dist_to_player < self.attack_range:
            self.state = "attack"
        elif dist_to_player < self.detection_range:
            self.state = "chase"
        else:
            self.state = "idle"

        # Handle different states
        if self.state == "chase":
            # Move towards player
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist != 0:
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed
                self.animation_frame = (self.animation_frame + 1) % 30
        
        elif self.state == "attack":
            if self.attack_cooldown <= 0:
                player.take_damage(self.damage)
                self.attack_cooldown = 60  # 1 second at 60 FPS
            self.attack_cooldown = max(0, self.attack_cooldown - 1)

    def draw(self, screen, camera_x, camera_y):
        # Draw particles
        self.particles.draw(screen, camera_x, camera_y)
        
        # Draw enemy with hit flash
        enemy_color = {
            "Skeleton": (200, 200, 200),
            "Demon": (200, 0, 0),
            "Ghost": (200, 200, 255)
        }[self.enemy_type]
        
        if self.hit_cooldown > 0:
            enemy_color = WHITE
        
        # Draw enemy shadow
        shadow_rect = pygame.Rect(self.x, self.y + 35, 40, 20)
        pygame.draw.ellipse(screen, (0, 0, 0, 128), shadow_rect)
        
        # Draw enemy body with bob animation when moving
        bob_offset = math.sin(self.animation_frame * 0.2) * 3 if self.state == "chase" else 0
        enemy_rect = pygame.Rect(self.x, self.y + bob_offset, 40, 40)
        pygame.draw.rect(screen, enemy_color, enemy_rect)
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 5
            health_width = int(bar_width * (self.health/self.max_health))
            pygame.draw.rect(screen, RED, (self.x, self.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, bar_height))

class Room:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[TileType.FLOOR for _ in range(width)] for _ in range(height)]
        self.enemies = []
        self.chests = []
        self.doors = []
        
    def generate(self):
        # Add walls around the room
        for x in range(self.width):
            self.tiles[0][x] = TileType.WALL
            self.tiles[self.height-1][x] = TileType.WALL
        for y in range(self.height):
            self.tiles[y][0] = TileType.WALL
            self.tiles[y][self.width-1] = TileType.WALL
            
        # Add random obstacles and features
        for _ in range(10):
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            self.tiles[y][x] = TileType.WALL
            
        # Add chests
        for _ in range(2):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            if self.tiles[y][x] == TileType.FLOOR:
                self.tiles[y][x] = TileType.CHEST
                self.chests.append((x, y))
                
        # Add enemies with proper positioning
        enemy_types = ["Skeleton", "Demon", "Ghost"]
        for _ in range(3):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            if self.tiles[y][x] == TileType.FLOOR:
                enemy_type = random.choice(enemy_types)
                self.enemies.append(Enemy(
                    x * TILE_SIZE,  # Convert grid to pixel position
                    y * TILE_SIZE, 
                    enemy_type
                ))

    def draw(self, screen, camera_x, camera_y):
        for y in range(self.height):
            for x in range(self.width):
                tile_x = x * TILE_SIZE
                tile_y = y * TILE_SIZE
                screen_x = tile_x - camera_x
                screen_y = tile_y - camera_y
                
                # Only draw tiles that are visible
                if (-TILE_SIZE < screen_x < WINDOW_WIDTH and 
                    -TILE_SIZE < screen_y < WINDOW_HEIGHT):
                    if self.tiles[y][x] == TileType.WALL:
                        pygame.draw.rect(screen, GRAY, 
                                       (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif self.tiles[y][x] == TileType.CHEST:
                        pygame.draw.rect(screen, GOLD, 
                                       (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif self.tiles[y][x] == TileType.DOOR:
                        pygame.draw.rect(screen, DARK_GREEN, 
                                       (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    else:  # FLOOR
                        pygame.draw.rect(screen, (30, 30, 30), 
                                       (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

class Game:
    def __init__(self):
        self.state = "menu"
        self.player = None
        self.current_room = None
        self.camera_x = 0
        self.camera_y = 0
        self.buttons = {
            "menu": [
                AnimatedButton(WINDOW_WIDTH//2 - 100, 250, 200, 50, "New Game", WHITE),
                AnimatedButton(WINDOW_WIDTH//2 - 100, 350, 200, 50, "Load Game", WHITE),
                AnimatedButton(WINDOW_WIDTH//2 - 100, 450, 200, 50, "Quit", WHITE)
            ],
            "class_select": [
                AnimatedButton(WINDOW_WIDTH//2 - 100, 250, 200, 50, "Warrior", RED),
                AnimatedButton(WINDOW_WIDTH//2 - 100, 350, 200, 50, "Mage", BLUE),
                AnimatedButton(WINDOW_WIDTH//2 - 100, 450, 200, 50, "Rogue", GREEN)
            ]
        }
        self.background_pos = 0
        self.title_animation = 0

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "game":
                        self.state = "menu"
                self.handle_event(event)

            screen.fill(BLACK)
            
            # Animated background
            self.background_pos = (self.background_pos + 1) % WINDOW_HEIGHT
            for i in range(-1, 2):
                y_pos = self.background_pos + (i * WINDOW_HEIGHT)
                self.draw_background(y_pos)

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "class_select":
                self.draw_class_select()
            elif self.state == "game":
                self.update_game()
                self.draw_game()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def draw_background(self, y_pos):
        # Draw animated background pattern
        for x in range(0, WINDOW_WIDTH, 40):
            for y in range(0, WINDOW_HEIGHT, 40):
                color = ((x + y) % 40 + 20, 0, (x + y) % 40 + 20)
                pygame.draw.rect(screen, color, (x, (y + y_pos) % WINDOW_HEIGHT, 20, 20))

    def handle_event(self, event):
        if self.state == "menu":
            for i, button in enumerate(self.buttons["menu"]):
                if button.handle_event(event):
                    if i == 0:  # New Game
                        self.state = "class_select"
                    elif i == 1:  # Load Game
                        self.load_game()
                    elif i == 2:  # Quit
                        pygame.quit()
                        sys.exit()

        elif self.state == "class_select":
            for i, button in enumerate(self.buttons["class_select"]):
                if button.handle_event(event):
                    class_types = ["Warrior", "Mage", "Rogue"]
                    self.start_new_game(class_types[i])

    def draw_menu(self):
        # Animated title
        self.title_animation = (self.title_animation + 0.05) % (2 * math.pi)
        title_offset = math.sin(self.title_animation) * 10
        
        title = FONT_LARGE.render("The Lost Treasure", True, GOLD)
        subtitle = FONT_LARGE.render("of Pythonia", True, GOLD)
        
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 
                           100 + title_offset))
        screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 
                              160 + title_offset))

        for button in self.buttons["menu"]:
            button.draw(screen)

    def draw_class_select(self):
        title = FONT_LARGE.render("Choose Your Class", True, GOLD)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))

        # Class descriptions
        descriptions = {
            "Warrior": ["High Health & Strength", "Special: Berserk Mode"],
            "Mage": ["High Mana & Intelligence", "Special: Arcane Burst"],
            "Rogue": ["High Agility & Balance", "Special: Shadow Step"]
        }

        for i, (class_name, desc) in enumerate(descriptions.items()):
            y_pos = 250 + i * 100
            for j, line in enumerate(desc):
                text = FONT_SMALL.render(line, True, WHITE)
                screen.blit(text, (WINDOW_WIDTH//2 + 120, y_pos + j * 25))

        for button in self.buttons["class_select"]:
            button.draw(screen)

    def start_new_game(self, class_type):
        self.player = Player.create("Player", class_type)
        self.current_room = Room(20, 15)
        self.current_room.generate()
        self.player.current_room = self.current_room
        self.state = "game"

    def update_game(self):
        keys = pygame.key.get_pressed()
        
        # Handle player movement
        self.player.move(keys)
        
        # Update camera position to center on player
        self.camera_x = self.player.x + PLAYER_SIZE//2 - WINDOW_WIDTH//2
        self.camera_y = self.player.y + PLAYER_SIZE//2 - WINDOW_HEIGHT//2
        
        # Clamp camera to room boundaries
        max_camera_x = (self.current_room.width * TILE_SIZE) - WINDOW_WIDTH
        max_camera_y = (self.current_room.height * TILE_SIZE) - WINDOW_HEIGHT
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
        
        # Handle attacks
        if keys[pygame.K_SPACE]:
            self.player.attack(self.current_room.enemies)
        
        # Update enemies
        current_time = pygame.time.get_ticks()
        for enemy in self.current_room.enemies:
            enemy.update(self.player, current_time)

    def draw_game(self):
        # Draw room and environment
        self.current_room.draw(screen, self.camera_x, self.camera_y)
        
        # Draw enemies with camera offset
        for enemy in self.current_room.enemies:
            enemy.draw(screen, self.camera_x, self.camera_y)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw UI elements
        self.draw_game_ui()

    def draw_game_ui(self):
        # Draw mini-map in top-right corner
        map_size = 150
        map_surface = pygame.Surface((map_size, map_size))
        map_surface.fill((0, 0, 0))
        map_surface.set_alpha(200)
        
        # Calculate scale factors
        room_width = self.current_room.width * TILE_SIZE
        room_height = self.current_room.height * TILE_SIZE
        scale_x = map_size / room_width
        scale_y = map_size / room_height
        scale = min(scale_x, scale_y)
        
        # Draw room layout
        for y in range(self.current_room.height):
            for x in range(self.current_room.width):
                if self.current_room.tiles[y][x] == TileType.WALL:
                    color = GRAY
                elif self.current_room.tiles[y][x] == TileType.CHEST:
                    color = GOLD
                elif self.current_room.tiles[y][x] == TileType.DOOR:
                    color = DARK_GREEN
                else:
                    color = (30, 30, 30)
                
                pygame.draw.rect(map_surface, color,
                               (x * TILE_SIZE * scale, 
                                y * TILE_SIZE * scale,
                                TILE_SIZE * scale, 
                                TILE_SIZE * scale))
        
        # Draw player position
        player_x = (self.player.x) * scale
        player_y = (self.player.y) * scale
        pygame.draw.circle(map_surface, GREEN, (player_x, player_y), 3)
        
        # Draw enemies
        for enemy in self.current_room.enemies:
            enemy_x = (enemy.x) * scale
            enemy_y = (enemy.y) * scale
            pygame.draw.circle(map_surface, RED, (enemy_x, enemy_y), 2)
        
        # Draw map border
        pygame.draw.rect(map_surface, WHITE, (0, 0, map_size, map_size), 2)
        
        # Position and draw the map
        screen.blit(map_surface, (WINDOW_WIDTH - map_size - 10, 10))

    def load_game(self):
        try:
            with open('save_game.json', 'r') as f:
                data = json.load(f)
                self.player = Player(**data)
                self.state = "game"
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    game = Game()
    game.run()
