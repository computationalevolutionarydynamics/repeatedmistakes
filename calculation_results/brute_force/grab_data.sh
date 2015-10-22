#!/bin/bash

OUTFILE="calculation_results.txt"
echo "epsilon,continuation_probability,mistake_probability,TFNT,InverseTitForTat" >> $OUTFILE

# Look over all of the files in the folder
for f in results*
do
    # Grab the line we want from the file
    results=`awk 'NR==117' $f`
    # Tokenize the filename to extract parameters
    IFS='_'
    tokens=( $f )
    # Tokenize results on the comma
    IFS=','
    result_tokens=( $results )
    # Trim some of the result tokens
    # Trim the leading ( from the first result
    result1=${result_tokens[2]:1}
    # Trim the leading whitespace from the second result
    result2=${result_tokens[3]:1}
    # Write the values we want to our summary
    echo "${tokens[1]},${tokens[2]},${tokens[3]},$result1,$result2" >> $OUTFILE
done
