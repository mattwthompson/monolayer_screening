import getopt
import os
import sys

from atools.structure import calc_nematic_order
import signac

opts, args = getopt.getopt(sys.argv[1:], "a", ["all"])

project = signac.get_project()

for job in project.find_jobs():
    gro_file = os.path.join(job.workspace(), 'nvt.gro')
    if '-a' not in opts[0] and os.path.isfile(job.workspace() + 'nematic-order.txt'):
        continue
    elif os.path.isfile(gro_file):
        traj = os.path.join(job.workspace(), 'nvt.xtc')
        if not os.path.isfile(traj):
            continue
        unwrapped_traj = os.path.join(job.workspace(), 'nvt-unwrapped.xtc')
        if not os.path.isfile(unwrapped_traj):
            os.system("echo 0 | gmx trjconv -f {} -o {} -s {} -pbc nojump".format(traj, unwrapped_traj, gro_file))
        out_file = os.path.join(job.workspace(), 'nematic-order.txt')
        calc_nematic_order(unwrapped_traj, gro_file, out_file, job.statepoint()['n'])
