assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]


digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
boxes  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')] +
            [[rows[int(n)-1] + n for n in cols]] +  [[rows[9-int(n)] + n for n in cols]])
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:  
        # for each unit: row,column,square,diagonal
        # create inverse maps value to box dictionary 'inv_twin_dict' 
        # value of that box is key, and the box label is value
        unit_values = [values[element] for element in unit]
        unit_dict = dict(zip(unit, unit_values))
        inverse_map = {}
        for key, value in unit_dict.items():
            inverse_map.setdefault(value, []).append(key)
        # make inverse twin dictionary
        inv_twin_dict = {key: value for key, value in inverse_map.items() if len(value) == 2 and len(key) == 2}

        # list of unsolved boxes in unit
        unsolved_boxes = [key for key in unit_dict.keys() if len(unit_dict[key]) > 1]
        # if a digit is in any twin box, delete that from the unsolved boxes
        for twin_value, twin_box in inv_twin_dict.items():
            for unsolved_box in unsolved_boxes:
                if unsolved_box not in twin_box:
                    for digit in twin_value:
                        new_value = values[unsolved_box].replace(digit, '')
                        assign_value(values, unsolved_box, new_value)
    return values
                            


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    assert all(char in '123456789.' for char in grid)
    chars = [c if c != '.' else '123456789' for c in grid]
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in 'ABCDEFGHI':
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in '123456789'))
        if r in 'CF': print(line)
    return

def eliminate(values):

    # first of all, let's find all solved boxes
    solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
    # secondly, eliminate they from peers
    for box in solved_boxes:
        value = values[box]
        for peer in peers[box]:  
            values[peer] = values[peer].replace(value,'')
    return values

def only_choice(values):
    for unit in unitlist:
        for possible_answer in '123456789': 
            dplaces = [box for box in unit if possible_answer in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], possible_answer)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Eliminate Strategy
        values = eliminate(values)
        # Only Choice Strategy
        values = only_choice(values)
        # Naked twins
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values
def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ##
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1) #beautifull!
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values = grid_values(grid)
    values = search(values)
    if values is False:
        return False ## Failed earlier
    return values
    

    

if __name__ == '__main__':
    
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
        
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
