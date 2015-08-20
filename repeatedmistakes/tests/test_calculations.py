from repeatedmistakes.calculations import calculate_normalised_payoff
from repeatedmistakes.strategies import *
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from hypothesis import given, assume
from hypothesis.strategies import tuples, floats
import nose

from math import isnan, isfinite, isinf

"""
In order to test that our normalised payoff function is calculating the correct values, we will attempt to replicate
the results found in Garcia and Traulsen, "The Structure of Mutations and the Evolution of Cooperation", PLoS ONE 10(10)
http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0035287

In the Appendix section, exact forms of the normalised payoff are given for 64 permutations of 8 simple strategies.
These combinations of strategies show the following behaviours:
    * A single outcome for every round
    * Different behaviour in the first round, then the same for every other round
    * Different behaviour in the first two rounds, then the same for every other round
    * Cyclic behaviour with period two
    * Cyclic behaviour with period four

In order to test our calculation method, we will be using hypothesis to provide a range of payoff matrices and
continuation probabilities for each of these 36 combinations of strategies, and ensuring that the correct value is given
for each combination (within some level of tolerance because we must truncate the series at some point).
"""
# The global epsilon used to truncate small terms in the sum
EPSILON = 0.0001
# The global tolerance between expected and actual values
TOLERANCE = 0.01

# First, let's define some of the functions that will give the exact values of the combinations in particular
# scenarios
def first_round_distinct(first_round_payoff, other_rounds_payoff, continuation_probability):
    """This gives the normalised payoff where the first round is distinct, and the other rounds have the same result"""
    return first_round_payoff * (1 - continuation_probability) + other_rounds_payoff * continuation_probability

def first_two_rounds_distinct(first_round_payoff, second_round_payoff, other_rounds_payoff, continuation_probability):
    """This gives the normalised payoff when the first two rounds are distinct and the others have the same result"""
    return first_round_payoff * (1 - continuation_probability) +\
           second_round_payoff * (1 - continuation_probability) * continuation_probability +\
           other_rounds_payoff * (continuation_probability ** 2)

def two_action_cycle(first_action_payoff, second_action_payoff, continuation_probability):
    """This gives the normalised payoff when two actions repeat in a cycle"""
    return (first_action_payoff + second_action_payoff * continuation_probability) / (1 + continuation_probability)

def four_action_cycle(first_action_payoff, second_action_payoff, third_action_payoff, fourth_action_payoff,
                      continuation_probability):
    """This gives the normalised payoff when four actions repeat in a cycle"""
    return (first_action_payoff + second_action_payoff * continuation_probability +
            third_action_payoff * (continuation_probability ** 2) + fourth_action_payoff * (continuation_probability ** 3))/\
           (1 + continuation_probability + continuation_probability ** 2 + continuation_probability ** 3)

# Now that we've defined all of the exact value functions, we can start going through the matrix systematically
# We will start with all of the combinations that only yield a single result
single_result_combos = [(AllC, AllC),
                        (AllC, TitForTat),
                        (AllC, SuspiciousInverseTitForTat),
                        (AllC, AllD),
                        (TitForTat, AllC),
                        (TitForTat, TitForTat),
                        (InverseTitForTat, SuspiciousInverseTitForTat),
                        (InverseTitForTat, AllD),
                        (SuspiciousTitForTat, SuspiciousTitForTat),
                        (SuspiciousTitForTat, AllD),
                        (SuspiciousInverseTitForTat, AllC),
                        (SuspiciousInverseTitForTat, InverseTitForTat),
                        (AllD, AllC),
                        (AllD, InverseTitForTat),
                        (AllD, SuspiciousTitForTat),
                        (AllD, AllD)]

# And their corresponding expected values. Since we're pulling these from the payoff matrix, we're going to have to
# phrase them as lambda functions and then use each of them on the payoff matrix object
single_result_values = [lambda matrix, delta: matrix.R,
                        lambda matrix, delta: matrix.R,
                        lambda matrix, delta: matrix.S,
                        lambda matrix, delta: matrix.S,
                        lambda matrix, delta: matrix.R,
                        lambda matrix, delta: matrix.R,
                        lambda matrix, delta: matrix.S,
                        lambda matrix, delta: matrix.S,
                        lambda matrix, delta: matrix.P,
                        lambda matrix, delta: matrix.P,
                        lambda matrix, delta: matrix.T,
                        lambda matrix, delta: matrix.T,
                        lambda matrix, delta: matrix.T,
                        lambda matrix, delta: matrix.T,
                        lambda matrix, delta: matrix.P,
                        lambda matrix, delta: matrix.P
                        ]

# Now we will move on to testing the combinations that produce different behaviour in the first round, and then
# the same after that
round_one_different_combos = [(AllC, InverseTitForTat),
                              (AllC, NiceAllD),
                              (AllC, SuspiciousAllC),
                              (AllC, SuspiciousTitForTat),
                              (TitForTat, AllD),
                              (InverseTitForTat, AllC),
                              (NiceAllD, AllC),
                              (NiceAllD, NiceAllD),
                              (NiceAllD, SuspiciousAllC),
                              (NiceAllD, AllD),
                              (SuspiciousAllC, AllC),
                              (SuspiciousAllC, NiceAllD),
                              (SuspiciousAllC, SuspiciousAllC),
                              (SuspiciousAllC, AllD),
                              (SuspiciousTitForTat, AllC),
                              (SuspiciousInverseTitForTat, AllD),
                              (AllD, TitForTat),
                              (AllD, NiceAllD),
                              (AllD, SuspiciousAllC),
                              (AllD, SuspiciousInverseTitForTat)
                              ]

round_one_different_values = [lambda matrix, delta: first_round_distinct(matrix.R, matrix.S, delta),
                              lambda matrix, delta: first_round_distinct(matrix.R, matrix.S, delta),
                              lambda matrix, delta: first_round_distinct(matrix.S, matrix.R, delta),
                              lambda matrix, delta: first_round_distinct(matrix.S, matrix.R, delta),
                              lambda matrix, delta: first_round_distinct(matrix.S, matrix.P, delta),
                              lambda matrix, delta: first_round_distinct(matrix.R, matrix.T, delta),
                              lambda matrix, delta: first_round_distinct(matrix.R, matrix.T, delta),
                              lambda matrix, delta: first_round_distinct(matrix.R, matrix.P, delta),
                              lambda matrix, delta: first_round_distinct(matrix.S, matrix.T, delta),
                              lambda matrix, delta: first_round_distinct(matrix.S, matrix.P, delta),
                              lambda matrix, delta: first_round_distinct(matrix.T, matrix.R, delta),
                              lambda matrix, delta: first_round_distinct(matrix.T, matrix.S, delta),
                              lambda matrix, delta: first_round_distinct(matrix.P, matrix.R, delta),
                              lambda matrix, delta: first_round_distinct(matrix.P, matrix.S, delta),
                              lambda matrix, delta: first_round_distinct(matrix.T, matrix.R, delta),
                              lambda matrix, delta: first_round_distinct(matrix.P, matrix.S, delta),
                              lambda matrix, delta: first_round_distinct(matrix.T, matrix.P, delta),
                              lambda matrix, delta: first_round_distinct(matrix.T, matrix.P, delta),
                              lambda matrix, delta: first_round_distinct(matrix.P, matrix.T, delta),
                              lambda matrix, delta: first_round_distinct(matrix.P, matrix.T, delta),
                              ]

strategy_combinations = single_result_combos + round_one_different_combos
results_list = single_result_values + round_one_different_values

small_float = floats(min_value=0, max_value=1e4)
# We need to provide each one with four random values for the payoff matrix and a continuation probability
@given(payoff_values=tuples(small_float, small_float, small_float, small_float), delta=floats(min_value=0.01, max_value=0.99))
def test_calculations_singleResultCombosGiven_ExpectedResultReturned(payoff_values, delta):
    """Test that single result combinations produce the correct expected values"""
    # We need to assume a few things, namely, that the floats are not infinities or nans
    for value in payoff_values:
        assume(not isnan(value))
    # Finally, the test. We need to iterate over each of the result combos
    for index, combo in enumerate(strategy_combinations):
        # Construct the payoff matrix
        payoff_matrix = PrisonersDilemmaPayoff(P=payoff_values[0], R=payoff_values[1],
                                               S=payoff_values[2], T=payoff_values[3])
        first_strategy = combo[0]
        second_strategy = combo[1]
        # Get the expected result
        expected_result = results_list[index](payoff_matrix, delta)
        # Compute the result (throw away the result for the other strategy)
        actual_result, _ = calculate_normalised_payoff(first_strategy, second_strategy, payoff_matrix, delta, EPSILON)
        # See if they match, within a percentage of tolerance. If the expected result is very small just use the
        # difference itself
        print(index)
        print(strategy_combinations[index])
        print(payoff_values)
        print(expected_result)
        print(actual_result)
        if abs(expected_result) > TOLERANCE:
            assert abs(expected_result - actual_result) / abs(expected_result) <= TOLERANCE
        else:
            assert abs(expected_result - actual_result) <= TOLERANCE

if __name__ == '__main__':
    nose.main()
