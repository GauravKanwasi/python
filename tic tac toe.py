import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os
import math
import time
from PIL import Image, ImageTk
import winsound
import sys

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe++ Ultra")
        self.current_player = "X"
        self.two_player = True
        self.difficulty = 'medium'
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0
        self.settings_file = "game_settings.json"
        self.game_history = []
        self.undo_stack = []
        self.animation_speed = 100  # ms
        self.sounds_enabled = True
        
        # Enhanced themes with gradients
        self.themes = {
            'light': {
                'name': 'Light Mode',
                'bg': '#f0f0f0', 
                'button_bg': '#ffffff', 
                'button_fg': '#000000',
                'hover_bg': '#e0e0e0', 
                'active_bg': '#b3e5fc', 
                'text_bg': '#f0f0f0',
                'text_fg': '#000000', 
                'highlight_colors': ['#c8e6c9', '#bbdefb'],
                'gradient': ('#f0f0f0', '#e0e0e0'),
                'player_x': '#2196F3',
                'player_o': '#F44336',
                'grid_color': '#bdbdbd'
            },
            'dark': {
                'name': 'Dark Mode',
                'bg': '#2d2d2d', 
                'button_bg': '#404040', 
                'button_fg': '#ffffff',
                'hover_bg': '#505050', 
                'active_bg': '#607d8b', 
                'text_bg': '#2d2d2d',
                'text_fg': '#ffffff', 
                'highlight_colors': ['#4a635d', '#3d4d6e'],
                'gradient': ('#2d2d2d', '#404040'),
                'player_x': '#64B5F6',
                'player_o': '#EF5350',
                'grid_color': '#616161'
            },
            'ocean': {
                'name': 'Ocean',
                'bg': '#e0f7fa', 
                'button_bg': '#b2ebf2', 
                'button_fg': '#006064',
                'hover_bg': '#80deea', 
                'active_bg': '#4dd0e1', 
                'text_bg': '#e0f7fa',
                'text_fg': '#006064', 
                'highlight_colors': ['#a5d6a7', '#90caf9'],
                'gradient': ('#e0f7fa', '#b2ebf2'),
                'player_x': '#0288D1',
                'player_o': '#D32F2F',
                'grid_color': '#4DB6AC'
            },
            'sunset': {
                'name': 'Sunset',
                'bg': '#fff3e0', 
                'button_bg': '#ffccbc', 
                'button_fg': '#bf360c',
                'hover_bg': '#ffab91', 
                'active_bg': '#ff8a65', 
                'text_bg': '#fff3e0',
                'text_fg': '#bf360c', 
                'highlight_colors': ['#ffcdd2', '#ffcc80'],
                'gradient': ('#fff3e0', '#ffccbc'),
                'player_x': '#FF5722',
                'player_o': '#7B1FA2',
                'grid_color': '#FFAB91'
            },
            'neon': {
                'name': 'Neon',
                'bg': '#0a0a12', 
                'button_bg': '#1a1a2e', 
                'button_fg': '#ffffff',
                'hover_bg': '#2a2a4e', 
                'active_bg': '#3a3a6e', 
                'text_bg': '#0a0a12',
                'text_fg': '#ffffff', 
                'highlight_colors': ['#ff00cc', '#00ccff'],
                'gradient': ('#0a0a12', '#1a1a2e'),
                'player_x': '#00ffff',
                'player_o': '#ff00ff',
                'grid_color': '#4a0080'
            },
            'forest': {
                'name': 'Forest',
                'bg': '#e8f5e9', 
                'button_bg': '#c8e6c9', 
                'button_fg': '#1b5e20',
                'hover_bg': '#a5d6a7', 
                'active_bg': '#81c784', 
                'text_bg': '#e8f5e9',
                'text_fg': '#1b5e20', 
                'highlight_colors': ['#a5d6a7', '#4caf50'],
                'gradient': ('#e8f5e9', '#c8e6c9'),
                'player_x': '#2e7d32',
                'player_o': '#ff8f00',
                'grid_color': '#66bb6a'
            }
        }
        
        # Default to dark theme
        self.current_theme = self.themes['neon']
        self.load_settings()
        self.create_widgets()
        self.create_menu()
        self.apply_theme()
        self.root.minsize(500, 650)
        self.root.resizable(True, True)
        self.bind_keys()
        
        # Start with a subtle animation
        self.animate_background()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    theme_name = settings.get('theme', 'neon')
                    self.current_theme = self.themes.get(theme_name, self.themes['neon'])
                    self.difficulty = settings.get('difficulty', 'medium')
                    self.two_player = settings.get('two_player', True)
                    self.x_wins = settings.get('x_wins', 0)
                    self.o_wins = settings.get('o_wins', 0)
                    self.ties = settings.get('ties', 0)
                    self.sounds_enabled = settings.get('sounds_enabled', True)
                    self.animation_speed = settings.get('animation_speed', 100)
            except json.JSONDecodeError:
                print("Error loading settings, using defaults.")

    def save_settings(self):
        settings = {
            'theme': next(k for k, v in self.themes.items() if v == self.current_theme),
            'difficulty': self.difficulty,
            'two_player': self.two_player,
            'x_wins': self.x_wins,
            'o_wins': self.o_wins,
            'ties': self.ties,
            'sounds_enabled': self.sounds_enabled,
            'animation_speed': self.animation_speed
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game, accelerator="Ctrl+N")
        game_menu.add_command(label="Two Player", command=lambda: self.set_game_mode(True))
        game_menu.add_command(label="Single Player", command=lambda: self.set_game_mode(False))
        
        # Difficulty submenu
        difficulty_menu = tk.Menu(game_menu, tearoff=0)
        for diff in ['easy', 'medium', 'hard']:
            difficulty_menu.add_command(
                label=diff.capitalize(), 
                command=lambda d=diff: self.set_difficulty(d)
            )
        game_menu.add_cascade(label="Difficulty", menu=difficulty_menu)
        
        # Undo/Redo
        game_menu.add_command(label="Undo", command=self.undo_move, accelerator="Ctrl+Z", state=tk.DISABLED)
        game_menu.add_command(label="Redo", command=self.redo_move, accelerator="Ctrl+Y", state=tk.DISABLED)
        
        game_menu.add_command(label="Reset Scores", command=self.reset_scores)
        game_menu.add_separator()
        
        # Settings submenu
        settings_menu = tk.Menu(game_menu, tearoff=0)
        settings_menu.add_checkbutton(
            label="Enable Sounds", 
            variable=tk.BooleanVar(value=self.sounds_enabled),
            command=self.toggle_sounds
        )
        
        # Animation speed submenu
        speed_menu = tk.Menu(settings_menu, tearoff=0)
        for speed in [50, 100, 200, 300]:
            speed_menu.add_radiobutton(
                label=f"{speed}ms", 
                variable=tk.IntVar(value=self.animation_speed),
                value=speed,
                command=lambda s=speed: self.set_animation_speed(s)
            )
        settings_menu.add_cascade(label="Animation Speed", menu=speed_menu)
        
        game_menu.add_cascade(label="Settings", menu=settings_menu)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.quit_game, accelerator="Alt+F4")
        
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        for theme in self.themes:
            theme_menu.add_command(
                label=self.themes[theme]['name'], 
                command=lambda t=theme: self.set_theme(t)
            )
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="Game Statistics", command=self.show_stats)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Add menus to menubar
        menu_bar.add_cascade(label="Game", menu=game_menu)
        menu_bar.add_cascade(label="Themes", menu=theme_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.reset_game())
        self.root.bind("<Control-N>", lambda e: self.reset_game())
        self.root.bind("<Control-z>", lambda e: self.undo_move())
        self.root.bind("<Control-Z>", lambda e: self.undo_move())
        self.root.bind("<Control-y>", lambda e: self.redo_move())
        self.root.bind("<Control-Y>", lambda e: self.redo_move())

    def create_widgets(self):
        # Main container with gradient background
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with game title
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=20, pady=(15, 5))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="TIC TAC TOE++ ULTRA", 
            font=('Arial', 20, 'bold'),
            foreground=self.current_theme['player_x']
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Theme name display
        self.theme_label = ttk.Label(
            self.header_frame, 
            text=self.current_theme['name'],
            font=('Arial', 10),
            foreground=self.current_theme['player_o']
        )
        self.theme_label.pack(side=tk.RIGHT)
        
        # Turn indicator with animation
        self.turn_frame = ttk.Frame(self.main_frame)
        self.turn_frame.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        self.turn_label = ttk.Label(
            self.turn_frame, 
            text=f"Player {self.current_player}'s turn", 
            font=('Arial', 16, 'bold'),
            foreground=self.current_theme['text_fg']
        )
        self.turn_label.pack()
        
        # Game board with custom grid
        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.pack(pady=20)
        
        # Create a canvas for drawing grid lines
        self.canvas = tk.Canvas(
            self.board_frame, 
            width=330, 
            height=330, 
            bg=self.current_theme['bg'],
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # Draw the grid
        self.draw_grid()
        
        # Create transparent buttons over the grid
        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    self.canvas, 
                    text="", 
                    font=('Arial', 40, 'bold'),
                    width=3, 
                    height=1,
                    command=lambda r=row, c=col: self.button_click(r, c),
                    relief='flat',
                    borderwidth=0,
                    highlightthickness=0,
                    bg='',
                    activebackground=self.current_theme['hover_bg'],
                    fg=self.current_theme['button_fg']
                )
                # Position buttons over the grid
                x = col * 110 + 15
                y = row * 110 + 15
                self.canvas.create_window(x, y, anchor='nw', window=btn, width=100, height=100)
                self.buttons[row][col] = btn
        
        # Scoreboard
        self.score_frame = ttk.Frame(self.main_frame)
        self.score_frame.pack(fill=tk.X, padx=50, pady=(15, 10))
        
        # Player X score
        self.x_frame = ttk.Frame(self.score_frame)
        self.x_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(self.x_frame, text="PLAYER X", 
                 font=('Arial', 12, 'bold'),
                 foreground=self.current_theme['player_x']).pack()
        self.x_score = ttk.Label(self.x_frame, text=str(self.x_wins), 
                                font=('Arial', 24, 'bold'),
                                foreground=self.current_theme['player_x'])
        self.x_score.pack()
        
        # Ties
        self.ties_frame = ttk.Frame(self.score_frame)
        self.ties_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(self.ties_frame, text="TIES", 
                 font=('Arial', 12, 'bold'),
                 foreground=self.current_theme['text_fg']).pack()
        self.tie_score = ttk.Label(self.ties_frame, text=str(self.ties), 
                                  font=('Arial', 24, 'bold'),
                                  foreground=self.current_theme['text_fg'])
        self.tie_score.pack()
        
        # Player O score
        self.o_frame = ttk.Frame(self.score_frame)
        self.o_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(self.o_frame, text="PLAYER O", 
                 font=('Arial', 12, 'bold'),
                 foreground=self.current_theme['player_o']).pack()
        self.o_score = ttk.Label(self.o_frame, text=str(self.o_wins), 
                                font=('Arial', 24, 'bold'),
                                foreground=self.current_theme['player_o'])
        self.o_score.pack()
        
        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, padx=50, pady=10)
        
        # Restart button
        self.restart_btn = ttk.Button(
            self.control_frame, 
            text="New Game", 
            command=self.reset_game,
            style='Control.TButton'
        )
        self.restart_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Undo button
        self.undo_btn = ttk.Button(
            self.control_frame, 
            text="Undo", 
            command=self.undo_move,
            style='Control.TButton',
            state=tk.DISABLED
        )
        self.undo_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Theme button
        self.theme_btn = ttk.Button(
            self.control_frame, 
            text="Change Theme", 
            command=self.cycle_theme,
            style='Control.TButton'
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame, height=25)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.update_status()
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var, 
            font=('Arial', 9),
            foreground=self.current_theme['text_fg'],
            background=self.current_theme['bg']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Animation indicator
        self.animation_indicator = ttk.Label(
            self.status_frame, 
            text="⚡", 
            font=('Arial', 12),
            foreground=self.current_theme['player_x']
        )
        self.animation_indicator.pack(side=tk.RIGHT, padx=10)

    def draw_grid(self):
        """Draw the tic-tac-toe grid with custom styling"""
        self.canvas.delete("grid")  # Clear previous grid
        
        # Draw vertical lines
        for i in range(1, 3):
            self.canvas.create_line(
                i * 110, 10, 
                i * 110, 320, 
                fill=self.current_theme['grid_color'], 
                width=4,
                tags="grid"
            )
        
        # Draw horizontal lines
        for i in range(1, 3):
            self.canvas.create_line(
                10, i * 110, 
                320, i * 110, 
                fill=self.current_theme['grid_color'], 
                width=4,
                tags="grid"
            )
        
        # Add subtle corner decorations
        decor_size = 15
        decor_points = [
            (10, 10, 10+decor_size, 10),  # Top-left
            (320, 10, 320-decor_size, 10),  # Top-right
            (10, 320, 10, 320-decor_size),  # Bottom-left
            (320, 320, 320, 320-decor_size)  # Bottom-right
        ]
        
        for points in decor_points:
            self.canvas.create_line(
                *points,
                fill=self.current_theme['grid_color'],
                width=2,
                tags="grid"
            )

    def update_status(self):
        """Update the status bar text"""
        mode = "Two Player" if self.two_player else f"Single Player ({self.difficulty.capitalize()})"
        sounds = "ON" if self.sounds_enabled else "OFF"
        self.status_var.set(f"Mode: {mode} | Sounds: {sounds} | Animation: {self.animation_speed}ms")

    def bind_keys(self):
        """Bind keyboard shortcuts"""
        for i in range(9):
            self.root.bind(str(i+1), lambda e, pos=i: self.handle_key(pos))

    def handle_key(self, pos):
        """Handle keyboard input for moves"""
        row, col = divmod(pos, 3)
        if 0 <= row <= 2 and 0 <= col <= 2:
            self.button_click(row, col)

    def button_click(self, row, col):
        """Handle button click event"""
        if self.board[row][col] == "":
            self.play_sound("click")
            self.animate_button_click(row, col)
            self.make_move(row, col)
            if not self.two_player and self.current_player == "O":
                self.toggle_buttons_state(tk.DISABLED)
                self.root.after(800, self.computer_move)  # Delay for realism

    def animate_button_click(self, row, col):
        """Animate the button click with a ripple effect"""
        btn = self.buttons[row][col]
        color = self.current_theme['player_x'] if self.current_player == "X" else self.current_theme['player_o']
        self.ripple_effect(btn, color, 0, 5)

    def ripple_effect(self, widget, color, step, max_steps):
        """Create a ripple animation effect on the button"""
        if step >= max_steps:
            return
            
        # Calculate ripple size and opacity
        size = 100 + step * 10
        opacity = 1.0 - (step / max_steps)
        
        # Create ripple circle
        x = widget.winfo_x() + 50
        y = widget.winfo_y() + 50
        ripple = self.canvas.create_oval(
            x-size/2, y-size/2, 
            x+size/2, y+size/2,
            outline=self.blend_colors(color, self.current_theme['bg'], opacity),
            width=2,
            tags="ripple"
        )
        
        # Schedule next step
        self.root.after(self.animation_speed, 
                       lambda: self.update_ripple(ripple, widget, color, step+1, max_steps))

    def update_ripple(self, ripple, widget, color, step, max_steps):
        """Update the ripple animation"""
        if step >= max_steps:
            self.canvas.delete(ripple)
            return
            
        # Update ripple size and opacity
        size = 100 + step * 10
        opacity = 1.0 - (step / max_steps)
        
        x = widget.winfo_x() + 50
        y = widget.winfo_y() + 50
        self.canvas.coords(ripple, 
                          x-size/2, y-size/2, 
                          x+size/2, y+size/2)
        self.canvas.itemconfig(ripple, 
                             outline=self.blend_colors(color, self.current_theme['bg'], opacity))
        
        # Schedule next update
        self.root.after(self.animation_speed, 
                       lambda: self.update_ripple(ripple, widget, color, step+1, max_steps))

    def blend_colors(self, color1, color2, alpha):
        """Blend two colors with a given alpha value"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 * alpha + r2 * (1 - alpha))
        g = int(g1 * alpha + g2 * (1 - alpha))
        b = int(b1 * alpha + b2 * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"

    def make_move(self, row, col):
        """Process a player move"""
        # Save state for undo
        self.undo_stack.append({
            'board': [row[:] for row in self.board],
            'player': self.current_player
        })
        
        # Clear redo stack
        self.undo_stack = self.undo_stack[-10:]  # Keep only last 10 moves
        
        # Update board
        self.buttons[row][col].config(
            text=self.current_player, 
            fg=self.current_theme['player_x'] if self.current_player == "X" else self.current_theme['player_o']
        )
        self.board[row][col] = self.current_player
        
        # Enable undo button
        self.undo_btn.config(state=tk.NORMAL)
        
        # Check game state
        if winner_cells := self.check_winner():
            self.play_sound("win")
            self.handle_win(winner_cells)
        elif self.is_tie():
            self.play_sound("tie")
            self.handle_tie()
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.animate_turn_label()

    def computer_move(self):
        """Computer makes a move based on difficulty"""
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
        """Easy computer - random moves"""
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty:
            row, col = random.choice(empty)
            self.make_move(row, col)

    def computer_move_medium(self):
        """Medium computer - blocks wins when possible"""
        # Try to win
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
        
        # Take center if available
        if self.board[1][1] == "":
            self.make_move(1, 1)
            return
            
        # Take a corner
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        random.shuffle(corners)
        for row, col in corners:
            if self.board[row][col] == "":
                self.make_move(row, col)
                return
                
        # Take any available space
        self.computer_move_easy()

    def computer_move_hard(self):
        """Hard computer - uses minimax algorithm"""
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
            self.x_score.config(text=str(self.x_wins))
        else:
            self.o_wins += 1
            self.o_score.config(text=str(self.o_wins))
        self.save_settings()
        self.game_history.append({
            'winner': winner,
            'board': [row[:] for row in self.board],
            'date': time.strftime("%Y-%m-%d %H:%M")
        })
        self.root.after(1000, lambda: messagebox.showinfo("Game Over", f"Player {winner} wins!"))
        self.root.after(1200, self.reset_game)

    def handle_tie(self):
        self.ties += 1
        self.tie_score.config(text=str(self.ties))
        self.save_settings()
        self.game_history.append({
            'winner': 'tie',
            'board': [row[:] for row in self.board],
            'date': time.strftime("%Y-%m-%d %H:%M")
        })
        self.root.after(1000, lambda: messagebox.showinfo("Game Over", "It's a tie!"))
        self.root.after(1200, self.reset_game)

    def highlight_winner(self, winner_cells):
        color1, color2 = self.current_theme['highlight_colors']
        self.pulse_winner_cells(winner_cells, color1, color2)

    def pulse_winner_cells(self, cells, color1, color2, count=0, max_count=8):
        if count >= max_count:
            # Draw a permanent highlight
            for row, col in cells:
                self.buttons[row][col].config(
                    bg=self.blend_colors(color1, self.current_theme['button_bg'], 0.3)
                )
            return
            
        alpha = (math.sin(count / 2) + 1) / 2
        blended_color = self.blend_colors(color1, color2, alpha)
        
        for row, col in cells:
            self.buttons[row][col].config(bg=blended_color)
            
        self.root.after(self.animation_speed, 
                       lambda: self.pulse_winner_cells(cells, color1, color2, count + 1))

    def reset_game(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    text="", 
                    bg=self.current_theme['button_bg'],
                    fg=self.current_theme['button_fg']
                )
        self.toggle_buttons_state(tk.NORMAL)
        self.undo_btn.config(state=tk.DISABLED)
        self.undo_stack = []
        self.animate_turn_label()
        self.play_sound("reset")

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
        self.theme_label.config(text=self.current_theme['name'])
        self.apply_theme()
        self.save_settings()

    def cycle_theme(self):
        """Cycle through available themes"""
        themes = list(self.themes.keys())
        current_index = themes.index(next(k for k, v in self.themes.items() if v == self.current_theme))
        next_index = (current_index + 1) % len(themes)
        self.set_theme(themes[next_index])
        self.play_sound("click")

    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        # Configure main window
        self.root.config(bg=self.current_theme['bg'])
        self.main_frame.config(style='TFrame')
        self.header_frame.config(style='TFrame')
        
        # Configure labels
        self.title_label.config(foreground=self.current_theme['player_x'])
        self.theme_label.config(foreground=self.current_theme['player_o'])
        self.turn_label.config(foreground=self.current_theme['text_fg'])
        self.status_label.config(
            foreground=self.current_theme['text_fg'],
            background=self.current_theme['bg']
        )
        self.status_frame.config(style='TFrame')
        
        # Configure scores
        self.x_score.config(foreground=self.current_theme['player_x'])
        self.o_score.config(foreground=self.current_theme['player_o'])
        self.tie_score.config(foreground=self.current_theme['text_fg'])
        
        # Configure buttons
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    bg=self.current_theme['button_bg'],
                    fg=self.current_theme['button_fg'],
                    activebackground=self.current_theme['hover_bg']
                )
        
        # Redraw grid
        self.canvas.config(bg=self.current_theme['bg'])
        self.draw_grid()
        
        # Update status
        self.update_status()

    def animate_turn_label(self):
        """Animate the turn label with a pulsing effect"""
        text = f"Player {self.current_player}'s turn" if self.two_player or self.current_player == "X" else "Computer's turn"
        self.turn_label.config(text=text)
        self.pulse_effect(self.turn_label, self.current_theme['active_bg'], self.current_theme['text_fg'], 0, 6)

    def pulse_effect(self, widget, color1, color2, count=0, max_count=6):
        """Create a pulsing animation effect"""
        if count >= max_count:
            widget.config(foreground=color2)
            return
            
        alpha = (math.sin(count) + 1) / 2
        blended_color = self.blend_colors(color1, color2, alpha)
        widget.config(foreground=blended_color)
        
        self.root.after(self.animation_speed, 
                       lambda: self.pulse_effect(widget, color1, color2, count + 1))

    def reset_scores(self):
        """Reset all scores and history"""
        self.x_wins = self.o_wins = self.ties = 0
        self.x_score.config(text="0")
        self.o_score.config(text="0")
        self.tie_score.config(text="0")
        self.game_history = []
        self.save_settings()
        messagebox.showinfo("Scores Reset", "All scores have been reset to zero")

    def undo_move(self):
        """Undo the last move"""
        if not self.undo_stack:
            return
            
        # Get last state
        state = self.undo_stack.pop()
        
        # Restore board state
        self.board = state['board']
        self.current_player = state['player']
        
        # Update UI
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(
                    text=self.board[row][col] if self.board[row][col] else "",
                    fg=self.current_theme['player_x'] if self.board[row][col] == "X" 
                         else self.current_theme['player_o'] if self.board[row][col] == "O" 
                         else self.current_theme['button_fg'],
                    bg=self.current_theme['button_bg']
                )
        
        # Update turn display
        self.animate_turn_label()
        
        # Disable undo button if no more moves to undo
        if not self.undo_stack:
            self.undo_btn.config(state=tk.DISABLED)
        
        self.play_sound("undo")

    def redo_move(self):
        """Redo the last undone move"""
        # Not implemented in this version
        pass

    def toggle_sounds(self):
        """Toggle sound effects on/off"""
        self.sounds_enabled = not self.sounds_enabled
        self.update_status()
        self.save_settings()
        status = "enabled" if self.sounds_enabled else "disabled"
        messagebox.showinfo("Sounds", f"Sound effects {status}")

    def set_animation_speed(self, speed):
        """Set animation speed"""
        self.animation_speed = speed
        self.update_status()
        self.save_settings()
        self.animation_indicator.config(text="⚡" * (4 - [50, 100, 200, 300].index(speed)))

    def play_sound(self, sound_type):
        """Play sound effects"""
        if not self.sounds_enabled or 'win' not in sys.platform:
            return
            
        try:
            if sound_type == "click":
                winsound.Beep(800, 100)
            elif sound_type == "win":
                winsound.Beep(1000, 300)
                winsound.Beep(1200, 200)
                winsound.Beep(1500, 400)
            elif sound_type == "tie":
                winsound.Beep(500, 300)
                winsound.Beep(400, 300)
                winsound.Beep(300, 300)
            elif sound_type == "reset":
                winsound.Beep(1200, 100)
                winsound.Beep(1000, 100)
            elif sound_type == "undo":
                winsound.Beep(600, 150)
                winsound.Beep(700, 150)
        except:
            pass  # Silently ignore sound errors

    def show_help(self):
        """Show game instructions"""
        messagebox.showinfo("How to Play",
            "TIC TAC TOE++ ULTRA - INSTRUCTIONS\n\n"
            "1. Click a square or use keys 1-9 (numpad layout) to place your mark (X)\n"
            "2. Get 3 in a row horizontally, vertically, or diagonally to win\n"
            "3. In single player mode, choose difficulty from the Game menu\n"
            "4. Explore different themes from the Themes menu\n"
            "5. Use Undo to take back moves (Ctrl+Z)\n"
            "6. View game statistics from the Help menu\n"
            "7. Customize sounds and animation speed in Settings")

    def show_stats(self):
        """Show game statistics"""
        stats = f"Games Played: {len(self.game_history)}\n"
        stats += f"X Wins: {self.x_wins}\n"
        stats += f"O Wins: {self.o_wins}\n"
        stats += f"Ties: {self.ties}\n\n"
        
        if self.game_history:
            stats += "Recent Games:\n"
            for i, game in enumerate(self.game_history[-5:], 1):
                winner = "X" if game['winner'] == "X" else "O" if game['winner'] == "O" else "Tie"
                stats += f"{i}. {game['date']} - {winner}\n"
        
        messagebox.showinfo("Game Statistics", stats)

    def show_about(self):
        """Show about information"""
        about_text = (
            "TIC TAC TOE++ ULTRA\n"
            "Version 4.0\n\n"
            "Features:\n"
            "- 6 Beautiful Themes\n"
            "- 3 Difficulty Levels\n"
            "- Move Undo Function\n"
            "- Game Statistics\n"
            "- Sound Effects\n"
            "- Smooth Animations\n"
            "- Responsive Design\n\n"
            "© 2023 Tic Tac Toe++ Team"
        )
        messagebox.showinfo("About", about_text)

    def animate_background(self):
        """Create subtle background animation"""
        if not self.running and not self.paused:
            # Animate the lightning bolt
            text = self.animation_indicator.cget("text")
            if text == "⚡":
                self.animation_indicator.config(text="⚡")
            else:
                self.animation_indicator.config(text="⚡")
        
        self.root.after(500, self.animate_background)

    def quit_game(self):
        """Quit the game"""
        self.save_settings()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configure styles
    style = ttk.Style()
    style.configure('TFrame', background='#1a1a2e')
    style.configure('Control.TButton', font=('Arial', 10, 'bold'), padding=5)
    
    game = TicTacToe(root)
    root.mainloop()
