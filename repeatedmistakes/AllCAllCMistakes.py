"""
Test that what we *think* should be the theoretical normalised payoff of a game between AllC and AllC with mistakes
against the value computed by simulations and the value computed by naive calculation
"""
from repeatedmistakes.strategies import AllC
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from repeatedmistakes.simulations import simulate_payoff
from repeatedmistakes.simulations_multiprocessed import simulate_payoff as mult_simulate_payoff
from repeatedmistakes.calculations import calculate_payoff_with_mistakes
from repeatedmistakes.calculations_multiprocessed import calculate_payoff_with_mistakes as mult_calculate_payoff
from repeatedmistakes.expected_only import expected_only

from time import time

def compute_values():
    payoff_matrix = PrisonersDilemmaPayoff()
    delta = 0.9
    mu = 0.0005

    sim_time = time()
    sim = simulate_payoff(AllC, AllC, payoff_matrix, delta, mistake_probability=mu, estimator_stdev=0.4)
    sim_time = time() - sim_time

    print("Simulated value = " + str(sim))
    print("Time taken " + str(sim_time))

    mult_sim_time = time()
    mult_sim = mult_simulate_payoff(AllC, AllC, payoff_matrix, delta, mistake_probability=mu, estimator_stdev=0.4)
    mult_sim_time = time() - mult_sim_time

    print("Multiprocessed simulated value = " + str(mult_sim))
    print("Time taken " + str(mult_sim_time))

    calc_simple_time = time()
    calc_simple = [0., 0.]
    no_mistake = [0., 0.]
    one_mistake = [0., 0.]
    two_mistakes = [0., 0.]
    for i in range(0, 100000):
        for k in [0, 1]:
            no_mistake[k] = ((1 - mu) ** 2) * (payoff_matrix.CC)[k]
            two_mistakes[k] =  (mu ** 2) * (payoff_matrix.DD)[k]
            one_mistake[k] = (mu * (1 - mu)) * ((payoff_matrix.CD)[k] + (payoff_matrix.DC)[k])
            calc_simple[k] += (delta ** i) * (no_mistake[k] + one_mistake[k] + two_mistakes[k])

    calc_simple[0] *= (1 - delta)
    calc_simple[1] *= (1 - delta)
    calc_simple_time = time() - calc_simple_time

    print("Calculated value (simplified) = " + str(calc_simple))
    print("Time taken " + str(calc_simple_time))

    calc_naive_time = time()
    calc_naive = calculate_payoff_with_mistakes(AllC, AllC, payoff_matrix, delta, mu, 1e-5)
    calc_naive_time = time() - calc_naive_time

    print("Calculated value (naive) = " + str(calc_naive))
    print("Time taken " + str(calc_naive_time))

    mult_calc_naive_time = time()
    mult_calc_naive = mult_calculate_payoff(AllC, AllC, payoff_matrix, delta, mu, 1e-5)
    mult_calc_naive_time = time() - mult_calc_naive_time

    print("Multiprocessed calculated value (naive) = " + str(mult_calc_naive))
    print("Time taken " + str(mult_calc_naive_time))

    expected_only_time = time()
    expected_only_value = expected_only(AllC, AllC, payoff_matrix, delta, mu, 1e-5)
    expected_only_time = time() - expected_only_time

    print("Expected value only calculated value = " + str(expected_only_value))
    print("Time taken " + str(expected_only_time))

if __name__ == '__main__':
    compute_values()
