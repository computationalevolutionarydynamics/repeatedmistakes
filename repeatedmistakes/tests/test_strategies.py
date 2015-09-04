from hypothesis import given, assume
from hypothesis.strategies import text, just, integers, tuples, sampled_from
import nose
from nose.tools import raises

from repeatedmistakes.strategies import *
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

@given(history = valid_history_strategy, strategy = sampled_from(strategy_list))
def test_strategy_passedCharactersetAndHistories_returnsCharacterInCharacterset(history, strategy):
    """Test that if we pass a characterset and histories to a strategy, it only returns actions in that characterset"""
    characterset = history[0]
    strat_history = list(history[1])
    opponent_history = list(history[2])
    # Create an object with the correct characterset
    test_object = strategy(C=characterset[0], D=characterset[1])
    # Set up the object's history
    test_object.history = strat_history
    # Assert that the returned action is still in the characterset
    assert test_object.next_move(opponent_history) in characterset

# We want to define a strategy that will give us two random length text strings from the same characterset
# We also want to remove cases where the lengths are the same
length_mistmatch_strategy = two_characters.flatmap(
                                lambda chars: tuples(just(chars), text(alphabet=chars), text(alphabet=chars))
                            )

@raises(HistoryLengthMismatch)
@given(history = length_mistmatch_strategy, strategy = sampled_from(strategy_list))
def test_strategy_historyLengthMismatch_raisesHistoryLengthMistmatchException(history, strategy):
    """Test that if the history length doesn't match the opponent history length, an exception is raised"""
    characterset = history[0]
    strat_history = history[1]
    opponent_history = history[2]
    # Assume that the lengths of the histories are not the same
    assume(not len(history) == len(opponent_history))
    # Create an object with the correct characterset
    test_object = strategy(C=characterset[0], D=characterset[1])
    # Set up the object's history
    test_object.history = strat_history
    # Try and get the next move which should raise an error
    test_object.next_move(opponent_history)

# We also want to test that if we pass an opponent history with invalid characters that an error is thrown
# Define a strategy that will generate one random text with one characterset and another with a different characterset
different_characterset_strategy = two_characters.flatmap(
                                        lambda chars: integers(min_value=0).flatmap(
                                            lambda n: tuples(just(chars), text(alphabet=chars, min_size=n, max_size=n),
                                                             text(alphabet=two_characters, min_size=n, max_size=n))
                                            )
                                        )

@raises(InvalidActionError)
@given(history = different_characterset_strategy, strategy = sampled_from(strategy_list))
def test_strategy_invalidCharactersPassed_raisesInvalidActionError(history, strategy):
    """Test that if the opponent's history doesn't match the characterset, an InvalidActionError is thrown."""
    characterset = history[0]
    strat_history = history[1]
    opponent_history = history[2]
    # Assume that the charactersets are not the same between the history and the opponent history
    assume(set(characterset) != set(opponent_history))
    # Create an object with the correct characterset
    test_object = strategy(C=characterset[0], D=characterset[1])
    # Set up the object's history
    test_object.history = strat_history
    # Try and get the next move which should raise an error
    test_object.next_move(opponent_history)

# We want to test that if we pass a new history to a strategy with a different characterset, an exception is thrown
# We need to define a strategy to generate two different charactersets, and a history made of the second one
different_history_characterset_strategy = tuples(two_characters, two_characters).flatmap(
                                            lambda tup: tuples(just(tup[0]), text(alphabet=tup[1])))

@raises(InvalidActionError)
@given(history = different_history_characterset_strategy, strategy = sampled_from(strategy_list))
def test_strategy_historyWithWrongCharacterset_raisesInvalidActionError(history, strategy):
    """Test that if you pass a history with the wrong characterset, an InvalidActionError is thrown."""
    characterset = history[0]
    strat_history = history[1]
    # Assume that the history characterset isn't a subset of the characterset
    assume(not set(strat_history) <= set(characterset))
    # Set up the object
    test_object = strategy(C=characterset[0], D=characterset[1])
    # Try and pass a history which should raise an error
    test_object.history = strat_history

# We want to test that given any history, the reset method will return the strategy's history to empty
@given(history = two_characters.flatmap(lambda chars: tuples(just(chars), text(alphabet=chars))),
       strategy = sampled_from(strategy_list))
def test_strategy_passHistoryThenReset_historyIsEmpty(history, strategy):
    """Test that regardless of characterset or history, reset clears the history"""
    characterset = history[0]
    strat_history = history[1]
    test_object = strategy(C=characterset[0], D=characterset[1])
    test_object.history = strat_history
    test_object.reset()
    assert test_object.history == []
"""
Individual strategy tests
"""
@given(valid_history_strategy)
def test_AllC_passAnyHistory_ReturnsC(s):
    """Test that AllC always returns a C regardless of history or input"""
    characterset = s[0]
    history = s[1]
    opponent_history = s[2]
    test_object = AllC(C=characterset[0], D=characterset[1])
    test_object.history = history
    assert test_object.next_move(opponent_history) == test_object.C

@given(valid_history_strategy)
def test_AllD_passAnyHistory_ReturnsD(s):
    """Test that AllD always returns a D regardless of history or input"""
    characterset = s[0]
    history = s[1]
    opponent_history = s[2]
    test_object = AllD(C=characterset[0], D=characterset[1])
    test_object.history = history
    assert test_object.next_move(opponent_history) == test_object.D

if __name__ == '__main__':
    nose.main()
