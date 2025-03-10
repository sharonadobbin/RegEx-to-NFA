import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import graphviz

# Define State and NFA classes
class State:
    def __init__(self):
        self.transitions = {}
        self.is_accept = False

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

# Functions to build NFA components
def create_basic_nfa(char):
    start = State()
    accept = State()
    start.transitions[char] = [accept]
    return NFA(start, accept)

def apply_concatenation(nfa1, nfa2):
    nfa1.accept.transitions['ε'] = [nfa2.start]
    return NFA(nfa1.start, nfa2.accept)

def apply_union(nfa1, nfa2):
    start = State()
    accept = State()
    start.transitions['ε'] = [nfa1.start, nfa2.start]
    nfa1.accept.transitions['ε'] = [accept]
    nfa2.accept.transitions['ε'] = [accept]
    return NFA(start, accept)

def apply_kleene_star(nfa):
    start = State()
    accept = State()
    start.transitions['ε'] = [nfa.start, accept]
    nfa.accept.transitions['ε'] = [nfa.start, accept]
    return NFA(start, accept)

def regex_to_postfix(regex):
    precedence = {'*': 3, '.': 2, '|': 1}
    output = []
    operators = []
    chars = set("abcdefghijklmnopqrstuvwxyz0123456789")

    new_regex = []
    for i, char in enumerate(regex):
        new_regex.append(char)
        if i + 1 < len(regex) and (
            char in chars or char == ')' or char == '*') and (
            regex[i + 1] in chars or regex[i + 1] == '('):
            new_regex.append('.')
    regex = ''.join(new_regex)

    for char in regex:
        if char in chars:
            output.append(char)
        elif char == '(':
            operators.append(char)
        elif char == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()
        elif char in precedence:
            while (operators and operators[-1] != '(' and
                   precedence[operators[-1]] >= precedence[char]):
                output.append(operators.pop())
            operators.append(char)
    while operators:
        output.append(operators.pop())

    return ''.join(output)

def thompsons_construction(regex):
    stack = []
    postfix = regex_to_postfix(regex)

    for char in postfix:
        if char.isalnum():  
            stack.append(create_basic_nfa(char))
        elif char == '.':  
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(apply_concatenation(nfa1, nfa2))
        elif char == '|':  
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(apply_union(nfa1, nfa2))
        elif char == '*':  
            nfa = stack.pop()
            stack.append(apply_kleene_star(nfa))

    if len(stack) != 1:
        raise ValueError("Invalid regular expression: remaining items on the stack after processing.")
    
    return stack[0]

def visualize_nfa(nfa, filename='nfa'):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR')  # Set horizontal layout
    dot.attr(dpi='300')  # Increase DPI for higher resolution
    state_ids = {}

    def get_state_id(state):
        if state not in state_ids:
            state_ids[state] = f's{len(state_ids)}'
        return state_ids[state]

    def add_state(state, is_initial=False, is_final=False):
        state_id = get_state_id(state)
        if is_initial:
            fillcolor = 'lightgreen'
        elif is_final:
            fillcolor = 'lightgreen'
        else:
            fillcolor = 'lightblue'  # Very light pink for non-initial, non-final states

        shape = 'doublecircle' if state.is_accept else 'circle'
        dot.node(state_id, shape=shape, style='filled', fillcolor=fillcolor)

        for char, next_states in state.transitions.items():
            for next_state in next_states:
                dot.edge(state_id, get_state_id(next_state), label=char)

    def traverse(state, visited, is_initial=False):
        if state in visited:
            return
        visited.add(state)
        add_state(state, is_initial=is_initial, is_final=state.is_accept)
        for next_states in state.transitions.values():
            for next_state in next_states:
                traverse(next_state, visited, is_initial=False)

    # Set the initial state as light blue
    traverse(nfa.start, set(), is_initial=True)
    dot.render(filename, cleanup=True)

# Tkinter GUI Code
def on_generate_click():
    regex = regex_entry.get()  # Get regex input from entry widget
    try:
        # Perform NFA generation and visualization
        nfa = thompsons_construction(regex)
        nfa.accept.is_accept = True
        visualize_nfa(nfa, 'nfa')

        # Display success message in terminal output
        terminal_output.insert(tk.END, f"Successfully generated NFA for regex: {regex}\n")

        # Load and display the NFA image
        img = Image.open('nfa.png')
        # Dynamically resize the image to fit in the GUI window
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        max_width = int(window_width * 0.8)
        max_height = int(window_height * 0.6)
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        img_label.config(image=img)
        img_label.image = img  # Keep a reference to prevent garbage collection

    except Exception as e:
        terminal_output.insert(tk.END, f"Error: {e}\n")

# Create Tkinter window
root = tk.Tk()
root.title("NFA Visualization")
root.geometry("1000x700")  # Initial window size

# Create Widgets
regex_label = tk.Label(root, text="Enter Regular Expression:")
regex_label.pack()

regex_entry = tk.Entry(root, width=40)
regex_entry.pack()

generate_button = tk.Button(root, text="Generate NFA", command=on_generate_click)
generate_button.pack()

terminal_output = tk.Text(root, height=10, width=50)
terminal_output.pack()

img_label = tk.Label(root)
img_label.pack()

# Run the Tkinter main loop
root.mainloop()