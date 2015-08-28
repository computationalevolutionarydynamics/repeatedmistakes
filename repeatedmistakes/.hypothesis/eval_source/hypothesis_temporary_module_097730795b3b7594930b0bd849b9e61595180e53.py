from hypothesis.utils.conventions import not_set

def accept(f):
    def test_calculations_singleResultCombosGiven_ExpectedResultReturned(payoff_values=not_set, delta=not_set, combo=not_set):
        return f(payoff_values, delta, combo)
    return test_calculations_singleResultCombosGiven_ExpectedResultReturned
