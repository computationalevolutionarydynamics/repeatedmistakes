from hypothesis import given, assume
from hypothesis.strategies import text, just, integers, tuples
from inspect import isclass, isabstract
import nose
from nose.tools import raises

import repeatedmistakes.strategies as strategies
"""
Test all of the strategies in the strategies module for common functionality
"""
# First we will define a strategy which gives us strings of length two. This will enable use to test the strategies
# across all inputs for C and D
two_characters = text(min_size=2, max_size=2)

# Next we need a strategy which will produce two texts with the same characterset and of the same length, but with
# random lengths. We generate this as a tuple with the first element being the characterset and the second and third
# elements being the generated histories
valid_history_strategy = two_characters.flatmap(
                        lambda chars: integers(min_value=0).flatmap(
                            lambda n: tuples(just(chars), text(alphabet=chars, min_size=n, max_size=n),
                                       text(alphabet=chars, min_size=n, max_size=n)
                                       )
                        )
                    )

for strategy in strategies.strategy_list:
    @given(valid_history_strategy)
    def test_strategy_passedCharactersetAndHistories_returnsCharacterInCharacterset(s):
        """Test that if we pass a characterset and histories to a strategy, it only returns actions in that characterset"""
        characterset = s[0]
        history = s[1]
        opponent_history = s[2]
        # Create an object with the correct characterset
        test_object = strategy(C=characterset[0], D=characterset[1])
        # Set up the object's history
        test_object.history = history
        # Assert that the returned action is still in the characterset
        assert test_object.next_move(opponent_history) in characterset

# We want to define a strategy that will give us two random length text strings from the same characterset
# We also want to remove cases where the lengths are the same
length_mistmatch_strategy = two_characters.flatmap(
                                lambda chars: tuples(just(chars), text(alphabet=chars), text(alphabet=chars))
                            )

for strategy in strategies.strategy_list:
    @given(length_mistmatch_strategy)
    @raises(strategies.HistoryLengthMismatch)
    def test_strategy_historyLengthMismatch_raisesHistoryLengthMistmatchException(s):
        """Test that if the history length doesn't match the opponent history length, an exception is raised"""
        # Assume that the lengths of the strings are not the same
        assume(not len(s[1]) == len(s[2]))
        characterset = s[0]
        history = s[1]
        opponent_history = s[2]
        # Create an object with the correct characterset
        test_object = strategy(C=characterset[0], D=characterset[1])
        # Set up the object's history
        test_object.history = history
        # Try and get the next move which should raise an error
        test_object.next_move(opponent_history)

if __name__ == '__main__':
    nose.main()
