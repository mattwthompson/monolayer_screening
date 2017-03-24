import getopt
import os
import re
import sys

import numpy as np

import MDAnalysis as mda
import signac

"""
Generates the friction force trajectory for each job in the project

Sums up the forces on all atoms in the bottom half of the system (surface
+ chains) in the x-direction at each point in the trajectory.

Command Line Options
--------------------
-a, --all : Perform the calculation for all jobs. By default the
            calculation is skipped for jobs where it has already
            been performed.

Output Files
------------
friction-XnN.txt : Friction force (in nN) on bottom surface + chains at
                   each point in the trajectory. One file is written per
                   normal load.

"""

opts, args = getopt.getopt(sys.argv[1:], "a", ["all"])

project = signac.get_project()

for job in project.find_jobs():
    loads = []
    for fname in os.listdir(path=job.workspace()):
        if 'shear' in fname and os.path.splitext(fname)[1] == '.trr':
            loads.append(re.findall('\d+', fname)[0])

    for load in loads:
        trr_file = os.path.join(job.workspace(), 'shear_{}nN.trr'.format(load))
        out_file = os.path.join(job.workspace(), 'friction-{}nN.txt'.format(load))
        if opts and '-a' not in opts[0] and os.path.isfile(out_file):
            continue
        elif os.path.isfile(trr_file):
            print('Writing friction trajectory for job: {}'.format(job.get_id()))
            print('{}nN'.format(load))
            fric = []
            trr = mda.coordinates.TRR.TRRReader(trr_file)
            for frame in trr:
                forces_on_bottom = frame.forces[:int(frame.n_atoms/2)]
                fric.append([frame.time, np.sum(forces_on_bottom[:,0]) * 0.0166])
            np.savetxt(out_file, fric)
