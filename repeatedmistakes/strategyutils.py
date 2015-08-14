"""
A set of utilities required by the strategies
"""

def valid_history(history, C = 'C', D = 'D'):
    """
    Checks for a valid game history string given a set of moves

    Args:
        history (string): A string representing the history of the game
        C (string): A string representing a cooperation. Defaults to 'C'
        D (string): A string representing a defection. Defaults to 'D'

    Returns:
        True if the history string consists of only the symbols for C and D, False otherwise
    """
    allowed_characters = [C, D]
    return all(char in allowed_characters for char in history)