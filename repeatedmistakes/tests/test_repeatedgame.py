"""
Tests for the repeated game class
"""
from .. import strategies
from ..repeatedgame import RepeatedGame

from hypothesis import given
from hypothesis.strategies import sampled_from, integers
import nose

# We want to test that given any combination of strategies and any number of rounds, the result we get back from the
# simulate function has the correct number of elements in each history
@given(strat1=sampled_from(strategies.strategy_list), strat2=sampled_from(strategies.strategy_list),
            rounds=integers(min_value=0))
def test_repeatedGameSimulate_passStrategiesAndNumberOfRounds_ReturnedHistoriesMatchInLength(strat1, strat2, rounds):
    """Test that any simulating any number of rounds with any strategies gives results of the correct length"""
    game = RepeatedGame(strat1, strat2)
    results = game.simulate(rounds)
    assert len(results[strat1]) == rounds
    assert len(results[strat2]) == rounds

if __name__ == '__main__':
    nose.main()
