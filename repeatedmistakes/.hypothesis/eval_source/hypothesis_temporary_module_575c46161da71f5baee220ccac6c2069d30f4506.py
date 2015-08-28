from hypothesis.utils.conventions import not_set

def accept(f):
    def integers(min_value=not_set, max_value=not_set):
        return f(min_value, max_value)
    return integers
