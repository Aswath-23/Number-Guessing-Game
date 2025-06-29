import tkinter as tk
from tkinter import ttk, messagebox, font
import random
import json
from pathlib import Path

class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Number Guessing Game")
        self.root.geometry("500x650")
        self.root.configure(bg="#2E2E2E")  # Dark background for contrast

        # Brighter color scheme (neon-inspired)
        self.colors = {
            "Easy": "#00FF9D",    # Neon green
            "Medium": "#00D1FF",  # Neon blue
            "Hard": "#FF2D75",    # Neon pink
            "correct": "#00FF00", # Bright green
            "error": "#FF0000",   # Bright red
            "hint": "#FFA500",    # Bright orange
            "entry_bg": "#FFFFFF", # White
            "button_bg": "#6200EA", # Purple
            "button_fg": "#FFFFFF", # White
            "history_even": "#1E1E1E", # Dark gray (even rows)
            "history_odd": "#2E2E2E",  # Slightly lighter gray (odd rows)
            "text_fg": "#FFFFFF",      # White text for dark mode
            "bg": "#2E2E2E"            # Dark background
        }

        # Custom bold font
        self.bold_font = font.Font(family="Arial", size=10, weight="bold")
        self.title_font = font.Font(family="Arial", size=12, weight="bold")

        # Initialize high scores
        self.high_scores_file = Path("high_scores.json")
        if self.high_scores_file.exists():
            with open(self.high_scores_file, "r") as f:
                self.high_scores = json.load(f)
        else:
            self.high_scores = {"Easy": "N/A", "Medium": "N/A", "Hard": "N/A"}

        # Game variables
        self.min_num = 1
        self.max_num = 100
        self.max_attempts = 7
        self.secret_number = 0
        self.attempts = 0
        self.difficulty = "Medium"
        self.guess_history = []

        # GUI Widgets
        self.setup_widgets()
        self.start_new_game()

    def setup_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Title Label
        tk.Label(
            main_frame,
            text="NUMBER GUESSING GAME",
            bg=self.colors["bg"],
            fg="#00FF9D",  # Neon green
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Difficulty Selection
        tk.Label(
            main_frame,
            text="SELECT DIFFICULTY:",
            bg=self.colors["bg"],
            fg=self.colors["text_fg"],
            font=self.title_font
        ).pack(pady=5)

        self.difficulty_var = tk.StringVar(value="Medium")

        # Difficulty radio buttons with bright colors
        difficulties = [
            ("EASY (1-50, 10 attempts)", "Easy"),
            ("MEDIUM (1-100, 7 attempts)", "Medium"),
            ("HARD (1-200, 5 attempts)", "Hard")
        ]

        for text, level in difficulties:
            tk.Radiobutton(
                main_frame,
                text=text,
                variable=self.difficulty_var,
                value=level,
                command=self.set_difficulty,
                bg=self.colors["bg"],
                fg=self.colors[level],  # Neon color for text
                selectcolor=self.colors[level],
                activebackground=self.colors["bg"],
                font=self.bold_font,
                indicatoron=0,  # Button-style appearance
                width=25,
                relief="raised"
            ).pack(pady=5, padx=20)

        # Guess Entry
        tk.Label(
            main_frame,
            text="ENTER YOUR GUESS:",
            bg=self.colors["bg"],
            fg=self.colors["text_fg"],
            font=self.title_font
        ).pack(pady=5)

        self.guess_entry = tk.Entry(
            main_frame,
            bg=self.colors["entry_bg"],
            fg="#000000",  # Black text
            font=("Arial", 12, "bold"),
            relief="flat",
            highlightthickness=2,
            highlightbackground=self.colors["Medium"],
            highlightcolor=self.colors["Medium"]
        )
        self.guess_entry.pack(ipady=5)  # Taller entry field
        self.guess_entry.bind("<Return>", self.check_guess)

        # Submit Button (styled with bright purple)
        self.submit_button = tk.Button(
            main_frame,
            text="SUBMIT GUESS",
            command=self.check_guess,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            font=self.bold_font,
            relief="raised",
            bd=0,
            padx=20,
            pady=5
        )
        self.submit_button.pack(pady=10)

        # Game Status Labels
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text_fg"]
        )
        self.status_label.pack(pady=5)

        self.attempts_label = tk.Label(
            main_frame,
            text="",
            font=self.bold_font,
            bg=self.colors["bg"],
            fg=self.colors["text_fg"]
        )
        self.attempts_label.pack()

        # High Score Display
        self.high_score_label = tk.Label(
            main_frame,
            text="",
            font=self.bold_font,
            bg=self.colors["bg"],
            fg="#00D1FF"  # Neon blue
        )
        self.high_score_label.pack(pady=10)
        self.update_high_score_label()

        # Guess History
        tk.Label(
            main_frame,
            text="GUESS HISTORY:",
            bg=self.colors["bg"],
            fg=self.colors["text_fg"],
            font=self.title_font
        ).pack(pady=5)

        self.history_listbox = tk.Listbox(
            main_frame,
            height=8,
            width=35,
            font=("Courier", 10, "bold"),
            bg=self.colors["history_odd"],
            fg="#FFFFFF",  # White text
            selectbackground="#FF2D75",  # Neon pink for selection
            relief="flat",
            highlightthickness=0
        )
        self.history_listbox.pack(pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            main_frame,
            orient="vertical",
            command=self.history_listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # Play Again Button
        self.play_again_button = tk.Button(
            main_frame,
            text="🔄 PLAY AGAIN",
            command=self.start_new_game,
            bg="#FF2D75",  # Neon pink
            fg="#FFFFFF",
            font=self.bold_font,
            state=tk.DISABLED,
            relief="raised",
            padx=20
        )
        self.play_again_button.pack(pady=10)

    def set_difficulty(self):
        difficulty = self.difficulty_var.get()
        self.difficulty = difficulty
        self.start_new_game()

    def start_new_game(self):
        # Set range based on difficulty
        if self.difficulty == "Easy":
            self.min_num, self.max_num, self.max_attempts = 1, 50, 10
        elif self.difficulty == "Medium":
            self.min_num, self.max_num, self.max_attempts = 1, 100, 7
        elif self.difficulty == "Hard":
            self.min_num, self.max_num, self.max_attempts = 1, 200, 5

        self.secret_number = random.randint(self.min_num, self.max_num)
        self.attempts = 0
        self.guess_history = []
        self.history_listbox.delete(0, tk.END)

        self.status_label.config(
            text=f"Guess a number between {self.min_num} and {self.max_num}!",
            fg=self.colors["text_fg"]
        )
        self.attempts_label.config(text=f"Attempts left: {self.max_attempts}")

        self.guess_entry.config(state=tk.NORMAL)
        self.play_again_button.config(state=tk.DISABLED)
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus()

    def check_guess(self, event=None):
        try:
            guess = int(self.guess_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
            return

        self.attempts += 1
        attempts_left = self.max_attempts - self.attempts

        # Determine hint and color
        if guess < self.secret_number:
            hint = "Too low! ⬆"
            hint_color = self.colors["hint"]
        elif guess > self.secret_number:
            hint = "Too high! ⬇"
            hint_color = self.colors["hint"]
        else:
            hint = "🎉 Correct! You win!"
            hint_color = self.colors["correct"]

        self.guess_history.append((guess, hint))
        self.update_history_listbox()

        # Update status label with color
        self.status_label.config(text=hint, fg=hint_color)

        if guess == self.secret_number:
            self.update_high_scores()
            self.guess_entry.config(state=tk.DISABLED)
            self.play_again_button.config(state=tk.NORMAL)
        else:
            self.attempts_label.config(text=f"Attempts left: {attempts_left}")
            if attempts_left <= 0:
                self.status_label.config(
                    text=f"Game Over! The number was {self.secret_number}.",
                    fg=self.colors["error"]
                )
                self.guess_entry.config(state=tk.DISABLED)
                self.play_again_button.config(state=tk.NORMAL)

        self.guess_entry.delete(0, tk.END)

    def update_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        for idx, (guess, hint) in enumerate(self.guess_history):
            self.history_listbox.insert(tk.END, f"{guess} → {hint}")
            # Alternate row colors
            if idx % 2 == 0:
                self.history_listbox.itemconfig(idx, bg=self.colors["history_even"])
            else:
                self.history_listbox.itemconfig(idx, bg=self.colors["history_odd"])

    def update_high_scores(self):
        current_score = self.attempts
        difficulty = self.difficulty

        if (
            self.high_scores[difficulty] == "N/A" or
            current_score < int(self.high_scores[difficulty])
        ):
            self.high_scores[difficulty] = str(current_score)
            with open(self.high_scores_file, "w") as f:
                json.dump(self.high_scores, f)
            messagebox.showinfo(
                "New High Score!",
                f"🏆 New record for {difficulty}: {current_score} attempts!"
            )

        self.update_high_score_label()

    def update_high_score_label(self):
        text = "🏆 HIGH SCORES 🏆\n"
        for level, score in self.high_scores.items():
            text += f"{level}: {score}\n"
        self.high_score_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()