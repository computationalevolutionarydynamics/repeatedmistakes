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
#$ -S /bin/sh
#$ -m bea
#$ -M nmsko2@student.monash.edu
#$ -l h_vmem=8G
#$ -pe smp 8
echo "Current working directory is \`pwd\`"
echo "Starting run "\$0" at: \`date\`"
module load python/3.4.3
python3 simulation.py $delta $gamma
echo "Program "\$0" finished with exit code \$? at: \`date\`"
EOF
