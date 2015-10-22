#!/bin/sh
python3 ../simulation_multiproc.py 0.5 0.001
echo "Done"
python3 ../simulation_multiproc.py 0.5 0.1
echo "Done"
python3 ../simulation_multiproc.py 0.8 0.1
echo "Done"
python3 ../simulation_multiproc.py 0.9 0.1
echo "Done"
python3 ../simulation_multiproc.py 0.9 0.0001
echo "Done"
python3 ../simulation_multiproc.py 0.9 0.0001
echo "Done"
