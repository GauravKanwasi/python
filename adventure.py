import pygame
import random
import math
from dataclasses import dataclass

# Initialize Pygame
pygame.init()

# Constants (adjust as needed for your game)
TILE_SIZE = 64
PLAYER_SIZE = 40
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
FPS = 60

# Font for UI elements
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
    defense: int = 10  # Base defense stat
    inventory: list = None
    gold: int = 0
    is_invisible: bool = False  # For Rogue's Shadow Step
    special_duration: int = 0   # Duration of active ability
    special_cooldown: int = 0   # Cooldown timer

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

    @classmethod
    def create(cls, name: str, class_type: str) -> 'Player':
        """Create a player with class-specific stats."""
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
        """Activate the player's special ability if it's not on cooldown."""
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
        """Warrior: Boost strength by 50%, reduce defense by 50% for 10 seconds."""
        self.strength = int(self.strength * 1.5)
        self.defense = int(self.defense * 0.5)
        self.special_duration = 600  # 10 seconds at 60 FPS

    def cast_arcane_burst(self):
        """Mage: Damage all enemies in the room based on intelligence."""
        if hasattr(self, 'current_room') and self.current_room:
            for enemy in self.current_room.enemies:
                damage = self.intelligence * 5
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = math.sqrt(dx**2 + dy**2) or 1
                knockback_dir = (dx/dist, dy/dist)
                enemy.take_damage(damage, knockback_dir)

    def use_shadow_step(self):
        """Rogue: Teleport to a random location and become invisible for 5 seconds."""
        if hasattr(self, 'current_room'):
            max_x = self.current_room.width * TILE_SIZE - PLAYER_SIZE
            max_y = self.current_room.height * TILE_SIZE - PLAYER_SIZE
            self.x = random.randint(0, max_x)
            self.y = random.randint(0, max_y)
        self.is_invisible = True
        self.special_duration = 300  # 5 seconds at 60 FPS

    def get_special_cooldown(self):
        """Return the cooldown duration in frames based on class."""
        return {
            "Warrior": 1800,  # 30 seconds at 60 FPS
            "Mage": 1200,     # 20 seconds at 60 FPS
            "Rogue": 1500     # 25 seconds at 60 FPS
        }[self.class_type]

    def update(self):
        """Update special ability states each frame."""
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
        """Reduce health based on damage minus defense."""
        damage_taken = max(1, amount - self.defense)  # Minimum 1 damage
        self.health = max(0, self.health - damage_taken)

    def draw(self, screen):
        """Draw the player with special ability effects."""
        player_color = {
            "Warrior": RED,
            "Mage": BLUE,
            "Rogue": GREEN
        }[self.class_type]
        bob_offset = int(math.sin(pygame.time.get_ticks() * 0.01) * 5)  # Simple bob effect

        if self.class_type == "Warrior" and self.special_duration > 0:
            # Red aura for Berserk
            pygame.draw.rect(screen, (255, 0, 0, 100), 
                             (self.x-5, self.y-5+bob_offset, PLAYER_SIZE+10, PLAYER_SIZE+10), 2)
        elif self.class_type == "Rogue" and self.is_invisible:
            # Semi-transparent for invisibility
            player_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            player_surf.fill((*player_color[:3], 100))  # Alpha 100
            screen.blit(player_surf, (self.x, self.y + bob_offset))
        else:
            pygame.draw.rect(screen, player_color, 
                             (self.x, self.y + bob_offset, PLAYER_SIZE, PLAYER_SIZE))

    def draw_status_bars(self, screen):
        """Draw health, mana, and special cooldown bars."""
        bar_width = 200
        bar_height = 20
        
        # Health bar
        pygame.draw.rect(screen, RED, (10, 10, bar_width * (self.health / self.max_health), bar_height))
        pygame.draw.rect(screen, WHITE, (10, 10, bar_width, bar_height), 2)
        
        # Mana bar
        pygame.draw.rect(screen, BLUE, (10, 40, bar_width * (self.mana / self.max_mana), bar_height))
        pygame.draw.rect(screen, WHITE, (10, 40, bar_width, bar_height), 2)
        
        # Special cooldown bar
        if self.special_cooldown > 0:
            cooldown_max = self.get_special_cooldown()
            cooldown_width = int(bar_width * (1 - self.special_cooldown / cooldown_max))
            pygame.draw.rect(screen, PURPLE, (10, 70, cooldown_width, bar_height))
            pygame.draw.rect(screen, WHITE, (10, 70, bar_width, bar_height), 2)
            cooldown_text = FONT_SMALL.render("Special", True, WHITE)
            screen.blit(cooldown_text, (15, 72))

# Enemy class with updated behavior for invisible player
@dataclass
class Enemy:
    x: int
    y: int
    health: int = 50
    attack_range: int = 50
    detection_range: int = 200
    state: str = "idle"

    def update(self, player):
        """Update enemy behavior based on player state."""
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

    def take_damage(self, amount, knockback_dir):
        """Reduce enemy health and apply knockback."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0  # Enemy dies
        # Apply knockback (adjust as needed)
        self.x += knockback_dir[0] * 10
        self.y += knockback_dir[1] * 10

# Game class with integrated special abilities
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The Lost Treasure of Pythonia")
        self.clock = pygame.time.Clock()
        self.player = Player.create("Hero", "Warrior")  # Example: Warrior class
        self.running = True
        # Mock room setup for demonstration (adjust to your game's room structure)
        self.player.current_room = type('Room', (), {'width': 10, 'height': 10, 'enemies': [Enemy(400, 400)]})()

    def update_game(self):
        """Handle game updates."""
        keys = pygame.key.get_pressed()
        
        # Activate special ability with 'E' key
        if keys[pygame.K_e]:
            self.player.use_special()
        
        # Update player state
        self.player.update()
        
        # Update enemies
        for enemy in self.player.current_room.enemies:
            enemy.update(self.player)

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update_game()
            
            # Draw
            self.screen.fill(BLACK)  # Black background
            self.player.draw(self.screen)
            self.player.draw_status_bars(self.screen)
            pygame.display.flip()
            
            self.clock.tick(FPS)  # 60 FPS

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
