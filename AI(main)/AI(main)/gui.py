import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy

from sudoku_generator import generate_puzzle
from performance_evaluator import run_all, evaluate

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# --- BEIGE COLOR THEME ---
BG_COLOR = "#F5F5DC"          
FRAME_COLOR = "#EAE0C8"       
BORDER_COLOR = "#8B7355"      
CLUE_BORDER = "#8B7355"       # Same as table border, as requested
TEXT_COLOR = "#3E2723"        
MUTED_TEXT = "#5C4033"        
BUTTON_COLOR = "#D2B48C"      
BUTTON_HOVER = "#C19A6B"
ACCENT_1 = "#228B22"          
ACCENT_2 = "#008080"          

class AdversarialRaceWindow(ctk.CTkToplevel):
    def __init__(self, master, original_grid=None):
        super().__init__(master)
        self.title("Adversarial Competitive Mode")
        self.geometry("1000x750")
        self.configure(fg_color=BG_COLOR)
        
        if not original_grid or not any(original_grid[r][c] != 0 for r in range(9) for c in range(9)):
            self.original_grid = generate_puzzle("Medium")
        else:
            self.original_grid = copy.deepcopy(original_grid)
            
        self.grid_data1 = [row[:] for row in self.original_grid]
        self.grid_data2 = [row[:] for row in self.original_grid]
        
        self.algorithms = ["Backtracking", "Forward Checking", "AC-3 + MRV", "Simulated Annealing"]
        self._setup_ui()
        
    def _setup_ui(self):
        self.control_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, border_width=2, border_color=BORDER_COLOR, corner_radius=10)
        self.control_frame.pack(fill="x", padx=20, pady=10)
        
        self.control_frame.grid_columnconfigure(5, weight=1)
        
        # Row 0
        ctk.CTkLabel(self.control_frame, text="Difficulty:", text_color=TEXT_COLOR, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(20, 5), pady=(15, 5), sticky="w")
        self.difficulty_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(self.control_frame, values=["Easy", "Medium", "Hard", "Expert"], variable=self.difficulty_var, width=120, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, button_color=BORDER_COLOR).grid(row=0, column=1, padx=5, pady=(15, 5))
        
        ctk.CTkButton(self.control_frame, text="Generate Puzzle", command=self.generate_new_puzzle, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER, width=130, border_width=1, border_color=BORDER_COLOR).grid(row=0, column=2, padx=10, pady=(15, 5))
        
        ctk.CTkButton(self.control_frame, text="Return to Main Menu", command=self.destroy, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color=TEXT_COLOR, border_width=1, border_color=BORDER_COLOR, width=160).grid(row=0, column=6, padx=20, pady=(15, 5), sticky="e")
        
        # Row 1
        ctk.CTkLabel(self.control_frame, text="AI Agent 1:", text_color=TEXT_COLOR, font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=(20, 5), pady=(5, 15), sticky="w")
        self.algo1_var = ctk.StringVar(value="Backtracking")
        ctk.CTkOptionMenu(self.control_frame, values=self.algorithms, variable=self.algo1_var, width=120, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, button_color=BORDER_COLOR).grid(row=1, column=1, padx=5, pady=(5, 15))
        
        ctk.CTkLabel(self.control_frame, text="VS", font=ctk.CTkFont(weight="bold", size=16), text_color=MUTED_TEXT).grid(row=1, column=2, padx=10, pady=(5, 15))
        
        ctk.CTkLabel(self.control_frame, text="AI Agent 2:", text_color=TEXT_COLOR, font=ctk.CTkFont(weight="bold")).grid(row=1, column=3, padx=5, pady=(5, 15))
        self.algo2_var = ctk.StringVar(value="AC-3 + MRV")
        ctk.CTkOptionMenu(self.control_frame, values=self.algorithms, variable=self.algo2_var, width=120, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, button_color=BORDER_COLOR).grid(row=1, column=4, padx=5, pady=(5, 15))
        
        self.start_btn = ctk.CTkButton(self.control_frame, text="Start Race!", command=self.start_race, fg_color=ACCENT_2, hover_color="#006666", text_color="#FFFFFF", border_width=2, border_color=BORDER_COLOR, width=160)
        self.start_btn.grid(row=1, column=6, padx=20, pady=(5, 15), sticky="e")
        
        # Grid Frames
        self.grids_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grids_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.grids_container.grid_columnconfigure(0, weight=1)
        self.grids_container.grid_columnconfigure(1, weight=1)
        
        self.board1_container = ctk.CTkFrame(self.grids_container, fg_color=BORDER_COLOR, corner_radius=4)
        self.board1_container.grid(row=0, column=0, pady=10, padx=10)
        
        self.board2_container = ctk.CTkFrame(self.grids_container, fg_color=BORDER_COLOR, corner_radius=4)
        self.board2_container.grid(row=0, column=1, pady=10, padx=10)
        
        self.cells1, self.cell_frames1 = self._build_grid(self.board1_container)
        self.cells2, self.cell_frames2 = self._build_grid(self.board2_container)
        
        self.update_grid_ui(1, self.grid_data1)
        self.update_grid_ui(2, self.grid_data2)
        
        # Results Analysis Frame (Boxy design)
        self.result_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, border_width=2, border_color=BORDER_COLOR, corner_radius=10, height=80)
        self.result_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.result_frame.pack_propagate(False)
        
        self.result_title = ctk.CTkLabel(self.result_frame, text="STATUS:", font=ctk.CTkFont(size=14, weight="bold"), text_color=MUTED_TEXT)
        self.result_title.pack(side="left", padx=(20, 10), pady=25)
        
        self.result_content = ctk.CTkLabel(self.result_frame, text="Select algorithms and click Start Race to begin.", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR)
        self.result_content.pack(side="left", padx=10, pady=25)
        
    def generate_new_puzzle(self):
        diff = self.difficulty_var.get()
        self.result_title.configure(text="STATUS:", text_color=MUTED_TEXT)
        self.result_content.configure(text=f"Generating {diff} puzzle...", text_color=TEXT_COLOR)
        self.update_idletasks()
        
        self.original_grid = generate_puzzle(diff)
        self.grid_data1 = [row[:] for row in self.original_grid]
        self.grid_data2 = [row[:] for row in self.original_grid]
        
        self.update_grid_ui(1, self.grid_data1)
        self.update_grid_ui(2, self.grid_data2)
        self.result_content.configure(text=f"{diff} puzzle generated. Ready to race!")

    def _build_grid(self, container):
        cells = [[None for _ in range(9)] for _ in range(9)]
        cell_frames = [[None for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                top = 4 if r == 0 else (3 if r % 3 == 0 else 1)
                bottom = 4 if r == 8 else 0
                left = 4 if c == 0 else (3 if c % 3 == 0 else 1)
                right = 4 if c == 8 else 0
                
                cell_outer = ctk.CTkFrame(container, width=32, height=32, corner_radius=0, fg_color=BG_COLOR)
                cell_outer.grid(row=r, column=c, padx=(left, right), pady=(top, bottom))
                cell_outer.grid_propagate(False)
                cell_outer.pack_propagate(False)
                
                # Inner frame acts as the visual cell, adding a tiny margin to prevent border overlap
                cell_inner = ctk.CTkFrame(cell_outer, corner_radius=0, fg_color=BG_COLOR)
                cell_inner.pack(fill="both", expand=True, padx=1, pady=1)
                
                label = ctk.CTkLabel(cell_inner, text="", font=ctk.CTkFont(size=14, weight="bold"))
                label.place(relx=0.5, rely=0.5, anchor="center")
                cell_frames[r][c] = cell_inner
                cells[r][c] = label
        return cells, cell_frames
        
    def update_grid_ui(self, grid_num, grid_data):
        cells = self.cells1 if grid_num == 1 else self.cells2
        frames = self.cell_frames1 if grid_num == 1 else self.cell_frames2
        accent = ACCENT_1 if grid_num == 1 else ACCENT_2
        for r in range(9):
            for c in range(9):
                val = grid_data[r][c]
                cells[r][c].configure(text=str(val) if val != 0 else "")
                is_original = (val != 0 and self.original_grid[r][c] == val)
                if is_original:
                    frames[r][c].configure(border_width=2, border_color=CLUE_BORDER, fg_color=FRAME_COLOR)
                    cells[r][c].configure(text_color=TEXT_COLOR)
                elif val != 0:
                    frames[r][c].configure(border_width=0, fg_color=BG_COLOR)
                    cells[r][c].configure(text_color=accent)
                else:
                    frames[r][c].configure(border_width=0, fg_color=BG_COLOR)
                    cells[r][c].configure(text_color=TEXT_COLOR)
        self.update_idletasks()
        
    def start_race(self):
        self.start_btn.configure(state="disabled")
        self.result_title.configure(text="STATUS:", text_color=MUTED_TEXT)
        self.result_content.configure(text="Racing...", text_color=TEXT_COLOR)
        self.update_idletasks()
        
        algo1 = self.algo1_var.get()
        algo2 = self.algo2_var.get()
        
        grid1 = [row[:] for row in self.original_grid]
        grid2 = [row[:] for row in self.original_grid]
        
        moves1 = []
        moves2 = []
        s1, m1 = evaluate(grid1, algo1, moves=moves1)
        s2, m2 = evaluate(grid2, algo2, moves=moves2)
        
        empty_cells = sum(1 for r in range(9) for c in range(9) if self.original_grid[r][c] == 0)
        target_duration_ms = empty_cells * 200.0
        refresh_rate_ms = 20
        total_ticks = max(1, target_duration_ms / refresh_rate_ms)
        
        batch1 = max(1, int(len(moves1) / total_ticks)) if moves1 else 1
        batch2 = max(1, int(len(moves2) / total_ticks)) if moves2 else 1
        
        self.finished1 = not bool(moves1)
        self.finished2 = not bool(moves2)
        
        if m1['time'] <= m2['time']:
            self.winner_algo, w_m, loser, l_m = algo1, m1, algo2, m2
            self.winner_color = ACCENT_1
        else:
            self.winner_algo, w_m, loser, l_m = algo2, m2, algo1, m1
            self.winner_color = ACCENT_2
            
        self.winner_time = w_m['time']
        self.loser_time = l_m['time']
            
        if self.winner_algo == "AC-3 + MRV":
            self.reasoning = "Won by pruning search space and picking constrained variables."
        elif self.winner_algo == "Forward Checking":
            self.reasoning = "Won by instantly detecting empty domains early."
        elif self.winner_algo == "Backtracking":
            self.reasoning = "Won through sheer speed of state exploration without overhead."
        elif self.winner_algo == "Simulated Annealing":
            self.reasoning = "Quickly reduced conflicts via local search optimization."
            
        if s1: self.grid_data1 = [row[:] for row in self.original_grid]
        if s2: self.grid_data2 = [row[:] for row in self.original_grid]
        self.update_grid_ui(1, self.grid_data1)
        self.update_grid_ui(2, self.grid_data2)
        
        self._animate_race(moves1, moves2, 0, 0, batch1, batch2, s1, s2, refresh_rate_ms)
        
    def _animate_race(self, m1, m2, idx1, idx2, b1, b2, f1, f2, rate):
        if self.finished1 and self.finished2:
            self.result_title.configure(text="WINNER:", text_color=self.winner_color)
            formatted_text = f"{self.winner_algo}  |  Time: {self.winner_time:.4f}s (vs {self.loser_time:.4f}s)  |  Analysis: {self.reasoning}"
            self.result_content.configure(text=formatted_text, text_color=TEXT_COLOR)
            self.start_btn.configure(state="normal")
            return
            
        if not self.finished1:
            e1 = min(idx1 + b1, len(m1))
            for r, c, val in m1[idx1:e1]:
                self.grid_data1[r][c] = val
                self.cells1[r][c].configure(text=str(val) if val != 0 else "")
                if val == 0: self.cells1[r][c].configure(text_color="white")
                elif self.original_grid[r][c] == val: self.cells1[r][c].configure(text_color=MUTED_TEXT)
                else: self.cells1[r][c].configure(text_color=ACCENT_1)
            idx1 = e1
            if idx1 >= len(m1):
                self.grid_data1 = f1
                self.update_grid_ui(1, f1)
                self.finished1 = True
                
        if not self.finished2:
            e2 = min(idx2 + b2, len(m2))
            for r, c, val in m2[idx2:e2]:
                self.grid_data2[r][c] = val
                self.cells2[r][c].configure(text=str(val) if val != 0 else "")
                if val == 0: self.cells2[r][c].configure(text_color="white")
                elif self.original_grid[r][c] == val: self.cells2[r][c].configure(text_color=MUTED_TEXT)
                else: self.cells2[r][c].configure(text_color=ACCENT_2)
            idx2 = e2
            if idx2 >= len(m2):
                self.grid_data2 = f2
                self.update_grid_ui(2, f2)
                self.finished2 = True
                
        self.after(rate, lambda: self._animate_race(m1, m2, idx1, idx2, b1, b2, f1, f2, rate))

class SudokuGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI-Powered Multi-Level Sudoku Solver")
        self.geometry("1100x850")
        self.configure(fg_color=BG_COLOR)
        
        self.grid_data = [[0 for _ in range(9)] for _ in range(9)]
        self.original_grid = [[0 for _ in range(9)] for _ in range(9)]
        
        self.is_paused = False
        self.is_restarting = False
        self.is_animating = False
        
        self.show_splash_screen()
        
    def show_splash_screen(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.splash_frame.pack(fill="both", expand=True)
        
        title_lbl = ctk.CTkLabel(self.splash_frame, text="Sudoku AI", font=ctk.CTkFont(family="Brush Script MT", size=100, weight="bold", slant="italic"), text_color=BORDER_COLOR)
        title_lbl.place(relx=0.5, rely=0.35, anchor="center")
        
        sub_lbl = ctk.CTkLabel(self.splash_frame, text="Advanced Search & Logic", font=ctk.CTkFont(family="Georgia", size=24, slant="italic"), text_color=MUTED_TEXT)
        sub_lbl.place(relx=0.5, rely=0.45, anchor="center")
        
        start_btn = ctk.CTkButton(
            self.splash_frame, text="START GAME", 
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=BUTTON_COLOR, border_width=2, border_color=BORDER_COLOR, 
            text_color=TEXT_COLOR, hover_color=BUTTON_HOVER,
            width=250, height=60, corner_radius=15,
            command=self.start_main_game
        )
        start_btn.place(relx=0.5, rely=0.6, anchor="center")

    def start_main_game(self):
        self.splash_frame.destroy()
        self._setup_main_ui()

    def _setup_main_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=150) 
        self.grid_columnconfigure(1, weight=5)              
        self.grid_columnconfigure(2, weight=1, minsize=150) 
        
        self.title_lbl = ctk.CTkLabel(self, text="Sudoku AI", font=ctk.CTkFont(family="Georgia", size=32, weight="bold", slant="italic"), text_color=TEXT_COLOR)
        self.title_lbl.grid(row=0, column=0, columnspan=3, pady=15)
        
        # COLUMN 0: LEFT
        self.left_col = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=10, border_width=2, border_color=BORDER_COLOR)
        self.left_col.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
        
        ctk.CTkLabel(self.left_col, text="Computations", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR).pack(pady=15)
        
        self.metric_cards = {}
        headers = ["Status", "Total Time (s)", "States Explored", "Time/Node (ms)", "Backtracks", "Clues"]
        for header in headers:
            card = ctk.CTkFrame(self.left_col, fg_color=BG_COLOR, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", padx=15, pady=8)
            
            title = ctk.CTkLabel(card, text=header, text_color=MUTED_TEXT, font=ctk.CTkFont(size=12, weight="bold"))
            title.pack(pady=(5, 0))
            
            val_text = "Ready" if header == "Status" else ("0/81" if header == "Clues" else "-")
            value = ctk.CTkLabel(card, text=val_text, font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR)
            value.pack(pady=(0, 5))
            
            self.metric_cards[header] = value
            
        # COLUMN 1: CENTER
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.grid(row=0, column=0, sticky="nsew")
        
        self.board_container = ctk.CTkFrame(self.grid_frame, fg_color=BORDER_COLOR, corner_radius=4)
        self.board_container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.cell_frames = [[None for _ in range(9)] for _ in range(9)]
        
        for r in range(9):
            for c in range(9):
                top = 4 if r == 0 else (3 if r % 3 == 0 else 1)
                bottom = 4 if r == 8 else 0
                left = 4 if c == 0 else (3 if c % 3 == 0 else 1)
                right = 4 if c == 8 else 0
                
                pad_y = (top, bottom)
                pad_x = (left, right)
                
                # Restored cell size to 45x45 to prevent overcrowding and layout glitches
                cell_outer = ctk.CTkFrame(self.board_container, width=45, height=45, corner_radius=0, fg_color=BG_COLOR)
                cell_outer.grid(row=r, column=c, padx=pad_x, pady=pad_y)
                cell_outer.grid_propagate(False)
                cell_outer.pack_propagate(False)
                
                cell_inner = ctk.CTkFrame(cell_outer, corner_radius=0, fg_color=BG_COLOR)
                cell_inner.pack(fill="both", expand=True, padx=2, pady=2)
                
                label = ctk.CTkLabel(cell_inner, text="", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR)
                label.place(relx=0.5, rely=0.5, anchor="center")
                self.cell_frames[r][c] = cell_inner
                self.cells[r][c] = label
                
        # COLUMN 2: RIGHT
        self.right_col = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=10, border_width=2, border_color=BORDER_COLOR)
        self.right_col.grid(row=1, column=2, sticky="nsew", padx=(10, 20), pady=(0, 20))
        
        ctk.CTkLabel(self.right_col, text="Controls", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR).pack(pady=15)
        
        self.difficulty_var = ctk.StringVar(value="Medium")
        ctk.CTkLabel(self.right_col, text="Difficulty:", text_color=MUTED_TEXT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkOptionMenu(self.right_col, values=["Easy", "Medium", "Hard", "Expert"], variable=self.difficulty_var, fg_color=BUTTON_COLOR, button_color=BORDER_COLOR, text_color=TEXT_COLOR).pack(fill="x", padx=20, pady=5)
        
        self.generate_btn = ctk.CTkButton(self.right_col, text="Generate Puzzle", command=self.generate_new_puzzle, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER, border_width=1, border_color=BORDER_COLOR)
        self.generate_btn.pack(fill="x", padx=20, pady=(5, 15))
        
        self.algo_var = ctk.StringVar(value="Backtracking")
        ctk.CTkLabel(self.right_col, text="Algorithm:", text_color=MUTED_TEXT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkOptionMenu(self.right_col, values=["Backtracking", "Forward Checking", "AC-3 + MRV", "Simulated Annealing"], variable=self.algo_var, fg_color=BUTTON_COLOR, button_color=BORDER_COLOR, text_color=TEXT_COLOR).pack(fill="x", padx=20, pady=5)
        
        self.solve_btn = ctk.CTkButton(self.right_col, text="Solve", command=self.solve_puzzle, fg_color=ACCENT_1, hover_color="#1E6E1E", text_color="#FFFFFF")
        self.solve_btn.pack(fill="x", padx=20, pady=(5, 10))
        
        # Pause / Restart Controls stacked vertically
        self.anim_ctrl_frame = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.anim_ctrl_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.pause_btn = ctk.CTkButton(self.anim_ctrl_frame, text="Pause", command=self.toggle_pause, state="disabled", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, text_color_disabled=MUTED_TEXT, hover_color=BUTTON_HOVER, border_width=1, border_color=BORDER_COLOR)
        self.pause_btn.pack(fill="x", pady=(0, 5))
        
        self.restart_btn = ctk.CTkButton(self.anim_ctrl_frame, text="Restart", command=self.restart_animation, state="disabled", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, text_color_disabled=MUTED_TEXT, hover_color=BUTTON_HOVER, border_width=1, border_color=BORDER_COLOR)
        self.restart_btn.pack(fill="x")
        
        ctk.CTkLabel(self.right_col, text="Modes", text_color=MUTED_TEXT, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.compare_btn = ctk.CTkButton(self.right_col, text="Dashboard", command=self.compare_all, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER, border_width=1, border_color=BORDER_COLOR)
        self.compare_btn.pack(fill="x", padx=20, pady=5)
        
        self.race_btn = ctk.CTkButton(self.right_col, text="Race Mode", command=self.open_race_window, fg_color=ACCENT_2, hover_color="#006666", text_color="#FFFFFF")
        self.race_btn.pack(fill="x", padx=20, pady=5)
            
    def update_grid_ui(self, grid):
        clues_count = 0
        for r in range(9):
            for c in range(9):
                val = grid[r][c]
                self.cells[r][c].configure(text=str(val) if val != 0 else "")
                
                is_original = (val != 0 and self.original_grid[r][c] == val)
                
                if is_original:
                    clues_count += 1
                    # Give clues border color same as table but with padding it won't overlap visually
                    self.cell_frames[r][c].configure(border_width=2, border_color=CLUE_BORDER, fg_color=FRAME_COLOR)
                    self.cells[r][c].configure(text_color=TEXT_COLOR)
                elif val != 0:
                    self.cell_frames[r][c].configure(border_width=0, fg_color=BG_COLOR)
                    self.cells[r][c].configure(text_color=ACCENT_1) 
                else:
                    self.cell_frames[r][c].configure(border_width=0, fg_color=BG_COLOR)
                    self.cells[r][c].configure(text_color=TEXT_COLOR)
                    
        self.metric_cards["Clues"].configure(text=f"{clues_count}/81")
        self.update_idletasks()
        
    def open_race_window(self):
        race_window = AdversarialRaceWindow(self, self.original_grid)
        # Ensure it pops to the front and stays briefly to gain focus over main window
        race_window.lift()
        race_window.focus_force()
        race_window.attributes('-topmost', True)
        race_window.after(50, lambda: race_window.attributes('-topmost', False))
        
    def generate_new_puzzle(self):
        self.is_restarting = True  # kill any ongoing animation
        diff = self.difficulty_var.get()
        self.metric_cards["Status"].configure(text=f"Generating...")
        self.update_idletasks()
        
        self.original_grid = generate_puzzle(diff)
        self.grid_data = [row[:] for row in self.original_grid]
        self.update_grid_ui(self.grid_data)
        self.metric_cards["Status"].configure(text=f"{diff} Ready")
        for h in ["Total Time (s)", "States Explored", "Time/Node (ms)", "Backtracks"]:
            self.metric_cards[h].configure(text="-")
        
        for widget in self.main_frame.grid_slaves(row=0, column=0):
            if widget != self.grid_frame:
                widget.destroy()
        self.grid_frame.tkraise()
        
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_btn.configure(text="Resume" if self.is_paused else "Pause")
        if self.is_paused:
            self.metric_cards["Status"].configure(text="Paused")
        else:
            self.metric_cards["Status"].configure(text="Animating...")
            
    def restart_animation(self):
        self.is_restarting = True
        
    def solve_puzzle(self):
        if not any(self.original_grid[r][c] != 0 for r in range(9) for c in range(9)):
            self.metric_cards["Status"].configure(text="Generate first!")
            return
            
        algo = self.algo_var.get()
        self.metric_cards["Status"].configure(text="Solving...")
        for h in ["Total Time (s)", "States Explored", "Time/Node (ms)", "Backtracks"]:
            self.metric_cards[h].configure(text="-")
        
        self._disable_buttons_for_solve()
        
        self.grid_data = [row[:] for row in self.original_grid]
        self.update_grid_ui(self.grid_data)
        self.update_idletasks()
        
        grid_to_solve = [row[:] for row in self.original_grid]
        moves = []
        solved_grid, metrics = evaluate(grid_to_solve, algo, moves=moves)
        
        if solved_grid:
            self.metric_cards["Status"].configure(text="Animating...")
            self.is_animating = True
            self.is_paused = False
            self.is_restarting = False
            self.pause_btn.configure(text="Pause")
            
            # Calculate exactly how long the animation will take, to match user perception
            empty_cells = sum(1 for r in range(9) for c in range(9) if self.original_grid[r][c] == 0)
            target_duration_ms = empty_cells * 250.0 
            refresh_rate_ms = 20
            total_ticks = max(1, target_duration_ms / refresh_rate_ms)
            batch_size = max(1, int(len(moves) / total_ticks)) if moves else 1
            
            anim_time = (len(moves) / batch_size) * refresh_rate_ms / 1000.0 if moves else metrics.get('time', 0.0)
            metrics['time'] = anim_time
            
            self._playback_moves(moves, solved_grid, metrics, algo)
        else:
            self.metric_cards["Status"].configure(text="Failed.")
            self._enable_buttons()

    def _disable_buttons_for_solve(self):
        self.solve_btn.configure(state="disabled")
        self.generate_btn.configure(state="disabled")
        self.compare_btn.configure(state="disabled")
        self.race_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.restart_btn.configure(state="normal")

    def _enable_buttons(self):
        self.solve_btn.configure(state="normal")
        self.generate_btn.configure(state="normal")
        self.compare_btn.configure(state="normal")
        self.race_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.restart_btn.configure(state="disabled")

    def _playback_moves(self, moves, final_grid, metrics, algo):
        if not moves:
            self.grid_data = final_grid
            self.update_grid_ui(self.grid_data)
            self._finish_solve(metrics)
            return
            
        empty_cells = sum(1 for r in range(9) for c in range(9) if self.original_grid[r][c] == 0)
        target_duration_ms = empty_cells * 250.0 
        
        refresh_rate_ms = 20
        total_ticks = max(1, target_duration_ms / refresh_rate_ms)
        batch_size = max(1, int(len(moves) / total_ticks))
            
        self._animate_step(moves, 0, batch_size, final_grid, metrics, refresh_rate_ms)

    def _animate_step(self, moves, index, batch_size, final_grid, metrics, refresh_rate_ms):
        if self.is_restarting:
            self.is_animating = False
            self.is_restarting = False
            self.grid_data = [row[:] for row in self.original_grid]
            self.update_grid_ui(self.grid_data)
            self.metric_cards["Status"].configure(text="Restarted")
            self._enable_buttons()
            return
            
        if self.is_paused:
            self.after(100, lambda: self._animate_step(moves, index, batch_size, final_grid, metrics, refresh_rate_ms))
            return

        if index >= len(moves):
            self.grid_data = final_grid
            self.update_grid_ui(self.grid_data)
            self._finish_solve(metrics)
            return
            
        end_idx = min(index + batch_size, len(moves))
        for r, c, val in moves[index:end_idx]:
            self.grid_data[r][c] = val
            self.cells[r][c].configure(text=str(val) if val != 0 else "")
            if val == 0:
                self.cells[r][c].configure(text_color="white")
            elif self.original_grid[r][c] == val:
                self.cells[r][c].configure(text_color=MUTED_TEXT)
            else:
                self.cells[r][c].configure(text_color=ACCENT_1) 
                
        self.after(refresh_rate_ms, lambda: self._animate_step(moves, end_idx, batch_size, final_grid, metrics, refresh_rate_ms))

    def _finish_solve(self, metrics):
        self.is_animating = False
        self.update_grid_ui(self.grid_data) 
        self.metric_cards["Status"].configure(text="Optimal" if metrics['optimal'] else "Local Min")
        
        time_taken = metrics['time']
        states = metrics['states_explored']
        backtracks = metrics['backtracks']
        
        self.metric_cards["Total Time (s)"].configure(text=f"{time_taken:.4f}")
        self.metric_cards["States Explored"].configure(text=str(states))
        self.metric_cards["Backtracks"].configure(text=str(backtracks))
        
        if states > 0:
            time_per_node = (time_taken / states) * 1000
            self.metric_cards["Time/Node (ms)"].configure(text=f"{time_per_node:.4f}")
        else:
            self.metric_cards["Time/Node (ms)"].configure(text="0.0000")
            
        self._enable_buttons()
            
    def compare_all(self):
        if not any(self.original_grid[r][c] != 0 for r in range(9) for c in range(9)):
            self.show_dashboard(None) # show empty dashboard
            return
            
        self.metric_cards["Status"].configure(text="Comparing...")
        self.update_idletasks()
        
        results = run_all(self.original_grid)
        self.show_dashboard(results)
        self.metric_cards["Status"].configure(text="Comparison Done.")
        
    def show_dashboard(self, results):
        dashboard_frame = ctk.CTkFrame(self.main_frame, fg_color=FRAME_COLOR, corner_radius=10, border_width=2, border_color=BORDER_COLOR)
        dashboard_frame.grid(row=0, column=0, sticky="nsew")
        
        header_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 0))
        
        title = ctk.CTkLabel(header_frame, text="Performance Dashboard", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR)
        title.pack(side="left", padx=20)
        
        close_btn = ctk.CTkButton(header_frame, text="Return to Grid", command=lambda: dashboard_frame.destroy(), width=120, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color=TEXT_COLOR, border_width=1, border_color=BORDER_COLOR)
        close_btn.pack(side="right", padx=20)
        
        if results is None:
            empty_lbl = ctk.CTkLabel(dashboard_frame, text="No game has been played yet.\nPlease generate and play a puzzle first to see comparisons.", font=ctk.CTkFont(size=18, slant="italic"), text_color=MUTED_TEXT)
            empty_lbl.pack(expand=True)
            return
        
        algos = list(results.keys())
        short_algos = [a.replace(" ", "\n") for a in algos]
        times = [results[a]['metrics']['time'] for a in algos]
        states = [results[a]['metrics']['states_explored'] for a in algos]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), facecolor=FRAME_COLOR)
        colors = [ACCENT_1, ACCENT_2, '#4682B4', '#D2691E']
        
        ax1.bar(short_algos, times, color=colors)
        ax1.set_title('Total Time (s)', color=TEXT_COLOR)
        ax1.tick_params(axis='x', colors=TEXT_COLOR)
        ax1.tick_params(axis='y', colors=TEXT_COLOR)
        ax1.set_facecolor(FRAME_COLOR)
        for spine in ax1.spines.values(): spine.set_edgecolor(BORDER_COLOR)
        
        for i, v in enumerate(times):
            ax1.text(i, v, f"{v:.2f}s", color=TEXT_COLOR, ha='center', va='bottom', fontsize=9)
        
        ax2.bar(short_algos, states, color=colors)
        ax2.set_title('States Explored', color=TEXT_COLOR)
        ax2.set_yscale('log')
        ax2.tick_params(axis='x', colors=TEXT_COLOR)
        ax2.tick_params(axis='y', colors=TEXT_COLOR)
        ax2.set_facecolor(FRAME_COLOR)
        for spine in ax2.spines.values(): spine.set_edgecolor(BORDER_COLOR)
        
        for i, v in enumerate(states):
            ax2.text(i, v, str(v), color=TEXT_COLOR, ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=20, pady=10)

        # Draw Table Analysis
        table_frame = ctk.CTkFrame(dashboard_frame, fg_color=BG_COLOR, corner_radius=10, border_width=2, border_color=BORDER_COLOR)
        table_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        headers = ["Algorithm", "Time (s)", "States Explored", "Time/Node (ms)", "Backtracks", "Optimal?"]
        for i, h in enumerate(headers):
            table_frame.grid_columnconfigure(i, weight=1)
            lbl = ctk.CTkLabel(table_frame, text=h, text_color=MUTED_TEXT, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=i, pady=10, padx=5, sticky="ew")
            
        for row_idx, algo in enumerate(algos, start=1):
            m = results[algo]['metrics']
            time_per_node = (m['time'] / m['states_explored'] * 1000) if m['states_explored'] > 0 else 0
            data = [
                algo, 
                f"{m['time']:.2f}", 
                str(m['states_explored']), 
                f"{time_per_node:.2f}",
                str(m['backtracks']), 
                "Yes" if m['optimal'] else "No"
            ]
            for col_idx, val in enumerate(data):
                lbl = ctk.CTkLabel(table_frame, text=val, font=ctk.CTkFont(size=13), text_color=TEXT_COLOR)
                lbl.grid(row=row_idx, column=col_idx, pady=5, padx=5, sticky="ew")

def run_app():
    app = SudokuGUI()
    app.mainloop()

if __name__ == "__main__":
    run_app()
