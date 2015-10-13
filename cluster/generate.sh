#!/bin/sh

# Generate a bunch of pbs files using the generate_pbs.sh script

# Define an array for all of the individual values of the continuation
# probability that we want to test
continuationProbability=(0.5 0.6 0.7 0.8 0.9 0.99 0.999)

# Define an array for all of the individual values of mistake probability
# that we want to test
mistakeProbability=(0.1 0.01 0.001 0.0001)

# Define then name of the batchfile
batchFile=batch_file.sh

# Define the folder to output to
batchFolder=JobFiles

# Remove existing folder with job files and make a folder for all of the job
# files as well as the batch file
rm -r ./$batchFolder ; mkdir ./$batchFolder

# Make a folder for results
mkdir results

# echo the shebang line to the batch file
echo "#!/bin/sh" >> ./$batchFolder/$batchFile

# Loop over each of the values in each array, generating a pbs file for each
# set of values
for contProb in "${continuationProbability[@]}"
do
    for mistakeProb in "${mistakeProbability[@]}"
    do
        # Generate the filename for the jobfile
        filename=job_$contProb\_$mistakeProb.pbs
        # Generate the job file
        ./generate_pbs.sh $contProb $mistakeProb >> ./$batchFolder/$filename
        # Add the qsub command for the job file to a batch file
        echo "qsub $filename" >> ./$batchFolder/$batchFile
    done
done
