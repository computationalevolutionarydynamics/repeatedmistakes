from hypothesis import given
from hypothesis.strategies import text, just
import nose

from repeatedmistakes import strategies

"""
Test all of the strategies in the strategies module to make sure that they only return a C (cooperate) or D (defect)
regardless of their input. We do this by iterating over all of the callables in the strategies module.
"""
# Grab all callables from the strategies module and make list of them
strategy_list = [f for _, f in strategies.__dict__.items() if callable(f)]

def check_returnsCsAndds(s, strategy):
    """Make sure the function returns either a c or a d"""
    assert strategy(s) in ['c', 'd']

@given(text(alphabet='cd'))
def test_strategy_passHistoryTextContainingCsAndDs_returnsCsAndDs(s):
    """Test that when a history string is passed, all we get back is either a c or a d"""
    for strategy in strategy_list:
        yield check_returnsCsAndds, s, strategy

@given(text(alphabet='CD'))
def test_strategy_passHistoryTextContainingUpperCase_returnsCsAndDs(s):
    """Test that when a history string is passed with uppercase history, all we get back is either a c or a d"""
    for strategy in strategy_list:
        yield check_returnsCsAndds, s, strategy

# Test individual strategies to make sure that they return the correct value as per their desired behaviour
@given(text(alphabet='cd'))
def test_allc_passAnyHistory_returnsC(s):
    """Test that allc always returns a c for any history"""
    assert strategies.allc(s) == 'c'

@given(text(alphabet='cd'))
def test_alld_passAnyHistory_returnsD(s):
    """Test that alld always returns a d for any history"""
    assert strategies.alld(s) == 'd'

@given(just(''))
def test_titForTat_passEmptyHistory_strategyCooperates(s):
    """Test that tit for tat cooperates on the first turn"""
    assert strategies.tit_for_tat(s) == 'c'

@given(text(alphabet='cd', min_size=1))
def test_titForTat_passHistory_strategyReturnsLastElement(s):
    """Test that tit for tat returns the opponent's last move on any turn but the first"""
    assert strategies.tit_for_tat(s) == s[-1]

@given(just(''))
def test_inverseTitForTat_passEmptyHistory_strategyCooperates(s):
    """Test that inverse tit for tat cooperates on the first move"""
    assert strategies.inverse_tit_for_tat(s) == 'c'

@given(text(alphabet='cd', min_size=1))
def test_inverseTitForTat_passHistory_strategyReturnsOppositeOfLastElement(s):
    """Test that inverse tit for tat returns the opposite of the last move on any turn but the first"""
    if s[-1] == 'c':
        assert strategies.inverse_tit_for_tat(s) == 'd'
    else:
        assert strategies.inverse_tit_for_tat(s) == 'c'

if __name__ == '__main__':
    nose.main()
