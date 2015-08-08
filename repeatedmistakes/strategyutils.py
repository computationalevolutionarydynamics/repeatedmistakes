"""
A set of utilities required by the strategies
"""

def valid_history(history):
    """
    Checks for a valid game history string

    Args:
        history (string): A string representing the history of the game

    Returns:
        True if the history string consists of only cs or ds (case insensitive), False otherwise
    """
    allowed_characters = ['c', 'd']
    return all(char in allowed_characters for char in history.lower())