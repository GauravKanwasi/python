import pygame
import random
import math
from dataclasses import dataclass

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 64
PLAYER_SIZE = 40
WINDOW_WIDTH = 640
GAME_AREA_HEIGHT = 640
WINDOW_HEIGHT = GAME_AREA_HEIGHT + 100  # 740, with 100 for UI panel
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
FPS = 60

# Fonts
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)

# Player class with special abilities
@dataclass
class Player:
    name: str
    class_type: str
    x: int = 300
    y: int = 300
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    strength: int = 5
    intelligence: int = 5
    agility: int = 5
    defense: int = 10
    inventory: list = None
    gold: int = 0
    is_invisible: bool = False
    special_duration: int = 0
    special_cooldown: int = 0

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

    @classmethod
    def create(cls, name: str, class_type: str) -> 'Player':
        base_stats = {
            "Warrior": {"health": 120, "mana": 40, "strength": 10, "intelligence": 4, "agility": 6, "defense": 15},
            "Mage": {"health": 80, "mana": 120, "strength": 4, "intelligence": 10, "agility": 6, "defense": 5},
            "Rogue": {"health": 100, "mana": 60, "strength": 6, "intelligence": 6, "agility": 10, "defense": 10}
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
            defense=stats["defense"],
            inventory=["Health Potion", "Mana Potion"],
            gold=100
        )

    def use_special(self):
        if self.special_cooldown > 0:
            return
        if self.class_type == "Warrior":
            self.activate_berserk()
        elif self.class_type == "Mage":
            self.cast_arcane_burst()
        elif self.class_type == "Rogue":
            self.use_shadow_step()
        self.special_cooldown = self.get_special_cooldown()

    def activate_berserk(self):
        self.strength = int(self.strength * 1.5)
        self.defense = int(self.defense * 0.5)
        self.special_duration = 600  # 10 seconds at 60 FPS

    def cast_arcane_burst(self):
        if hasattr(self, 'current_room') and self.current_room:
            for enemy in self.current_room.enemies:
                damage = self.intelligence * 5
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = math.sqrt(dx**2 + dy**2) or 1
                knockback_dir = (dx/dist, dy/dist)
                enemy.take_damage(damage, knockback_dir)

    def use_shadow_step(self):
        if hasattr(self, 'current_room'):
            max_x = self.current_room.width * TILE_SIZE - PLAYER_SIZE
            max_y = self.current_room.height * TILE_SIZE - PLAYER_SIZE
            self.x = random.randint(0, max_x)
            self.y = random.randint(0, max_y)
        self.is_invisible = True
        self.special_duration = 300  # 5 seconds at 60 FPS

    def get_special_cooldown(self):
        return {
            "Warrior": 1800,  # 30 seconds
            "Mage": 1200,     # 20 seconds
            "Rogue": 1500     # 25 seconds
        }[self.class_type]

    def update(self):
        if self.special_duration > 0:
            self.special_duration -= 1
            if self.special_duration == 0:
                if self.class_type == "Warrior":
                    self.strength = int(self.strength / 1.5)
                    self.defense = int(self.defense / 0.5)
                elif self.class_type == "Rogue":
                    self.is_invisible = False
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

    def take_damage(self, amount):
        damage_taken = max(1, amount - self.defense)
        self.health = max(0, self.health - damage_taken)

    def draw(self, screen):
        player_color = {
            "Warrior": RED,
            "Mage": BLUE,
            "Rogue": GREEN
        }[self.class_type]
        bob_offset = int(math.sin(pygame.time.get_ticks() * 0.01) * 5)
        if self.class_type == "Warrior" and self.special_duration > 0:
            pygame.draw.rect(screen, (255, 0, 0, 100),
                             (self.x-5, self.y-5+bob_offset, PLAYER_SIZE+10, PLAYER_SIZE+10), 2)
        elif self.class_type == "Rogue" and self.is_invisible:
            player_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            player_surf.fill((*player_color[:3], 100))
            screen.blit(player_surf, (self.x, self.y + bob_offset))
        else:
            pygame.draw.rect(screen, player_color,
                             (self.x, self.y + bob_offset, PLAYER_SIZE, PLAYER_SIZE))

    def draw_status_bars(self, screen):
        bar_width = 200
        bar_height = 20
        # Health bar
        pygame.draw.rect(screen, RED, (10, 10, bar_width * (self.health / self.max_health), bar_height))
        pygame.draw.rect(screen, WHITE, (10, 10, bar_width, bar_height), 2)
        health_text = FONT_SMALL.render(f"Health: {self.health}/{self.max_health}", True, WHITE)
        screen.blit(health_text, (220, 10))
        # Mana bar
        pygame.draw.rect(screen, BLUE, (10, 40, bar_width * (self.mana / self.max_mana), bar_height))
        pygame.draw.rect(screen, WHITE, (10, 40, bar_width, bar_height), 2)
        mana_text = FONT_SMALL.render(f"Mana: {self.mana}/{self.max_mana}", True, WHITE)
        screen.blit(mana_text, (220, 40))
        # Special cooldown bar
        cooldown_max = self.get_special_cooldown()
        if self.special_cooldown > 0:
            cooldown_ratio = 1 - self.special_cooldown / cooldown_max
            bar_color = PURPLE
            cooldown_time = math.ceil(self.special_cooldown / FPS)
            special_text = FONT_SMALL.render(f"Special Cooldown: {cooldown_time}s", True, WHITE)
        else:
            cooldown_ratio = 1
            bar_color = GREEN
            special_text = FONT_SMALL.render("Special Ready", True, WHITE)
        pygame.draw.rect(screen, bar_color, (10, 70, bar_width * cooldown_ratio, bar_height))
        pygame.draw.rect(screen, WHITE, (10, 70, bar_width, bar_height), 2)
        screen.blit(special_text, (220, 70))

# Enemy class
@dataclass
class Enemy:
    x: int
    y: int
    health: int = 50
    attack_range: int = 50
    detection_range: int = 200
    state: str = "idle"

    def update(self, player):
        if player.is_invisible:
            self.state = "idle"
        else:
            dist_to_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
            if dist_to_player < self.attack_range:
                self.state = "attack"
            elif dist_to_player < self.detection_range:
                self.state = "chase"
            else:
                self.state = "idle"
        if self.state == "chase":
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.x += (dx / dist) * 2
                self.y += (dy / dist) * 2
        # Bound position to game area
        self.x = max(0, min(self.x, WINDOW_WIDTH - PLAYER_SIZE))
        self.y = max(0, min(self.y, GAME_AREA_HEIGHT - PLAYER_SIZE))

    def take_damage(self, amount, knockback_dir):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
        self.x += knockback_dir[0] * 10
        self.y += knockback_dir[1] * 10
        # Bound position to game area
        self.x = max(0, min(self.x, WINDOW_WIDTH - PLAYER_SIZE))
        self.y = max(0, min(self.y, GAME_AREA_HEIGHT - PLAYER_SIZE))

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The Lost Treasure of Pythonia")
        self.clock = pygame.time.Clock()
        self.player = Player.create("Hero", "Warrior")
        self.running = True
        # Mock room: 10x10 tiles (640x640 pixels)
        self.player.current_room = type('Room', (), {'width': 10, 'height': 10, 'enemies': [Enemy(400, 400)]})()

    def update_game(self):
        keys = pygame.key.get_pressed()
        speed = 5
        if keys[pygame.K_LEFT]:
            self.player.x -= speed
        if keys[pygame.K_RIGHT]:
            self.player.x += speed
        if keys[pygame.K_UP]:
            self.player.y -= speed
        if keys[pygame.K_DOWN]:
            self.player.y += speed
        # Bound player to game area
        self.player.x = max(0, min(self.player.x, WINDOW_WIDTH - PLAYER_SIZE))
        self.player.y = max(0, min(self.player.y, GAME_AREA_HEIGHT - PLAYER_SIZE))
        if keys[pygame.K_e]:
            self.player.use_special()
        self.player.update()
        for enemy in self.player.current_room.enemies:
            enemy.update(self.player)
        self.player.current_room.enemies = [enemy for enemy in self.player.current_room.enemies if enemy.health > 0]

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.update_game()
            self.screen.fill(BLACK)
            self.player.draw(self.screen)
            for enemy in self.player.current_room.enemies:
                pygame.draw.rect(self.screen, (255, 0, 0), (enemy.x, enemy.y, PLAYER_SIZE, PLAYER_SIZE))
                enemy_bar_width = 30
                enemy_bar_height = 5
                enemy_health_ratio = enemy.health / 50
                pygame.draw.rect(self.screen, RED, (enemy.x + 5, enemy.y - 10, enemy_bar_width * enemy_health_ratio, enemy_bar_height))
                pygame.draw.rect(self.screen, WHITE, (enemy.x + 5, enemy.y - 10, enemy_bar_width, enemy_bar_height), 1)
            self.player.draw_status_bars(self.screen)
            # Draw UI panel below game area
            ui_y = GAME_AREA_HEIGHT
            pygame.draw.rect(self.screen, (50, 50, 50), (0, ui_y, WINDOW_WIDTH, WINDOW_HEIGHT - ui_y))
            name_text = FONT_MEDIUM.render(f"{self.player.name} ({self.player.class_type})", True, WHITE)
            self.screen.blit(name_text, (10, ui_y + 5))
            stats_text = FONT_SMALL.render(f"STR: {self.player.strength}  INT: {self.player.intelligence}  AGI: {self.player.agility}  DEF: {self.player.defense}", True, WHITE)
            self.screen.blit(stats_text, (10, ui_y + 35))
            inventory_text = FONT_SMALL.render(f"Inventory: {', '.join(self.player.inventory)}", True, WHITE)
            self.screen.blit(inventory_text, (10, ui_y + 60))
            gold_text = FONT_SMALL.render(f"Gold: {self.player.gold}", True, WHITE)
            self.screen.blit(gold_text, (10, ui_y + 85))
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
