"""
Test that what we *think* should be the theoretical normalised payoff of a game between AllC and AllC with mistakes
against the value computed by simulations and the value computed by naive calculation
"""
from repeatedmistakes.strategies import AllC
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from repeatedmistakes.simulations import simulate_payoff
from repeatedmistakes.calculations import calculate_payoff_with_mistakes

from time import time

def compute_values():
    payoff_matrix = PrisonersDilemmaPayoff()
    delta = 0.9
    mu = 0.

    sim_time = time()
    sim = simulate_payoff(AllC, AllC, payoff_matrix, delta, mistake_probability=mu, estimator_stdev=0.1)
    sim_time = time() - sim_time

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

    calc_naive_time = time()
    calc_naive = calculate_payoff_with_mistakes(AllC, AllC, payoff_matrix, delta, mu, 0.000000001, 'naive')
    calc_naive_time = time() - calc_naive_time

    print("Calculated value (simplified) = " + str(calc_simple))
    print("Time taken " + str(calc_simple_time))
    print("Calculated value (naive) = " + str(calc_naive))
    print("Time taken " + str(calc_naive_time))
    print("Simulated value = " + str(sim))
    print("Time taken " + str(sim_time))

if __name__ == '__main__':
    compute_values()
