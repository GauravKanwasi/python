import time

def countdown(seconds: int) -> None:
    """Count down with a clean terminal display."""
    try:
        for remaining in range(seconds, -1, -1):
            mins, secs = divmod(remaining, 60)
            print(f"⏳ Time remaining: {mins:02d}:{secs:02d}", end="\r", flush=True)
            time.sleep(1)
        print("\n🔥 Time's up!")
    except KeyboardInterrupt:
        print("\n⏹️ Countdown stopped by user.")

# Example usage
countdown(10)  # Handles Ctrl+C gracefully
