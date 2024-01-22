class Node:
    def __init__(self, figure, next=None, position_in_stack=0):
        self.figure = figure
        self.next = next
        self.position_in_stack = position_in_stack

class Stack:
    def __init__(self):
        self.first = None
        self.last = None
        self.size = 0
        self.max_size = 8

    def add_figure(self, figure):
        if self.size < self.max_size:
            new_node = Node(figure, position_in_stack=self.size)
            if not self.first:
                self.first = new_node
                self.last = new_node
            else:
                self.last.next = new_node
                self.last = new_node
            self.size += 1
        else:
            print("Stack is full. Cannot add more figures.")
            
    def move_figure_to(self, position, other_stack):
        if 0 <= position < self.size:
            current_node = self.first
            prev_node = None
            for _ in range(position):
                prev_node = current_node
                current_node = current_node.next
            if(other_stack.size==0):
                other_stack.first=current_node
                other_stack.last=self.last
            else:
                other_stack.last.next = current_node
                other_stack.last=self.last
            if position > 0:
                prev_node.next = None
            else:
                self.first = None
            self.update_stack()
            other_stack.update_stack()
        else:
            print("Invalid position. Cannot move a figure.")
    
    def display_stack(self):
        current_node = self.first
        print("\n Stack:")
        figures = []
        while current_node:
            figures.append(current_node.figure)
            current_node = current_node.next
        figures.reverse()
        for figure in figures:
            print(figure.color)

    def get_all_figures(self):
        current_node = self.first
        figures = []
        while current_node:
            figures.append(current_node.figure)
            current_node = current_node.next
        return figures

    def find_figure(self, target_figure):
        current_node = self.first
        position = 0
        while current_node:
            if current_node.figure == target_figure:
                return position
            current_node = current_node.next
            position += 1
        return None  # Return None if the figure is not found

    def get_figure(self, position):
        if 0 <= position < self.size:
            current_node = self.first
            for _ in range(position):
                current_node = current_node.next
            return current_node.figure
        else:
            print("Invalid position. Cannot get a figure.")
            return None
        
    def clear(self):
        self.first=None
        self.last=None
        self.size=0

    def update_stack(self):
        current_node = self.first
        position = 0
        self.size=0
        prev=current_node
        while current_node:
            prev=current_node
            current_node.position_in_stack = position
            current_node = current_node.next
            position += 1
            self.size += 1
        self.last=prev