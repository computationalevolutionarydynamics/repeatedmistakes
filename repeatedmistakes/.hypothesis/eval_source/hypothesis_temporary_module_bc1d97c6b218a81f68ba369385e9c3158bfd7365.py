from hypothesis.utils.conventions import not_set

def accept(f):
    def comparison_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations(payoff_values=not_set, delta=not_set, combo=not_set):
        return f(payoff_values, delta, combo)
    return comparison_simulations_passAnyDeltaAndPayoffMatrix_simulationsMatchCalculations
