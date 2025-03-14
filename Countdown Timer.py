import time

def countdown(seconds: int) -> None:
    """Count down from given seconds with precise timing and clean display.
    
    Args:
        seconds: Non-negative integer representing the countdown duration
    
    Raises:
        ValueError: If input is negative or not an integer
    """
    if not isinstance(seconds, int) or seconds < 0:
        raise ValueError("Seconds must be a non-negative integer")

    try:
        end_time = time.monotonic() + seconds
        while True:
            remaining = end_time - time.monotonic()
            if remaining <= 0:
                break
            
            mins, secs = divmod(int(remaining) + 1, 60)  
            timer_str = f"⏳ Time remaining: {mins:02d}:{secs:02d}\033[K"
            print(timer_str, end="\r", flush=True)
            
            time.sleep(max(0, min(0.1, remaining)))
        
        print("\n🔥 Time's up!")
    except KeyboardInterrupt:
        print("\n⏹️ Countdown stopped by user.")

if __name__ == "__main__":
    try:
        duration = int(input("Enter countdown duration in seconds: "))
        countdown(duration)
    except ValueError:
        print("⚠️ Please enter a valid non-negative integer.")
