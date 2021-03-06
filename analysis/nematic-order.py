import getopt
import os
import sys

from atools.structure import calc_nematic_order
import signac

"""
Performs a nematic order calculation for each job in the project

Computes the nematic order of the top and bottom monolayers at each
timestep and prints the average to a text file. Requires an unwrapped
trajectory. If an unwrapped trajectory is not found, one will be created.

Command Line Options
--------------------
-a, --all : Perform the calculation for all jobs. By default the
            calculation is skipped for jobs where it has already
            been performed.

Output Files
------------
nvt-unwrapped.xtc : Unwrapped equilibration trajectory

nematic-order.txt : Average nematic order of the top and bottom
                    monolayers at each timestep.

"""

opts, args = getopt.getopt(sys.argv[1:], "a", ["all"])

project = signac.get_project()

for job in project.find_jobs():
    gro_file = os.path.join(job.workspace(), 'nvt.gro')
    out_file = os.path.join(job.workspace(), 'nematic-order.txt')
    if '-a' not in opts[0] and os.path.isfile(out_file):
        continue
    elif os.path.isfile(gro_file):
        traj = os.path.join(job.workspace(), 'nvt.xtc')
        if not os.path.isfile(traj):
            continue
        unwrapped_traj = os.path.join(job.workspace(), 'nvt-unwrapped.xtc')
        if not os.path.isfile(unwrapped_traj):
            os.system("echo 0 | gmx trjconv -f {} -o {} -s {} -pbc nojump".format(traj, unwrapped_traj, gro_file))
        calc_nematic_order(unwrapped_traj, gro_file, out_file, job.statepoint()['n'])
