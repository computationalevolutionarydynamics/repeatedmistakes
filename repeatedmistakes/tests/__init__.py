from hypothesis import Settings

def setup():
    # We want to set the default hypothesis settings object to have no timeout
    Settings.default.timeout = 0
    # We also want to derandomize the testing, because sometimes it times out and sometimes it doesn't.
    Settings.default.derandomize = True
    # And we want a larger number of examples
    Settings.default.max_examples = 750
