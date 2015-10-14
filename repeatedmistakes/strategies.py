"""
Contains classes that can be used to model strategies in the repeated prisoner's dilemma.

All strategies should inherit from the Strategy abstract base class to make use of common functions like validation
of histories and possibly other functions down the track
"""
from abc import abstractmethod


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
        if len(self.history == 0):
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
    def __init__(self, n):
        super().__init__(self)
        self.n = n

    def _strategy(self, opponent_history):
        # Take a slice of the opponent's last history
        recent_history = opponent_history[-self.n:]

        # See if there is a C in the recent history
        if self.C in recent_history:
            return self.C
        else:
            return self.D

# Keep a list of all of the strategies
strategy_list = [AllC, AllD, TitForTat, InverseTitForTat, SuspiciousTitForTat, SuspiciousInverseTitForTat, NiceAllD,
                 SuspiciousAllC, Grim, WSLS]
