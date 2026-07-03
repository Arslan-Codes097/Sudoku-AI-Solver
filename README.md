# 🧠 Sudoku AI Solver

An intelligent Sudoku solver and visualizer built in Python. This project frames Sudoku as a Constraint Satisfaction Problem (CSP) and implements various foundational Artificial Intelligence search algorithms to solve puzzles of varying difficulties efficiently. 

It features a modern Graphical User Interface (GUI) and a built-in performance evaluator to benchmark the speed and step counts of different algorithms.

## ✨ Features

- **Play or Watch**: Manually solve Sudoku puzzles or watch the AI solve them in real-time.
- **Multiple AI Algorithms**: Compare different search strategies on the same puzzle.
- **Modern GUI**: A sleek, interactive interface built with `CustomTkinter`.
- **Performance Evaluation**: Generates comparative graphs using `Matplotlib` to visualize how each algorithm performs based on time and computational steps.
- **Puzzle Generation**: Generates valid Sudoku puzzles for testing.

## 🤖 Algorithms Implemented

This project implements the following Constraint Satisfaction Problem (CSP) algorithms from scratch:

1. **Backtracking Search**: A naive depth-first search approach that tries all possibilities.
2. **Forward Checking**: An optimization over backtracking that keeps track of remaining legal values for unassigned variables to catch failures early.
3. **AC-3 with MRV (Minimum Remaining Values)**: Uses Arc Consistency to reduce the search space and the MRV heuristic to always choose the variable with the fewest legal options next, significantly improving performance.
4. **Local Search**: An iterative approach that starts with a complete (but flawed) assignment and makes local modifications to reduce the number of constraint violations.

## 🛠️ Technologies Used

- **Python 3**
- **CustomTkinter**: For building the modern graphical interface.
- **Matplotlib**: For plotting algorithm performance comparisons.

## 🚀 How to Run

1. **Clone the repository** (or download the source code):
   ```bash
   git clone https://github.com/YOUR_USERNAME/Sudoku-AI-Solver.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd Sudoku-AI-Solver/AI(main)/AI(main)
   ```
3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the game**:
   ```bash
   python Game.py
   ```

