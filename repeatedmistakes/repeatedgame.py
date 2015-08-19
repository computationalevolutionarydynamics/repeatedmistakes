class RepeatedGamne:
    """
    A class for modelling a repeated game between two players, with functions for simulation and calculation of results
    """
    def __init__(self, strategy_one, strategy_two, C='C', D='D'):
        """
        Initialise the object with two strategies and a characterset
        """
        self.strategy_one = strategy_one
        self.strategy_two = strategy_two
        self.C = C
        self.D = D

    def simulate(self, rounds):
        """
        Simulate a repeated game between the two strategys for the given number of rounds and return the result

        Args:
            rounds (int): The number of rounds to simulate the two strategies playing against each other

        Returns:
            results (dict): A dictionary where the key is the strategy and the value is the list of moves it played
        """
        # Set up the two strategies
        player_one = self.strategy_one(C=self.C, D=self.D)
        player_two = self.strategy_two(C=self.C, D=self.D)
        # For each round
        for _ in range(rounds):
            # Figure out what move each strategy makes by passing each other the other player's history
            move_one = player_one.next_move(player_two.history)
            move_two = player_two.next_move(player_one.history)
            # Update the histories of each player
            player_one.history += move_one
            player_two.history += move_two

        # Construct the result dictionary
        results = {self.strategy_one: player_one.history, self.strategy_two: player_two.history}
        return results
