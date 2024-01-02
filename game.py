import copy
from queue import SimpleQueue
import tkinter as tk
from tkinter import messagebox
from stack import Stack
import math

class Figure:
    def __init__(self, color):
        self.color = color
        
def find_fastest_paths(state, start_position):
    start_row, start_col = start_position

    size=len(state)
    visited = [[False] * size for _ in range(size)]
    queue = SimpleQueue()
    queue.put((start_row, start_col, 0, []))  # Include distance and path in the queue
    visited[start_row - 1][start_col - 1] = True  # Mark the starting position as visited

    shortest_paths = []

    while not queue.empty():
        current_row, current_col, distance, path = queue.get()

        for row_offset, col_offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            next_row, next_col = current_row + row_offset, current_col + col_offset
            if 1 <= next_row <= size and 1 <= next_col <= size and not visited[next_row - 1][next_col - 1]:
                new_path = path + [(next_row, next_col)]
                if state[next_row - 1][next_col - 1].size > 0:
                    shortest_paths.append((next_row, next_col, distance + 1, new_path))  # Found a non-empty square and its distance and path
                else:
                    visited[next_row - 1][next_col - 1] = True
                    queue.put((next_row, next_col, distance + 1, new_path))
                    
    # Filter out paths with greater distances
    min_distance = float('inf')
    result_paths = []
    for path_info in shortest_paths:
        if path_info[2] < min_distance:
            min_distance = path_info[2]
            result_paths = [path_info[3]]
        elif path_info[2] == min_distance:
            result_paths.append(path_info[3])

    return result_paths
        
def is_valid_move(state, current_position, destination):
    stack_at_current=state[current_position[0]][current_position[1]]
    stack_at_dest=state[destination[0]][destination[1]]
    
    if stack_at_current.size>=8:
        return 0
    elif stack_at_dest.size <= current_position[2]:
        return 0
    elif stack_at_dest.size+stack_at_current.size-current_position[2] > 8:
        return 0
    
    return 1

def available_moves(state, color):
    available_moves=[]
        
    for i in range(7):
        for j in range(7):
            stack_at_ij=state[i][j]
            if stack_at_ij.size > 0:
                figures=stack_at_ij.get_all_figures()
                for idx,figure in enumerate(figures):
                    if figure.color=='W' if color=="White" else 'B':
                        current_position=(i,j,idx) 
                        
                        valid_positions = [
                            (current_position[0] - 1, current_position[1] - 1),  # upper left
                            (current_position[0] - 1, current_position[1] + 1),  # upper right
                            (current_position[0] + 1, current_position[1] - 1),  # lower left
                            (current_position[0] + 1, current_position[1] + 1),  # lower right
                        ]
                        for valid_position in valid_positions:
                            if(valid_position[0]==-1 or valid_position[0]==8 or valid_position[1]==-1 or valid_position[1]==8):
                                valid_positions.remove(valid_position)
                        if (state[row - 1][col - 1].size == 0 or state[row - 1][col - 1].size == 8 for row, col in valid_positions):
                            paths = find_fastest_paths(state, (current_position[0], current_position[1]))
                            for row,col in valid_positions:
                                for path in paths:
                                    if ((row,col) in path):
                                        if is_valid_move(state, current_position, (row,col)):
                                            available_moves.append((current_position,(row,col)))
                        else:
                            for valid_position in valid_positions:
                                if(state[valid_position[0]][valid_position[1]].size!=0):
                                    if is_valid_move(state, current_position, valid_position):
                                        available_moves.append((current_position, valid_position))
    
    return available_moves

def oceni(stanje):
    ocena=0
    for i in range(7):
        for j in range(7):
            if stanje[i][j].last!=None:
                if stanje[i][j].last.figure.color=='B':
                    ocena+=1
                else:
                    ocena-=1
    return ocena

def kraj(stanje):
    winner=0
    for i in range(7):
        for j in range(7):
            if stanje[i][j].size==8:
                if stanje[i][j].last.figure.color=='W':
                    winner-=1
                else:
                    winner+=1
    return winner

def igraj(potez, stanje):
    if is_valid_move(stanje, potez[0], potez[1]):
        stanje[potez[0][0]][potez[0][1]].move_figure_to(potez[0][2],stanje[potez[1][0]][potez[1][1]])
    return stanje

def max_stanje(lsv):
    return max(lsv, key=lambda x: x[1])

def min_stanje(lsv):
    return min(lsv, key=lambda x: x[1])

def minimax(stanje, dubina, moj_potez, boja):
    lista_stanja=[]
    kopijastanja = copy.deepcopy(stanje)
    for potez in available_moves(stanje, boja):
        lista_stanja.append(igraj(potez, kopijastanja))
        kopijastanja = copy.deepcopy(stanje)
    min_max_stanje = max_stanje if boja=='Black' else min_stanje
    if dubina == 0 or lista_stanja is None:
        return(stanje, oceni(stanje))
    return min_max_stanje([minimax(x, dubina - 1, not moj_potez, 'White'if boja =='Black' else 'Black') for x in lista_stanja])

class Chessboard(tk.Tk):
    def __init__(self, size, first_player):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        board_size = min(screen_width, screen_height) - 100 
        canvas_size = board_size - 50 

        self.state('zoomed')
        self.points=0
        self.size = size
        self.nbStacksOut=0
        self.title("Byte M2S")
        self.geometry(f"{board_size}x{board_size + 100}")

        self.stacks = [[Stack() for _ in range(size)] for _ in range(size)]  # 2D array of Stack objects
        self.current_player = first_player  # 'human' or 'computer'
        self.computer_color="White" if first_player=='computer' else "Black"
        self.game_started = False

        # Canvas on the left side
        self.canvas = tk.Canvas(self, width=canvas_size, height=canvas_size, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=4, sticky="nsew")

        # FIGURE
        self.black_image = tk.PhotoImage(file="resources/FIGURE_BLACK.png").subsample(math.floor(size/2))
        self.white_image = tk.PhotoImage(file="resources/FIGURE_WHITE.png").subsample(math.floor(size/2))

        entry_width = 1
        self.move_label = tk.Label(self, text="", width=entry_width, height=0)
        self.move_label.grid(row=7, column=0, columnspan=2, sticky="nsew")


        self.current_position_label = tk.Label(self, text="Selected field, stack position and move direction",
                                               width=entry_width, height=0)
        self.current_position_label.grid(row=0, column=1, sticky="nsew")

        self.current_position_entry = tk.Entry(self, width=entry_width)
        self.current_position_entry.grid(row=1, column=1, sticky="nsew")

        self.new_height_entry = tk.Entry(self, width=entry_width)
        self.new_height_entry.grid(row=2, column=1, sticky="nsew")

        self.new_position_entry = tk.Entry(self, width=entry_width)
        self.new_position_entry.grid(row=3, column=1, sticky="nsew")

        # Button to save the new position
        button_width = 2
        button_height = 2

        self.save_button = tk.Button(self, text="Move", command=self.on_button_click, width=button_width,height=button_height)
        self.save_button.grid(row=6, column=1, sticky="nsew")

        self.create_chessboard()
        self.initial_position()
        self.create_controls()

        # Configure grid row and column weights so that they expand proportionally
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            
        if(self.current_player == "computer"):
            self.computer_move()
        
    def computer_move(self):
        self.stacks=copy.deepcopy(minimax(self.stacks, 1, True, self.computer_color)[0])
        self.draw_all_figures()
    
    
    def proizvoljno_stanje(self, state):
        self.stacks=copy.deepcopy(state)
        self.draw_all_figures()
   
    def create_chessboard(self):
        square_size = self.canvas.winfo_reqwidth() // self.size

        for i in range(self.size):
            for j in range(self.size):
                color = "grey" if (i + j) % 2 == 0 else "white"
                square_id = self.canvas.create_rectangle(
                    j * square_size, i * square_size, (j + 1) * square_size, (i + 1) * square_size, fill=color,
                    tags="square"
                )

    def initial_position(self):
        for i in range(2, self.size):
            for j in range(1, self.size + 1):
                if i % 2 == 0 and j % 2 == 0:
                    self.place_figure(i, j, 'B') 
                elif i % 2 != 0 and j % 2 != 0:
                    self.place_figure(i, j, 'W') 
        self.move_label.config(text=f"{self.current_player} to move")
        self.make_symetrical()
        self.draw_all_figures()
        self.game_started = True  
    
    def make_symetrical(self):
        if(self.size==12):
            self.stacks[1][self.size-1].clear()
            self.stacks[1][1].clear()
            self.stacks[self.size-2][self.size-2].clear()
            self.stacks[self.size-2][0].clear()
        elif(self.size==14):
            for i in range(6):
                self.stacks[i*2+2][0].clear()
                self.stacks[i*2+1][self.size-1].clear()


    def place_figure(self, row, column, color):
        stack_at_ij = self.stacks[row - 1][column - 1]
        stack_at_ij.add_figure(Figure(color))
        

    def toggle_player(self):
        self.current_player = 'computer' if self.current_player == 'human' else 'human'
        self.move_label.config(text=f"{self.current_player} to move")
        if(self.current_player == "computer"):
            self.computer_move()
            self.toggle_player()

    def on_figure_click(self, position, position_in_stack):
        row, col = position
        stack_at_ij = self.stacks[row - 1][col - 1]
        figures = stack_at_ij.get_all_figures()

        if figures and ((figures[position_in_stack].color == 'W' and self.current_player == 'human') or (
                figures[position_in_stack].color == 'B' and self.current_player == 'computer')):
            self.selected_position = position
            self.selected_stack_position = position_in_stack
            self.current_position_entry.config(state='normal')
            self.current_position_entry.delete(0, tk.END)
            self.current_position_entry.insert(0, f"{row},{col}")
            self.current_position_entry.config(state='readonly')
            self.new_position_entry.delete(0, tk.END)

            self.new_height_entry.config(state='normal')
            self.new_height_entry.delete(0, tk.END)
            self.new_height_entry.insert(0, f"{position_in_stack}")
            self.new_height_entry.config(state='readonly')

        
    def save_new_position(self, position):
        dest_row, dest_col = position
        
        # Check if the move is diagonal and adjacent
        current_row, current_col = self.selected_position
        stack_at_current = self.stacks[current_row - 1][current_col - 1]
        selected_figure_position = self.selected_stack_position
        print(self.selected_stack_position)
        valid_positions = [
            (current_row - 1, current_col - 1),  # upper left
            (current_row - 1, current_col + 1),  # upper right
            (current_row + 1, current_col - 1),  # lower left
            (current_row + 1, current_col + 1),  # lower right
        ]
        
        if (dest_row, dest_col) in valid_positions:
            # Check if the destination square is already occupied
            stack_at_dest = self.stacks[dest_row - 1][dest_col - 1]
            if stack_at_current.size>=8:
                print("The source stack is full and is out of play.")
            elif 1>stack_at_dest.size:
                #print("Invalid move. The destination square must be occupied by at least 1 figure")
                if (self.stacks[row - 1][col - 1].size == 0 for row, col in valid_positions):
                    paths = find_fastest_paths(self.stacks, (current_row, current_col))
                    print("Path: ",paths)
                    if any((dest_row, dest_col) in path for path in paths):
                        self.new_position_entry.delete(0, tk.END)
                        self.new_position_entry.insert(0, f"{dest_row},{dest_col}")
                        self.move_figure(self.selected_stack_position, (dest_row, dest_col))
                    else:
                        print("Figure must move towards the closest stack.")
            elif stack_at_dest.size <= selected_figure_position:
                print("Invalid move. Cant move figure from higher to lower position!!!")
            elif stack_at_dest.size+stack_at_current.size-(int(self.new_height_entry.get())) > 8:
                figuresCnt=stack_at_current.size-int(self.new_height_entry.get())
                emptySp=8-stack_at_dest.size
                print("Invalid move. Trying to put ",figuresCnt," move but destination ",(dest_row, dest_col)," only has ",emptySp ," empty spaces.")
            else:
                # Update the new position entry
                self.new_position_entry.delete(0, tk.END)
                self.new_position_entry.insert(0, f"{dest_row},{dest_col}")
                self.move_figure(self.selected_stack_position, (dest_row, dest_col))
        else:
            print("Invalid move. The figure can only move to a diagonal and adjacent square.")

    def on_button_click(self):
        new_position_str = self.new_position_entry.get().lower()
        direction_mapping = {'gl': (-1, -1), 'gd': (-1, 1), 'dl': (1, -1), 'dd': (1, 1)}

        if new_position_str in direction_mapping:
            direction = direction_mapping[new_position_str]
            print("selected positoin ",self.selected_position)
            current_row, current_col = self.selected_position
            dest_row, dest_col = current_row + direction[0], current_col + direction[1]

            if 1 <= dest_row <= self.size and 1 <= dest_col <= self.size:
                self.save_new_position((dest_row, dest_col))
            else:
                print("Invalid move. The figure can only move to a valid square.")
        else:
            try:
                dest_row, dest_col = map(int, new_position_str.split(","))
                self.save_new_position((dest_row, dest_col))
            except ValueError:
                print(
                    "Invalid input. Please enter either 'gl', 'gd', 'dl', 'dd' or coordinates in the format 'row,column'.")

    def move_figure(self, selected_stack_position, destination):
        dest_row, dest_col = destination

        current_row, current_col = self.selected_position
        stack_at_current = self.stacks[current_row - 1][current_col - 1]
        fig= stack_at_current.get_figure(selected_stack_position)
        # Check if the selected figure matches the current player's color
        if (fig.color == 'W' and self.current_player == 'human') or (
                fig.color == 'B' and self.current_player == 'computer'):

            # Remove the figure from the current position

            # Add the figure to the new position
            stack_at_destination = self.stacks[dest_row - 1][dest_col - 1]
            
            stack_at_current.move_figure_to(selected_stack_position,stack_at_destination)

            # Draw all figures whenever the stack changes
            self.draw_all_figures()

            # Clear the selected figure and position
            self.selected_position = None
            self.selected_figures = None

            self.current_position_entry.delete(0, tk.END)
            self.new_height_entry.delete(0, tk.END)
            self.new_position_entry.delete(0, tk.END)

            stack_at_destination.update_stack()
            stack_at_current.update_stack()
            nodeTmp=stack_at_current.first
            print("Previous stack:", " size ", stack_at_current.size)
            while nodeTmp:
                print(nodeTmp.position_in_stack,nodeTmp.figure.color)
                nodeTmp=nodeTmp.next
            nodeTmp=stack_at_destination.first
            print("Current stack:", " size ", stack_at_destination.size)
            while nodeTmp:
                print(nodeTmp.position_in_stack,nodeTmp.figure.color)
                nodeTmp=nodeTmp.next
            if(stack_at_destination.size==8):
                self.end_game(stack_at_destination)
            self.toggle_player()

    def end_game(self,stack):
        if(stack.last.figure.color=='W'):
            self.points+=1
            self.nbStacksOut+=1
            print("Points ",self.points)
        elif(stack.last.figure.color=='B'):
            self.points-=1
            self.nbStacksOut+=1
            print("Points ",self.points)
        else:
            print("Error color is not black or white")
        
        #self.draw_all_figures()
        minus_one_for_14=0
        if(self.size==14):
            minus_one_for_14=1
        if self.points>=math.floor(self.size/2*(self.size-2)/16+1)-minus_one_for_14:
            self.print_winner('W')
        if self.points<=-(math.floor(self.size/2*(self.size-2)/16+1))+minus_one_for_14:
            self.print_winner('B')
        if self.nbStacksOut==math.floor(self.size/2*(self.size-2)/8)-minus_one_for_14:
            if(self.points>0):
                self.print_winner('W')
            if(self.points<0):
                self.print_winner('B')

    def print_winner(self,winner):
        if(winner=='W'):
            print("White won!")
        if(winner=='B'):
            print("Black won!")

    def draw_all_figures(self):
        self.canvas.delete("figure") 

        for i in range(self.size):
            for j in range(self.size):
                stack_at_ij = self.stacks[i][j]
                figures = stack_at_ij.get_all_figures()
                if figures:
                    for position_in_stack, figure in enumerate(figures):
                        shift=0
                        if(self.size==14 or self.size==10):
                            shift = 10/self.size
                        x = j * self.canvas.winfo_reqwidth() / self.size + self.canvas.winfo_reqwidth() / (2 * self.size) - j*shift
                        y = i * self.canvas.winfo_reqheight() / self.size + self.canvas.winfo_reqheight() / (2 * self.size) - position_in_stack * 10 - i*shift 
                        
                        figure_image = self.black_image if figure.color == 'B' else self.white_image
                        figure_id = self.canvas.create_image(x, y, image=figure_image, tags="figure")
                        figure.figure_id = figure_id

                        self.canvas.tag_bind(
                            figure_id,
                            "<Button-1>",
                            lambda event, pos=(i + 1, j + 1), pos_in_stack=position_in_stack: self.on_figure_click(pos, pos_in_stack))

    def create_controls(self):
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                self.canvas.create_rectangle(
                    (j - 1) * (self.canvas.winfo_reqwidth() // self.size),
                    (i - 1) * (self.canvas.winfo_reqheight() // self.size),
                    j * (self.canvas.winfo_reqwidth() // self.size),
                    i * (self.canvas.winfo_reqheight() // self.size),
                    outline="black", tags="square"
                )
        restart_button = tk.Button(self, text="Restart Game", command=self.restart_game, width=2,height=2)
        restart_button.grid(row=8, column=1, sticky="nsew")
        
    def restart_game(self):
        # Reset the game state
        self.stacks = [[Stack() for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = first_player
        self.game_started = False
        self.points = 0
        self.nbStacksOut = 0

        # Clear board
        self.canvas.delete("square")
        self.canvas.delete("figure")

        # Revert game to start
        self.create_chessboard()
        self.initial_position()
        self.create_controls()

        messagebox.showinfo("Game Restarted", "The game has been restarted.")


if __name__ == "__main__":
    while True:
        try:
            size = int(input("Enter an even number between 8 and 16 for the chessboard size: "))
            if 8 <= size <= 16 and size % 2 == 0:
                break
            else:
                print("Please enter a valid even number between 8 and 16.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    while True:
        player_input = input("Who plays first? Enter 'human' or 'computer': ").lower()
        if 'human'.startswith(player_input):
            first_player="human"
            break
        elif 'computer'.startswith(player_input):
            first_player='computer'
            break
        else:
            print("Invalid input. Please enter 'human' or 'computer'.")

    chessboard = Chessboard(size,first_player)
    # available_moves(chessboard.stacks,True)
    # print("Minmax: ")
    # x=minimax(chessboard.stacks,3,True)
    # print(x)
    chessboard.mainloop()

