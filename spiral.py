import turtle
import random

# Setup the screen
screen = turtle.Screen()
screen.bgcolor("black")  # Set background color to black
screen.setup(width=800, height=600)

# Create a turtle object
spiral = turtle.Turtle()
spiral.speed(0)  # Fastest drawing speed
spiral.width(2)  # Set pen width

# List of colors to cycle through
colors = ['red', 'yellow', 'green', 'blue', 'purple', 'orange', 'pink']

# Draw a colorful spiral
angle = 10
distance = 1
while True:
    spiral.color(random.choice(colors))  # Randomly choose a color
    spiral.forward(distance)  # Move the turtle forward
    spiral.left(angle)  # Turn the turtle left
    distance += 1  # Gradually increase the distance for the spiral effect
