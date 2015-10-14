"""
Contains functions used to simulate different scenarios involving the iterated prisoner's dilemma, but taking advantage
of multithreading
"""
from numpy.random import RandomState
from abc import abstractmethod
import numpy as np
from math import sqrt
from multiprocessing import Pool, cpu_count, Manager
from functools import partial
import argparse

TRIAL_INCREMENT = 1000
TRIALS = 1000


def simulate_payoff(strategy_one, strategy_two, payoff_matrix, continuation_probability,
                    mistake_probability=0., trials=1000, estimator_stdev=None):
    """
    Calculate the normalised payoff for each strategy in the iterated prisoner's dilemma

    This method calculates the normalised payoff for two strategies in the iterated prisoner's dilemma using a monte
    carlo method. The prisoner's dilemma is played for a random number of rounds (as determined by the continuation
    probability). The number of trials performed is either passed as a parameter or alternatively we generate enough
    trials so that we can guarantee that the standard deviation of the normalised payoff is within the passed bound.
    In order to facilitate efficient multiprocessing:
        * If we are given a set number of trials, we simply split up the work evenly among the processes
        * If we are given a target standard deviation then we use the number of trials as a baseline, and then compute
            further trials in batches from there until we have the required standard deviation. This allows us to make
            efficient use of the processors.
    We then calculate the mean of tese trials to get our simulated normalised payoff

    Args:
        strategy_one (Strategy): The strategy to be tested
        strategy_two (Strategy): The other strategy
        payoff_matrix (PayoffMatrix): A payoff matrix representing the rewards for each set of actions
        continuation_probability (float): The probability of continuing the game
        mistake_probability (float): The probability of a single player making a single mistake in a single round
        trials (int): The number of games to simulate in order to calculate the normalised payoff
        estimator_stdev (float): The allowable deviation of our estimator.

    Returns:
        strategy_one_normalised_payoff, strategy_two_normalised_payoff: the normalised payoffs
    """
    strategy_one_payoffs = []
    strategy_two_payoffs = []

    # Set up a queue to store results
    m = Manager()
    q = m.Queue()

    # Split the trials into chunks for each process
    trial_chunks = [trials//cpu_count() for _ in range(cpu_count())]

    # Since all of the parameters remain the same across each process other than the number of trials, we create
    # a partial function with these values already prefilled, and map these onto the processes.
    partial_trials = partial(perform_multiple_trials, q=q, strategy_one=strategy_one, strategy_two=strategy_two,
                             payoff_matrix=payoff_matrix,
                             continuation_probability=continuation_probability,
                             mistake_probability=mistake_probability)

    # We need to count the number of trials in order to compute the estimator stdev
    number_of_trials = 0

    while True:
        # Get a pool of workers
        with Pool() as pool:
            # Get the workers to do the work. The results are placed into a queue as lists
            pool.map(partial_trials, trial_chunks)

            # Get the lists from the queue
            for i in range(cpu_count()):
                # Update the number of trials. Might as well do it when we're already looping
                number_of_trials += trial_chunks[i]
                # Get the trial list
                trial_list = q.get()
                # Split each trial into the first and second strategy payoffs
                for trial in trial_list:
                    strategy_one_payoffs.append(trial[0])
                    strategy_two_payoffs.append(trial[1])

            # If we didn't pass a target stdev for the estimator then we've done all the trials we need
            if estimator_stdev is None:
                break

            # If we have passed an estimator stdev target
            else:
                # Compute the sample standard deviation for both players
                strategy_one_stdev = np.array(strategy_one_payoffs).std()
                strategy_two_stdev = np.array(strategy_two_payoffs).std()
                # Divide these by the sqrt of the number of trials
                strategy_one_stdev /= sqrt(number_of_trials)
                strategy_two_stdev /= sqrt(number_of_trials)
                # If both are below threshold, break
                if strategy_one_stdev < estimator_stdev and strategy_two_stdev < estimator_stdev:
                    break
                else:
                    # Otherwise, recompute the trial chunk lists. This effectively queues some more trials for when
                    # we go through the look again.
                    trial_chunks = [TRIAL_INCREMENT//cpu_count() for _ in range(cpu_count())]

    strategy_one_normalised_payoff = np.array(strategy_one_payoffs).mean() * (1 - continuation_probability)
    strategy_two_normalised_payoff = np.array(strategy_two_payoffs).mean() * (1 - continuation_probability)
    return strategy_one_normalised_payoff, strategy_two_normalised_payoff


def perform_multiple_trials(n, q, strategy_one, strategy_two, payoff_matrix, continuation_probability, mistake_probability):
    # Create an PRNG instance. This instance will take a random seed. This is good because we don't want all instances
    # using the same seed and then creating the same data.
    random_instance = RandomState()

    # Create the players with the movesets from the payoff matrix
    player_one = strategy_one(C=payoff_matrix.C, D=payoff_matrix.D)
    player_two = strategy_two(C=payoff_matrix.C, D=payoff_matrix.D)

    trial_list = []

    for _ in range(n):
        # Perform the trials and add them to the list
        trial_list.append(perform_trial(player_one, player_two, payoff_matrix, continuation_probability, random_instance, mistake_probability))

    # When we've compute all of the trials in this chunk, put the results in the result queue so that the main process
    # can aggregate them.
    q.put(trial_list)


def perform_trial(player_one, player_two, payoff_matrix, continuation_probability, random_instance,
                  mistake_probability=0.):
    """
    Perform one game of the iterated prisoners dilemma and return the payoff for each player

    This simulates the game between two players, recording the total payoff. We keep simulating the game until the
    random value we pick is above the continuation probability.

    Args:
        player_one (Strategy): The first player
        player_two (Strategy): The second player
        payoff_matrix (PayoffMatrix): The payoff matrix representing the reward for each action
        continuation_probability (float): The probability of continuing each game
        random_instance (RandomState): A random state instance with which to generate random numbers
        mistake_probability (float): Probability of a single player making a single mistake in a round, default is 0

    Returns:
        player_one_payoff, player_two_payoff: The payoffs of each player
    """
    # Set up the total payoffs
    player_one_payoff = 0.
    player_two_payoff = 0.

    # Set up the continuation variable
    cont = True

    # Reset the strategy objects
    player_one.reset()
    player_two.reset()

    while cont:
        player_one_move = player_one.next_move(player_two.history)
        player_two_move = player_two.next_move(player_one.history)

        # Check for mistake in player one
        if random_instance.random_sample() < mistake_probability:
            player_one_move = player_one.opposite(player_one_move)

        # Check for mistake in player two
        if random_instance.random_sample() < mistake_probability:
            player_two_move = player_two.opposite(player_two_move)

        # Calculate payoffs and add them to the total
        payoff_one, payoff_two = payoff_matrix.payoff(player_one=player_one_move, player_two=player_two_move)
        player_one_payoff += payoff_one
        player_two_payoff += payoff_two

        # Update the histories of the strategies
        player_one.history += player_one_move
        player_two.history += player_two_move

        # Figure out whether we should continue or not
        if random_instance.random_sample() > continuation_probability:
            cont = False

    return player_one_payoff, player_two_payoff


"""
Contains classes that can be used to model strategies in the repeated prisoner's dilemma.

All strategies should inherit from the Strategy abstract base class to make use of common functions like validation
of histories and possibly other functions down the track
"""


class InvalidActionError(BaseException):
    pass


class HistoryLengthMismatch(BaseException):
    pass


class Strategy():
    def __init__(self, C='C', D='D'):
        """
        Initialise the strategy's history to empty and define the symbols used to represent cooperation and defection

        Args:
            C (string): The symbol to be used for representing cooperation. Defaults to 'C'.
            D (string): The symbol to be used for representing defection. Defaults to 'D'.
        """
        self.C = C
        self.D = D
        self.history = []

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, new_history):
        if set(new_history) <= {self.C, self.D}:
            self.reset()
            self._history = new_history
        else:
            raise InvalidActionError("New history \n" + str(new_history) + "\n does not match the current " +
                                     "characterset\nC = " + str(self.C) + ", D = " + str(self.D))

    def next_move(self, opponent_history):
        """
        This method validates the history string and then gets the next move of the strategy.

        Args:
            opponent_history (iterable): An iterable representing the the history of the oppoentn's moves

        Raises:
            InvalidActionError: Raised if any of the items in the opponent_history do not match either self.C or
                self.D
            HistoryLengthMismatch: Raised if opponent_history is not of the same length as self.history. The reasoning
                here is that if the opponent_history is shorter than our history, something probably went wrong since
                the caller could just use this.history. If the opponent_history is longer than our history, the query
                doesn't really make sense for the opponent because their moves should be dependant on what we do, and
                it appears that they've already decided what to do.

        Returns:
            action: The action taken by the strategy, either a C or a D
        """
        if not set(opponent_history) <= set([self.C, self.D]):
            raise InvalidActionError("Action must be either " + str(self.C) + " or " + str(self.D))

        if len(opponent_history) != len(self.history):
            raise HistoryLengthMismatch("Internal history was of length " + str(len(self.history)) + " and opponent" +
                                        " history was of length " + str(len(opponent_history)))

        action = self._strategy(opponent_history)
        return action

    @abstractmethod
    def _strategy(self, opponent_history):
        """
        This method should be implemented by child classes and should contain logic for computing the next move

        This method should not peform any update of internal state or history
        """

    def opposite(self, move):
        """
        Returns the opposite move to the one given, in the context of this strategy's characterset

        Args:
            move: The move to reverse

        Returns:
            opposite; The opposite move to the one passed
        """
        if move not in [self.C, self.D]:
            raise InvalidActionError("Action must be either " + str(self.C) + " or " + str(self.D))
        else:
            if move == self.D:
                return self.C
            else:
                return self.D

    def reset(self):
        """
        This method resets the state of the strategy to an empty history

        Any children of this class that use extra instance variables should override this method and reset instance
        variable as necessary
        """
        self._history = []


class AllC(Strategy):
    """
    A class implementing the AllC strategy that always cooperates
    """
    def _strategy(self, opponent_history):
        """
        This strategy always returns a C regardless of the opponent's move

        Returns:
            C
        """
        return self.C


class AllD(Strategy):
    """
    A class implementing the AllD strategy that always defects
    """
    def _strategy(self, opponent_history):
        """
        This strategy always returns a D regardless of the opponent's move

        Returns:
            D
        """
        return self.D


class TitForTat(Strategy):
    """
    A class implementing the tit for tat strategy. This strategy cooperates in the first round and the copies the
    opponent thereafter
    """
    def _strategy(self, opponent_history):
        if len(self.history) == 0:
            return self.C
        else:
            if opponent_history[-1] == self.C:
                return self.C
            else:
                return self.D


class InverseTitForTat(Strategy):
    """
    A class implementing the inverse tit for tat strategy. This strategy cooperates in the first round and then does
    the opposite of the opponent's last move thereafter
    """
    def _strategy(self, opponent_history):
        if len(self.history) == 0:
            return self.C
        else:
            if opponent_history[-1] == self.C:
                return self.D
            else:
                return self.C


class SuspiciousTitForTat(Strategy):
    """
    A class implementing the suspicious tit for tat strategy. This strategy defects in the first round, then copies
    the opponent thereafter
    """
    def _strategy(self, opponent_history):
        if len(self.history) == 0:
            return self.D
        else:
            if opponent_history[-1] == self.C:
                return self.C
            else:
                return self.D


class SuspiciousInverseTitForTat(Strategy):
    """
    A class implementing the suspicious inverse tit for tat strategy. This strategy defects in the first round and
    then does the opposite of the opponent's last move thereafter
    """
    def _strategy(self, opponent_history):
        if len(self.history) == 0:
            return self.D
        else:
            if opponent_history[-1] == self.C:
                return self.D
            else:
                return self.C


class NiceAllD(Strategy):
    """
    A class implementing the nice alld strategy. This strategy cooperates in the first round and then defects for all
    other rounds.
    """
    def _strategy(self, opponent_history):
        if len(self.history) == 0:
            return self.C
        else:
            return self.D


class SuspiciousAllC(Strategy):
    """
    A class implementing the suspicious allc strategy. This strategy defects in the first round and the cooperates
    for all other rounds.
    """
    def _strategy(self, opponent_history):
        if len(self.history) == 0:
            return self.D
        else:
            return self.C


class Grim(Strategy):
    """
    A class implementing the Grim strategy. This strategy cooperates until the first defection, the defects forever.
    """
    def _strategy(self, opponent_history):
        # Check whether the opponent has defected
        if self.D in opponent_history:
            return self.D
        else:
            return self.C


class WSLS(Strategy):
    """
    A class implementing the Win Stay Lose Shift strategy. If the result is a CC or a DC, they will stay with their
    current move. If it's a DD or a CD they will shift to the other move.
    """
    def _strategy(self, opponent_history):
        # Cooperate in the first round
        if len(self.history) == 0:
            return self.C
        else:
            # Enumerate the possibilities
            if self.history[-1] == self.C:
                if opponent_history[-1] == self.C:
                    # Win, so stay
                    return self.C
                else:
                    # Lose, so shift
                    return self.D
            # We played a D
            else:
                if opponent_history[-1] == self.C:
                    # Win, so stay
                    return self.D
                else:
                    # Lose, so shift
                    return self.C


class TFNT(Strategy):
    """
    A class that implements the Tit for N Tats strategy. If there is a C in the last n rounds, else defect.

    Args:
        n (int): The number of rounds to check for a cooperation
    """
    def __init__(self, C='C', D='D', n=2):
        Strategy.__init__(self, C, D)
        self.n = n

    def _strategy(self, opponent_history):
        # If the strategy's history is less than n, cooperate
        if len(self.history) < self.n:
            return self.C
        else:
            # Take a slice of the opponent's last history
            recent_history = opponent_history[-self.n:]

            # See if there is a C in the recent history
            if self.C in recent_history:
                return self.C
            else:
                return self.D

# Keep a list of all of the strategies
strategy_list = [AllC, AllD, TitForTat, InverseTitForTat, SuspiciousTitForTat, SuspiciousInverseTitForTat, NiceAllD,
                 SuspiciousAllC, Grim, WSLS, TFNT]


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
    def __init__(self, C='C', D='D', CC=(2, 2), CD=(0, 3), DC=(3, 0), DD=(1, 1)):
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
    def __init__(self, C='C', D='D', P=2.0, R=4.0, S=0.0, T=6.0):
        super().__init__(C=C, D=D, CC=(R, R), CD=(S, T), DC=(T, S), DD=(P, P))
        self.P = P
        self.T = T
        self.R = R
        self.S = S


def main(continuation_probability, mistake_probability):
    # Create an instance of the Payoff Matrix
    payoff_matrix = PrisonersDilemmaPayoff()

    # Create a file to output to
    with open("results_" + str(continuation_probability) + "_" + str(mistake_probability), "w") as file:

        # Print headers for the results
        print("Continuation probability: " + str(continuation_probability), file=file)
        print("Mistake probability: " + str(mistake_probability), file=file)
        print("strategyone,strategytwo,payoff", file=file)

        # Iterate through each pair of strategies
        for strategy_one in strategy_list:
            for strategy_two in strategy_list:
                # Compute the result
                result = simulate_payoff(strategy_one, strategy_two, payoff_matrix, continuation_probability,
                                         mistake_probability, trials=TRIALS)
                # Print the strategies and the results
                print(str(strategy_one) + "," + str(strategy_two) + "," + str(result), file=file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Add arguments for the continuation prob and the mistake prob
    parser.add_argument('cont_prob', help="Continuation probability", type=float)
    parser.add_argument('mistake_prob', help="Mistake probability", type=float)

    # Parse the arguments
    args = parser.parse_args()

    # Pass them to main
    main(args.cont_prob, args.mistake_prob)
