from repeatedmistakes.simulations import simulate_payoff
from repeatedmistakes.calculations import calculate_payoff
from repeatedmistakes.strategies import InvalidActionError

class RepeatedGame:
    """
    A class for modelling a repeated game between two players, with functions for simulation and calculation of results
    """
    def __init__(self, strategy_one, strategy_two, C='C', D='D'):
        """
        Initialise the object with two strategies and a characterset
        """
        self.strategy_one = strategy_one
        self.strategy_two = strategy_two
        self.C = C
        self.D = D

    def simulate(self, rounds):
        """
        Simulate a repeated game between the two strategys for the given number of rounds and return the result

        Args:
            rounds (int): The number of rounds to simulate the two strategies playing against each other

        Returns:
            results (dict): A dictionary where the key is the strategy and the value is the list of moves it played
        """
        # Set up the two strategies
        player_one = self.strategy_one(C=self.C, D=self.D)
        player_two = self.strategy_two(C=self.C, D=self.D)
        # For each round
        for _ in range(rounds):
            # Figure out what move each strategy makes by passing each other the other player's history
            move_one = player_one.next_move(player_two.history)
            move_two = player_two.next_move(player_one.history)
            # Update the histories of each player
            player_one.history += move_one
            player_two.history += move_two

        # Construct the result dictionary
        results = {self.strategy_one: player_one.history, self.strategy_two: player_two.history}
        return results

    def simulate_normalised_payoff(self, payoff_matrix, continuation_probability, trials=1000, seed=1234):
        """
        Compute the normalised payoff of each strategy using a monte carlo method.

        Args:
            As per simulations.simulate_normalised_payoff

        Returns:
            As per simulations.simulate_normalised_payoff
        """
        return simulate_payoff(self.strategy_one, self.strategy_two, payoff_matrix,
                                          continuation_probability, trials, seed)

    def calculate_normalised_payoff(self, payoff_matrix, continuation_probability, epsilon):
        """
        Compute the normalised payoff of each strategy using an iterated sum that stops at some epsilon

        Args:
            As per calculations.calculate_normalised_payoff

        Returns;
            As per calculations.calculate_normalised_payoff
        """
        return calculate_payoff(self.strategy_one, self.strategy_two, payoff_matrix,
                                           continuation_probability, epsilon)


class PayoffMatrix:
    """
    A class that gives the payoffs for a round of the iterated prisoner's dilemma

    Vars:
        C (str): The symbol that represents cooperation
        D (str): The symbol that represents defection
        CC (float): The payoffs for each player if they both cooperate
        CD (float): The payoffs for each player if player one cooperates and the other defects
        DC (float): The payoffs for each player if player one defects and the other cooperates
        DD (float): The payoffs for each player if both players defect
    """
    def __init__(self, C='C', D='D', CC=(2,2), CD=(0,3), DC=(3,0), DD=(1,1)):
        self.C = C
        self.D = D
        self.CC = CC
        self.DD = DD
        self.CD = CD
        self.DC = DC

    def payoff(self, player_one, player_two):
        if player_one == self.C:
            if player_two == self.C:
                return self.CC
            elif player_two == self.D:
                return self.CD
        elif player_one == self.D:
            if player_two == self.C:
                return self.DC
            elif player_two == self.D:
                return self.DD
        else:
            raise InvalidActionError("Moves not in the characterset of this payoff matrix were passed.")

    def max(self):
        """
        Compute the maximum possible payoff for any player

        This is used in calculations to truncate the series once the maximum possible term is too small.
        """
        return max(max(self.CC, self.DD, self.DC, self.CD))


class PrisonersDilemmaPayoff(PayoffMatrix):
    """
    A class that models the payoff structure of the prisoner's dilemma

    Vars:
        C (str): As PayoffMatrix
        D (str): As PayoffMatrix
        P (float): The punishment both players receive if they defect
        R (float): The reward both players receive if they cooperate
        T (float): The temptation the defector receives if the other player cooperates
        S (float): The sucker prize the cooperator receives if the other player defects
    """
    def __init__(self, C='C', D='D', P=1, R=2, S=0, T=3):
        super().__init__(C=C, D=D, CC=(R,R), CD=(S,T), DC=(T,S), DD=(P,P))
        self.P = P
        self.T = T
        self.R = R
        self.S = S
