import sys
from tkinter import Frame, Label, CENTER
import random
import logic
import constants as c


import pickle
from env_2048 import encode_state 

# Load Q table
try:
    with open("q_table.pkl", "rb") as f:
        Q = pickle.load(f)
    print("Loaded Q table with", len(Q), "states")
except:
    print("Warning: Q table not found")
    Q = {}

def agent_best_action(matrix):
    state = encode_state(matrix)

    if state not in Q:
        # Unseen state, fallback to any move
        return random.choice([0, 1, 2, 3])

    q_vals = Q[state]
    max_q = max(q_vals)
    best_actions = [a for a, q in enumerate(q_vals) if q == max_q]
    return random.choice(best_actions)

def gen():
    return random.randint(0, c.GRID_LEN - 1)

class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_down)

        self.commands = {
            c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right,
            c.KEY_UP_ALT1: logic.up,
            c.KEY_DOWN_ALT1: logic.down,
            c.KEY_LEFT_ALT1: logic.left,
            c.KEY_RIGHT_ALT1: logic.right,
            c.KEY_UP_ALT2: logic.up,
            c.KEY_DOWN_ALT2: logic.down,
            c.KEY_LEFT_ALT2: logic.left,
            c.KEY_RIGHT_ALT2: logic.right,
        }

        self.grid_cells = []
        self.init_grid()
        self.matrix = logic.new_game(c.GRID_LEN)
        self.history_matrixs = []
        self.update_grid_cells()
        if AUTO_AGENT:
            # start agent autoplay as soon as the GUI loads
            self.after(200, self.agent_autoplay)


        self.mainloop()

    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME,width=c.SIZE, height=c.SIZE)
        background.grid()

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(
                    background,
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    width=c.SIZE / c.GRID_LEN,
                    height=c.SIZE / c.GRID_LEN
                )
                cell.grid(
                    row=i,
                    column=j,
                    padx=c.GRID_PADDING,
                    pady=c.GRID_PADDING
                )
                t = Label(
                    master=cell,
                    text="",
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    justify=CENTER,
                    font=c.FONT,
                    width=5,
                    height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="",bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number]
                    )
        self.update_idletasks()

    def _handle_post_move(self):
        """Common logic after a successful move."""
        self.matrix = logic.add_two(self.matrix)
        self.history_matrixs.append(self.matrix)
        self.update_grid_cells()

        state = logic.game_state(self.matrix)
        if state == "win":
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
        elif state == "lose":
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)

    def agent_autoplay(self):
        if logic.game_state(self.matrix) in ("win", "lose"):
            return

        # pick best action
        action = agent_best_action(self.matrix)
        move_map = {
            0: logic.up,
            1: logic.down,
            2: logic.left,
            3: logic.right
        }
        move_fn = move_map[action]

        new_matrix, done, _ = move_fn(self.matrix)

        if done:
            self.matrix = new_matrix
            self._handle_post_move()

        # if not done, the move was invalid; just try again immediately
        self.after(50, self.agent_autoplay)



    def key_down(self, event):
        key = event.keysym
        print(event)
        if key == c.KEY_QUIT: exit()
        if key == c.KEY_BACK and len(self.history_matrixs) > 1:
            self.matrix = self.history_matrixs.pop()
            self.update_grid_cells()
            print('back on step total step:', len(self.history_matrixs))
            return

        # Single step agent move with "a"
        if key == "a":
            action = agent_best_action(self.matrix)
            move_map = {
                0: logic.up,
                1: logic.down,
                2: logic.left,
                3: logic.right
            }
            move_fn = move_map[action]

            self.matrix, done, _ = move_fn(self.matrix)
            if done:
                self._handle_post_move()
            return

       
        # Human arrow key or alternate mapping
        if key in self.commands:
            self.matrix, done, _ = self.commands[key](self.matrix)

            if done:
                self._handle_post_move()

    def generate_next(self):
        index = (gen(), gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (gen(), gen())
        self.matrix[index[0]][index[1]] = 2

AUTO_AGENT = False
if len(sys.argv) > 1 and sys.argv[1] == "agent":
    AUTO_AGENT = True
    print("Running in agent autoplay mode")

game_grid = GameGrid()