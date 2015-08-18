"""
Contains classes that can be used to model strategies in the repeated prisoner's dilemma.

All strategies should inherit from the Strategy abstract base class to make use of common functions like validation
of histories and possibly other functions down the track
"""
from abc import ABC, abstractmethod

class InvalidActionError(BaseException):
    pass


class HistoryLengthMismatch(BaseException):
    pass


class Strategy(ABC):
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
            self._history = new_history
        else:
            raise InvalidActionError("New history \n" + str(new_history) + "\n does not match the current " +
                                     "characterset\nC = " + str(self.C) + ", D = " + str(self.D))

    def play(self, opponent_history):
        """
        Computes the next move given the opponent's history and updates the strategy's history.

        This base class does not contain any instance variables relating the the strategy other than the history.
        However if child classes need to store additional instance variables related to state, they should call this
        method and then update any state accordinly before returning the result to the caller.

        Args:
            opponent_history (iterable): An iterable representing the history of the opponent's moves.

        Returns:
            action: The action taken by the strategy, either a C or a D
        """
        # Figure out the action
        action = self.next_move(opponent_history)
        self.history.append(action)

        return action

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
        if not all([move in [self.C, self.D] for move in opponent_history]):
            raise InvalidActionError("Action must be either " + str(self.C) + " or " + str(self.D))

        if len(opponent_history) != len(self.history):
            raise HistoryLengthMismatch("Internal history was of length " + str(len(self.history)) + " and opponent" \
                                        + " history was of length " + str(len(opponent_history)))

        action = self._strategy(opponent_history)
        return action

    @abstractmethod
    def _strategy(self, opponent_history):
        """
        This method should be implemented by child classes and should contain logic for computing the next move

        This method should not peform any update of internal state or history
        """

    def reset(self):
        """
        This method resets the state of the strategy to an empty history

        Any children of this class that use extra instance variables should override this method and reset instance
        variable as necessary
        """
        self.history = []


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

# Keep a list of all of the strategies
strategy_list = [AllC]
