"""
Contains functions that allow for the analysis of different strategies or combinations of strategies and for performing
computations.
"""
def calculate_normalised_payoff(player, opponent, payoff_matrix, continuation_probability, epsilon):
    """
    Calculate the normalised payoff for a particular strategy and opponent in the iterated prisoner's dilemma

    This method is used to calculate the normalised value of the payoff when two strategies play each other in the
    iterated prisoner's dilemma with a given payoff structure and continuation probability.
    The payoff is calculated via a sum, until the size of the term is less than some epsilon, at which point the sum
    is truncated and the result is returned.

    Args:
        player (callable): A callable that represents the player for which the payoff is to be calculated. This callable
            should take as an argument a history of moves (in the form of a string of cs and ds) and return either a
            c or a d representing cooperation or defection in the iterated prisoner's dilemma.
        opponent (callable): A callable that represents the opponent of the player. The opponent should have similar
            behaviour to the player.
        payoff_matrix (pandas.DataFrame): A pandas dataframe that holds the payoff matrix. It is expected that columns
            and rows are labelled c and d, with the player along the columns and the opponent along the rows
        continuation_probability (float): The probability that another game is played after each round.
        epsilon (float): The minimum size of terms in the sum before the sum is truncated and the result is returned

    Returns:
        normalised_payoff (float): The normalised payoff for the player

    Raises:
        ValueError: If the continuation probability is greater than or equal to 1, as this would mean that the sum
            would not converge.
    """
    if continuation_probability >= 1:
        raise ValueError('Continuation probability must be less than 1 for the sum to converge')

    normalised_payoff = 0
    player_history = ''
    opponent_history = ''

    term = np.Infinity
    rounds = 0
    while term > epsilon:
        rounds += 1
        # Compute the moves that each strategy makes
        player_move = player(opponent_history)
        opponent_move = opponent(player_history)
        # Add these moves to each history
        player_history += player_move
        opponent_history += opponent_move
        # Get the payoff resulting from the last game
        payoff = payoff_matrix[player_move][opponent_move]
        # Compute the term from the sum
        term = (continuation_probability ** rounds) * payoff
        normalised_payoff += term

    # Multiply by (1 - continuation_probability) to normalise the value
    normalised_payoff = (1 - continuation_probability) * normalised_payoff

    return normalised_payoff
