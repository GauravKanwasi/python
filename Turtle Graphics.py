import turtle
import random

# Set up the screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Enhanced Spiral Pattern")

# Set up the pen
pen = turtle.Turtle()
pen.speed(0)  # Maximum speed
pen.hideturtle()  # Hide the turtle for cleaner visualization

# Expanded color palette with vibrant hex codes
colors = [
    "#FF5733",  # Red-Orange
    "#C70039",  # Crimson
    "#900C3F",  # Dark Red
    "#581845",  # Plum
    "#FFC300",  # Yellow
    "#DAF7A6",  # Light Green
    "#33FF57",  # Green
    "#33FFF3",  # Aqua
    "#337CFF",  # Blue
    "#8D33FF",  # Purple
    "#FF33F6",  # Pink
    "#FF3380"   # Rose
]

# Function to draw a small decorative circle
def draw_decorative_circle(radius, color):
    pen.penup()
    pen.goto(random.randint(-300, 300), random.randint(-300, 300))
    pen.pendown()
    pen.color(color)
    pen.begin_fill()
    pen.circle(radius)
    pen.end_fill()

# Draw the main spiral
for i in range(200):  # Keep the same number of iterations
    # Dynamically change pensize for depth
    pen.pensize(i / 50 + 1)  # Gradually increases as spiral grows
    
    # Select a random color for each segment for vibrancy
    pen.color(random.choice(colors))
    
    # Draw the spiral with increasing step size
    pen.forward(i * 1.5)
    
    # Add small random variation to the angle for uniqueness
    pen.right(60 + i / 10 + random.uniform(-5, 5))
    
    # Periodically add small decorative circles around the spiral
    if i % 20 == 0:
        current_pos = pen.position()
        current_heading = pen.heading()
        draw_decorative_circle(10, random.choice(colors))
        pen.penup()
        pen.setposition(current_pos)
        pen.setheading(current_heading)
        pen.pendown()

# Create a signature in the corner
pen.penup()
pen.goto(-screen.window_width() / 2 + 20, -screen.window_height() / 2 + 20)
pen.color("white")
pen.write("Enhanced Spiral Art", font=("Arial", 12, "bold"))

screen.exitonclick()  # Close the window when clicked
