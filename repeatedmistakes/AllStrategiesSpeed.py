"""
Test different methods of finding the expected payoff
"""
from repeatedmistakes.tests.test_calculations import strategy_combinations
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from repeatedmistakes.simulations_multiprocessed import simulate_payoff as mult_simulate_payoff
from repeatedmistakes.calculations import calculate_payoff_with_mistakes
from repeatedmistakes.calculations_multiprocessed import calculate_payoff_with_mistakes as mult_calculate_payoff

from time import time

def compute_values():
    payoff_matrix = PrisonersDilemmaPayoff()
    delta = 0.9
    mu = 0.0005

    for pair in strategy_combinations:
        print("Strategy one: " + str(pair[0]))
        print("Strategy two: " + str(pair[1]))
        print()

        mult_sim_time = time()
        mult_sim = mult_simulate_payoff(pair[0], pair[1], payoff_matrix, delta, mistake_probability=mu, estimator_stdev=0.2)
        mult_sim_time = time() - mult_sim_time

        print("Multiprocessed simulated value = " + str(mult_sim))
        print("Time taken " + str(mult_sim_time))

        calc_naive_time = time()
        calc_naive = calculate_payoff_with_mistakes(pair[0], pair[1], payoff_matrix, delta, mu, 1e-5, 'naive')
        calc_naive_time = time() - calc_naive_time

        print("Calculated value (naive) = " + str(calc_naive))
        print("Time taken " + str(calc_naive_time))

        mult_calc_naive_time = time()
        mult_calc_naive = mult_calculate_payoff(pair[0], pair[1], payoff_matrix, delta, mu, 1e-5, 'naive')
        mult_calc_naive_time = time() - mult_calc_naive_time

        print("Multiprocessed calculated value (naive) = " + str(mult_calc_naive))
        print("Time taken " + str(mult_calc_naive_time))
        print()

if __name__ == '__main__':
    compute_values()