"""
Contains functions used to simulate different scenarios involving the iterated prisoner's dilemma
"""
from numpy.random import RandomState


def simulate_normalised_payoff(strategy_one, strategy_two, payoff_matrix, continuation_probability, trials=1000, seed=1234):
    """
    Calculate the normalised payoff for each strategy in the iterated prisoner's dilemma

    This method calculates the normalised payoff for two strategies in the iterated prisoner's dilemma using a monte
    carlo method. The prisoner's dilemma is played for a random number of rounds (as determined by the continuation
    probability) for some given number of trials, and the normalised payoff of each strategy is then computed.

    Args:
        strategy_one (Strategy): The strategy to be tested
        strategy_two (Strategy): The other strategy
        payoff_matrix (PayoffMatrix): A payoff matrix representing the rewards for each set of actions
        continuation_probability (float): The probability of continuing the game
        trials (int): The number of games to simulate in order to calculate the normalised payoff
        seed (int): The seed for the PRNG

    Returns:
        normalised_payoff (dict): A dictionary where the keys are the strategies and the values are the normalised
            payoff.
    """
    # Create an PRNG instance and seed it
    random_instance = RandomState(seed)

    normalised_payoff = {strategy_one: 0, strategy_two: 0}

    # Create the strategy objects, taking the characterset from the payoff_matrix
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    # We want trials number of games
    for _ in range(trials):
        continue_game = 0.
        player_one_total_payoff  = 0.
        player_two_total_payoff  = 0.

        # Reset each player
        player_one.reset()
        player_two.reset()
        # We want to repeat until we pick a random number that's greater than the continuation probability
        while continue_game < continuation_probability:
            # Figure out what move each player plays
            move_one = player_one.next_move(player_two.history)
            move_two = player_two.next_move(player_one.history)
            # Add these moves to each player's history
            player_one.history += move_one
            player_two.history += move_two
            # Get the payoff for each player for this set of moves
            player_one_payoff, player_two_payoff = payoff_matrix.payoff(player_one=move_one, player_two=move_two)
            # Add this to the expected payoff
            player_one_total_payoff += player_one_payoff
            player_two_total_payoff += player_two_payoff
            # Choose a random float between zero and one. If this is greater than the continuation probability, the game
            # stops
            continue_game = random_instance.random_sample()

        # Multiply each payoff by (1-continuation_probability) to normalise it, then add it to the dict value
        normalised_payoff[player_one] += (1 - continuation_probability) * player_one_total_payoff
        normalised_payoff[player_two] += (1 - continuation_probability) * player_two_total_payoff

    # Divide the payoffs by the total number of trials and return the final answer
    normalised_payoff[player_one] /= trials
    normalised_payoff[player_two] /= trials

    return normalised_payoff
