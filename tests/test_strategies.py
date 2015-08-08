from hypothesis import given
from hypothesis.strategies import text

from repeatedmistakes import strategies

"""
Test all of the strategies in the strategies module to make sure that they only return a C (cooperate) or D (defect)
regardless of their input. We do this by iterating over all of the callables in the strategies module.
"""

# Get all of the callables in the module, so that we can test them for compliance
strategy_list = [f for _, f in strategies.__dict__.iteritems() if callable(f)]

# Iterate over the strategies
for strategy in strategy_list:

    @given(text(alphabet=['c', 'd']))
    def test_strategy_passHistoryTextContainingCsAndDs_returnsCsAndDs(s):
        """Ensure that when a history string is passed, all we get back is either a c or a d"""
        assert strategy(s) in ['c', 'd']

    @given(text(alphabet=['C', 'D']))
    def test_strategy_passHistoryTextContainingUpperCase_returnsCsAndDs(s):
        """Ensure that when a history string is passed with uppercase history, all we get back is either a c or a d"""
        assert strategy(s) in ['c', 'd']
