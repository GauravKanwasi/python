import turtle
import colorsys
import math
import random

# Setup the screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.title("Enhanced Rainbow Spiral Visualization")
screen.colormode(1.0)  # Using 0-1 range for color values
screen.tracer(0)  # Disable automatic screen updates for better performance

# Function to draw stars in the background
def draw_stars():
    stars = turtle.Turtle()
    stars.hideturtle()
    stars.penup()
    stars.speed(0)
    
    for _ in range(150):  # Increased number of stars
        # Vary star sizes and brightness for depth effect
        size = random.uniform(0.5, 3)
        brightness = random.uniform(0.3, 1.0)
        stars.color((brightness, brightness, brightness))
        
        # Position stars with more natural distribution
        x = random.randint(-390, 390)
        y = random.randint(-290, 290)
        stars.goto(x, y)
        stars.dot(size)

# Draw stars before anything else
draw_stars()

# Create the turtle object for the spiral
spiral = turtle.Turtle()
spiral.speed(0)        # Fastest animation speed
spiral.hideturtle()    # Hide the turtle cursor

# Function to draw enhanced spirals
def draw_enhanced_spiral(angle, max_distance, hue_offset=0, start_pos=(0, 0)):
    spiral.penup()
    spiral.goto(start_pos)
    spiral.pendown()
    
    distance = 1
    total_angle = 0
    previous_width = 0
    
    while distance < max_distance:
        # Calculate hue based on total angle for smoother transitions
        hue = (total_angle / 360 + hue_offset) % 1.0
        
        # Add dynamic saturation and brightness effects
        saturation = 0.85 + 0.15 * math.sin(total_angle * math.pi / 90)
        value = 0.9 + 0.1 * math.sin(total_angle * math.pi / 120)
        
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        spiral.color(rgb)
        
        # Dynamically adjust pen width with a pulsing effect
        width = 1.5 + 3 * abs(math.sin(total_angle * math.pi / 180))
        if abs(width - previous_width) > 0.5:  # Smooth width transitions
            spiral.width(width)
            previous_width = width
        
        # Draw and rotate
        spiral.forward(distance * 0.5)  # Slower expansion for smoother spiral
        spiral.left(angle)
        total_angle += angle
        distance += 0.8  # Slower expansion rate for tighter spiral
        
        # Periodically update the screen for smoother animation
        if int(distance) % 10 == 0:
            screen.update()

# Draw multiple spirals for a more complex visual
draw_enhanced_spiral(angle=25, max_distance=250, hue_offset=0, start_pos=(-20, 10))
draw_enhanced_spiral(angle=-25, max_distance=200, hue_offset=0.5, start_pos=(20, -10))
draw_enhanced_spiral(angle=45, max_distance=180, hue_offset=0.3, start_pos=(0, 0))

# Draw a fourth spiral in the center for more complexity
draw_enhanced_spiral(angle=-45, max_distance=120, hue_offset=0.7, start_pos=(0, 0))

# Add title text
title = turtle.Turtle()
title.hideturtle()
title.penup()
title.goto(0, 250)
title.color("white")
title.write("RAINBOW SPIRAL VISUALIZATION", align="center", font=("Arial", 28, "bold"))

# Add subtitle
subtitle = turtle.Turtle()
subtitle.hideturtle()
subtitle.penup()
subtitle.goto(0, 210)
subtitle.color("lightblue")
subtitle.write("Mathematical Art in Motion", align="center", font=("Arial", 18, "italic"))

# Add information text
info = turtle.Turtle()
info.hideturtle()
info.penup()
info.goto(0, -280)
info.color("lightgray")
info.write("Four Interlocking Spirals with Dynamic Color Effects", align="center", font=("Arial", 14))

# Add instructions
instructions = turtle.Turtle()
instructions.hideturtle()
instructions.penup()
instructions.goto(0, -320)
instructions.color("yellow")
instructions.write("Click anywhere to exit", align="center", font=("Arial", 12, "bold"))

# Add decorative elements around the edges
def draw_decorative_elements():
    decor = turtle.Turtle()
    decor.hideturtle()
    decor.speed(0)
    decor.penup()
    
    # Draw small dots around the edges
    for angle in range(0, 360, 15):
        decor.color(colorsys.hsv_to_rgb(angle/360, 0.7, 1.0))
        decor.goto(380 * math.cos(math.radians(angle)), 280 * math.sin(math.radians(angle)))
        decor.dot(4)
    
    # Draw connecting lines
    decor.pensize(0.5)
    decor.goto(380, 0)
    for _ in range(36):
        hue = random.random()
        decor.color(colorsys.hsv_to_rgb(hue, 0.5, 0.8))
        decor.pendown()
        decor.goto(380 * math.cos(math.radians(_ * 10)), 280 * math.sin(math.radians(_ * 10)))
        decor.penup()

draw_decorative_elements()

# Final screen update
screen.update()

# Finish up
screen.exitonclick()
