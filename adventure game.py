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
                "exits": {"north": "hallway", "east": "armory"},
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
                "items": ["magic_scroll"]
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
            }
        }
        
        self.items = {
            "torch": "A flaming torch to light your way in dark places.",
            "key": "A rusted iron key, too corroded to fit any lock.",
            "sword": "A sharp blade capable of piercing dragon scales.",
            "magic_scroll": "A scroll with dragon-banishment runes. It pulses with magical energy.",
            "gold_coin": "A shiny gold coin worth a small fortune.",
            "jewel": "A brilliant gemstone sparkling with inner fire.",
            "dragon_scale": "A tough scale from a dragon's hide.",
            "dragon_treasure": "A magnificent hoard left by the vanquished dragon."
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
        print("\nWelcome brave adventurer! You've entered a mysterious dungeon")
        print("in search of treasure. Be careful of the dangers that lurk within!")
        print("\nYour goal is to find the treasure room and escape with valuables.")
        print("But beware of the dragon!")
        print("\nCommands:")
        print("  go [direction]  - Move in a direction (north, south, east, west)")
        print("  look           - Re-examine your surroundings")
        print("  inventory      - Check your inventory")
        print("  take [item]    - Pick up an item")
        print("  drop [item]    - Drop an item")
        print("  examine [item] - Inspect an item in your inventory")
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
            print("\nItems here:", ", ".join(item.replace('_', ' ') for item in room["items"]))
        
        print("\nExits:", ", ".join(room["exits"].keys()).title() or "None")

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
            valid_exits = list(current_room["exits"].keys())
            exits_str = ', '.join(valid_exits) if valid_exits else "none"
            print(f"Can't go {direction}! Valid exits: {exits_str}.")
            return False

    def take_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        room = self.rooms[self.player["current_room"]]
        if item_name in room["items"]:
            self.player["inventory"].append(item_name)
            room["items"].remove(item_name)
            print(f"You take the {item_name.replace('_', ' ')}.")
            return True
        print(f"No {item_name.replace('_', ' ')} here.")
        return False

    def drop_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        if item_name in self.player["inventory"]:
            self.player["inventory"].remove(item_name)
            self.rooms[self.player["current_room"]]["items"].append(item_name)
            print(f"You drop the {item_name.replace('_', ' ')}.")
        else:
            print(f"You don't have a {item_name.replace('_', ' ')}.")

    def examine_item(self, item_name):
        item_name = item_name.replace(' ', '_')
        if item_name in self.player["inventory"]:
            print(f"{item_name.replace('_', ' ')}: {self.items.get(item_name, 'A mysterious item.')}")
        else:
            print(f"You don't have a {item_name.replace('_', ' ')}.")

    def show_inventory(self):
        if self.player["inventory"]:
            print("Inventory:", ", ".join(item.replace('_', ' ') for item in self.player["inventory"]))
        else:
            print("Your inventory is empty.")

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
                print("\nThe dragon's fiery breath engulfs you!")
                print("Without the sword and scroll, you stand no chance...")
                self.game_over = True

    def check_win_condition(self):
        if (self.player["current_room"] == "treasure_room" and 
            any(item in self.player["inventory"] for item in ["gold_coin", "jewel"])):
            self.win = True
            self.game_over = True

    def show_help(self):
        print("\nCommands:")
        print("go [direction] - Move (north/south/east/west)")
        print("look           - View current room again")
        print("inventory      - Check carried items")
        print("take [item]    - Pick up an item")
        print("drop [item]    - Drop an item")
        print("examine [item] - Inspect an item")
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
                if self.take_item(target):
                    self.check_win_condition()
            elif action == "drop":
                self.drop_item(target)
            elif action == "examine":
                self.examine_item(target)
            elif action == "inventory":
                self.show_inventory()
            elif action == "help":
                self.show_help()
            elif action in ["quit", "exit"]:
                print("\nThanks for playing! Farewell.")
                self.quit_flag = True
                self.game_over = True
            elif action == "look":
                continue  # Room will re-display on next loop
            else:
                print("Invalid command. Type 'help' for options.")
            
            if not self.game_over:
                input("\nPress Enter to continue...")
        
        # Final messages
        self.clear_screen()
        if self.quit_flag:
            print("\nYou leave the dungeon, your story untold...")
        elif self.win:
            print("\n*** YOU ESCAPE WITH THE TREASURE! VICTORY IS YOURS! ***")
        else:
            print("\n~~~ Your adventure ends here. Better luck next time! ~~~")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    TextAdventureGame().play()
