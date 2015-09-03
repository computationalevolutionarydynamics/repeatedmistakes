from repeatedmistakes.simulations import simulate_payoff
from repeatedmistakes.calculations import calculate_payoff
from repeatedmistakes.tests.test_calculations import strategy_combinations
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

import time
"""
Here we want to test the simulations against the numerical calculations. We will reuse the sets of strategy pairs from
the tests for the calculations
"""
# The global epsilon for trunacting the calculation sum
EPSILON = 0.001
# The tolerance allowed between the simulations and the calculations
TOLERANCE = 0.1
# The continuation probability
DELTA = 0.8

def comparison_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations():
    """This tests that the results returned by the simulations match the results of the calculations."""
    # Construct the payoff matrix
    payoff_matrix = PrisonersDilemmaPayoff()
    for combo in strategy_combinations:
        # Pull out each strategy
        strategy_one = combo[0]
        strategy_two = combo[1]
        # Get the result from the calcs
        calculation_result, _ = calculate_payoff(strategy_one, strategy_two, payoff_matrix, DELTA, EPSILON)
        # Get the result from the sims
        simulation_result, _ = simulate_payoff(strategy_one, strategy_two, payoff_matrix, DELTA, trials = 1000)
        # Compare them
        if abs(simulation_result) > TOLERANCE:
            diff = abs(simulation_result - calculation_result) / abs(calculation_result)
            if diff <= TOLERANCE:
                report_success()
            else:
                report_failure(combo, payoff_matrix, DELTA, diff)
        else:
            diff = abs(simulation_result - calculation_result)
            if diff <= TOLERANCE:
                report_success()
            else:
                report_failure(combo, payoff_matrix, DELTA, diff)

def report_success():
    """Report a successful test"""
    print(".", end="")

def report_failure(combo, payoff_matrix, delta, diff):
    """Report when the difference between simulation is outside tolerance"""
    print("\nFailed")
    print("Strategies: " + str(combo[0]) + " " + str(combo[1]))
    print("Payoff matrix: " + str(payoff_matrix))
    print("Delta: " + str(delta))
    print("Difference was " + str(diff))

if __name__ == '__main__':
    t1 = time.time()
    comparison_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations()
    t2 = time.time()
    print("\nTime taken was " + str(t2-t1) + "s")
