#!/bin/sh
# Based on code found at https://stackoverflow.com/a/6215113/4042597

# This file generates a job file based on the passed parameters, and it prints
# this to the standard output

# Define parameters which are passed in.
delta=$1    # The continuation probability
gamma=$2    # The mistake probability

# Define the template.
cat << EOF
#!/bin/sh
#PBS -S /bin/sh
#PBS -m bea
#PBS -l mem=1000mb
#PBS -o simulations_$delta_$gamma
#PBS -e simulations_$delta_$gamma_error
#PBS -l ncpus=8
cd ~/test/results
echo "Current working directory is `pwd`"
echo "Starting run "$0" at: `date`"
module load python/3.4.3
python3 ../simulation.py $delta $gamma
echo "Program "$0" finished with exit code $? at: `date`"
EOF
