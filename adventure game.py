import time
import os

class TextAdventureGame:
    def __init__(self):
        self.player = {
            "name": "",
            "health": 100,
            "inventory": [],
            "current_room": "entrance"
        }
        
        self.rooms = {
            "entrance": {
                "description": "You stand at the entrance of a mysterious dungeon. Torches flicker on the walls.",
                "exits": {"north": "hallway", "east": "armory", "south": "outside"},
                "items": ["torch"]
            },
            "hallway": {
                "description": "A long, dark hallway stretches before you. Strange noises echo in the distance.",
                "exits": {"north": "treasure_room", "south": "entrance", "east": "library"},
                "items": ["key"]
            },
            "armory": {
                "description": "An old armory with rusted weapon racks. A gleaming sword catches your eye.",
                "exits": {"west": "entrance", "north": "library"},
                "items": ["sword"]
            },
            "library": {
                "description": "Dusty bookshelves line the walls. A magical scroll radiates power.",
                "exits": {"west": "hallway", "south": "armory", "east": "monster_room"},
                "items": ["magic_scroll", "healing_potion"]
            },
            "treasure_room": {
                "description": "Piles of gold and jewels glitter before you. The treasure is yours!",
                "exits": {"south": "hallway"},
                "items": ["gold_coin", "jewel"]
            },
            "monster_room": {
                "description": "A fearsome dragon blocks your path, its scales glinting in the dim light!",
                "exits": {"west": "library"},
                "items": ["dragon_scale"],
                "monster": "dragon"
            },
            "outside": {
                "description": "You are outside the dungeon. Fresh air fills your lungs.",
                "exits": {},
                "items": []
            }
        }
        
        self.items = {
            "torch": "A flaming torch to light your way in dark places.",
            "key": "A rusted iron key, too corroded to fit any lock.",
            "sword": "A sharp blade capable of piercing dragon scales.",
            "magic_scroll": "A scroll with dragon-banishment runes. It pulses with magical energy.",
            "gold_coin": "A shiny gold coin worth a small fortune.",
            "jewel": "A brilliant gemstone sparkling with inner fire.",
            "dragon_scale": "A tough scale from a dragon’s hide.",
            "dragon_treasure": "A magnificent hoard left by the vanquished dragon.",
            "healing_potion": "A potion that restores health."
        }
        
        self.game_over = False
        self.win = False
        self.quit_flag = False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def intro(self):
        self.clear_screen()
        print("=" * 60)
        print("                   DUNGEON ADVENTURE")
        print("=" * 60)
        print("\nWelcome, brave adventurer! You’ve entered a mysterious dungeon")
        print("in search of treasure. Be wary of the dangers within!")
        print("\nYour goal is to find treasure and escape the dungeon alive.")
        print("Beware the dragon guarding its hoard!")
        print("\nCommands:")
        print("  go [direction]  - Move (north, south, east, west)")
        print("  look           - Re-examine your surroundings")
        print("  inventory      - Check your inventory")
        print("  take [item]    - Pick up an item")
        print("  drop [item]    - Drop an item")
        print("  examine [item] - Inspect an item in your inventory")
        print("  use [item]     - Use an item from your inventory")
        print("  help           - Show available commands")
        print("  quit           - Exit the game")
        print("=" * 60)
        
        self.player["name"] = input("\nWhat is your name, brave adventurer? ").strip()
        print(f"\nWelcome, {self.player['name']}! Your adventure begins now...")
        time.sleep(2)

    def display_room(self):
        room = self.rooms[self.player["current_room"]]
        print(f"\n{room['description']}")
        
        if room["items"]:
            items = ", ".join(item.replace('_', ' ') for item in room["items"])
            print(f"\nYou see {items} here.")
        
        exits = ", ".join(room["exits"].keys()).title()
        print("\nYou can go " + (exits if exits else "nowhere from here."))

    def get_command(self):
        cmd = input("\nWhat would you like to do? ").strip().lower()
        return cmd.split(' ', 1) if cmd else ['', '']

    def move(self, direction):
        current_room = self.rooms[self.player["current_room"]]
        if direction in current_room["exits"]:
            self.player["current_room"] = current_room["exits"][direction]
            print(f"You move {direction}.")
            return True
        else:
            valid_exits = ', '.join(current_room["exits"].keys()) if current_room["exits"] else "none"
            print(f"Can’t go {direction}! Valid exits: {valid_exits}.")
            return False

    def take_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        room = self.rooms[self.player["current_room"]]
        if item_name in room["items"]:
            self.player["inventory"].append(item_name)
            room["items"].remove(item_name)
            print(f"You take the {item_name.replace('_', ' ')}.")
            return True
        print(f"You don’t see a {item_name.replace('_', ' ')} here.")
        return False

    def drop_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        if item_name in self.player["inventory"]:
            self.player["inventory"].remove(item_name)
            self.rooms[self.player["current_room"]]["items"].append(item_name)
            print(f"You drop the {item_name.replace('_', ' ')}.")
        else:
            print(f"You don’t have a {item_name.replace('_', ' ')}.")

    def examine_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        if item_name in self.player["inventory"]:
            print(f"{item_name.replace('_', ' ')}: {self.items.get(item_name, 'A mysterious item.')}")
        else:
            print(f"You don’t have a {item_name.replace('_', ' ')}.")

    def use_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        if item_name in self.player["inventory"]:
            if item_name == "healing_potion":
                self.player["health"] = min(100, self.player["health"] + 50)
                print("You drink the healing potion and feel invigorated!")
                self.player["inventory"].remove(item_name)
            else:
                print(f"You can’t use the {item_name.replace('_', ' ')}.")
        else:
            print(f"You don’t have a {item_name.replace('_', ' ')}.")

    def show_inventory(self):
        if self.player["inventory"]:
            items = ", ".join(item.replace('_', ' ') for item in self.player["inventory"])
            print(f"You are carrying {items}.")
        else:
            print("You are carrying nothing.")

    def check_encounter(self):
        room = self.rooms[self.player["current_room"]]
        if "monster" in room:
            print("\nThe dragon awakens with a thunderous roar!")
            time.sleep(1)
            if "sword" in self.player["inventory"] and "magic_scroll" in self.player["inventory"]:
                print("\nYou brandish the sword and read the magic scroll!")
                print("The dragon recoils and flees, leaving behind treasure!")
                del room["monster"]
                room["items"].append("dragon_treasure")
            else:
                print("\nThe dragon’s fiery breath scorches you!")
                self.player["health"] -= 50
                if self.player["health"] <= 0:
                    print("You succumb to your injuries...")
                    self.game_over = True
                else:
                    print("You barely escape back to the library.")
                    self.player["current_room"] = "library"

    def check_win_condition(self):
        if self.player["current_room"] == "outside":
            self.game_over = True
            if any(item in self.player["inventory"] for item in ["gold_coin", "jewel", "dragon_treasure"]):
                self.win = True
            else:
                self.win = False

    def show_help(self):
        print("\nCommands:")
        print("go [direction] - Move (north/south/east/west)")
        print("look           - View current room again")
        print("inventory      - Check carried items")
        print("take [item]    - Pick up an item")
        print("drop [item]    - Drop an item")
        print("examine [item] - Inspect an item")
        print("use [item]     - Use an item")
        print("help           - Show this help")
        print("quit           - Exit the game")

    def play(self):
        self.intro()
        while not self.game_over:
            self.clear_screen()
            print(f"Health: {self.player['health']} | Location: {self.player['current_room'].replace('_', ' ').title()}\n")
            self.display_room()
            
            action, target = self.get_command()
            
            if action == "go":
                if self.move(target):
                    self.check_encounter()
                    self.check_win_condition()
            elif action == "take":
                self.take_item(target)
            elif action == "drop":
                self.drop_item(target)
            elif action == "examine":
                self.examine_item(target)
            elif action == "use":
                self.use_item(target)
            elif action == "inventory":
                self.show_inventory()
            elif action == "help":
                self.show_help()
            elif action in ["quit", "exit"]:
                print("\nThanks for playing! Farewell.")
                self.quit_flag = True
                self.game_over = True
            elif action == "look":
                continue  # Room re-displays on next loop
            else:
                print("Invalid command. Type 'help' for options.")
            
            if not self.game_over:
                input("\nPress Enter to continue...")
        
        self.clear_screen()
        if self.quit_flag:
            print("\nYou leave the dungeon, your story untold...")
        elif self.win:
            print("\n*** YOU ESCAPE WITH THE TREASURE! VICTORY IS YOURS! ***")
        else:
            print("\n~~~ You leave the dungeon empty-handed. Better luck next time! ~~~")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    TextAdventureGame().play()
