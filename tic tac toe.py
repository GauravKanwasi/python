import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe+")
        self.current_player = "X"
        self.two_player = True
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0
        
        # Default theme
        self.current_theme = {
            'bg': 'lightgrey',
            'button_bg': 'white',
            'button_fg': 'black',
            'active_bg': 'lightblue',
            'text_bg': 'lightgrey',
            'text_fg': 'black',
            'highlight_colors': ['#9bff9b', '#9bcdff', '#ff9b9b', '#ffff9b']
        }
        
        self.create_widgets()
        self.create_menu()
        self.apply_theme()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_command(label="Two Player", command=lambda: self.set_game_mode(True))
        game_menu.add_command(label="Single Player", command=lambda: self.set_game_mode(False))
        game_menu.add_command(label="Reset Scores", command=self.reset_scores)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Light", command=lambda: self.set_theme('light'))
        theme_menu.add_command(label="Dark", command=lambda: self.set_theme('dark'))
        theme_menu.add_command(label="Ocean", command=lambda: self.set_theme('ocean'))
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        menu_bar.add_cascade(label="Game", menu=game_menu)
        menu_bar.add_cascade(label="Themes", menu=theme_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)

    def create_widgets(self):
        # Turn indicator
        self.turn_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn", 
                                 font=('Arial', 18, 'bold'), pady=10)
        self.turn_label.grid(row=0, column=0, columnspan=3)
        
        # Game board
        for row in range(3):
            for col in range(3):
                self.buttons[row][col] = tk.Button(
                    self.root, text="", font=('Arial', 40), width=4, height=2,
                    command=lambda row=row, col=col: self.button_click(row, col)
                )
                self.buttons[row][col].grid(row=row+1, column=col, sticky='nsew', padx=2, pady=2)
        
        # Scoreboard
        self.score_frame = tk.Frame(self.root)
        self.score_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.x_score = tk.Label(self.score_frame, text="X: 0", font=('Arial', 12, 'bold'))
        self.x_score.pack(side='left', padx=10)
        
        self.o_score = tk.Label(self.score_frame, text="O: 0", font=('Arial', 12, 'bold'))
        self.o_score.pack(side='left', padx=10)
        
        self.tie_score = tk.Label(self.score_frame, text="Ties: 0", font=('Arial', 12))
        self.tie_score.pack(side='left', padx=10)
        
        # Configure grid layout
        for i in range(3):
            self.root.grid_rowconfigure(i+1, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

    def button_click(self, row, col):

    def make_move(self, row, col):
        self.buttons[row][col].config(text=self.current_player)
        self.board[row][col] = self.current_player
        
        if winner := self.check_winner():
            self.handle_win(winner)
        elif self.is_tie():
            self.handle_tie()
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.update_turn_label()

    def computer_move(self):
        # Try to win
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "O"
                    if self.check_winner():
                        self.make_move(row, col)
                        return
                    self.board[row][col] = ""
        
        # Block player
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "X"
                    if self.check_winner():
                        self.board[row][col] = ""
                        self.make_move(row, col)
                        return
                    self.board[row][col] = ""
        
        # Random move
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty:
            row, col = random.choice(empty)
            self.make_move(row, col)

    def check_winner(self):
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] != "":
                return [(self.board.index(row), 0), (self.board.index(row), 1), (self.board.index(row), 2)]
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return [(0, col), (1, col), (2, col)]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return [(0, 0), (1, 1), (2, 2)]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return [(0, 2), (1, 1), (2, 0)]
        
        return None

    def handle_win(self, winner):
        self.highlight_winner(winner)
        winner_symbol = self.current_player
        if winner_symbol == "X":
            self.x_wins += 1
            self.x_score.config(text=f"X: {self.x_wins}")
        else:
            self.o_wins += 1
            self.o_score.config(text=f"O: {self.o_wins}")
        
        messagebox.showinfo("Game Over", f"Player {winner_symbol} wins!")
        self.reset_game()

    def handle_tie(self):
        self.ties += 1
        self.tie_score.config(text=f"Ties: {self.ties}")
        messagebox.showinfo("Game Over", "It's a tie!")
        self.reset_game()

    def highlight_winner(self, winner):
        color = random.choice(self.current_theme['highlight_colors'])
        for row, col in winner:
            self.buttons[row][col].config(bg=color)



    def reset_game(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    text="", 
                    bg=self.current_theme['button_bg']
                )
        self.update_turn_label()

    def reset_scores(self):
        self.x_wins = self.o_wins = self.ties = 0
        self.x_score.config(text="X: 0")
        self.o_score.config(text="O: 0")
        self.tie_score.config(text="Ties: 0")

    def set_game_mode(self, two_player):
        self.two_player = two_player
        self.reset_game()

    def set_theme(self, theme_name):
        themes = {
            'light': {
                'bg': '#f0f0f0',
                'button_bg': '#ffffff',
                'button_fg': '#000000',
                'active_bg': '#e0e0e0',
                'text_bg': '#f0f0f0',
                'text_fg': '#000000',
                'highlight_colors': ['#c8e6c9', '#bbdefb', '#ffcdd2', '#fff9c4']
            },
            'dark': {
                'bg': '#2d2d2d',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'active_bg': '#606060',
                'text_bg': '#2d2d2d',
                'text_fg': '#ffffff',
                'highlight_colors': ['#4a635d', '#3d4d6e', '#634a4a', '#6e6e3d']
            },
            'ocean': {
                'bg': '#e0f7fa',
                'button_bg': '#b2ebf2',
                'button_fg': '#006064',
                'active_bg': '#80deea',
                'text_bg': '#e0f7fa',
                'text_fg': '#006064',
                'highlight_colors': ['#a5d6a7', '#90caf9', '#ef9a9a', '#fff59d']
            }
        }
        self.current_theme = themes[theme_name]
        self.apply_theme()

    def apply_theme(self):
        self.root.config(bg=self.current_theme['bg'])
        self.turn_label.config(
            bg=self.current_theme['text_bg'],
            fg=self.current_theme['text_fg']
        )
        self.score_frame.config(bg=self.current_theme['bg'])
        
        for widget in [self.x_score, self.o_score, self.tie_score]:
            widget.config(
                bg=self.current_theme['text_bg'],
                fg=self.current_theme['text_fg']
            )
            
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    bg=self.current_theme['button_bg'],
                    fg=self.current_theme['button_fg'],
                    activebackground=self.current_theme['active_bg']
                )

    def update_turn_label(self):
        text = f"Player {self.current_player}'s turn"
        if not self.two_player and self.current_player == "O":
            text = "Computer's turn"
        self.turn_label.config(text=text)

    def show_help(self):
        messagebox.showinfo("How to Play",
            "1. Click a square to place your mark (X)\n"
            "2. Try to get 3 in a row to win\n"
            "3. In single player mode, play against the computer\n"
            "4. Choose different themes from the menu")

    def show_about(self):
        messagebox.showinfo("About", "Tic Tac Toe Enhanced\nVersion 2.0")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
