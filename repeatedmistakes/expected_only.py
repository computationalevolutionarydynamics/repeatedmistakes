import math
from collections import namedtuple
from scipy.optimize import broyden1

HistoryFrame = namedtuple('HistoryFrame', ['player_one_history',
                                           'player_two_history',
                                           'mistakes'])

def expected_only(strategy_one, strategy_two, payoff_matrix, continuation_probability, mistake_probability, epsilon):
    """
    Compute the expected value of the payoff in an iterated prisoners dilemma using only the expected game length terms

    This takes an approximate approach to computing the expected payoff by only considerining the terms that arise
    from games with length equal to the expected game length
    """
    # Compute the expected number of rounds
    expected_rounds = math.floor(1 / continuation_probability)

    # Set up a function that we can solve for the maximum number of mistakes above the threshold
    def max_mistakes(n):
        term = (continuation_probability ** (expected_rounds - 1)) * (1 - continuation_probability)
        term = term * (mistake_probability ** (2 * expected_rounds - n))
        term = term * (1 - mistake_probability) ** n
        return term

    # Solve for the maximum number of allowable mistakes
    max_mistakes = broyden1(lambda x: max_mistakes(x) - epsilon, x0=2)

    # Take the floor
    max_mistakes = math.floor(max_mistakes)

    # Set up an initial HistoryFrame
    initial_frame = HistoryFrame([], [], 0)

    # Add this to a frame list
    frame_list = [initial_frame]

    # Create strategy objects that we will use
    player_one = strategy_one(payoff_matrix.C, payoff_matrix.D)
    player_two = strategy_two(payoff_matrix.C, payoff_matrix.D)

    # Loop until we've got the right length of history
    for _ in range(expected_rounds):
        # We want to pull each value out of the frame_list and put the new values into a new list
        new_frame_list = []
        for frame in frame_list:
            # Load the histories into some strategy objects
            player_one.history = frame.player_one_history
            player_two.history = frame.player_two_history
            # Compute the next moves
            player_one_move = player_one.next_move(player_two.history)
            player_two_move = player_two.next_move(player_one.history)
            # Create a new frame with the no-mistake moves
            new_frame_list.append(HistoryFrame(player_one.history + [player_one_move],
                                               player_two.history + [player_two_move],
                                               frame.mistakes))
            # Make mistakes if we haven't made enough yet
            if frame.mistakes != max_mistakes:
                # Make one mistake
                new_frame_list.append(HistoryFrame(player_one.history + [player_one.opposite(player_one_move)],
                                                   player_two.history + [player_two_move],
                                                   frame.mistakes + 1))
                # Make the other mistake
                new_frame_list.append(HistoryFrame(player_one.history + [player_one_move],
                                                   player_two.history + [player_two.opposite(player_two_move)],
                                                   frame.mistakes + 1))
            # See if we can make two mistakes
            if frame.mistakes + 2 <= max_mistakes:
                # Add the frame to the list with both mistakes
                new_frame_list.append(HistoryFrame(player_one.history + [player_one.opposite(player_one_move)],
                                                   player_two.history + [player_two.opposite(player_two_move)],
                                                   frame.mistakes + 2))

        # Load the new frames into the old list
        frame_list = new_frame_list

    # Now we should have a list that contains all of the correct length games with upto the maximum number of mistakes
    # Now we loop through each case, compute the total payoff and multiply by the coefficient
    # Set up variables to hold the expected payoff
    player_one_expected_payoff = 0
    player_two_expected_payoff = 0
    # We want the game length portion of the coefficient, since this wont change
    game_length_coefficient = (continuation_probability ** (expected_rounds - 1)) * (1 - continuation_probability)

    for frame in frame_list:
        # Figure out the total payoff
        player_one_payoff = 0
        player_two_payoff = 0

        # Loop over the history, adding the payoff each time
        for player_one_move, player_two_move in zip(frame.player_one_history, frame.player_two_history):
            payoff = payoff_matrix.payoff(player_one_move, player_two_move)
            player_one_payoff += payoff[0]
            player_two_payoff += payoff[1]

        # Compute the coefficient for the number of mistakes
        mistake_coefficient = (mistake_probability ** (2 * expected_rounds - frame.mistakes)) * (1 - mistake_probability) ** frame.mistakes

        # Finally, multiply each player's payoff by the two coefficients and add to the total
        player_one_expected_payoff += player_one_payoff * game_length_coefficient * mistake_coefficient
        player_two_expected_payoff += player_two_payoff * game_length_coefficient * mistake_coefficient

    # Return the results
    return player_one_expected_payoff, player_two_expected_payoff
