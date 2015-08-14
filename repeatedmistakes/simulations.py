"""
Contains functions used to simulate different scenarios involving the iterated prisoner's dilemma
"""
from numpy.random import RandomState


def simulate_expected_payoff(player, opponent, payoff_matrix, continuation_probability, trials=1000, seed=1234):
    """
    Calculate the expected payoff for a particular strategy and opponent in the iterated prisoner's dilemma

    This method calculates the expected payoff for a particular strategy against an opponent strategy with a given
    payoff structure and continuatione probability in the iterated prisoners dilemma using a monte-carlo method to
    simulate games of random length.

    Args:
         player (callable): A callable that represents the player for which the payoff is to be calculated. This callable
            should take as an argument a history of moves (in the form of a string of cs and ds) and return either a
            c or a d representing cooperation or defection in the iterated prisoner's dilemma.
        opponent (callable): A callable that represents the opponent of the player. The opponent should have similar
            behaviour to the player.
        payoff_matrix (pandas.DataFrame): A pandas dataframe that holds the payoff matrix. It is expected that columns
            and rows are labelled c and d, with the player along the columns and the opponent along the rows
        continuation_probability (float): The probability that another game is played after each round.
        trials (int): The number of games to simulate.

    Returns:
        expected_payoff (float): The expected payoff for the player
    """
    # Create an PRNG instance and seed it
    random_instance = RandomState(seed)
    total_payoff = 0

    # We want trials number of games
    for _ in range(trials):
        continue_game = 0.

        # Reset the histories of each player
        player_history = ''
        opponent_history = ''
        # We want to repeat until we pick a random number that's greater than the continuation probability
        while continue_game < continuation_probability:
            # Figure out what move each player plays
            player_move = player(opponent_history)
            opponent_move = opponent(player_history)
            # Add these moves to each player's history
            player_history += player_move
            opponent_history += opponent_move
            # Get the payoff for this set of moves
            payoff = payoff_matrix[player_move][opponent_move]
            # Add this to the expected payoff
            total_payoff += payoff

            # Choose a random float between zero and one. If this is greater than the continuation probability, the game
            # stops
            continue_game = random_instance.random_sample()

    # Divide the total payoff by the number of trials to give the expected payoff
    expected_payoff = total_payoff / trials
    return expected_payoff
