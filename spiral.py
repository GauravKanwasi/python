import turtle
import colorsys
import math
import random

# Setup the screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.title("Enhanced Rainbow Spiral")
screen.colormode(1.0)  # Using 0-1 range for color values

# Draw stars in the background
stars = turtle.Turtle()
stars.hideturtle()
stars.speed(0)
stars.color("white")
for _ in range(50):
    stars.penup()
    stars.goto(random.randint(-400, 400), random.randint(-300, 300))
    stars.pendown()
    stars.dot(2)

# Create the turtle object for the spiral
spiral = turtle.Turtle()
spiral.speed(0)        # Fastest animation speed
spiral.hideturtle()    # Hide the turtle cursor

def draw_enhanced_spiral(angle, max_distance, hue_offset=0):
    distance = 1
    total_angle = 0
    while distance < max_distance:
        # Calculate hue based on total angle for smoother transitions
        hue = ((total_angle / 360) % 1.0) + hue_offset
        hue %= 1.0  # Ensure hue stays between 0 and 1
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        spiral.color(rgb)
        
        # Dynamically adjust pen width with a pulsing effect
        width = 1 + 3 * abs(math.sin(total_angle * math.pi / 180))
        spiral.width(width)
        
        # Draw and rotate
        spiral.forward(distance)
        spiral.left(angle)
        total_angle += angle
        distance += 1

# Draw the first spiral
spiral.penup()
spiral.goto(0, 0)
spiral.pendown()
draw_enhanced_spiral(angle=30, max_distance=200, hue_offset=0)

# Draw the second spiral
spiral.penup()
spiral.goto(0, 0)
spiral.pendown()
draw_enhanced_spiral(angle=-30, max_distance=150, hue_offset=0.5)

# Add title text
spiral.penup()
spiral.goto(0, -280)
spiral.color("white")
spiral.write("Rainbow Spiral", align="center", font=("Arial", 24, "bold"))

# Finish up
screen.exitonclick()
