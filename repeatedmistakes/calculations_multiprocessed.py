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
                                  mistake_probability, epsilon):
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

    Returns:
        strategy_one_payoff, strategy_two_payoff (float): The normalised payoff result

    Raises:
        ValueError: If the continuation probability is greater than or equal to 1 or less than zero
        ValueError: If the mistake_probability is greater than or equal to 1 or less than zero
        ValueError: If the calc_method is not one of the valid ones
    """
    # Validate some input
    if continuation_probability >= 1 or continuation_probability < 0:
        raise ValueError('Continuation probability must less than 1 (for convergence) and greater than or equal to zero')

    if mistake_probability >= 1 or mistake_probability < 0:
        raise ValueError('Mistake probability must be a valid probability ie. in the range [0, 1]')

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
    naive_partial = partial(worker,
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


def worker(nodeq, resultq, strategy_one, strategy_two, payoff_matrix, continuation_probability, mistake_probability, epsilon):
    """
    This method is dispatched to do the work involved in processing each item in the queue
    """
    # Set up the strategy objects
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    # Initialise per process totals
    per_process_total = [0., 0.]

    # Set up an internal queue. This minimizes overhead by allowing each queue to work on chunks of the tree, only
    # stopping to get another chunk once it has finished
    internalq = queue.Queue()

    # Figure out the max payoff, since this doesn't change
    payoff_max = payoff_matrix.max()

    while True:
        try:
            try:
                # Get the first item in the internal queue
                node = internalq.get_nowait()
            except queue.Empty:
                # If it's empty, get the first item in the external queue instead
                node = nodeq.get(True, 0.1)


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
            per_process_total[0] += strategy_one_payoff
            per_process_total[1] += strategy_two_payoff

            # Add an item to the queue, if the max term size is large enough
            coefficient = continuation_probability * ((1 - mistake_probability) ** 2) * node.coefficient
            publish_node(coefficient, payoff_max, epsilon, player_one.history + player_one_move, player_two.history + player_two_move, internalq, nodeq)

            # Figure out the case for one mistake
            # Compute the payoff
            # Make one mistake
            player_one_move = player_one.opposite(player_one_move)
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            strategy_two_payoff = payoff[1] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            per_process_total[0] += strategy_one_payoff
            per_process_total[1] += strategy_two_payoff

            # Add to the queue if max term size is large enough
            coefficient = continuation_probability * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            publish_node(coefficient, payoff_max, epsilon, player_one.history + player_one_move, player_two.history + player_two_move, internalq, nodeq)

            # Now the other one mistake case
            # Reverse the mistake we just made
            player_one_move = player_one.opposite(player_one_move)
            # Make another mistake
            player_two_move = player_two.opposite(player_two_move)
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            strategy_two_payoff = payoff[1] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            per_process_total[0] += strategy_one_payoff
            per_process_total[1] += strategy_two_payoff

            # Add to the queue if the max term size is large enough
            coefficient = continuation_probability * (mistake_probability * (1 - mistake_probability)) * node.coefficient
            publish_node(coefficient, payoff_max, epsilon, player_one.history + player_one_move, player_two.history + player_two_move, internalq, nodeq)

            # Lastly the two mistake case
            # Make another mistake for a total of two (the second player has already made a mistake)
            player_one_move = player_one.opposite(player_one_move)
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            strategy_one_payoff = payoff[0] * (mistake_probability ** 2) * node.coefficient
            strategy_two_payoff = payoff[1] * (mistake_probability ** 2) * node.coefficient
            per_process_total[0] += strategy_one_payoff
            per_process_total[1] += strategy_two_payoff

            # Add to the queue if the max term size is large enough
            coefficient = continuation_probability * (mistake_probability ** 2) * node.coefficient
            publish_node(coefficient, payoff_max, epsilon, player_one.history + player_one_move, player_two.history + player_two_move, internalq, nodeq)

        except queue.Empty:
            # If the external queue is empty for longer than .5 of a second, we're going to take that as a sign that
            # there are no mure pieces of the tree to process so we'll return
            resultq.put(per_process_total)
            return

def publish_node(coefficient, payoff_matrix_max, epsilon, p_one_history, p_two_history, internal_queue, external_queue):
    """
    Publish a node to a particular queue, depending on the size of the resultant maximum term and the length of the
    history

    This method first decides whether we should even publish to the queue by comparing the product of the max term size
    and the epsilon. If the max term size * coefficient is less than the epsilon, we don't publish to the queue.

    If the max term size * epsilon is greater than the epsilon, we must decide which queue to publish too.
    If the length of the history is sufficiently small (as determined by a constant for now, possibly a variable later
    if we decide it should be tweakable) then we publish to the global queue that all processes pull form. If the
    history length is greater than this constant size, we publish to an internal queue.

    Args:
        coefficient (float): The coefficient of the node to be published.
        payoff_matrix_max (float): The maximum payoff for the payoff matrix. Used to determine if we should publish
            the node.
        epsilon (float): The term size below which we no longer publish nodes.
        p_one_history (string): The history of player one. Used as part of the node to publish
        p_two_history (string): The history of player two. Used as part of the node to publish
        internal_queue (Queue): The internal queue to publish to if the history length is large
        external_queue (Queue): The external queue to publish to if the history length is small
    """
    EXTERNAL_HISTORY_LIMIT = 2
    # Decide if we should publish or not
    if coefficient * payoff_matrix_max < epsilon:
        # Don't publish
        pass
    else:
        # Create the node object
        new_node = Node(coefficient, [p_one_history, p_two_history])
        # Figure out where the node should go
        if len(p_one_history) <= EXTERNAL_HISTORY_LIMIT:
            # Publish to the external history
            external_queue.put(new_node)
        else:
            # Publish to the internal queue
            internal_queue.put(new_node)
