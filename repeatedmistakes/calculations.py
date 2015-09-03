"""
Contains functions that allow for the analysis of different strategies or combinations of strategies and for performing
computations.
"""
def calculate_payoff(strategy_one, strategy_two, payoff_matrix, continuation_probability, epsilon):
    """
    Calculate the normalised payoff for strategies in the iterated prisoner's dilemma

    This method is used to calculate the normalised value of the payoff when two strategies play each other in the
    iterated prisoner's dilemma with a given payoff structure and continuation probability.
    The payoff is calculated until the maximum possible payoff for the current round is less than some epsilon, at which
    point the series is truncated and returned.

    Args:
        strategy_one (Strategy): The first strategy in the game
        strategy_two (Strategy): The other strategy in the game
        payoff_matrix (PayoffMatrix): An object that gives the payoff for each player given certain actions
        continuation_probability (float): The probability that another game is played after each round.
        epsilon (float): The minimum possible size of a term before the series is truncated

    Returns:
        strategy_one_payoff, strategy_two_payoff (float): The normalised payoffs

    Raises:
        ValueError: If the continuation probability is greater than or equal to 1, as this would mean that the sum
            would not converge.
    """
    if continuation_probability >= 1:
        raise ValueError('Continuation probability must be less than 1 for the sum to converge')

    strategy_one_payoff = 0
    strategy_two_payoff = 0

    # Create the player objects using the characterset from the payoff matrix
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    max_term_size = float('inf')

    # Set the rounds coutner to -1 so that the first round will be round 0
    rounds = -1
    while max_term_size > epsilon:
        rounds += 1
        # Compute the moves that each strategy makes
        move_one = player_one.next_move(player_two.history)
        move_two = player_two.next_move(player_one.history)
        # Add these moves to each history
        player_one.history += move_one
        player_two.history += move_two
        # Get the payoff resulting from the last game
        player_one_payoff, player_two_payoff = payoff_matrix.payoff(player_one=move_one, player_two=move_two)
        # Compute the term from the sum
        player_one_term = (continuation_probability ** rounds) * player_one_payoff
        player_two_term = (continuation_probability ** rounds) * player_two_payoff
        strategy_one_payoff += player_one_term
        strategy_two_payoff += player_two_term

        # Compute the max term size
        max_term_size = (continuation_probability ** rounds) * payoff_matrix.max()


    # Multiply by (1 - continuation_probability) to normalise the value
    strategy_one_payoff *= (1 - continuation_probability)
    strategy_two_payoff *= (1 - continuation_probability)

    return strategy_one_payoff, strategy_two_payoff
