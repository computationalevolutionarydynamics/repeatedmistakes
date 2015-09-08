"""
Contains functions used to simulate different scenarios involving the iterated prisoner's dilemma, but taking advantage
of multithreading
"""
from numpy.random import RandomState
import numpy as np
from math import sqrt
from repeatedmistakes.simulations import perform_trial
from multiprocessing import Pool, Queue, cpu_count, Manager
from functools import partial

TRIAL_INCREMENT = 1000

def simulate_payoff(strategy_one, strategy_two, payoff_matrix, continuation_probability,
                               mistake_probability=0., trials=1000, estimator_stdev=None):
    """
    Calculate the normalised payoff for each strategy in the iterated prisoner's dilemma

    This method calculates the normalised payoff for two strategies in the iterated prisoner's dilemma using a monte
    carlo method. The prisoner's dilemma is played for a random number of rounds (as determined by the continuation
    probability). The number of trials performed is either passed as a parameter or alternatively we generate enough
    trials so that we can guarantee that the standard deviation of the normalised payoff is within the passed bound.
    In order to facilitate efficient multiprocessing:
        * If we are given a set number of trials, we simply split up the work evenly among the processes
        * If we are given a target standard deviation then we use the number of trials as a baseline, and then compute
            further trials in batches from there until we have the required standard deviation. This allows us to make
            efficient use of the processors.
    We then calculate the mean of tese trials to get our simulated normalised payoff

    Args:
        strategy_one (Strategy): The strategy to be tested
        strategy_two (Strategy): The other strategy
        payoff_matrix (PayoffMatrix): A payoff matrix representing the rewards for each set of actions
        continuation_probability (float): The probability of continuing the game
        mistake_probability (float): The probability of a single player making a single mistake in a single round
        trials (int): The number of games to simulate in order to calculate the normalised payoff
        estimator_stdev (float): The allowable deviation of our estimator.

    Returns:
        strategy_one_normalised_payoff, strategy_two_normalised_payoff: the normalised payoffs
    """
    strategy_one_payoffs = []
    strategy_two_payoffs = []

    # Set up a queue to store results
    m = Manager()
    q = m.Queue()

    # Split the trials into chunks for each process
    trial_chunks = [trials//cpu_count() for _ in range(cpu_count())]

    # Since all of the parameters remain the same across each process other than the number of trials, we create
    # a partial function with these values already prefilled, and map these onto the processes.
    partial_trials = partial(perform_multiple_trials, q=q, strategy_one=strategy_one, strategy_two=strategy_two,
                             payoff_matrix=payoff_matrix,
                             continuation_probability=continuation_probability,
                             mistake_probability=mistake_probability)

    # We need to count the number of trials in order to compute the estimator stdev
    number_of_trials = 0

    while True:
        # Get a pool of workers
        with Pool() as pool:
            # Get the workers to do the work. The results are placed into a queue as lists
            pool.map(partial_trials, trial_chunks)

            # Get the lists from the queue
            for i in range(cpu_count()):
                # Update the number of trials. Might as well do it when we're already looping
                number_of_trials += trial_chunks[i]
                # Get the trial list
                trial_list = q.get()
                # Split each trial into the first and second strategy payoffs
                for trial in trial_list:
                    strategy_one_payoffs.append(trial[0])
                    strategy_two_payoffs.append(trial[1])

            # If we didn't define an estimator then we've done all the trials we need
            if estimator_stdev is None:
                break

            else:
                # Compute the sample standard deviation for both players
                strategy_one_stdev = np.array(strategy_one_payoffs).std()
                strategy_two_stdev = np.array(strategy_two_payoffs).std()
                # Divide these by the sqrt of the number of trials
                strategy_one_stdev /= sqrt(number_of_trials)
                strategy_two_stdev /= sqrt(number_of_trials)
                # If both are below threshold, break
                if strategy_one_stdev < estimator_stdev and strategy_two_stdev < estimator_stdev:
                    break
                else:
                    # Otherwise, add few more trials
                    trial_chunks = [TRIAL_INCREMENT//cpu_count() for _ in range(cpu_count())]

    strategy_one_normalised_payoff = np.array(strategy_one_payoffs).mean() * (1 - continuation_probability)
    strategy_two_normalised_payoff = np.array(strategy_two_payoffs).mean() * (1 - continuation_probability)
    return strategy_one_normalised_payoff, strategy_two_normalised_payoff


def perform_multiple_trials(n, q, strategy_one, strategy_two, payoff_matrix, continuation_probability, mistake_probability):
    # Create an PRNG instance and seed it
    random_instance = RandomState()

    # Create the players with the movesets from the payoff matrix
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    trial_list = []

    for _ in range(n):
        # Perform the trials and add them to the dataframe
        trial_list.append(perform_trial(player_one, player_two, payoff_matrix, continuation_probability, random_instance, mistake_probability))

    q.put(trial_list)
