from hypothesis import given
from hypothesis.strategies import text, just, integers, tuples
from inspect import isclass, isabstract
import nose

from repeatedmistakes import strategies

"""
Test all of the strategies in the strategies module to make sure that they only return a C (cooperate) or D (defect)
regardless of their input. We do this by iterating over all of the non-abstract classes in the strategies module
"""
# First we will define a strategy which gives us strings of length two. This will enable use to test the strategies
# across all inputs for C and D
two_characters = text(min_size=2, max_size=2)

# Next we need a strategy which will produce two texts with the same characterset and of the same length, but with
# random lengths. We generate this as a tuple with the first element being the characterset and the second and third
# elements being the generated histories
history_strategy = two_characters.flatmap(
                        lambda chars: integers(min_value=0).flatmap(
                            lambda n: tuples(just(chars), text(alphabet=chars, min_size=n, max_size=n),
                                       text(alphabet=chars, min_size=n, max_size=n)
                                       )
                        )
                    )

for strategy in strategies.strategy_list:
    @given(history_strategy)
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

if __name__ == '__main__':
    nose.main()
