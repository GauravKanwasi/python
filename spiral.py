import turtle
import colorsys

# Setup the screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.title("Rainbow Spiral")
screen.colormode(1.0)  # Using 0-1 range for color values

# Create the turtle object
spiral = turtle.Turtle()
spiral.speed(0)        # Fastest animation speed
spiral.hideturtle()    # Hide the turtle cursor

def draw_enhanced_spiral(angle, max_distance):
    distance = 1
    while distance < max_distance:
        # Calculate rainbow color using HSV to RGB conversion
        hue = (distance / 50) % 1.0  # Cycle colors every 50 steps
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        spiral.color(rgb)
        
        # Dynamically adjust pen width
        spiral.width(0.5 + (distance / max_distance) * 4)
        
        # Draw and rotate
        spiral.forward(distance)
        spiral.left(angle)
        
        distance += 1

# Position the turtle and draw
spiral.penup()
spiral.goto(0, 0)
spiral.pendown()

draw_enhanced_spiral(angle=12, max_distance=120)

# Finish up
screen.exitonclick()
