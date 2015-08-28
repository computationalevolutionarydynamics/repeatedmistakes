__author__ = 'juliangarcia'
from repeatedmistakes import strategies
from repeatedmistakes import repeatedgame
from repeatedmistakes.simulations import  simulate_normalised_payoff
from repeatedmistakes.calculations import calculate_normalised_payoff


def main():
    pd  = repeatedgame.PrisonersDilemmaPayoff()
    strategy1 = strategies.SuspiciousTitForTat()
    strategy2 = strategies.TitForTat()
    simulated_value  = simulate_normalised_payoff(strategies.SuspiciousTitForTat, strategies.TitForTat, pd, continuation_probability=0.9, trials=1000, seed=1234)
    print("The simulated value is {} ".format(simulated_value))
    approximated_value = calculate_normalised_payoff(strategies.SuspiciousTitForTat, strategies.TitForTat, pd, continuation_probability=0.9, epsilon=0.001)
    print("The approximated value is {} ".format(approximated_value))



if __name__ == '__main__':
    main()