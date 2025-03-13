import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe++")
        self.current_player = "X"
        self.two_player = True
        self.difficulty = 'medium'  # 'easy', 'medium', 'hard'
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0
        
        # Default theme with animation properties
        self.current_theme = {
            'bg': 'lightgrey',
            'button_bg': 'white',
            'button_fg': 'black',
            'hover_bg': '#e0e0e0',
            'active_bg': 'lightblue',
            'text_bg': 'lightgrey',
            'text_fg': 'black',
            'highlight_colors': ['#9bff9b', '#9bcdff', '#ff9b9b', '#ffff9b']
        }
        
        self.create_widgets()
        self.create_menu()
        self.apply_theme()
        self.root.minsize(400, 500)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_command(label="Two Player", command=lambda: self.set_game_mode(True))
        game_menu.add_command(label="Single Player", command=lambda: self.set_game_mode(False))
        
        # Difficulty submenu
        difficulty_menu = tk.Menu(game_menu, tearoff=0)
        difficulty_menu.add_command(label="Easy", command=lambda: self.set_difficulty('easy'))
        difficulty_menu.add_command(label="Medium", command=lambda: self.set_difficulty('medium'))
        difficulty_menu.add_command(label="Hard", command=lambda: self.set_difficulty('hard'))
        game_menu.add_cascade(label="Difficulty", menu=difficulty_menu)
        
        game_menu.add_command(label="Reset Scores", command=self.reset_scores)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Light", command=lambda: self.set_theme('light'))
        theme_menu.add_command(label="Dark", command=lambda: self.set_theme('dark'))
        theme_menu.add_command(label="Ocean", command=lambda: self.set_theme('ocean'))
        theme_menu.add_command(label="Sunset", command=lambda: self.set_theme('sunset'))
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        menu_bar.add_cascade(label="Game", menu=game_menu)
        menu_bar.add_cascade(label="Themes", menu=theme_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)

    def create_widgets(self):
        # Turn indicator with animation support
        self.turn_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn", 
                                 font=('Arial', 18, 'bold'), pady=10)
        self.turn_label.grid(row=0, column=0, columnspan=3)
        
        # Game board with hover effects
        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    self.root, text="", font=('Arial', 40), width=4, height=2,
                    command=lambda row=row, col=col: self.button_click(row, col)
                )
                btn.bind("<Enter>", self.on_button_enter)
                btn.bind("<Leave>", self.on_button_leave)
                btn.grid(row=row+1, column=col, sticky='nsew', padx=2, pady=2)
                self.buttons[row][col] = btn
        
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

    def on_button_enter(self, event):
        event.widget.config(bg=self.current_theme['hover_bg'])

    def on_button_leave(self, event):
        event.widget.config(bg=self.current_theme['button_bg'])

    def button_click(self, row, col):
        if self.board[row][col] == "":
            self.animate_button_click(row, col)
            self.make_move(row, col)
            
            if not self.two_player and self.current_player == "O":
                self.toggle_buttons_state(tk.DISABLED)
                self.root.after(500, self.computer_move)

    def animate_button_click(self, row, col):
        btn = self.buttons[row][col]
        original_bg = btn.cget('bg')
        btn.config(bg=self.current_theme['active_bg'])
        self.root.after(100, lambda: btn.config(bg=original_bg))

    def make_move(self, row, col):
        self.buttons[row][col].config(text=self.current_player)
        self.board[row][col] = self.current_player
        
        if winner_cells := self.check_winner():
            self.handle_win(winner_cells)
        elif self.is_tie():
            self.handle_tie()
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.animate_turn_label()

    def computer_move(self):
        if self.difficulty == 'easy':
            self.computer_move_easy()
        elif self.difficulty == 'medium':
            self.computer_move_medium()
        elif self.difficulty == 'hard':
            self.computer_move_hard()
        
        self.toggle_buttons_state(tk.NORMAL)

    def computer_move_easy(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty:
            row, col = random.choice(empty)
            self.make_move(row, col)

    def computer_move_medium(self):
        # Win if possible
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "O"
                    if self.check_winner():
                        self.board[row][col] = ""
                        self.make_move(row, col)
                        return
                    self.board[row][col] = ""
        
        # Block player win
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "X"
                    if self.check_winner():
                        self.board[row][col] = ""
                        self.make_move(row, col)
                        return
                    self.board[row][col] = ""
        
        # Take center
        if self.board[1][1] == "":
            self.make_move(1, 1)
            return
            
        # Random move
        self.computer_move_easy()

    def computer_move_hard(self):
        best_move = self.get_best_move()
        if best_move:
            self.make_move(best_move[0], best_move[1])

    def get_best_move(self):
        best_score = -float('inf')
        best_move = None
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "O"
                    score = self.minimax(False)
                    self.board[row][col] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        return best_move

    def minimax(self, is_maximizing):
        winner = self.get_winner()
        if winner == "O": return 1
        if winner == "X": return -1
        if self.is_tie(): return 0

        if is_maximizing:
            best_score = -float('inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == "":
                        self.board[row][col] = "O"
                        score = self.minimax(False)
                        self.board[row][col] = ""
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == "":
                        self.board[row][col] = "X"
                        score = self.minimax(True)
                        self.board[row][col] = ""
                        best_score = min(score, best_score)
            return best_score

    def get_winner(self):
        winner_cells = self.check_winner()
        if winner_cells:
            return self.board[winner_cells[0][0]][winner_cells[0][1]]
        return None

    def check_winner(self):
        # Check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != "":
                return [(row, 0), (row, 1), (row, 2)]
        
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

    def is_tie(self):
        return all(cell != "" for row in self.board for cell in row)

    def handle_win(self, winner_cells):
        self.highlight_winner(winner_cells)
        winner = self.board[winner_cells[0][0]][winner_cells[0][1]]
        if winner == "X":
            self.x_wins += 1
            self.x_score.config(text=f"X: {self.x_wins}")
        else:
            self.o_wins += 1
            self.o_score.config(text=f"O: {self.o_wins}")
        
        self.root.after(100, lambda: messagebox.showinfo("Game Over", f"Player {winner} wins!"))
        self.root.after(200, self.reset_game)

    def handle_tie(self):
        self.ties += 1
        self.tie_score.config(text=f"Ties: {self.ties}")
        self.root.after(100, lambda: messagebox.showinfo("Game Over", "It's a tie!"))
        self.root.after(200, self.reset_game)

    def highlight_winner(self, winner_cells):
        color1, color2 = self.current_theme['highlight_colors'][:2]
        self.pulse_winner_cells(winner_cells, color1, color2)

    def pulse_winner_cells(self, cells, color1, color2, count=0):
        if count >= 4:
            for row, col in cells:
                self.buttons[row][col].config(bg=self.current_theme['button_bg'])
            return
        current_color = color1 if count % 2 == 0 else color2
        for row, col in cells:
            self.buttons[row][col].config(bg=current_color)
        self.root.after(200, lambda: self.pulse_winner_cells(cells, color1, color2, count + 1))

    def reset_game(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="", bg=self.current_theme['button_bg'])
        self.toggle_buttons_state(tk.NORMAL)
        self.animate_turn_label()

    def toggle_buttons_state(self, state):
        for row in self.buttons:
            for btn in row:
                btn.config(state=state)

    def set_game_mode(self, two_player):
        self.two_player = two_player
        self.reset_game()
        mode = "Two Player" if two_player else "Single Player"
        messagebox.showinfo("Game Mode", f"Changed to {mode} mode")

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        messagebox.showinfo("Difficulty", f"Difficulty set to {difficulty.capitalize()}")

    def set_theme(self, theme_name):
        themes = {
            'light': {
                'bg': '#f0f0f0',
                'button_bg': '#ffffff',
                'button_fg': '#000000',
                'hover_bg': '#e0e0e0',
                'active_bg': '#b3e5fc',
                'text_bg': '#f0f0f0',
                'text_fg': '#000000',
                'highlight_colors': ['#c8e6c9', '#bbdefb']
            },
            'dark': {
                'bg': '#2d2d2d',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'hover_bg': '#505050',
                'active_bg': '#607d8b',
                'text_bg': '#2d2d2d',
                'text_fg': '#ffffff',
                'highlight_colors': ['#4a635d', '#3d4d6e']
            },
            'ocean': {
                'bg': '#e0f7fa',
                'button_bg': '#b2ebf2',
                'button_fg': '#006064',
                'hover_bg': '#80deea',
                'active_bg': '#4dd0e1',
                'text_bg': '#e0f7fa',
                'text_fg': '#006064',
                'highlight_colors': ['#a5d6a7', '#90caf9']
            },
            'sunset': {
                'bg': '#fff3e0',
                'button_bg': '#ffccbc',
                'button_fg': '#bf360c',
                'hover_bg': '#ffab91',
                'active_bg': '#ff8a65',
                'text_bg': '#fff3e0',
                'text_fg': '#bf360c',
                'highlight_colors': ['#ffcdd2', '#ffcc80']
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

    def animate_turn_label(self):
        text = f"Player {self.current_player}'s turn"
        if not self.two_player and self.current_player == "O":
            text = "Computer's turn"
        
        # Flash animation
        colors = [self.current_theme['text_fg'], self.current_theme['active_bg']]
        for i in range(4):
            self.turn_label.config(fg=colors[i % 2])
            self.root.update()
            self.root.after(100)
        self.turn_label.config(text=text, fg=self.current_theme['text_fg'])

    def reset_scores(self):
        self.x_wins = self.o_wins = self.ties = 0
        self.x_score.config(text="X: 0")
        self.o_score.config(text="O: 0")
        self.tie_score.config(text="Ties: 0")

    def show_help(self):
        messagebox.showinfo("How to Play",
            "1. Click a square to place your mark (X)\n"
            "2. Try to get 3 in a row to win\n"
            "3. Choose difficulty in single player mode\n"
            "4. Select themes from the menu\n"
            "5. Computer's turn is automated in single player")

    def show_about(self):
        messagebox.showinfo("About", "Tic Tac Toe++\nEnhanced Version 3.0\nWith Animations & AI")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
