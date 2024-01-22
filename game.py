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
    start_row += 1
    start_col += 1
    size=len(state)
    
    visited = [[False] * size for _ in range(size)]
    queue = SimpleQueue()
    queue.put((start_row, start_col, 0, []))  
    visited[start_row - 1][start_col - 1] = True  

    shortest_paths = []

    while not queue.empty():
        current_row, current_col, distance, path = queue.get()

        for row_offset, col_offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            next_row, next_col = current_row + row_offset, current_col + col_offset
            if 1 <= next_row <= size and 1 <= next_col <= size and not visited[next_row - 1][next_col - 1]:
                new_path = path + [(next_row-1, next_col-1)]
                if state[next_row - 1][next_col - 1].size > 0:
                    shortest_paths.append((next_row, next_col, distance + 1, new_path)) 
                else:
                    visited[next_row - 1][next_col - 1] = True
                    queue.put((next_row, next_col, distance + 1, new_path))

    min_distance = float('inf')
    result_paths = []
    for path_info in shortest_paths:
        if path_info[2] < min_distance:
            min_distance = path_info[2]
            result_paths = [path_info[3]]
        elif path_info[2] == min_distance:
            result_paths.append(path_info[3])

    return result_paths

        
def is_valid_move(state, current_position, destination, nffp):
    stack_at_current=state[current_position[0]][current_position[1]]
    stack_at_dest=state[destination[0]][destination[1]]
    
    if stack_at_current.size>=8:
        return 0
    elif stack_at_dest.size < current_position[2] and nffp:
        return 0
    elif stack_at_dest.size+stack_at_current.size-current_position[2] > 8:
        return 0
    
    return 1

def available_moves(state, color):
    size=len(state)
    available_moves=[]
        
    for i in range(size):
        for j in range(size):
            stack_at_ij=state[i][j]
            if stack_at_ij.size > 0:
                figures=stack_at_ij.get_all_figures()
                for idx,figure in enumerate(figures):
                    if figure.color==color:
                        current_position=(i,j,idx) 
                        
                        valid_positions = [
                            (current_position[0] - 1, current_position[1] - 1),  # upper left
                            (current_position[0] - 1, current_position[1] + 1),  # upper right
                            (current_position[0] + 1, current_position[1] - 1),  # lower left
                            (current_position[0] + 1, current_position[1] + 1),  # lower right
                        ]
                        for valid_position in valid_positions:
                            if(valid_position[0]<=-1 or valid_position[0]>=size or valid_position[1]<=-1 or valid_position[1]>=size):
                                valid_positions.remove(valid_position)
                        flag=True
                        for valid_position in valid_positions:
                            if state[valid_position[0]][valid_position[1]].size!=0:
                                flag=False
                        if flag:
                            paths = find_fastest_paths(state, (current_position[0], current_position[1]))
                            for valid_position in valid_positions:
                                
                                if(valid_position[0]!=size and valid_position[1]!=size):
                                    if any(valid_position in path for path in paths):    
                                        if is_valid_move(state, current_position, valid_position, False):
                                            available_moves.append((current_position,valid_position))
                        else:
                            for valid_position in valid_positions:
                                if is_valid_move(state, current_position, valid_position, True):
                                    available_moves.append((current_position, valid_position))
    
    return available_moves

def oceni(stanje, boja):
    size = len(stanje)
    ocena = 0

    for i in range(size):
        for j in range(size):
            stack_at_ij = stanje[i][j]
            if stack_at_ij.last is not None:
                last_figure = stack_at_ij.last.figure
                if stack_at_ij.size == 7:
                    opposite_color = 'White' if boja == 'Black' else 'Black'
                    valid_positions = [
                        (i - 1, j - 1),  # upper left
                        (i - 1, j + 1),  # upper right
                        (i + 1, j - 1),  # lower left
                        (i + 1, j + 1),  # lower right
                    ]
                    valid_positions = [(row, col) for row, col in valid_positions if 0 <= row < size and 0 <= col < size]

                    for row, col in valid_positions:
                        if stanje[row][col].last is not None and stanje[row][col].last.figure.color == boja:
                            ocena -= 15

                if stack_at_ij.size == 8:
                    if last_figure.color == boja:
                        ocena -= 20
                    else:
                        ocena += 20

                if last_figure.color == boja:
                    ocena -= 2
                else:
                    ocena += 2

    return ocena



def igraj(potez, stanje):
    stanje[potez[0][0]][potez[0][1]].move_figure_to(potez[0][2], stanje[potez[1][0]][potez[1][1]])
    return stanje 

def max_value_alpha(stanje, dubina, alpha, beta, boja):
    lista_stanja=[]
    kopijastanja = copy.deepcopy(stanje)
    lista_poteza=available_moves(stanje,boja)
    if dubina == 0 or lista_poteza is None:
        return (stanje, oceni(stanje, boja))
    else:
        for potez in lista_poteza:
            lista_stanja.append(igraj(potez, kopijastanja))
            kopijastanja = copy.deepcopy(stanje)

        for s in lista_stanja:
            result = min_value_alpha(s, dubina - 1, alpha, beta, 'White' if boja=='Black' else 'Black')
            if result[1] > alpha[1]:
                alpha = (result[0], result[1])
            if alpha[1] >= beta[1]:
                return beta
        return alpha

def min_value_alpha(stanje, dubina, alpha, beta, boja):
    lista_stanja=[]
    kopijastanja = copy.deepcopy(stanje)
    lista_poteza=available_moves(stanje,boja)
    if dubina == 0 or lista_poteza is None:
        return (stanje, oceni(stanje, boja))
    else:
        for potez in lista_poteza:
            lista_stanja.append(igraj(potez, kopijastanja))
            kopijastanja = copy.deepcopy(stanje)

        for s in lista_stanja:
            result = max_value_alpha(s, dubina - 1, alpha, beta, 'White' if boja=='Black' else 'Black')
            if result[1] < beta[1]:
                beta = (result[0], result[1])
            if beta[1] <= alpha[1]:
                return alpha
        return beta

def minimax_alpha_beta(stanje, dubina, moj_potez, alpha, beta, boja):
    alpha=(stanje,alpha)
    beta=(stanje,beta)
    if moj_potez:
        return max_value_alpha(stanje, dubina, alpha, beta, boja)[0]
    else:
        return min_value_alpha(stanje, dubina, alpha, beta, boja)[0]
    
class Chessboard(tk.Tk):
    def __init__(self, size, first_player):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        board_size = min(screen_width, screen_height) - 140 
        canvas_size = board_size - 50 

        self.state('zoomed')
        self.points=0
        self.size = size
        self.nbStacksOut=0
        self.title("Byte M2S")
        self.geometry(f"{board_size}x{board_size + 100}")

        self.stacks = [[Stack() for _ in range(size)] for _ in range(size)]
        self.first_player=first_player
        self.current_player = first_player
        self.current_player_color='White'
        self.computer_color="White" if first_player=='computer' else "Black"
        self.human_color="White" if first_player=='human' else "Black"
        self.game_started = False

        self.canvas = tk.Canvas(self, width=canvas_size, height=canvas_size, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=4, sticky="nsew")

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

        button_width = 2
        button_height = 2

        self.save_button = tk.Button(self, text="Move", command=self.on_button_click, width=button_width,height=button_height)
        self.save_button.grid(row=6, column=1, sticky="nsew")

        self.create_chessboard()
        self.initial_position()
        self.create_controls()

        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            
        if(self.current_player == "computer"):
            self.computer_move()
        
    def computer_move(self):
        self.stacks=copy.deepcopy(minimax_alpha_beta(self.stacks,1,True,-9999,9999, self.computer_color))
        for i in range(self.size):
            for j in range(self.size):
                if(self.stacks[i][j].size==8):
                    self.end_game(self.stacks[i][j])
                    break
        self.toggle_player()
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
                    self.place_figure(i, j, 'Black') 
                elif i % 2 != 0 and j % 2 != 0:
                    self.place_figure(i, j, 'White') 
        
        self.move_label.config(text=f"{self.current_player_color} to move")
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
        self.current_player_color= 'Black' if self.current_player_color=='White' else 'White'
        self.move_label.config(text=f"{self.current_player_color} to move")

        if(self.current_player == "computer"):
            self.computer_move()

    def on_figure_click(self, position, position_in_stack):
        row, col = position
        stack_at_ij = self.stacks[row - 1][col - 1]
        figures = stack_at_ij.get_all_figures()

        if figures and (self.current_player == 'human' and self.human_color==self.current_player_color and figures[position_in_stack].color == self.current_player_color):
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
        potezi=available_moves(self.stacks, self.human_color)

        if len(potezi)==0:
            self.toggle_player()
        elif(((self.selected_position[0]-1,self.selected_position[1]-1,self.selected_stack_position),(dest_row-1,dest_col-1)) in potezi):
            self.move_figure(self.selected_stack_position, (dest_row, dest_col))
        else:
            print("Invalid move.")

    def on_button_click(self):
        new_position_str = self.new_position_entry.get().lower()
        direction_mapping = {'gl': (-1, -1), 'gd': (-1, 1), 'dl': (1, -1), 'dd': (1, 1)}

        if new_position_str in direction_mapping:
            direction = direction_mapping[new_position_str]
            current_row, current_col = self.selected_position
            dest_row, dest_col = current_row + direction[0], current_col + direction[1]

            if 1 <= dest_row <= self.size and 1 <= dest_col <= self.size:
                self.save_new_position((dest_row, dest_col))
            else:
                print("Invalid move. The figure can only move to a valid square.")
        else:
            try:
                dest_row, dest_col = map(int, new_position_str.split(","))
                print("Point 1")
                self.save_new_position((dest_row, dest_col))
            except ValueError:
                print(
                    "Invalid input. Please enter either 'gl', 'gd', 'dl', 'dd' or coordinates in the format 'row,column'.")

    def move_figure(self, selected_stack_position, destination):
        dest_row, dest_col = destination

        current_row, current_col = self.selected_position
        stack_at_current = self.stacks[current_row - 1][current_col - 1]
        fig= stack_at_current.get_figure(selected_stack_position)
        
        if (fig.color == self.current_player_color and self.current_player == 'human'):
            stack_at_destination = self.stacks[dest_row - 1][dest_col - 1]
            
            stack_at_current.move_figure_to(selected_stack_position,stack_at_destination)

            self.draw_all_figures()

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
        if(stack.last.figure.color=='White'):
            self.points+=1
            self.nbStacksOut+=1
            print("Points ",self.points)
        elif(stack.last.figure.color=='Black'):
            self.points-=1
            self.nbStacksOut+=1
            print("Points ",self.points)
        else:
            print("Error color is not black or white")
        stack.first=None
        stack.update_stack()
        self.draw_all_figures()
        minus_one_for_14=0
        if(self.size==14):
            minus_one_for_14=1
        if self.points>=math.floor(self.size/2*(self.size-2)/16+1)-minus_one_for_14:
            self.print_winner('White')
        if self.points<=-(math.floor(self.size/2*(self.size-2)/16+1))+minus_one_for_14:
            self.print_winner('Black')
        if self.nbStacksOut==math.floor(self.size/2*(self.size-2)/8)-minus_one_for_14:
            if(self.points>0):
                self.print_winner('White')
            if(self.points<0):
                self.print_winner('Black')

    def print_winner(self, winner):
        if winner == 'White':
            messagebox.showinfo("Game Over", "White won!")
        elif winner == 'Black':
            messagebox.showinfo("Game Over", "Black won!")

        self.destroy()

    def draw_all_figures(self):
        self.canvas.delete("figure") 
        for i in range(self.size):
            for j in range(self.size):
                stack_at_ij = self.stacks[i][j]
                figures = stack_at_ij.get_all_figures()
                if figures:
                    for position_in_stack, figure in enumerate(figures):
                        x = (j + 0.5)*(self.canvas.winfo_reqheight() // self.size)
                        y = (i + 0.5)*(self.canvas.winfo_reqheight() // self.size)- position_in_stack * 10
                        figure_image = self.black_image if figure.color == 'Black' else self.white_image
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
        self.stacks = [[Stack() for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = self.first_player
        self.current_player_color='White'
        self.move_label.config(text=f"White to move")
        self.game_started = False
        self.points = 0
        self.nbStacksOut = 0

        self.canvas.delete("square")
        self.canvas.delete("figure")

        self.create_chessboard()
        self.initial_position()
        self.create_controls()

        messagebox.showinfo("Game Restarted", "The game has been restarted.")
        
        if(self.current_player == "computer"):
            self.computer_move()


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

    chessboard = Chessboard(size, first_player)
    
    chessboard.mainloop()