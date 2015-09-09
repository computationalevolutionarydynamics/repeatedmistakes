"""
Contains functions that allow for the analysis of different strategies or combinations of strategies and for performing
computations, utilising multiprocessing for speed improvements.
"""
from multiprocessing import Manager, cpu_count, Process
from functools import partial
import queue
from collections import namedtuple

# Set up a namedtuple to structure the data on our queue
Node = namedtuple('Node',['coefficient', 'history'])

def calculate_payoff_with_mistakes(strategy_one, strategy_two, payoff_matrix, continuation_probability,
                                  mistake_probability, epsilon, calc_method='naive'):
    """
    Calculate the normalised payoff for strategies in the iterated prisoner's dilemma with mistakes

    Args:
        strategy_one (Strategy): The first strategy in the game
        strategy_two (Strategy): The second strategy in the game
        payoff_matrix (PayoffMatrix): An object that gives the payoff for each player given certain actions
        continuation_probability (float): The probability that another game is played after each round
        mistake_probability (float): The probability of a single strategy making a mistake in a single round
        epsilon (float): The value at which we truncate the series. We truncate when the largest possible term is lower
            than this value
        calc_method (string): A calculation method. We may offer a few of these, and we may later split this function
            up if there isn't enough in common between the calculation methods.

    Returns:
        strategy_one_payoff, strategy_two_payoff (float): The normalised payoff result

    Raises:
        ValueError: If the continuation probability is greater than or equal to 1 or less than zero
        ValueError: If the mistake_probability is greater than or equal to 1 or less than zero
        ValueError: If the calc_method is not one of the valid ones

    Calculation methods:
        naive: This calculates the sum by enumerating all of the possibilities. The implementation method is a queue,
            where terms and associated state are dequeue, processed and added to the totals, and then the new terms
            generated by that path are enqueued.
    """
    # Validate some input
    if continuation_probability >= 1 or continuation_probability < 0:
        raise ValueError('Continuation probability must less than 1 (for convergence) and greater than or equal to zero')

    if mistake_probability >= 1 or mistake_probability < 0:
        raise ValueError('Mistake probability must be a valid probability ie. in the range [0, 1]')

    strategy_one_payoff = 0.
    strategy_two_payoff = 0.

    # Dict mapping calculation methods to functions
    calc_methods = {'naive': naive_method}

    if calc_method in calc_methods.keys():
        strategy_one_payoff, strategy_two_payoff = calc_methods[calc_method](strategy_one, strategy_two, payoff_matrix,
                                                                             continuation_probability,
                                                                             mistake_probability, epsilon)
    else:
        raise ValueError('Invalid calculation method selected. Valid options are ' + str(calc_methods))

    return strategy_one_payoff, strategy_two_payoff


def naive_method(strategy_one, strategy_two, payoff_matrix, continuation_probability, mistake_probability, epsilon):
    # This queue will hold the terms that need to be computed and the results returned from the processes.
    m = Manager()
    nodeq = m.Queue()
    resultq = m.Queue()


    # We initialise the queue with an empty history and a term of 1
    nodeq.put(Node(coefficient=1, history=('', '')))

    # Set up the values we're going to return
    strategy_one_payoff = 0.
    strategy_two_payoff = 0.

    # Set up a partial function for the worker functions
    naive_partial = partial(naive_worker,
                            nodeq=nodeq,
                            resultq=resultq,
                            strategy_one=strategy_one,
                            strategy_two=strategy_two,
                            payoff_matrix=payoff_matrix,
                            continuation_probability=continuation_probability,
                            mistake_probability=mistake_probability,
                            epsilon=epsilon)

    # Fire up the workers
    processes = []
    for _ in range(cpu_count()):
        proc = Process(target=naive_partial)
        proc.start()
        processes.append(proc)

    # Join the processes
    for proc in processes:
        proc.join()

    # Read the values from the result queue and add them up
    while not resultq.empty():
        result = resultq.get()
        strategy_one_payoff += result[0]
        strategy_two_payoff += result[1]

    # Normalise by multiplying by 1 - continuation_probability
    strategy_one_payoff *= (1 - continuation_probability)
    strategy_two_payoff *= (1 - continuation_probability)

    return strategy_one_payoff, strategy_two_payoff


def naive_worker(nodeq, resultq, strategy_one, strategy_two, payoff_matrix, continuation_probability, mistake_probability, epsilon):
    """
    This method is dispatched by the naive method to do the work involved in processing each item in the queue
    """
    # Set up the strategy objects
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    while True:
        try:
            # Get the first item in the queue
            node = nodeq.get(True, 1)

            # Process the no-mistake case
            # Unpack the histories
            player_one.history, player_two.history = node.history

            # Get the next moves
            player_one_move = player_one.next_move(player_two.history)
            player_two_move = player_two.next_move(player_one.history)

            # Compute the payoff and add it to the total
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * ((1 - mistake_probability) ** 2) * node.coefficient
            strategy_two_payoff = payoff[1] * ((1 - mistake_probability) ** 2) * node.coefficient
            resultq.put((strategy_one_payoff, strategy_two_payoff))

            # Add an item to the queue, if the max term size is large enough
            coefficient = continuation_probability * ((1 - mistake_probability) ** 2) * node.coefficient
            if coefficient * payoff_matrix.max() > epsilon:
                nodeq.put(Node(coefficient=coefficient, history=[player_one.history + player_one_move,
                                                                 player_two.history + player_two_move]))

            # Figure out the case for one mistake
            # Compute the payoff
            # Make one mistake
            player_one_move = player_one.opposite(player_one_move)
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            strategy_two_payoff = payoff[1] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            resultq.put((strategy_one_payoff, strategy_two_payoff))

            # Add to the queue if max term size is large enough
            coefficient = continuation_probability * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            if coefficient * payoff_matrix.max() > epsilon:
                nodeq.put(Node(coefficient=coefficient, history=[player_one.history + player_one_move,
                                                                 player_two.history + player_two_move]))

            # Now the other one mistake case
            # Reverse the mistake we just made
            player_one_move = player_one.opposite(player_one_move)
            # Make another mistake
            player_two_move = player_two.opposite(player_two_move)
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            strategy_two_payoff = payoff[1] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            resultq.put((strategy_one_payoff, strategy_two_payoff))

            # Add to the queue if the max term size is large enough
            coefficient = continuation_probability * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            if coefficient * payoff_matrix.max() > epsilon:
                nodeq.put(Node(coefficient=coefficient, history=[player_one.history + player_one_move,
                                                                 player_two.history + player_two_move]))

            # Lastly the two mistake case
            # Make another mistake for a total of two (the second player has already made a mistake)
            player_one_move = player_one.opposite(player_one_move)
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * (mistake_probability ** 2) * node.coefficient
            strategy_two_payoff = payoff[1] * (mistake_probability ** 2) * node.coefficient
            resultq.put((strategy_one_payoff, strategy_two_payoff))

            # Add to the queue if the max term size is large enough
            coefficient = continuation_probability * (mistake_probability ** 2) * node.coefficient
            if coefficient * payoff_matrix.max() > epsilon:
                nodeq.put(Node(coefficient=coefficient, history=[player_one.history + player_one_move,
                                                                 player_two.history + player_two_move]))

        except queue.Empty:
            # If the queue is empty for longer than 1 second, we're going to assume that we've run out of data
            # to process and we'll return
            return
