import time
import os
import random
import json
import sys

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def c(color, text):
    return f"{color}{text}{Colors.RESET}"

class Item:
    def __init__(self, name, description, weight=1, value=0, usable=True):
        self.name = name
        self.description = description
        self.weight = weight
        self.value = value
        self.usable = usable

    def display_name(self):
        return self.name.replace('_', ' ')

ITEMS = {
    "torch": Item("torch", "A flaming torch that lights dark rooms and reveals hidden passages.", weight=1, value=5),
    "rusty_key": Item("rusty_key", "A corroded iron key. It looks old but still functional.", weight=1, value=2),
    "silver_key": Item("silver_key", "A polished silver key with intricate engravings. Must open something valuable.", weight=1, value=20),
    "sword": Item("sword", "A razor-sharp blade capable of piercing dragon scales. Balance is perfect.", weight=3, value=50),
    "dagger": Item("dagger", "A swift dagger ideal for quick strikes. Less powerful but faster.", weight=1, value=25),
    "shield": Item("shield", "A sturdy wooden shield reinforced with iron. Reduces combat damage.", weight=4, value=40),
    "magic_scroll": Item("magic_scroll", "A scroll inscribed with dragon-banishment runes. It hums with ancient power.", weight=1, value=100),
    "fireball_scroll": Item("fireball_scroll", "A battle scroll that unleashes a ball of fire at enemies.", weight=1, value=60),
    "gold_coin": Item("gold_coin", "A shiny gold coin stamped with a forgotten king's face.", weight=1, value=10),
    "gold_chest": Item("gold_chest", "A chest brimming with gold. Heavy but worth a fortune!", weight=5, value=500),
    "jewel": Item("jewel", "A brilliant gemstone that shimmers with inner fire.", weight=1, value=75),
    "ancient_crown": Item("ancient_crown", "A crown of a long-dead king. Priceless.", weight=2, value=300),
    "dragon_scale": Item("dragon_scale", "A tough iridescent scale from a dragon's hide.", weight=2, value=80),
    "dragon_heart": Item("dragon_heart", "The pulsing heart of a slain dragon. It radiates immense magic.", weight=3, value=250),
    "healing_potion": Item("healing_potion", "A crimson potion that restores 50 health points.", weight=1, value=30),
    "greater_healing_potion": Item("greater_healing_potion", "A vibrant potion that fully restores your health.", weight=1, value=75),
    "antidote": Item("antidote", "Cures poison. A must-have in dangerous dungeons.", weight=1, value=25),
    "rope": Item("rope", "A sturdy length of rope. Useful for climbing.", weight=2, value=10),
    "old_map": Item("old_map", "A tattered map showing secret passages within this dungeon.", weight=1, value=15),
    "lockpick": Item("lockpick", "A set of delicate lockpicks for bypassing locked doors.", weight=1, value=20),
    "amulet": Item("amulet", "A magical amulet. When worn, it grants resistance to fire.", weight=1, value=120),
    "food_ration": Item("food_ration", "Dried meat and hardtack. Restores 20 health.", weight=1, value=5),
    "bomb": Item("bomb", "A volatile explosive. Deals massive damage to a single target.", weight=2, value=55),
    "skeleton_key": Item("skeleton_key", "A key that can open any simple lock in the dungeon.", weight=1, value=90),
    "enchanted_arrow": Item("enchanted_arrow", "An arrow tipped with magical energy, highly effective against undead.", weight=1, value=35),
}

MONSTERS = {
    "goblin": {
        "name": "Goblin",
        "health": 30, "max_health": 30,
        "attack": (5, 15),
        "defense": 2,
        "loot": ["gold_coin", "dagger"],
        "loot_chance": 0.6,
        "xp": 20,
        "description": "A small green creature with beady red eyes and a rusty blade.",
        "flee_chance": 0.7,
    },
    "skeleton": {
        "name": "Skeleton",
        "health": 40, "max_health": 40,
        "attack": (8, 18),
        "defense": 5,
        "loot": ["rusty_key", "gold_coin"],
        "loot_chance": 0.5,
        "xp": 30,
        "description": "Animated bones clad in tattered armor, wielding a cracked sword.",
        "flee_chance": 0.5,
    },
    "troll": {
        "name": "Troll",
        "health": 80, "max_health": 80,
        "attack": (15, 30),
        "defense": 8,
        "loot": ["healing_potion", "gold_coin"],
        "loot_chance": 0.65,
        "xp": 60,
        "description": "A hulking grey-skinned beast. Regenerates health each turn.",
        "regenerates": 5,
        "flee_chance": 0.3,
    },
    "vampire": {
        "name": "Vampire",
        "health": 60, "max_health": 60,
        "attack": (12, 25),
        "defense": 6,
        "loot": ["amulet", "jewel"],
        "loot_chance": 0.55,
        "xp": 50,
        "description": "A pale, cloaked figure whose eyes glow crimson. It drains your life force.",
        "drains_health": True,
        "flee_chance": 0.4,
    },
    "dragon": {
        "name": "Ancient Dragon",
        "health": 150, "max_health": 150,
        "attack": (25, 50),
        "defense": 15,
        "loot": ["dragon_heart", "ancient_crown", "gold_chest"],
        "loot_chance": 1.0,
        "xp": 200,
        "description": "A colossal dragon with obsidian scales. Its eyes burn like molten gold.",
        "fire_breath_chance": 0.3,
        "fire_breath_damage": (30, 60),
        "flee_chance": 0.1,
    },
}

ROOMS = {
    "entrance": {
        "name": "Dungeon Entrance",
        "description": "You stand at the entrance of an ancient dungeon. Moss-covered stone walls surround you. Iron torches flicker, casting long shadows. A cool draft carries the smell of earth and something metallic.",
        "exits": {"north": "hallway", "east": "armory", "south": "outside"},
        "items": ["torch", "food_ration"],
        "first_visit": True,
        "dark": False,
    },
    "hallway": {
        "name": "The Long Hallway",
        "description": "A long corridor stretches ahead. Faded tapestries hang on the walls depicting ancient battles. Strange scratching sounds come from behind the stones.",
        "exits": {"north": "junction", "south": "entrance", "east": "library", "west": "crypt"},
        "items": ["rusty_key", "old_map"],
        "first_visit": True,
        "dark": False,
        "monster_spawn": "goblin",
        "monster_spawn_chance": 0.5,
    },
    "armory": {
        "name": "The Old Armory",
        "description": "Rusted weapon racks line the walls. Most weapons have crumbled to dust, but a few remain. Moonlight filters through a crack in the ceiling.",
        "exits": {"west": "entrance", "north": "library", "south": "guard_post"},
        "items": ["sword", "shield", "dagger"],
        "first_visit": True,
        "dark": False,
    },
    "guard_post": {
        "name": "Guard Post",
        "description": "A small room that once housed dungeon guards. Rotten furniture lies scattered. A locked chest sits in the corner.",
        "exits": {"north": "armory"},
        "items": ["lockpick", "food_ration"],
        "first_visit": True,
        "dark": False,
        "monster_spawn": "skeleton",
        "monster_spawn_chance": 0.7,
        "locked_chest": {"locked": True, "key": "rusty_key", "items": ["silver_key", "gold_coin", "gold_coin"]},
    },
    "library": {
        "name": "Ancient Library",
        "description": "Towering bookshelves groan under the weight of forgotten tomes. A magical scroll pulses with soft blue light on a reading desk. The air smells of old parchment.",
        "exits": {"west": "hallway", "south": "armory", "east": "sanctum", "north": "junction"},
        "items": ["magic_scroll", "fireball_scroll", "healing_potion"],
        "first_visit": True,
        "dark": False,
    },
    "crypt": {
        "name": "The Crypt",
        "description": "Stone sarcophagi line the walls. Names have been worn away by centuries of damp. An unnatural cold permeates the air.",
        "exits": {"east": "hallway", "north": "sealed_vault"},
        "items": ["antidote", "enchanted_arrow"],
        "first_visit": True,
        "dark": True,
        "monster_spawn": "skeleton",
        "monster_spawn_chance": 0.8,
    },
    "sealed_vault": {
        "name": "Sealed Vault",
        "description": "A vault sealed behind a heavy door. Inside, shelves hold preserved relics and strange artifacts. This place was meant to never be opened.",
        "exits": {"south": "crypt"},
        "items": ["amulet", "greater_healing_potion", "ancient_crown"],
        "first_visit": True,
        "dark": True,
        "locked": True,
        "required_key": "silver_key",
    },
    "junction": {
        "name": "The Junction",
        "description": "Four passages meet here. Arrows carved into the stone point in each direction, worn smooth by countless hands seeking guidance. A faint rumbling shakes the floor.",
        "exits": {"south": "hallway", "north": "treasure_room", "east": "dragon_lair", "west": "library"},
        "items": ["bomb"],
        "first_visit": True,
        "dark": False,
        "monster_spawn": "troll",
        "monster_spawn_chance": 0.4,
    },
    "sanctum": {
        "name": "The Sanctum",
        "description": "A circular chamber with a domed ceiling painted with constellations. An eerie glow emanates from an altar at the center.",
        "exits": {"west": "library"},
        "items": ["amulet", "magic_scroll"],
        "first_visit": True,
        "dark": False,
        "monster_spawn": "vampire",
        "monster_spawn_chance": 0.6,
    },
    "treasure_room": {
        "name": "The Treasure Chamber",
        "description": "Gold and jewels are piled high across the room. The air itself seems to shimmer with wealth. A magnificent chest dominates the center of the room.",
        "exits": {"south": "junction"},
        "items": ["gold_coin", "jewel", "jewel", "gold_coin"],
        "first_visit": True,
        "dark": False,
    },
    "dragon_lair": {
        "name": "Dragon's Lair",
        "description": "Scorched walls and the stench of sulfur tell you everything. Claw marks scar the stone floor. In the center, an enormous dragon coils around its hoard.",
        "exits": {"west": "junction"},
        "items": [],
        "first_visit": True,
        "dark": False,
        "boss": "dragon",
    },
    "outside": {
        "name": "Outside the Dungeon",
        "description": "You emerge into the open air. Trees sway in the breeze. The dungeon entrance yawns behind you like a dark mouth.",
        "exits": {"north": "entrance"},
        "items": [],
        "first_visit": True,
        "dark": False,
        "is_exit": True,
    },
}

SAVE_FILE = "dungeon_save.json"

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack_bonus = 0
        self.defense_bonus = 0
        self.inventory = []
        self.gold = 0
        self.xp = 0
        self.level = 1
        self.current_room = "entrance"
        self.visited_rooms = set()
        self.kills = 0
        self.steps = 0
        self.poisoned = False
        self.poison_turns = 0

    def xp_to_next_level(self):
        return self.level * 100

    def add_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next_level():
            self.xp -= self.xp_to_next_level()
            self.level += 1
            self.max_health += 20
            self.health = self.max_health
            self.attack_bonus += 3
            self.defense_bonus += 2
            leveled = True
        return leveled

    def carry_weight(self):
        return sum(ITEMS[i].weight for i in self.inventory if i in ITEMS)

    def max_carry(self):
        return 15 + self.level * 2

    def has_item(self, item_name):
        return item_name in self.inventory

    def to_dict(self):
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "inventory": self.inventory,
            "gold": self.gold,
            "xp": self.xp,
            "level": self.level,
            "current_room": self.current_room,
            "visited_rooms": list(self.visited_rooms),
            "kills": self.kills,
            "steps": self.steps,
            "poisoned": self.poisoned,
            "poison_turns": self.poison_turns,
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data["name"])
        p.health = data["health"]
        p.max_health = data["max_health"]
        p.attack_bonus = data.get("attack_bonus", 0)
        p.defense_bonus = data.get("defense_bonus", 0)
        p.inventory = data["inventory"]
        p.gold = data.get("gold", 0)
        p.xp = data["xp"]
        p.level = data["level"]
        p.current_room = data["current_room"]
        p.visited_rooms = set(data.get("visited_rooms", []))
        p.kills = data.get("kills", 0)
        p.steps = data.get("steps", 0)
        p.poisoned = data.get("poisoned", False)
        p.poison_turns = data.get("poison_turns", 0)
        return p


class TextAdventureGame:
    def __init__(self):
        self.player = None
        self.rooms = {k: dict(v) for k, v in ROOMS.items()}
        for room in self.rooms.values():
            room["items"] = list(room.get("items", []))
            if "locked_chest" in room:
                room["locked_chest"] = dict(room["locked_chest"])
                room["locked_chest"]["items"] = list(room["locked_chest"]["items"])
        self.active_monsters = {}
        self.game_over = False
        self.won = False

    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self, secs=1.5):
        time.sleep(secs)

    def print_slow(self, text, delay=0.03):
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def header(self):
        room = self.rooms[self.player.current_room]
        hp_color = Colors.GREEN if self.player.health > 50 else (Colors.YELLOW if self.player.health > 25 else Colors.RED)
        hp_bar_filled = int((self.player.health / self.player.max_health) * 20)
        hp_bar = c(hp_color, "█" * hp_bar_filled) + c(Colors.DIM, "░" * (20 - hp_bar_filled))
        xp_filled = int((self.player.xp / self.player.xp_to_next_level()) * 10)
        xp_bar = c(Colors.CYAN, "▪" * xp_filled) + c(Colors.DIM, "·" * (10 - xp_filled))

        print(c(Colors.DIM, "═" * 60))
        print(f" {c(Colors.BOLD + Colors.WHITE, self.player.name)}  {c(Colors.YELLOW, f'Lv.{self.player.level}')}  "
              f"XP [{xp_bar}{c(Colors.DIM, ']')}  "
              f"{c(Colors.YELLOW, f'⚔  {self.player.kills} kills')}")
        print(f" HP [{hp_bar}{c(Colors.DIM, ']')} "
              f"{c(hp_color, f'{self.player.health}/{self.player.max_health}')}  "
              f"  {c(Colors.YELLOW, f'💰 {self.player.gold}g')}  "
              f"  {c(Colors.CYAN, f'📦 {self.player.carry_weight()}/{self.player.max_carry()}')}")
        if self.player.poisoned:
            print(f" {c(Colors.GREEN, '☠  POISONED')} ({self.player.poison_turns} turns remaining)")
        print(c(Colors.DIM, "─" * 60))
        print(f" {c(Colors.BOLD + Colors.CYAN, room['name'])}")
        print(c(Colors.DIM, "═" * 60))

    def display_room(self):
        room = self.rooms[self.player.current_room]
        is_dark = room.get("dark") and not self.player.has_item("torch")

        if is_dark:
            print(c(Colors.DIM, "\nIt's pitch black. You can barely see your hand in front of your face."))
            print(c(Colors.DIM, "You'll need a torch to explore properly."))
        else:
            print(f"\n{c(Colors.WHITE, room['description'])}")

        room_key = self.player.current_room
        if room_key in self.active_monsters:
            m = self.active_monsters[room_key]
            hp_pct = m["health"] / m["max_health"]
            condition = "unharmed" if hp_pct == 1 else ("lightly wounded" if hp_pct > 0.6 else ("wounded" if hp_pct > 0.3 else "gravely wounded"))
            print(f"\n{c(Colors.RED + Colors.BOLD, f'⚠  A {m[\"name\"]} is here!')} {c(Colors.DIM, f'({condition})')}")

        if room.get("items") and not is_dark:
            items_display = ", ".join(c(Colors.YELLOW, ITEMS[i].display_name()) if i in ITEMS else i for i in room["items"])
            print(f"\n{c(Colors.DIM, 'You see:')} {items_display}")

        if room.get("locked_chest") and not is_dark:
            chest = room["locked_chest"]
            if chest["locked"]:
                print(f"\n{c(Colors.YELLOW, '🔒 There is a locked chest here.')}")
            else:
                if chest["items"]:
                    chest_items = ", ".join(c(Colors.YELLOW, ITEMS[i].display_name()) if i in ITEMS else i for i in chest["items"])
                    print(f"\n{c(Colors.GREEN, '📦 Open chest contains:')} {chest_items}")

        if not is_dark:
            exits = room.get("exits", {})
            exits_display = ", ".join(c(Colors.CYAN, d) for d in exits)
            print(f"\n{c(Colors.DIM, 'Exits:')} {exits_display if exits_display else c(Colors.RED, 'none')}")

    def get_command(self):
        try:
            cmd = input(f"\n{c(Colors.BOLD, '> ')}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "quit", ""
        parts = cmd.split(None, 1)
        if not parts:
            return "", ""
        return parts[0], (parts[1] if len(parts) > 1 else "")

    def move(self, direction):
        room = self.rooms[self.player.current_room]
        if not direction:
            print(c(Colors.RED, "Go where? Specify a direction."))
            return False
        if direction not in room.get("exits", {}):
            valid = ", ".join(room["exits"].keys()) if room.get("exits") else "none"
            print(c(Colors.RED, f"You can't go {direction}. Valid exits: {valid}"))
            return False

        dest = room["exits"][direction]
        dest_room = self.rooms[dest]

        if dest_room.get("locked"):
            req = dest_room.get("required_key")
            if req and not self.player.has_item(req):
                key_name = ITEMS[req].display_name() if req in ITEMS else req
                print(c(Colors.RED, f"The way is sealed. You need the {key_name} to proceed."))
                return False
            else:
                dest_room["locked"] = False
                print(c(Colors.GREEN, "You use your key. The door unlocks with a resonant click."))

        if self.player.current_room in self.active_monsters:
            flee_chance = self.active_monsters[self.player.current_room].get("flee_chance", 0.5)
            if random.random() > flee_chance:
                m = self.active_monsters[self.player.current_room]
                dmg = random.randint(*m["attack"]) - self.player.defense_bonus
                dmg = max(1, dmg)
                self.player.health -= dmg
                print(c(Colors.RED, f"The {m['name']} strikes you as you flee! You take {dmg} damage."))
                if self.player.health <= 0:
                    self.death("cut down while fleeing")
                    return False

        self.player.current_room = dest
        self.player.steps += 1
        self.player.visited_rooms.add(dest)

        self.process_poison_tick()

        if dest_room.get("first_visit", False):
            dest_room["first_visit"] = False
            self.spawn_monster(dest)

        return True

    def spawn_monster(self, room_key):
        room = self.rooms[room_key]
        if "boss" in room and room_key not in self.active_monsters:
            boss_key = room["boss"]
            m = dict(MONSTERS[boss_key])
            m["loot"] = list(m["loot"])
            self.active_monsters[room_key] = m
        elif "monster_spawn" in room and room_key not in self.active_monsters:
            if random.random() < room.get("monster_spawn_chance", 0.5):
                mk = room["monster_spawn"]
                m = dict(MONSTERS[mk])
                m["loot"] = list(m["loot"])
                self.active_monsters[room_key] = m

    def process_poison_tick(self):
        if self.player.poisoned:
            dmg = random.randint(3, 8)
            self.player.health -= dmg
            self.player.poison_turns -= 1
            print(c(Colors.GREEN, f"Poison courses through your veins! You take {dmg} damage."))
            if self.player.poison_turns <= 0:
                self.player.poisoned = False
                print(c(Colors.GREEN, "The poison has run its course. You feel slightly better."))
            if self.player.health <= 0:
                self.death("succumbing to poison")

    def take_item(self, item_name):
        if not item_name:
            print(c(Colors.RED, "Take what?"))
            return
        item_key = item_name.replace(' ', '_')
        room = self.rooms[self.player.current_room]

        if item_key in room["items"]:
            if self.player.carry_weight() + (ITEMS[item_key].weight if item_key in ITEMS else 1) > self.player.max_carry():
                print(c(Colors.RED, "You're carrying too much! Drop something first."))
                return
            self.player.inventory.append(item_key)
            room["items"].remove(item_key)
            item = ITEMS.get(item_key)
            print(c(Colors.GREEN, f"You pick up the {item.display_name() if item else item_name}."))
            if item and item.value > 0:
                print(c(Colors.DIM, f"(Worth approximately {item.value} gold)"))
            return

        chest = room.get("locked_chest")
        if chest and not chest["locked"] and item_key in chest.get("items", []):
            if self.player.carry_weight() + (ITEMS[item_key].weight if item_key in ITEMS else 1) > self.player.max_carry():
                print(c(Colors.RED, "Too heavy! Drop something first."))
                return
            self.player.inventory.append(item_key)
            chest["items"].remove(item_key)
            item = ITEMS.get(item_key)
            print(c(Colors.GREEN, f"You take the {item.display_name() if item else item_name} from the chest."))
            return

        print(c(Colors.RED, f"There is no {item_name} here."))

    def take_all(self):
        room = self.rooms[self.player.current_room]
        taken = []
        skipped = []
        for item_key in list(room["items"]):
            weight = ITEMS[item_key].weight if item_key in ITEMS else 1
            if self.player.carry_weight() + weight <= self.player.max_carry():
                self.player.inventory.append(item_key)
                room["items"].remove(item_key)
                taken.append(item_key)
            else:
                skipped.append(item_key)

        if taken:
            names = ", ".join(ITEMS[i].display_name() if i in ITEMS else i for i in taken)
            print(c(Colors.GREEN, f"You gather: {names}."))
        if skipped:
            names = ", ".join(ITEMS[i].display_name() if i in ITEMS else i for i in skipped)
            print(c(Colors.YELLOW, f"Too heavy to take: {names}."))
        if not taken and not skipped:
            print(c(Colors.DIM, "There's nothing here to take."))

    def drop_item(self, item_name):
        if not item_name:
            print(c(Colors.RED, "Drop what?"))
            return
        item_key = item_name.replace(' ', '_')
        if item_key in self.player.inventory:
            self.player.inventory.remove(item_key)
            self.rooms[self.player.current_room]["items"].append(item_key)
            item = ITEMS.get(item_key)
            print(c(Colors.YELLOW, f"You drop the {item.display_name() if item else item_name}."))
        else:
            print(c(Colors.RED, f"You don't have a {item_name}."))

    def examine_item(self, item_name):
        if not item_name:
            print(c(Colors.RED, "Examine what?"))
            return
        item_key = item_name.replace(' ', '_')
        room = self.rooms[self.player.current_room]
        item = ITEMS.get(item_key)
        if not item:
            print(c(Colors.DIM, "That's not something you can examine."))
            return
        if item_key in self.player.inventory or item_key in room.get("items", []):
            print(f"\n{c(Colors.BOLD, item.display_name().upper())}")
            print(f"  {c(Colors.WHITE, item.description)}")
            print(f"  Weight: {item.weight}  |  Value: ~{item.value}g")
        else:
            print(c(Colors.RED, f"You don't see a {item_name} here or in your pack."))

    def use_item(self, item_name):
        if not item_name:
            print(c(Colors.RED, "Use what?"))
            return
        item_key = item_name.replace(' ', '_')

        if item_key not in self.player.inventory:
            print(c(Colors.RED, f"You don't have a {item_name}."))
            return

        room_key = self.player.current_room
        room = self.rooms[room_key]

        if item_key == "healing_potion":
            healed = min(50, self.player.max_health - self.player.health)
            self.player.health += healed
            self.player.inventory.remove(item_key)
            print(c(Colors.GREEN, f"You drink the healing potion and recover {healed} HP! ({self.player.health}/{self.player.max_health})"))

        elif item_key == "greater_healing_potion":
            healed = self.player.max_health - self.player.health
            self.player.health = self.player.max_health
            self.player.inventory.remove(item_key)
            print(c(Colors.GREEN, f"A surge of vitality! You recover {healed} HP! Fully healed!"))

        elif item_key == "food_ration":
            healed = min(20, self.player.max_health - self.player.health)
            self.player.health += healed
            self.player.inventory.remove(item_key)
            print(c(Colors.GREEN, f"You eat the rations. {healed} HP restored. ({self.player.health}/{self.player.max_health})"))

        elif item_key == "antidote":
            if self.player.poisoned:
                self.player.poisoned = False
                self.player.poison_turns = 0
                self.player.inventory.remove(item_key)
                print(c(Colors.GREEN, "You drink the antidote. The poison is neutralized!"))
            else:
                print(c(Colors.DIM, "You aren't poisoned. Save it for when you need it."))

        elif item_key == "fireball_scroll":
            if room_key in self.active_monsters:
                m = self.active_monsters[room_key]
                dmg = random.randint(40, 70)
                m["health"] -= dmg
                self.player.inventory.remove(item_key)
                print(c(Colors.RED, f"You unleash a fireball! The {m['name']} takes {dmg} damage!"))
                if m["health"] <= 0:
                    self.defeat_monster(room_key)
            else:
                print(c(Colors.DIM, "There's no enemy here to unleash it on. (The scroll disintegrates.)"))
                self.player.inventory.remove(item_key)

        elif item_key == "bomb":
            if room_key in self.active_monsters:
                m = self.active_monsters[room_key]
                dmg = random.randint(50, 90)
                m["health"] -= dmg
                self.player.health -= random.randint(10, 20)
                self.player.inventory.remove(item_key)
                print(c(Colors.RED, f"BOOM! The explosion deals {dmg} damage to the {m['name']}! The blast also hurts you."))
                if m["health"] <= 0:
                    self.defeat_monster(room_key)
            else:
                print(c(Colors.YELLOW, "You throw the bomb and it detonates harmlessly. You take some blast damage!"))
                self.player.health -= random.randint(10, 20)
                self.player.inventory.remove(item_key)
                if self.player.health <= 0:
                    self.death("blown up by their own bomb")

        elif item_key == "lockpick":
            chest = room.get("locked_chest")
            if chest and chest["locked"]:
                if random.random() < 0.75:
                    chest["locked"] = False
                    self.player.inventory.remove(item_key)
                    print(c(Colors.GREEN, "You pick the lock successfully! The chest springs open."))
                else:
                    print(c(Colors.YELLOW, "Your lockpick slips. You'll have to try again."))
                    self.player.inventory.remove(item_key)
            else:
                print(c(Colors.DIM, "There's nothing to pick here."))

        elif item_key in ("rusty_key", "silver_key", "skeleton_key"):
            chest = room.get("locked_chest")
            if chest and chest["locked"]:
                required = chest.get("key")
                if required == item_key or item_key == "skeleton_key":
                    chest["locked"] = False
                    print(c(Colors.GREEN, "The key fits! The chest is now open."))
                else:
                    print(c(Colors.YELLOW, "The key doesn't fit this lock."))
            else:
                print(c(Colors.DIM, "There's nothing to unlock here. Keys for locked doors are used automatically when moving."))

        elif item_key == "old_map":
            self.show_map()

        else:
            item = ITEMS.get(item_key)
            print(c(Colors.DIM, f"You fidget with the {item.display_name() if item else item_name} but nothing happens."))

    def show_inventory(self):
        if not self.player.inventory:
            print(c(Colors.DIM, "Your pack is empty."))
            return
        print(f"\n{c(Colors.BOLD, 'INVENTORY')} (Weight: {self.player.carry_weight()}/{self.player.max_carry()})")
        print(c(Colors.DIM, "─" * 40))
        for item_key in self.player.inventory:
            item = ITEMS.get(item_key)
            if item:
                print(f"  {c(Colors.YELLOW, item.display_name()):<28} {c(Colors.DIM, f'wt:{item.weight}  ~{item.value}g')}")
            else:
                print(f"  {item_key}")
        print(c(Colors.DIM, "─" * 40))

    def show_stats(self):
        p = self.player
        print(f"\n{c(Colors.BOLD, 'CHARACTER STATS')}")
        print(c(Colors.DIM, "─" * 40))
        print(f"  Name:         {c(Colors.WHITE, p.name)}")
        print(f"  Level:        {c(Colors.YELLOW, str(p.level))}")
        print(f"  XP:           {p.xp}/{p.xp_to_next_level()}")
        print(f"  Health:       {p.health}/{p.max_health}")
        print(f"  Attack Bonus: +{p.attack_bonus}")
        print(f"  Defense:      +{p.defense_bonus}")
        print(f"  Gold:         {p.gold}g")
        print(f"  Kills:        {p.kills}")
        print(f"  Steps taken:  {p.steps}")
        print(f"  Rooms visited:{len(p.visited_rooms)}/{len(ROOMS)}")

    def show_map(self):
        if not self.player.has_item("old_map"):
            if self.player.current_room not in self.player.visited_rooms and self.player.current_room != "entrance":
                print(c(Colors.DIM, "You don't have a map."))
                return
        print(f"\n{c(Colors.BOLD, 'EXPLORED ROOMS')}")
        print(c(Colors.DIM, "─" * 40))
        for rk, room in ROOMS.items():
            if rk in self.player.visited_rooms or rk == self.player.current_room:
                marker = c(Colors.CYAN + Colors.BOLD, "► ") if rk == self.player.current_room else "  "
                monster_note = c(Colors.RED, " [!]") if rk in self.active_monsters else ""
                print(f"{marker}{c(Colors.WHITE, room['name'])}{monster_note}")

    def combat(self, action, target):
        room_key = self.player.current_room
        if room_key not in self.active_monsters:
            print(c(Colors.DIM, "There's no enemy here to fight."))
            return

        monster = self.active_monsters[room_key]

        if action == "attack":
            weapon_bonus = 0
            weapon_name = "your fists"
            for w in ["sword", "dagger"]:
                if self.player.has_item(w):
                    weapon_bonus = 15 if w == "sword" else 8
                    weapon_name = ITEMS[w].display_name()
                    break

            base_dmg = random.randint(10, 20)
            total_dmg = base_dmg + weapon_bonus + self.player.attack_bonus
            defense = monster.get("defense", 0)
            dealt = max(1, total_dmg - defense)

            crit = random.random() < 0.15
            if crit:
                dealt = int(dealt * 1.8)
                print(c(Colors.YELLOW + Colors.BOLD, f"CRITICAL HIT! "), end="")

            monster["health"] -= dealt
            print(c(Colors.WHITE, f"You strike with {weapon_name} for {c(Colors.RED, str(dealt))} damage! "
                                  f"({monster['name']}: {max(0, monster['health'])}/{monster['max_health']} HP)"))

            if monster["health"] <= 0:
                self.defeat_monster(room_key)
                return

        elif action == "cast" and target == "magic_scroll":
            if not self.player.has_item("magic_scroll"):
                print(c(Colors.RED, "You don't have a magic scroll."))
                return
            if monster.get("name") == "Ancient Dragon":
                print(c(Colors.MAGENTA + Colors.BOLD, "\nYou read the banishment runes aloud!"))
                print(c(Colors.MAGENTA, "The dragon writhes and howls as the magic takes hold!"))
                self.defeat_monster(room_key, consume_scroll=True)
                return
            else:
                dmg = random.randint(30, 50) + self.player.attack_bonus
                monster["health"] -= dmg
                print(c(Colors.MAGENTA, f"You channel the scroll! {dmg} magical damage!"))
                if monster["health"] <= 0:
                    self.defeat_monster(room_key, consume_scroll=True)
                    return

        else:
            print(c(Colors.RED, "Invalid combat action. Try: attack, or cast magic_scroll"))
            return

        self.monster_attacks(room_key)

    def monster_attacks(self, room_key):
        if room_key not in self.active_monsters:
            return
        monster = self.active_monsters[room_key]

        if monster.get("regenerates"):
            regen = monster["regenerates"]
            monster["health"] = min(monster["max_health"], monster["health"] + regen)
            print(c(Colors.DIM, f"The {monster['name']} regenerates {regen} HP."))

        fire_breath = monster.get("fire_breath_chance", 0)
        if random.random() < fire_breath:
            dmg_range = monster.get("fire_breath_damage", (20, 40))
            raw_dmg = random.randint(*dmg_range)
            defense_reduction = self.player.defense_bonus
            if self.player.has_item("amulet"):
                defense_reduction += 20
                print(c(Colors.CYAN, "Your amulet absorbs some of the fire!"))
            if self.player.has_item("shield"):
                defense_reduction += 10
            dmg = max(1, raw_dmg - defense_reduction)
            self.player.health -= dmg
            print(c(Colors.RED + Colors.BOLD, f"🔥 The dragon breathes fire! You take {dmg} damage!"))
        else:
            raw_dmg = random.randint(*monster["attack"])
            defense_reduction = self.player.defense_bonus
            if self.player.has_item("shield"):
                defense_reduction += 10
            dmg = max(1, raw_dmg - defense_reduction)

            if monster.get("drains_health"):
                drain = min(dmg // 2, dmg)
                monster["health"] = min(monster["max_health"], monster["health"] + drain)
                print(c(Colors.MAGENTA, f"The vampire drains your life! +{drain} HP restored to it."))

            self.player.health -= dmg
            print(c(Colors.RED, f"The {monster['name']} attacks you for {dmg} damage! ({self.player.health}/{self.player.max_health} HP)"))

            if random.random() < 0.1 and monster.get("name") != "Ancient Dragon":
                self.player.poisoned = True
                self.player.poison_turns = random.randint(3, 6)
                print(c(Colors.GREEN, "You've been poisoned!"))

        if self.player.health <= 0:
            self.death(f"slain by the {monster['name']}")

    def defeat_monster(self, room_key, consume_scroll=False):
        monster = self.active_monsters[room_key]
        print(c(Colors.GREEN + Colors.BOLD, f"\n⚔  The {monster['name']} has been defeated!"))

        xp_gain = monster.get("xp", 20)
        leveled = self.player.add_xp(xp_gain)
        print(c(Colors.CYAN, f"You gain {xp_gain} XP!"))
        if leveled:
            print(c(Colors.YELLOW + Colors.BOLD, f"✨ LEVEL UP! You are now level {self.player.level}! Max HP increased!"))

        self.player.kills += 1

        if consume_scroll and "magic_scroll" in self.player.inventory:
            self.player.inventory.remove("magic_scroll")
            print(c(Colors.DIM, "The magic scroll crumbles to ash."))

        if random.random() < monster.get("loot_chance", 0.5):
            loot_pool = monster.get("loot", [])
            if loot_pool:
                drop = random.choice(loot_pool)
                self.rooms[room_key]["items"].append(drop)
                item = ITEMS.get(drop)
                print(c(Colors.YELLOW, f"The {monster['name']} drops {item.display_name() if item else drop}!"))

        if monster.get("name") == "Ancient Dragon":
            boss_loot = ["dragon_heart", "ancient_crown", "gold_chest"]
            for loot_key in boss_loot:
                self.rooms[room_key]["items"].append(loot_key)
            print(c(Colors.YELLOW + Colors.BOLD, "The dragon's hoard is yours! It contains incredible treasures!"))

        del self.active_monsters[room_key]

    def death(self, cause="unknown causes"):
        self.game_over = True
        self.won = False
        print(c(Colors.RED + Colors.BOLD, f"\n☠  You have died — {cause}."))
        self.print_slow(c(Colors.DIM, "Your legend ends here, in the dark..."), delay=0.04)
        self.player.health = 0

    def check_win(self):
        if self.player.current_room == "outside":
            valuable_items = ["gold_coin", "jewel", "gold_chest", "dragon_heart", "ancient_crown", "jewel"]
            treasure_value = sum(ITEMS[i].value for i in self.player.inventory if i in ITEMS and ITEMS[i].value >= 50)
            self.game_over = True
            if treasure_value > 0 or any(i in self.player.inventory for i in valuable_items):
                self.won = True
                self.player.gold += sum(ITEMS[i].value for i in self.player.inventory if i in ITEMS)
            else:
                self.won = False

    def save_game(self):
        save_data = {
            "player": self.player.to_dict(),
            "rooms": {k: {"items": v["items"], "first_visit": v.get("first_visit", False),
                          "locked": v.get("locked", False)} for k, v in self.rooms.items()},
            "active_monsters": self.active_monsters,
        }
        for k, room in save_data["rooms"].items():
            if "locked_chest" in self.rooms[k]:
                room["locked_chest"] = dict(self.rooms[k]["locked_chest"])
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(save_data, f, indent=2)
            print(c(Colors.GREEN, f"Game saved to {SAVE_FILE}."))
        except Exception as e:
            print(c(Colors.RED, f"Save failed: {e}"))

    def load_game(self):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            self.player = Player.from_dict(data["player"])
            for rk, rdata in data.get("rooms", {}).items():
                if rk in self.rooms:
                    self.rooms[rk]["items"] = rdata["items"]
                    self.rooms[rk]["first_visit"] = rdata.get("first_visit", False)
                    self.rooms[rk]["locked"] = rdata.get("locked", self.rooms[rk].get("locked", False))
                    if "locked_chest" in rdata:
                        self.rooms[rk]["locked_chest"] = rdata["locked_chest"]
            self.active_monsters = data.get("active_monsters", {})
            print(c(Colors.GREEN, "Game loaded successfully!"))
            return True
        except FileNotFoundError:
            print(c(Colors.YELLOW, "No save file found."))
            return False
        except Exception as e:
            print(c(Colors.RED, f"Load failed: {e}"))
            return False

    def show_help(self):
        print(f"\n{c(Colors.BOLD, 'COMMANDS')}")
        print(c(Colors.DIM, "─" * 50))
        cmds = [
            ("go <direction>", "Move (north / south / east / west)"),
            ("look", "Examine current room again"),
            ("take <item>", "Pick up an item"),
            ("take all", "Pick up everything in the room"),
            ("drop <item>", "Drop an item from your pack"),
            ("examine <item>", "Inspect an item closely"),
            ("use <item>", "Use an item (potions, keys, etc.)"),
            ("inventory  (i)", "List carried items"),
            ("attack", "Attack a monster in the room"),
            ("cast <item>", "Cast a magic item in combat"),
            ("stats", "Show your character stats"),
            ("map", "Show explored rooms (needs old map item)"),
            ("save", "Save your progress"),
            ("load", "Load a saved game"),
            ("help  (?)", "Show this help menu"),
            ("quit", "Exit the game"),
        ]
        for cmd, desc in cmds:
            print(f"  {c(Colors.CYAN, f'{cmd:<22}')}{c(Colors.DIM, desc)}")

    def intro(self):
        self.cls()
        print(c(Colors.YELLOW, """
  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
  ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
  ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
  ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
  ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
        """))
        print(c(Colors.BOLD + Colors.WHITE, "                   A D V E N T U R E"))
        print(c(Colors.DIM, "\n  Explore. Fight. Loot. Survive.\n"))
        print(c(Colors.DIM, "═" * 60))

        print(c(Colors.DIM, "\n  [N]ew Game   [L]oad Game   [Q]uit\n"))
        choice = input(c(Colors.BOLD, "  > ")).strip().lower()

        if choice in ("l", "load"):
            if self.load_game():
                input(c(Colors.DIM, "\nPress Enter to continue..."))
                return
            print(c(Colors.YELLOW, "Starting new game instead."))

        if choice == "q":
            self.game_over = True
            return

        name = input(c(Colors.BOLD, "\n  What is your name, adventurer? ")).strip()
        if not name:
            name = "Stranger"
        self.player = Player(name)
        self.player.visited_rooms.add("entrance")

        print(c(Colors.DIM, f"\n  Welcome, {name}. The dungeon awaits..."))
        print(c(Colors.DIM, "  Find treasure. Defeat the dragon. Escape alive."))
        print(c(Colors.DIM, f"\n  Type {c(Colors.CYAN, 'help')} at any time for a list of commands."))
        self.pause(2)

    def end_screen(self):
        self.cls()
        p = self.player
        print(c(Colors.DIM, "═" * 60))
        if self.won:
            print(c(Colors.YELLOW + Colors.BOLD, "\n  ✦  VICTORY  ✦"))
            print(c(Colors.WHITE, f"\n  {p.name} escapes the dungeon with treasure and glory!"))
        elif self.game_over and not self.won and p.health <= 0:
            print(c(Colors.RED + Colors.BOLD, "\n  ✝  DEFEAT  ✝"))
            print(c(Colors.WHITE, f"\n  {p.name}'s story ends in darkness."))
        else:
            print(c(Colors.DIM, "\n  You leave the dungeon behind."))
        print(c(Colors.DIM, "\n  ─ Final Stats ─"))
        print(f"  Level reached:  {p.level}")
        print(f"  Enemies slain:  {p.kills}")
        print(f"  Rooms visited:  {len(p.visited_rooms)}/{len(ROOMS)}")
        print(f"  Steps taken:    {p.steps}")
        inv_value = sum(ITEMS[i].value for i in p.inventory if i in ITEMS)
        print(f"  Loot value:     ~{inv_value} gold")
        print(c(Colors.DIM, "\n  Thanks for playing."))
        print(c(Colors.DIM, "═" * 60))
        input("\n  Press Enter to exit...")

    def play(self):
        self.intro()
        if self.game_over or not self.player:
            return

        while not self.game_over:
            self.cls()
            self.header()
            self.display_room()

            action, target = self.get_command()

            if action in ("go", "move"):
                if self.move(target):
                    self.check_win()
            elif action == "take":
                if target == "all":
                    self.take_all()
                else:
                    self.take_item(target)
            elif action == "drop":
                self.drop_item(target)
            elif action in ("examine", "ex", "inspect"):
                self.examine_item(target)
            elif action == "use":
                self.use_item(target)
            elif action in ("inventory", "i", "inv"):
                self.show_inventory()
            elif action in ("attack", "fight", "hit", "kill"):
                self.combat("attack", target)
            elif action == "cast":
                self.combat("cast", target)
            elif action in ("stats", "status", "char"):
                self.show_stats()
            elif action in ("map", "m"):
                self.show_map()
            elif action in ("help", "?", "h"):
                self.show_help()
            elif action == "look":
                pass
            elif action == "save":
                self.save_game()
            elif action == "load":
                loaded = self.load_game()
                if loaded:
                    self.game_over = False
                    self.won = False
            elif action in ("quit", "exit", "q"):
                confirm = input(c(Colors.YELLOW, "\nReally quit? (y/n): ")).strip().lower()
                if confirm == "y":
                    self.game_over = True
                    self.won = False
                    self.player.health = 1
            elif action:
                print(c(Colors.DIM, f"Unknown command '{action}'. Type 'help' for a list."))

            if not self.game_over:
                input(c(Colors.DIM, "\nPress Enter..."))

        self.end_screen()


if __name__ == "__main__":
    TextAdventureGame().play()
