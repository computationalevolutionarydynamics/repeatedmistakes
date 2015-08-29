"""
Contains functions used to simulate different scenarios involving the iterated prisoner's dilemma
"""
from numpy.random import RandomState
import statistics


def simulate_normalised_payoff(strategy_one, strategy_two, payoff_matrix, continuation_probability,
                               trials=1000, seed=1234, estimator_stdev=None):
    """
    Calculate the normalised payoff for each strategy in the iterated prisoner's dilemma

    This method calculates the normalised payoff for two strategies in the iterated prisoner's dilemma using a monte
    carlo method. The prisoner's dilemma is played for a random number of rounds (as determined by the continuation
    probability). The number of trials performed is either passed as a parameter or alternatively we generate enough
    trials so that we can guarantee that the standard deviation of the normalised payoff is within the passed bound.
    We then calculate the mean of these trials to get our simulated normalised payoff

    Args:
        strategy_one (Strategy): The strategy to be tested
        strategy_two (Strategy): The other strategy
        payoff_matrix (PayoffMatrix): A payoff matrix representing the rewards for each set of actions
        continuation_probability (float): The probability of continuing the game
        trials (int): The number of games to simulate in order to calculate the normalised payoff
        seed (int): The seed for the PRNG
        estimator_stdev (float): The allowable deviation of our estimator.

    Returns:
        strategy_one_normalised_payoff, strategy_two_normalised_payoff: the normalised payoffs
    """
    # Create an PRNG instance and seed it
    random_instance = RandomState(seed)

    strategy_one_payoffs = []
    strategy_two_payoffs = []

    # Count the number of trials
    number_of_trials = 0

    # Set up the continuation variable
    cont = True

    while cont:
        number_of_trials += 1

        # Perform the trials and add them to the dataframe
        trial = perform_trial(strategy_one, strategy_two, payoff_matrix, continuation_probability, random_instance)
        strategy_one_payoffs.append(trial[0])
        strategy_two_payoffs.append(trial[1])

        if estimator_stdev is None:
            if number_of_trials >= trials:
                break
        else:
            if number_of_trials > 100:
                # Compute the sample standard deviation for both players
                strategy_one_stdev = statistics.stdev(strategy_one_payoffs)
                strategy_two_stdev = statistics.stdev(strategy_two_payoffs)
                # If both are below threshold, break
                if strategy_one_stdev < estimator_stdev and strategy_two_stdev < estimator_stdev:
                    break

    strategy_one_normalised_payoff = statistics.mean(strategy_one_payoffs) * (1 - continuation_probability)
    strategy_two_normalised_payoff = statistics.mean(strategy_two_payoffs) * (1 - continuation_probability)
    return strategy_one_normalised_payoff, strategy_two_normalised_payoff

def perform_trial(strategy_one, strategy_two, payoff_matrix, continuation_probability, random_instance):
    """
    Perform one game of the iterated prisoners dilemma and return the payoff for each player

    This simulates the game between two players, recording the total payoff. We keep simulating the game until the
    random value we pick is above the continuation probability.

    Args:
        strategy_one (Strategy): The first strategy
        strategy_two (Strategy): The second strategy
        payoff_matrix (PayoffMatrix): The payoff matrix representing the reward for each action
        continuation_probability (float): The probability of continuing each game
        random_instance (RandomState): A random state instance with which to generate random numbers

    Returns:
        player_one_payoff, player_two_payoff: The payoffs of each player
    """
    # Create the players with the movesets from the payoff matrix
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    # Set up the total payoffs
    player_one_payoff = 0.
    player_two_payoff = 0.

    # Set up the continuation variable
    cont = True

    while cont:
        player_one_move = player_one.next_move(player_two.history)
        player_two_move = player_two.next_move(player_one.history)

        # Calculate payoffs and add them to the total
        payoff_one, payoff_two = payoff_matrix.payoff(player_one=player_one_move, player_two=player_two_move)
        player_one_payoff += payoff_one
        player_two_payoff += payoff_two

        # Update the histories of the strategies
        player_one.history += player_one_move
        player_two.history += player_two_move

        # Figure out whether we should continue or not
        if random_instance.random_sample() > continuation_probability:
            cont = False

    return player_one_payoff, player_two_payoff

