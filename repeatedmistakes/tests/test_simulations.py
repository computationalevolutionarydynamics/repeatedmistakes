from repeatedmistakes.simulations import simulate_normalised_payoff
from repeatedmistakes.calculations import calculate_normalised_payoff
from repeatedmistakes.tests.test_calculations import strategy_combinations
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from hypothesis import given
from hypothesis.strategies import floats, tuples, sampled_from
import nose

"""
Here we want to test the simulations against the numerical calculations. We will reuse the sets of strategy pairs from
the tests for the calculations
"""
# The global epsilon for trunacting the calculation sum
EPSILON = 0.0001
# The tolerance allowed between the simulations and the calculations
TOLERANCE = 0.1
# The number of trials of the simulations to run
TRIALS = 2000

small_float = floats(min_value=0, max_value=10)
delta = floats(min_value=0.01, max_value = 0.99)
@given(payoff_values=tuples(small_float, small_float, small_float, small_float),
       delta=delta,
       combo = sampled_from(strategy_combinations))
def test_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations(payoff_values, delta, combo):
    """This tests that the results returned by the simulations match the results of the calculations."""
    # Construct the payoff matrix
    payoff_matrix = PrisonersDilemmaPayoff(P = payoff_values[0], R = payoff_values[1],
                                           S = payoff_values[2], T = payoff_values[3])
    # Pull out each strategy
    strategy_one = combo[0]
    strategy_two = combo[1]
    # Get the result from the calcs
    calculation_result, _ = calculate_normalised_payoff(strategy_one, strategy_two, payoff_matrix, delta, EPSILON)
    # Get the result from the sims
    simulation_result, _ = simulate_normalised_payoff(strategy_one, strategy_two, payoff_matrix, delta, TRIALS)
    # Debug code
    print(combo)
    print(calculation_result)
    print(simulation_result)
    # Compare them
    if abs(simulation_result) > TOLERANCE:
        assert abs(simulation_result - calculation_result) / abs(calculation_result) <= TOLERANCE
    else:
        assert abs(simulation_result - calculation_result) <= TOLERANCE

if __name__ == '__main__':
    nose.main()
