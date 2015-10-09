"""
Contains functions that allow for the analysis of different strategies or combinations of strategies and for performing
computations.
"""
from queue import Queue
from collections import namedtuple
from scipy.optimize import broyden1
import math

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
            would not converge. We also need it to be >= 0 to be a valid probability.
    """
    if continuation_probability >= 1 or continuation_probability < 0:
        raise ValueError('Continuation probability must be less than 1 for the sum to converge')

    strategy_one_payoff = 0.
    strategy_two_payoff = 0.

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
    """
    # Validate some input
    if continuation_probability >= 1 or continuation_probability < 0:
        raise ValueError('Continuation probability must less than 1 (for convergence) and greater than or equal to zero')

    if mistake_probability >= 1 or mistake_probability < 0:
        raise ValueError('Mistake probability must be a valid probability ie. in the range [0, 1]')

    # This queue will hold the terms that need to be computed
    q = Queue()

    # Set up a namedtuple to structure the data on our queue
    Node = namedtuple('Node',['coefficient', 'history', 'mistakes'])

    # We initialise the queue with an empty history and a term of 1 which of course has zero mistakes
    q.put(Node(coefficient=1, history=('', ''), mistakes=0))

    # Set up the values we're going to return
    strategy_one_payoff = 0.
    strategy_two_payoff = 0.

    # Set up the strategy objects we wish to use. Use the charset from the payoff matrix
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    # Store the maximum payoff in a variable
    max_payoff = payoff_matrix.max()

    # Now we need to solve for some values. Firstly, we solve for the maximum history length such that the new term
    # we add to the sum is greater than epsilon
    # We need to define a function to solve for
    def history_prob(n):
        coefficient = (continuation_probability ** n) * ((1 - mistake_probability) ** (2 * n))
        term = max_payoff * coefficient
        return term

    # Now solve for the longest possible game with our given epsilon
    max_game_length = broyden1(lambda x: history_prob(x) - epsilon, 0)

    # Round this value down
    max_game_length = math.floor(max_game_length)

    # Next, for each possible value of game length, we have to solve for the maximum allowable number of mistakes
    # that still keeps the term size above epsilon
    def mistake_prob(n, mistakes):
        coefficient = (continuation_probability ** n) * ((1 - mistake_probability) ** (2 * n - mistakes))
        coefficient *= (mistake_probability ** mistakes)
        term = max_payoff * coefficient
        return term

    # Now, for each value between 1 and max_game_length, we need to solve for the above value
    # We set up a list to hold the results
    allowable_mistakes = []
    allowable_mistakes.append(None) # First item should be None since we never use game length 0
    for i in range(1, max_game_length+1):
        max_mistakes = broyden1(lambda x: mistake_prob(i, x) - epsilon, 0)
        # Round down and append to the list
        allowable_mistakes.append(math.floor(max_mistakes))

    while not q.empty():
        # Get the first item in the queue
        node = q.get()

        # Process the no-mistake case
        # Unpack the histories
        player_one.history, player_two.history = node.history

        # Get the next moves
        player_one_move = player_one.next_move(player_two.history)
        player_two_move = player_two.next_move(player_one.history)

        # Compute the payoff and add it to the total
        payoff = payoff_matrix.payoff(player_one_move, player_two_move)
        strategy_one_payoff += payoff[0] * ((1 - mistake_probability) ** 2) * node.coefficient
        strategy_two_payoff += payoff[1] * ((1 - mistake_probability) ** 2) * node.coefficient

        # Add an item to the queue, if the max term size is large enough
        coefficient = continuation_probability * ((1 - mistake_probability) ** 2) * node.coefficient
        if coefficient * payoff_matrix.max() > epsilon:
            q.put(Node(coefficient=coefficient, history=[player_one.history + player_one_move,
                                                         player_two.history + player_two_move], mistakes=node.mistakes))

        # Figure out the case for one mistake
        # Compute the payoff
        # Make one mistake
        player_one_move = player_one.opposite(player_one_move)
        payoff = payoff_matrix.payoff(player_one_move, player_two_move)
        strategy_one_payoff += payoff[0] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
        strategy_two_payoff += payoff[1] * (mistake_probability * (1 - mistake_probability)) * node.coefficient

        # Add to the queue if max term size is large enough
        coefficient = continuation_probability * (mistake_probability * (1 - mistake_probability)) * node.coefficient
        if coefficient * payoff_matrix.max() > epsilon:
            q.put(Node(coefficient=coefficient,
                       history=[player_one.history + player_one_move,
                                player_two.history + player_two_move],
                       mistakes=node.mistakes + 1))

        # Now the other one mistake case
        # Reverse the mistake we just made
        player_one_move = player_one.opposite(player_one_move)
        # Make another mistake
        player_two_move = player_two.opposite(player_two_move)
        payoff = payoff_matrix.payoff(player_one_move, player_two_move)
        strategy_one_payoff += payoff[0] * (mistake_probability * (1 - mistake_probability)) * node.coefficient
        strategy_two_payoff += payoff[1] * (mistake_probability * (1 - mistake_probability)) * node.coefficient

        # Add to the queue if the max term size is large enough
        coefficient = continuation_probability * (mistake_probability * (1 - mistake_probability)) * node.coefficient
        if coefficient * payoff_matrix.max() > epsilon:
            q.put(Node(coefficient=coefficient,
                       history=[player_one.history + player_one_move,
                                player_two.history + player_two_move],
                       mistakes=node.mistakes + 1))
        # Lastly the two mistake case
        # Make another mistake for a total of two (the second player has already made a mistake)
        player_one_move = player_one.opposite(player_one_move)
        payoff = payoff_matrix.payoff(player_one_move, player_two_move)
        strategy_one_payoff += payoff[0] * (mistake_probability ** 2) * node.coefficient
        strategy_two_payoff += payoff[1] * (mistake_probability ** 2) * node.coefficient

        # Add to the queue if the max term size is large enough
        coefficient = continuation_probability * (mistake_probability ** 2) * node.coefficient
        if coefficient * payoff_matrix.max() > epsilon:
            q.put(Node(coefficient=coefficient,
                       history=[player_one.history + player_one_move,
                                player_two.history + player_two_move],
                       mistakes=node.mistakes + 2))

    # Normalise by multiplying by 1 - continuation_probability
    strategy_one_payoff *= (1 - continuation_probability)
    strategy_two_payoff *= (1 - continuation_probability)

    return strategy_one_payoff, strategy_two_payoff
