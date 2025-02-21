import random
import sys

def guess_the_number(min_num: int = 1, max_num: int = 100, max_attempts: int = 7) -> None:
    """Play a number guessing game with limits and hints."""
    number = random.randint(min_num, max_num)
    print(f"🔢 Guess a number between {min_num}-{max_num}. You have {max_attempts} tries.")
    
    for attempt in range(1, max_attempts + 1):
        try:
            guess = int(input(f"Attempt {attempt}/{max_attempts}: "))
        except ValueError:
            print("❌ Please enter a valid number.")
            continue
        
        if guess < number:
            print(f"⬆️ Higher! ({guess} is too low)")
        elif guess > number:
            print(f"⬇️ Lower! ({guess} is too high)")
        else:
            print(f"🎉 Correct! You won in {attempt} attempts!")
            return
    
    print(f"💀 Game over! The number was {number}.")

if __name__ == "__main__":
    guess_the_number()  # Run with custom ranges: guess_the_number(1, 500, 10)
