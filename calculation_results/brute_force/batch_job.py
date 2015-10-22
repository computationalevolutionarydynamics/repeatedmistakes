from repeatedmistakes.strategies import strategy_list
from repeatedmistakes.repeatedgame import PrisonersDilemmaPayoff
from repeatedmistakes.calculations import calculate_payoff_with_mistakes
import itertools

def main():
    """
    Iterate over combinations of strategies, continuation probability, mistake probability and epsilon, outputting
    to a file
    """

    continuation_values = [0.5, 0.6, 0.7, 0.8, 0.9]
    mistake_values = [0.1, 0.01, 0.001, 0.0001, 0.00001]
    epsilon_values = [1e-4, 1e-5, 1e-6]

    # For all values of epsilon
    for epsilon in epsilon_values:

        # For all values of continuation prob
        for continuation_probability in continuation_values:

            # for all values of mistake prob
            for mistake_probability in mistake_values:

                # Open a file to write to
                with open("results_" + str(epsilon) + "_" + str(continuation_probability) + "_" + str(mistake_probability), 'w') as file:

                    # Print the parameters for the run
                    print("Epsilon: " + str(epsilon), file=file)
                    print("Continuation prob: " + str(continuation_probability), file=file)
                    print("Mistake prob: " + str(mistake_probability), file=file)

                    # Spin up some iterators
                    list_one, list_two = itertools.tee(strategy_list, n=2)

                    # For each pair of strategies
                    for strategy_one in list_one:
                        for strategy_two in list_two:

                            # Compute the result
                            results = calculate_payoff_with_mistakes(strategy_one, strategy_two, PrisonersDilemmaPayoff(),
                                    continuation_probability, mistake_probability, epsilon)

                            # Write the results to the file
                            print(str(strategy_one.__name__) + "," + str(strategy_two.__name__) + "," + str(results), file=file)

                    # When we're done with all the strategies, print done, just so I know how long things are taking
                    print("Done eps=" + str(epsilon) + " delta=" + str(continuation_probability) + " gamma=" + str(mistake_probability))

if __name__ == '__main__':
    main()
