import turtle
import colorsys
import math
import random
import time

# --- Constants and Configuration ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
NUM_STARS = 200
STAR_TWINKLE_SPEED = 0.05
BACKGROUND_COLOR = "#00001a" # A dark midnight blue

# --- Setup the Screen ---
screen = turtle.Screen()
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.bgcolor(BACKGROUND_COLOR)
screen.title("Interactive Spiral Nebula")
screen.colormode(1.0)  # Use 0-1 range for color values
screen.tracer(0)      # Disable automatic screen updates for performance

# --- Starfield Background ---
# Create a single turtle to efficiently draw all stars
star_drawer = turtle.Turtle()
star_drawer.hideturtle()
star_drawer.speed(0)
star_drawer.penup()

# Store star properties [x, y, size, brightness, pulse_direction]
stars = []
for _ in range(NUM_STARS):
    stars.append([
        random.randint(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2),
        random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2),
        random.uniform(0.5, 2.5),
        random.uniform(0.2, 1.0),
        random.choice([1, -1])
    ])

def draw_twinkling_stars():
    """Updates star brightness and redraws them for a twinkling effect."""
    star_drawer.clear()
    for star in stars:
        # Update brightness
        star[3] += star[4] * STAR_TWINKLE_SPEED
        if not 0.2 < star[3] < 1.0:
            star[4] *= -1 # Reverse pulse direction

        # Draw the star
        brightness = star[3]
        star_drawer.color(brightness, brightness, brightness)
        star_drawer.goto(star[0], star[1])
        star_drawer.dot(star[2])

# --- Spiral Class for Object-Oriented Drawing ---
class Spiral:
    """Manages the state and drawing of a single animated spiral."""
    def __init__(self, x, y):
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.turtle.penup()
        self.turtle.goto(x, y)
        self.turtle.pendown()

        # Spiral properties
        self.angle = random.uniform(20, 70) * random.choice([-1, 1])
        self.max_distance = random.uniform(150, 400)
        self.hue_offset = random.random()
        self.distance = 1
        self.total_angle = 0
        self.is_active = True

    def update(self):
        """Draws one segment of the spiral and updates its state."""
        if not self.is_active:
            return

        # Smooth hue transition based on total rotation
        hue = (self.total_angle / 360 + self.hue_offset) % 1.0
        
        # Dynamic saturation and value for a "glowing" effect
        saturation = 0.9 + 0.1 * math.sin(self.total_angle * math.pi / 90)
        value = 0.85 + 0.15 * math.sin(self.total_angle * math.pi / 180)
        
        self.turtle.color(colorsys.hsv_to_rgb(hue, saturation, value))

        # Pulsing pen width
        width = 2 + 2.5 * abs(math.sin(self.total_angle * math.pi / 270))
        self.turtle.width(width)
        
        # Draw and advance the spiral
        self.turtle.forward(self.distance * 0.2)
        self.turtle.left(self.angle)
        
        # Update state for the next frame
        self.total_angle += abs(self.angle)
        self.distance += 0.25
        
        # Deactivate spiral if it grows too large
        if self.distance > self.max_distance:
            self.is_active = False
            self.turtle.clear() # Clear the turtle's drawings

# --- Main Animation Logic ---
spirals = []

def create_new_spiral(x, y):
    """Callback function to create a new spiral at the clicked location."""
    spirals.append(Spiral(x, y))

# Write instructions
info_turtle = turtle.Turtle()
info_turtle.hideturtle()
info_turtle.penup()
info_turtle.color("white")
info_turtle.goto(0, SCREEN_HEIGHT // 2 - 40)
info_turtle.write("Click anywhere to create a spiral nebula", align="center", font=("Arial", 16, "normal"))

# Bind the click event
screen.onclick(create_new_spiral)

# Initial spirals to start the show
create_new_spiral(0, 0)
create_new_spiral(150, 100)

# --- Animation Loop ---
try:
    while True:
        # 1. Draw the dynamic background
        draw_twinkling_stars()
        
        # 2. Update and draw each active spiral
        for s in spirals:
            s.update()
            
        # 3. Clean up inactive spirals from the list to save memory
        spirals = [s for s in spirals if s.is_active]
        
        # 4. Refresh the screen with all the new drawings
        screen.update()
        
        # 5. Small delay to control frame rate and reduce CPU usage
        time.sleep(0.01)

except turtle.Terminator:
    # This block will be executed when the user closes the window
    print("Exiting the Spiral Nebula visualization. Goodbye!")
