from hypothesis import Settings

def setup():
    # We want to set the default hypothesis settings object to have no timeout
    Settings.default.timeout = 0
