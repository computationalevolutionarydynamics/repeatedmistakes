"""
Test that what we *think* should be the theoretical normalised payoff of a game between AllC and AllC with mistakes
against the value computed by simulations
"""
from repeatedmistakes.strategies import AllC
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff

from repeatedmistakes.simulations import simulate_normalised_payoff

def compute_values():
    payoff_matrix = PrisonersDilemmaPayoff()
    delta = 0.8
    mu = 0.1
    sim = simulate_normalised_payoff(AllC, AllC, payoff_matrix, delta, mistake_probability=mu, trials=10000)
    calc = 0.
    for i in range(0, 100):
        calc += (delta ** i) * ((mu * mu * payoff_matrix.DD) + ((mu * (1 - mu) * payoff_matrix.CD)) +
                               ((mu * (1 - mu)) * payoff_matrix.DC) + ((1 - mu) * (1 - mu) * payoff_matrix.CC))

    print("Calculated value = " + str(calc))
    print("Simulated value = " + str(sim))

if __name__ == '__main__':
    compute_values()
