"""
Test that what we *think* should be the theoretical normalised payoff of a game between AllC and AllC with mistakes
against the value computed by simulations
"""
from repeatedmistakes.strategies import AllC
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from repeatedmistakes.simulations import simulate_normalised_payoff

def compute_values():
    payoff_matrix = PrisonersDilemmaPayoff()
    delta = 0.9
    mu = 0.05
    sim = simulate_normalised_payoff(AllC, AllC, payoff_matrix, delta, mistake_probability=mu, estimator_stdev=0.2)
    calc = [0., 0.]
    no_mistake = [0., 0.]
    one_mistake = [0., 0.]
    two_mistakes = [0., 0.]
    for i in range(0, 10000):
        for k in [0, 1]:
            no_mistake[k] = ((1 - mu) ** 2) * (payoff_matrix.CC)[k]
            two_mistakes[k] =  (mu ** 2) * (payoff_matrix.DD)[k]
            one_mistake[k] = (mu * (1 - mu)) * ((payoff_matrix.CD)[k] + (payoff_matrix.DC)[k])
            calc[k] += (delta ** i) * (no_mistake[k] + one_mistake[k] + two_mistakes[k])

    calc[0] *= (1 - delta)
    calc[1] *= (1 - delta)

    print("Calculated value = " + str(calc))
    print("Simulated value = " + str(sim))

if __name__ == '__main__':
    compute_values()
