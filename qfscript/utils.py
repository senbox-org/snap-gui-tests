"""
Console utilities.

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""

class color:
    """console codes for different colors and print styles."""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    ITALIC = '\x1B[3m'


def print_error(code, pos):
    """prints a parsing error and show the line that generated it."""
    if pos is None:
        print("Error!!")
        return
    lines = code.split('\n')
    print(f"Parsing error detected at line {pos.lineno} at column {pos.colno}: ")
    
    for i, l in enumerate(lines):
        if i < pos.lineno - 2 or i > pos.lineno :
            continue 
        if i+1 == pos.lineno:
            c = pos.colno
            left = l[:c-1]
            right = l[c-1:]
            print(f'  {color.BOLD}{i+1:3d}. {left}{color.UNDERLINE}{right}{color.END}')
        else:
            print(f'  {i+1:3d}. {l}')