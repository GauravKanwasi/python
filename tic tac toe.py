import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.create_widgets()

    def create_widgets(self):
        self.turn_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn", font=('Arial', 20, 'bold'), bg='lightgrey', padx=20, pady=10)
        self.turn_label.grid(row=0, column=0, columnspan=3, sticky='nsew')

        for row in range(3):
            for col in range(3):
                self.buttons[row][col] = tk.Button(self.root, text="", font=('Arial', 40, 'bold'), width=5, height=2,
                                                   bg='white', fg='black', activebackground='lightblue', activeforeground='black',
                                                   command=lambda row=row, col=col: self.button_click(row, col))
                self.buttons[row][col].grid(row=row+1, column=col, sticky='nsew')

        for i in range(3):
            self.root.grid_rowconfigure(i+1, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

    def button_click(self, row, col):
        if self.buttons[row][col].cget("text") == "" and self.check_winner() is None:
            self.buttons[row][col].config(text=self.current_player)
            self.board[row][col] = self.current_player
            winner = self.check_winner()
            if winner:
                self.highlight_winner(winner)
                self.show_fireworks()
                messagebox.showinfo("Tic Tac Toe", f"Player {self.current_player} wins!")
                self.reset_game()
            elif all(all(cell != "" for cell in row) for row in self.board):
                messagebox.showinfo("Tic Tac Toe", "It's a tie!")
                self.reset_game()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.turn_label.config(text=f"Player {self.current_player}'s turn")

    def check_winner(self):
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != "":
                return [(row, 0), (row, 1), (row, 2)]
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return [(0, col), (1, col), (2, col)]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return [(0, 0), (1, 1), (2, 2)]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return [(0, 2), (1, 1), (2, 0)]
        return None

    def highlight_winner(self, winner):
        colors = ['lightgreen', 'lightblue', 'lightcoral', 'lightgoldenrod', 'lightpink', 'lightcyan']
        color = random.choice(colors)
        for row, col in winner:
            self.buttons[row][col].config(bg=color)

    def show_fireworks(self):
        # Create a new window for fireworks
        fireworks = tk.Toplevel(self.root)
        fireworks.title("Fireworks!")
        canvas = tk.Canvas(fireworks, width=400, height=400, bg='black')
        canvas.pack()

        def create_circle(x, y, r, **kwargs):
            return canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

        for _ in range(20):
            x = random.randint(50, 350)
            y = random.randint(50, 350)
            r = random.randint(10, 50)
            color = random.choice(["red", "yellow", "blue", "green", "orange", "purple"])
            create_circle(x, y, r, outline=color, width=2, fill=color)

        fireworks.after(5000, fireworks.destroy)  #  the fireworks window will be closed after 5 seconds

    def reset_game(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="", bg="white")
        self.turn_label.config(text=f"Player {self.current_player}'s turn")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
