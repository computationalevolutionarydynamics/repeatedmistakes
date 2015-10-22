#!/bin/bash

OUTFILE="results_summary.txt"

# Look over all of the files in the folder
for f in results*
do
    # Grab the line we want from the file
    results=`awk 'NR==118' $f`
    # Tokenize the filename to extract parameters
    IFS='_'
    tokens=( $f )
    # Tokenize results on the comma
    IFS=','
    result_tokens=( $results )
    # Write the values we want to our summary
    echo "${tokens[1]},${tokens[2]},${result_tokens[2]},${result_tokens[3]}" >> $OUTFILE
done
