from repeatedmistakes.simulations import simulate_normalised_payoff
from repeatedmistakes.calculations import calculate_normalised_payoff
from repeatedmistakes.tests.test_calculations import strategy_combinations
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from hypothesis import given
from hypothesis.strategies import floats, tuples, sampled_from

"""
Here we want to test the simulations against the numerical calculations. We will reuse the sets of strategy pairs from
the tests for the calculations
"""
# The global epsilon for trunacting the calculation sum
EPSILON = 0.0001
# The tolerance allowed between the simulations and the calculations
TOLERANCE = 0.1
# The number of trials of the simulations to run
TRIALS = 1000

small_float = floats(min_value=0, max_value=10)
delta = floats(min_value=0.01, max_value = 0.99)
@given(payoff_values=tuples(small_float, small_float, small_float, small_float),
       delta=delta,
       combo = sampled_from(strategy_combinations))
def comparison_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations(payoff_values, delta, combo):
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
    # Compare them
    if abs(simulation_result) > TOLERANCE:
        diff = abs(simulation_result - calculation_result) / abs(calculation_result)
        if diff <= TOLERANCE:
            report_success()
        else:
            report_failure(combo, payoff_values, delta, diff)
    else:
        diff = abs(simulation_result - calculation_result)
        if diff <= TOLERANCE:
            report_success()
        else:
            report_failure(combo, payoff_values, delta, diff)

def report_success():
    """Report a successful test"""
    print(".")

def report_failure(combo, payoff_matrix, delta, diff):
    """Report when the difference between simulation is outside tolerance"""
    print("Failed")
    print("Strategies: " + str(combo[0]) + " " + str(combo[1]))
    print("Payoff matrix: " + str(payoff_matrix))
    print("Delta: " + str(delta))
    print("Difference was " + str(diff))

if __name__ == '__main__':
    comparison_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations()
