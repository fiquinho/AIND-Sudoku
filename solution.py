assignments = []
ROWS = 'ABCDEFGHI'
COLS = '123456789'


def cross(a, b):
    """
    Returns the list formed by all the possible concatenations of
    a letter A in string a with a letter B in string b.
    :param a: String
    :param b: String
    :return: List with all possible concatenations
    """

    crossed = [A + B for A in a for B in b]
    return crossed


BOARD = cross(ROWS, COLS)

ROW_UNITS = [cross(r, COLS) for r in ROWS]
COLUMN_UNITS = [cross(ROWS, c) for c in COLS]
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

diagonal_1 = []
diagonal_2 = []
reversed_cols = COLS[::-1]
for i in range(len(ROWS)):
    diagonal_1.append(ROWS[i] + COLS[i])
    diagonal_2.append(ROWS[i] + reversed_cols[i])

DIAGONAL_UNITS = [diagonal_1, diagonal_2]

UNIT_LIST = ROW_UNITS + COLUMN_UNITS + SQUARE_UNITS + DIAGONAL_UNITS
UNITS = dict((s, [u for u in UNIT_LIST if s in u]) for s in BOARD)
PEERS = dict((s, set(sum(UNITS[s], [])) - {s}) for s in BOARD)


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

    # Check every unit for naked twins
    for unit in UNIT_LIST:
        # Empty list to hold the naked twins of this unit
        twins = []
        # Set created to keep track of witch box I have already checked
        unit_set = set(unit)

        # Check every box in the unit to see if it has a twin
        for box in unit:
            # Remove the actual box so it can compare to the rest
            unit_set.remove(box)

            # It only keeps going if the box can be a naked twin
            if len(values[box]) == 2:
                # Compare the actual box with all the remaining boxes
                for possible_twin in unit_set:
                    # If the two boxes are naked twins..
                    if values[box] == values[possible_twin]:
                        # .. append a tuple with the name of the boxes
                        twins.append((box, possible_twin))

        # If we found any naked twins
        if len(twins) != 0:
            for twin in twins:
                # Check every box in the unit. If the box isn't one of the naked twins, remove the values of the naked twins from it
                for box in unit:
                    if box != twin[0] and box != twin[1]:
                        for number in values[twin[0]]:
                            assign_value(values, box, values[box].replace(number, ""))

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
    
    empty = '123456789'
    result = {}

    for i in range(len(grid)):
        if grid[i] == '.':
            result[BOARD[i]] = empty
            #assign_value(result, BOARD[i], empty)
        else:
            result[BOARD[i]] = grid[i]
            #assign_value(result, BOARD[i], grid[i])

    return result


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in BOARD)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in ROWS:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '') for c in COLS))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """

    for pos in values.keys():

        if len(values[pos]) == 1:
            for peer in PEERS[pos]:
                # values[peer] = values[peer].replace(values[pos], "")
                assign_value(values, peer, values[peer].replace(values[pos], ""))

    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """

    for unit in UNIT_LIST:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                # values[dplaces[0]] = digit
                assign_value(values, dplaces[0], digit)

    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the naked twins strategy
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
    # Using depth-first search and propagation, create a search tree and solve the sudoku.
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False
    if all(len(values[s]) == 1 for s in BOARD):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in BOARD if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
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

    result = search(values)

    return result



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
