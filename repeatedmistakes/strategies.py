"""
Contains functions that model strategies for playing the iterated prisoner's dilemma

Each function should take as input a string consisting of c's and d's that represents the history of the opponent's
moves in a game of the iterated prisoner's dilemma, and return either a c or a d corresponding to that strategy's next
move. Any input not of the form of string of cs or ds should raise a ValueError

This module should not contain any non-strategy top-level callables, because the tests involve iterating over all of
the callables and testing against them.
"""
from repeatedmistakes.strategyutils import valid_history

def tit_for_tat(history):
    """
    The tit_for_tat strategy cooperates on the first round, and then plays whatever the opponent played last.

    Args:
        history (string): A string consisting of cs or ds (case insensitive) that represents the opponents moves

    Returns:
        A c or a d

    Raises:
        ValueError: If a character in the input is not recognised
    """
    # Make sure the history is a valid history string
    if not valid_history(history):
        raise ValueError('History string must consist of only cs and ds')

    # If the history is empty, cooperate
    if history == '':
        return 'c'
    else:
        # Copy the opponent's last move
        last_move = history[-1]
        return last_move.lower()

def allc(history):
    """
    The allc strategy always cooperates regardless of history.

    Args:
        history (string): A string consisting of cs or ds (case insensitive) that represents the opponents moves

    Returns:
        A c

    Raises:
        ValueError: If a character in the input is not recognised
    """
    # Make sure the history is a valid history string
    if not valid_history(history):
        raise ValueError('History string must consist of only cs and ds')

    return 'c'

def alld(history):
    """
    The alld strategy always cooperates regardless of history.

    Args:
        history (string): A string consisting of cs or ds (case insensitive) that represents the opponents moves

    Returns:
        A d

    Raises:
        ValueError: If a character in the input is not recognised
    """
    # Make sure the history is a valid history string
    if not valid_history(history):
        raise ValueError('History string must consist of only cs and ds')

    return 'd'

def inverse_tit_for_tat(history):
    """
    The inverse tit for tat strategy cooperates on the first round, then does the opposite of what the opponent did last

    Args:
        history (string): A string consisting of cs or ds (case insensitive) that represents the opponent's moves

    Returns:
        A c or a d

    Raises:
        ValueError: If a character in the input is not recognized
    """
    # Make sure the history is a valid history string
    if not valid_history(history):
        raise ValueError('History string must consist of only cs and ds')

    # If the history is empty, cooperate
    if history == '':
        return 'c'
    else:
        # Return the opposite of the opponent's last move
        last_move = history[-1].lower()
        if last_move == 'c':
            return 'd'
        else:
            return 'c'
