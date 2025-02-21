import turtle

# Set up the screen and the turtle
screen = turtle.Screen()
pen = turtle.Turtle()
pen.speed(5)  # Adjust the speed (1-10 scale)

# Draw a spiral pattern
for i in range(100):
    pen.forward(i * 2)  # Move forward with increasing steps
    pen.right(45)       # Turn right by 45 degrees

screen.exitonclick()  # Close the window when clicked
