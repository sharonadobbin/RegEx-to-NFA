import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
from typing import List, Tuple, Dict
import networkx as nx
import matplotlib.pyplot as plt


def parse_grammar(grammar_rules: List[str]) -> dict:
    """Parses grammar rules into a dictionary."""
    grammar = defaultdict(list)
    for rule in grammar_rules:
        head, productions = rule.split("->")
        head = head.strip()
        for prod in productions.split("|"):
            grammar[head].append(prod.strip())
    return grammar


def eliminate_left_recursion(grammar: dict) -> dict:
    """Eliminates left recursion in the grammar."""
    non_terminals = list(grammar.keys())
    new_grammar = defaultdict(list)

    for i, A in enumerate(non_terminals):
        for j in range(i):
            B = non_terminals[j]
            new_rules = []
            for rule in grammar[A]:
                if rule.startswith(B):
                    for b_rule in grammar[B]:
                        new_rules.append(b_rule + rule[len(B):])
                else:
                    new_rules.append(rule)
            grammar[A] = new_rules
        left_recursive = [rule for rule in grammar[A] if rule.startswith(A)]
        non_left_recursive = [rule for rule in grammar[A] if not rule.startswith(A)]

        if left_recursive:
            A_prime = A + "'"
            new_grammar[A] = [rule + A_prime for rule in non_left_recursive]
            new_grammar[A_prime] = [rule[len(A):] + A_prime for rule in left_recursive] + ["ε"]
        else:
            new_grammar[A] = grammar[A]

    return new_grammar


def generate_parse_trees(grammar: dict, symbol: str, target: str, position: int, memo: Dict = None) -> List[Tuple[str, List]]:
    """Generates parse trees for the given symbol and target string with memoization."""
    if memo is None:
        memo = {}
    if (symbol, position) in memo:
        return memo[(symbol, position)]

    # Base cases
    if position == len(target) and symbol == "ε":
        return [("ε", [])]  # Empty production matches end of target
    if position >= len(target) or not symbol:
        return []  # Invalid match

    trees = []
    for production in grammar.get(symbol, []):
        current_pos = position
        sub_trees = []
        valid = True

        for char in production:
            if char.isupper():  # Non-terminal
                sub_results = generate_parse_trees(grammar, char, target, current_pos, memo)
                if not sub_results:
                    valid = False
                    break
                sub_trees.append(sub_results)
            else:  # Terminal
                if current_pos < len(target) and target[current_pos] == char:
                    sub_trees.append([(char, [])])
                    current_pos += 1
                else:
                    valid = False
                    break

        if valid:
            for tree in combine_subtrees(sub_trees):
                trees.append((symbol, tree))

    memo[(symbol, position)] = trees
    return trees


def combine_subtrees(sub_trees: List[List[Tuple]]) -> List[List[Tuple]]:
    """Combines all possible subtree arrangements."""
    if not sub_trees:
        return [[]]
    first, rest = sub_trees[0], combine_subtrees(sub_trees[1:])
    return [[f] + r for f in first for r in rest]


def build_graph(tree: Tuple[str, List], graph: nx.Graph, parent=None, node_id=0) -> int:
    """Builds a graph from a parse tree."""
    symbol = tree[0]
    current_node = node_id
    graph.add_node(current_node, label=symbol)

    if parent is not None:
        graph.add_edge(parent, current_node)

    next_node_id = node_id + 1
    for child in tree[1]:
        next_node_id = build_graph(child, graph, current_node, next_node_id)

    return next_node_id


def display_graph(graph: nx.Graph):
    """Displays the parse tree graph using NetworkX and Matplotlib."""
    pos = nx.nx_pydot.graphviz_layout(graph, prog="dot")  # Ensure tree-like layout
    labels = nx.get_node_attributes(graph, "label")
    nx.draw(graph, pos, with_labels=True, labels=labels, node_size=3000, node_color="skyblue", font_size=12)
    plt.show()


def on_submit():
    """Handles the submit action from the GUI."""
    grammar_rules = input_text.get("1.0", "end-1c").splitlines()
    start_symbol = start_symbol_entry.get()
    test_string = test_string_entry.get()

    if not grammar_rules or not start_symbol or not test_string:
        messagebox.showerror("Input Error", "Please provide grammar rules, start symbol, and test string.")
        return

    try:
        grammar = parse_grammar(grammar_rules)
        grammar = eliminate_left_recursion(grammar)

        parse_trees = generate_parse_trees(grammar, start_symbol, test_string, 0)
        if not parse_trees:
            messagebox.showinfo("Result", f"No valid parse tree for the string '{test_string}'.")
            return

        messagebox.showinfo("Result", f"Valid parse trees for the string '{test_string}'.\nGenerating graph...")
        graph = nx.DiGraph()  # Use DiGraph to ensure directed edges
        for tree in parse_trees:
            build_graph(tree, graph)

        display_graph(graph)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Setting up the Tkinter GUI
root = tk.Tk()
root.title("Parse Tree Generator")

# Grammar input area
tk.Label(root, text="Enter Grammar Rules (Format: A -> a|bB):").pack(padx=10, pady=5)
input_text = tk.Text(root, height=10, width=40)
input_text.pack(padx=10, pady=5)

# Start symbol input
tk.Label(root, text="Enter Start Symbol:").pack(padx=10, pady=5)
start_symbol_entry = tk.Entry(root, width=40)
start_symbol_entry.pack(padx=10, pady=5)

# Test string input
tk.Label(root, text="Enter Test String:").pack(padx=10, pady=5)
test_string_entry = tk.Entry(root, width=40)
test_string_entry.pack(padx=10, pady=5)

# Submit button
submit_button = tk.Button(root, text="Generate Parse Tree", command=on_submit)
submit_button.pack(padx=10, pady=10)

# Start the Tkinter main loop
root.mainloop()