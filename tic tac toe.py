import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from math import sin

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe++ Enhanced")
        self.current_player = "X"
        self.two_player = True
        self.difficulty = 'medium'
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0
        self.settings_file = "game_settings.json"
        
        # Themes with gradients
        self.themes = {
            'light': {
                'bg': '#f0f0f0', 'button_bg': '#ffffff', 'button_fg': '#000000',
                'hover_bg': '#e0e0e0', 'active_bg': '#b3e5fc', 'text_bg': '#f0f0f0',
                'text_fg': '#000000', 'highlight_colors': ['#c8e6c9', '#bbdefb'],
                'gradient': ('#f0f0f0', '#e0e0e0')
            },
            'dark': {
                'bg': '#2d2d2d', 'button_bg': '#404040', 'button_fg': '#ffffff',
                'hover_bg': '#505050', 'active_bg': '#607d8b', 'text_bg': '#2d2d2d',
                'text_fg': '#ffffff', 'highlight_colors': ['#4a635d', '#3d4d6e'],
                'gradient': ('#2d2d2d', '#404040')
            },
            'ocean': {
                'bg': '#e0f7fa', 'button_bg': '#b2ebf2', 'button_fg': '#006064',
                'hover_bg': '#80deea', 'active_bg': '#4dd0e1', 'text_bg': '#e0f7fa',
                'text_fg': '#006064', 'highlight_colors': ['#a5d6a7', '#90caf9'],
                'gradient': ('#e0f7fa', '#b2ebf2')
            },
            'sunset': {
                'bg': '#fff3e0', 'button_bg': '#ffccbc', 'button_fg': '#bf360c',
                'hover_bg': '#ffab91', 'active_bg': '#ff8a65', 'text_bg': '#fff3e0',
                'text_fg': '#bf360c', 'highlight_colors': ['#ffcdd2', '#ffcc80'],
                'gradient': ('#fff3e0', '#ffccbc')
            }
        }
        self.current_theme = self.themes['light']
        self.load_settings()
        self.create_widgets()
        self.create_menu()
        self.apply_theme()
        self.root.minsize(400, 500)
        self.root.resizable(True, True)
        self.bind_keys()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = self.themes.get(settings.get('theme', 'light'), self.themes['light'])
                    self.difficulty = settings.get('difficulty', 'medium')
                    self.two_player = settings.get('two_player', True)
                    self.x_wins = settings.get('x_wins', 0)
                    self.o_wins = settings.get('o_wins', 0)
                    self.ties = settings.get('ties', 0)
            except json.JSONDecodeError:
                print("Error loading settings, using defaults.")

    def save_settings(self):
        settings = {
            'theme': next(k for k, v in self.themes.items() if v == self.current_theme),
            'difficulty': self.difficulty,
            'two_player': self.two_player,
            'x_wins': self.x_wins,
            'o_wins': self.o_wins,
            'ties': self.ties
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_command(label="Two Player", command=lambda: self.set_game_mode(True))
        game_menu.add_command(label="Single Player", command=lambda: self.set_game_mode(False))
        difficulty_menu = tk.Menu(game_menu, tearoff=0)
        for diff in ['easy', 'medium', 'hard']:
            difficulty_menu.add_command(label=diff.capitalize(), command=lambda d=diff: self.set_difficulty(d))
        game_menu.add_cascade(label="Difficulty", menu=difficulty_menu)
        game_menu.add_command(label="Reset Scores", command=self.reset_scores)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.quit_game)
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        for theme in self.themes:
            theme_menu.add_command(label=theme.capitalize(), command=lambda t=theme: self.set_theme(t))
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        menu_bar.add_cascade(label="Themes", menu=theme_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def create_widgets(self):
        # Gradient background canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=5, sticky='nsew')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Turn indicator
        self.turn_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn", 
                                 font=('Arial', 18, 'bold'), pady=10)
        self.turn_label.grid(row=0, column=0, columnspan=3)

        # Game board
        self.board_frame = tk.Frame(self.root, bg='transparent')
        self.board_frame.grid(row=1, column=0, columnspan=3, pady=10)
        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    self.board_frame, text="", font=('Arial', 40), width=4, height=2,
                    command=lambda r=row, c=col: self.button_click(r, c),
                    relief='flat', bd=2
                )
                btn.bind("<Enter>", self.on_button_enter)
                btn.bind("<Leave>", self.on_button_leave)
                btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
                self.buttons[row][col] = btn
            self.board_frame.grid_rowconfigure(row, weight=1)
            self.board_frame.grid_columnconfigure(col, weight=1)

        # Scoreboard and controls
        self.score_frame = tk.Frame(self.root)
        self.score_frame.grid(row=2, column=0, columnspan=3, pady=10)
        self.x_score = tk.Label(self.score_frame, text=f"X: {self.x_wins}", font=('Arial', 12, 'bold'))
        self.x_score.pack(side='left', padx=10)
        self.o_score = tk.Label(self.score_frame, text=f"O: {self.o_wins}", font=('Arial', 12, 'bold'))
        self.o_score.pack(side='left', padx=10)
        self.tie_score = tk.Label(self.score_frame, text=f"Ties: {self.ties}", font=('Arial', 12))
        self.tie_score.pack(side='left', padx=10)
        
        # Restart button
        self.restart_btn = tk.Button(self.score_frame, text="Restart", command=self.reset_game, font=('Arial', 10))
        self.restart_btn.pack(side='left', padx=10)

        # Status bar
        self.status_var = tk.StringVar()
        self.update_status()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=('Arial', 10), pady=5)
        self.status_label.grid(row=3, column=0, columnspan=3, sticky='ew')

    def update_status(self):
        mode = "Two Player" if self.two_player else f"Single Player ({self.difficulty.capitalize()})"
        self.status_var.set(f"Mode: {mode}")

    def bind_keys(self):
        for i in range(9):
            self.root.bind(str(i+1), lambda e, pos=i: self.handle_key(pos))

    def handle_key(self, pos):
        row, col = divmod(pos, 3)
        if 0 <= row <= 2 and 0 <= col <= 2:
            self.button_click(row, col)

    def on_button_enter(self, event):
        event.widget.config(bg=self.current_theme['hover_bg'], relief='raised')

    def on_button_leave(self, event):
        event.widget.config(bg=self.current_theme['button_bg'], relief='flat')

    def button_click(self, row, col):
        if self.board[row][col] == "":
            self.animate_button_click(row, col)
            self.make_move(row, col)
            if not self.two_player and self.current_player == "O":
                self.toggle_buttons_state(tk.DISABLED)
                self.root.after(800, self.computer_move)  # Delay for realism

    def animate_button_click(self, row, col):
        btn = self.buttons[row][col]
        original_bg = btn.cget('bg')
        self.pulse_effect(btn, self.current_theme['active_bg'], original_bg, 0)

    def pulse_effect(self, widget, color1, color2, count=0, max_count=6):
        if count >= max_count:
            widget.config(bg=color2)
            return
        alpha = (sin(count / 2) + 1) / 2
        blended_color = self.blend_colors(color1, color2, alpha)
        widget.config(bg=blended_color)
        self.root.after(50, lambda: self.pulse_effect(widget, color1, color2, count + 1))

    def blend_colors(self, color1, color2, alpha):
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 * alpha + r2 * (1 - alpha))
        g = int(g1 * alpha + g2 * (1 - alpha))
        b = int(b1 * alpha + b2 * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"

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
        self.turn_label.config(text="Computer thinking...")
        self.root.update()
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
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "O"
                    if self.check_winner():
                        self.board[row][col] = ""
                        self.make_move(row, col)
                        return
                    self.board[row][col] = ""
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "X"
                    if self.check_winner():
                        self.board[row][col] = ""
                        self.make_move(row, col)
                        return
                    self.board[row][col] = ""
        if self.board[1][1] == "":
            self.make_move(1, 1)
            return
        self.computer_move_easy()

    def computer_move_hard(self):
        best_move = self.get_best_move()
        if best_move:
            self.make_move(best_move[0], best_move[1])

    def get_best_move(self):
        best_score = -float('inf')
        best_move = None
        alpha = -float('inf')
        beta = float('inf')
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    self.board[row][col] = "O"
                    score = self.minimax(False, alpha, beta)
                    self.board[row][col] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        return best_move

    def minimax(self, is_maximizing, alpha, beta):
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
                        score = self.minimax(False, alpha, beta)
                        self.board[row][col] = ""
                        best_score = max(score, best_score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == "":
                        self.board[row][col] = "X"
                        score = self.minimax(True, alpha, beta)
                        self.board[row][col] = ""
                        best_score = min(score, best_score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
                if beta <= alpha:
                    break
            return best_score

    def get_winner(self):
        return self.board[self.check_winner()[0][0]][self.check_winner()[0][1]] if self.check_winner() else None

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
        self.save_settings()
        self.root.after(1000, lambda: messagebox.showinfo("Game Over", f"Player {winner} wins!"))
        self.root.after(1200, self.reset_game)

    def handle_tie(self):
        self.ties += 1
        self.tie_score.config(text=f"Ties: {self.ties}")
        self.save_settings()
        self.root.after(1000, lambda: messagebox.showinfo("Game Over", "It's a tie!"))
        self.root.after(1200, self.reset_game)

    def highlight_winner(self, winner_cells):
        color1, color2 = self.current_theme['highlight_colors']
        self.pulse_winner_cells(winner_cells, color1, color2)

    def pulse_winner_cells(self, cells, color1, color2, count=0, max_count=8):
        if count >= max_count:
            for row, col in cells:
                self.buttons[row][col].config(bg=self.current_theme['button_bg'])
            return
        alpha = (sin(count / 2) + 1) / 2
        blended_color = self.blend_colors(color1, color2, alpha)
        for row, col in cells:
            self.buttons[row][col].config(bg=blended_color)
        self.root.after(100, lambda: self.pulse_winner_cells(cells, color1, color2, count + 1))

    def reset_game(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="", bg=self.current_theme['button_bg'], relief='flat')
        self.toggle_buttons_state(tk.NORMAL)
        self.animate_turn_label()

    def toggle_buttons_state(self, state):
        for row in self.buttons:
            for btn in row:
                btn.config(state=state)

    def set_game_mode(self, two_player):
        self.two_player = two_player
        self.reset_game()
        self.update_status()
        self.save_settings()
        mode = "Two Player" if two_player else "Single Player"
        messagebox.showinfo("Game Mode", f"Changed to {mode} mode")

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.update_status()
        self.save_settings()
        messagebox.showinfo("Difficulty", f"Difficulty set to {difficulty.capitalize()}")

    def set_theme(self, theme_name):
        self.current_theme = self.themes[theme_name]
        self.apply_theme()
        self.save_settings()

    def apply_theme(self):
        self.root.config(bg=self.current_theme['bg'])
        self.canvas.delete("all")
        width = self.root.winfo_width() or 400
        height = self.root.winfo_height() or 500
        for i in range(height):
            alpha = i / height
            color = self.blend_colors(self.current_theme['gradient'][0], self.current_theme['gradient'][1], alpha)
            self.canvas.create_line(0, i, width, i, fill=color)
        self.turn_label.config(bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'])
        self.score_frame.config(bg=self.current_theme['bg'])
        self.restart_btn.config(bg=self.current_theme['button_bg'], fg=self.current_theme['button_fg'])
        self.status_label.config(bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'])
        for widget in [self.x_score, self.o_score, self.tie_score]:
            widget.config(bg=self.current_theme['text_bg'], fg=self.current_theme['text_fg'])
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    bg=self.current_theme['button_bg'], fg=self.current_theme['button_fg'],
                    activebackground=self.current_theme['active_bg'], relief='flat'
                )
        self.root.bind("<Configure>", lambda e: self.apply_theme())

    def animate_turn_label(self):
        text = f"Player {self.current_player}'s turn" if self.two_player or self.current_player == "X" else "Computer's turn"
        self.turn_label.config(text=text)
        self.pulse_effect(self.turn_label, self.current_theme['active_bg'], self.current_theme['text_fg'], 0, 6)

    def reset_scores(self):
        self.x_wins = self.o_wins = self.ties = 0
        self.x_score.config(text="X: 0")
        self.o_score.config(text="O: 0")
        self.tie_score.config(text="Ties: 0")
        self.save_settings()

    def show_help(self):
        messagebox.showinfo("How to Play",
            "1. Click a square or use keys 1-9 (numpad layout) to place your mark (X)\n"
            "2. Get 3 in a row to win\n"
            "3. Choose difficulty in single player mode\n"
            "4. Select themes from the menu\n"
            "5. Computer moves automatically in single player\n"
            "6. Use Restart button or menu to start a new game")

    def show_about(self):
        messagebox.showinfo("About", "Tic Tac Toe++ Enhanced\nVersion 3.1\nWith Animations, AI, and Settings Persistence")

    def quit_game(self):
        self.save_settings()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
