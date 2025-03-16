
import turtle
import random

screen = turtle.Screen()
screen.bgcolor("black") 
screen.title("Enhanced Spiral Pattern")

pen = turtle.Turtle()
pen.speed(0)  # Maximum speed
pen.pensize(2)  # Slightly thicker line
pen.hideturtle()  # Hide the turtle for cleaner visualization

# color palette
colors = ["red", "purple", "blue", "green", "orange", "yellow", "cyan", "magenta"]


for i in range(200):  # More iterations for a larger pattern
    # Change color every few steps
    pen.color(colors[i % len(colors)])
    
    # Draw the spiral with increasing step size
    pen.forward(i * 1.5)
    pen.right(60 + i/10)  # Gradually changing angle for interesting effect
    
    # Add small circles periodically
    if i % 10 == 0:
        current_pos = pen.position()
        current_heading = pen.heading()
        pen.pensize(1)
        
        # Draw a small filled circle
        pen.begin_fill()
        pen.circle(5)
        pen.end_fill()
        
        # Return to the spiral path
        pen.pensize(2)
        pen.setposition(current_pos)
        pen.setheading(current_heading)

# Create a signature in the corner
pen.penup()
pen.goto(-screen.window_width()/2 + 20, -screen.window_height()/2 + 20)
pen.color("white")
pen.write("Spiral Art", font=("Arial", 12, "bold"))

screen.exitonclick()  # Close the window when clicked
