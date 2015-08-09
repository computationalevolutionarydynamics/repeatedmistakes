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
    """Ensure that when a history string is passed, all we get back is either a c or a d"""
    for strategy in strategy_list:
        yield check_returnsCsAndds, s, strategy

@given(text(alphabet='CD'))
def test_strategy_passHistoryTextContainingUpperCase_returnsCsAndDs(s):
    """Ensure that when a history string is passed with uppercase history, all we get back is either a c or a d"""
    for strategy in strategy_list:
        yield check_returnsCsAndds, s, strategy

# Test individual strategies to make sure that they return the correct value as per their desired behaviour
@given(text(alphabet='cd'))
def test_allc_passAnyHistory_returnsC(s):
    assert strategies.allc(s) == 'c'

@given(text(alphabet='cd'))
def test_alld_passAnyHistory_returnsD(s):
    assert strategies.alld(s) == 'd'

@given(just(''))
def test_titForTat_passEmptyHistory_strategyCooperates(s):
    assert strategies.tit_for_tat(s) == 'c'


if __name__ == '__main__':
    nose.main()
