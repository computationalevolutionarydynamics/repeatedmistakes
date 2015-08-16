"""
Contains classes that can be used to model strategies in the repeated prisoner's dilemma.

All strategies should inherit from the Strategy abstract base class to make use of common functions like validation
of histories and possibly other functions down the track
"""
from abc import ABCMeta, abstractmethod

class InvalidActionError(BaseException):
    pass

class HistoryLengthMismatch(BaseException):
    pass

class Strategy:
    __metaclass__ = ABCMeta

    def __init__(self, C = 'C', D = 'D'):
        """
        Initialise the strategy's history to empty and define the symbols used to represent cooperation and defection

        Args:
            C (string): The symbol to be used for representing cooperation. Defaults to 'C'.
            D (string): The symbol to be used for representing defection. Defaults to 'D'.
        """
        self.history = []
        self.C = C
        self.D = D

    def play(self, opponent_history):
        """
        Computes the next move given the opponent's history and updates the strategy's history.

        This method performs checks on the opponent history it is given, and then computes what move the strategy makes
        next and updates the history of this strategy with this move. The default implementation has no internal state,
        however if any other state variables are used in child classes, these classes should call this method and return
        the result as well as updating any state variables as needed.

        Args:
            opponent_history (string): This should be an iterable representing the history of the opponent's moves in
                the format specified during construction. This should be the same length as the strategy's history.

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

        # Figure out the action
        action = self.next_move(opponent_history)
        self.history.append(action)

        return action

    @abstractmethod
    def next_move(self, opponent_history):
        """
        This method should be implemented by child classes. This method should contain all logic for determining what
        move the strategy should make, and should return this move. This method should not update the history or update
        internal state.
        """

    def reset(self):
        """
        This method resets the state of the strategy to an empty history

        Any children of this class that use extra instance variables should override this method and reset instance
        variable as necessary
        """
        self.history = []
