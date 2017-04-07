import getopt
import subprocess
import sys

import signac

opts, args = getopt.getopt(sys.argv[1:], "ao:j:")

project = signac.get_project()

def _write_pbs(jobid, op, root_dir):
    name = '{}-{}.pbs'.format(jobid, op)
    with open(name, 'w') as f:
        f.write('#!/bin/sh -l\n')
        f.write('#PBS -j oe\n')
        f.write('#PBS -l nodes=1:ppn=4\n')
        f.write('#PBS -l walltime=12:00:00\n')
        f.write('#PBS -N {}-{}\n'.format(jobid, op))
        f.write('#PBS -V\n\n')
        f.write('set -u\n')
        f.write('set -e\n')
        f.write('module load gromacs\n\n')
        f.write('cd {}\n'.format(root_dir))
        f.write('python scripts/run.py {} {} &\n'.format(op, jobid))
        f.write('wait')

    return name

def _submit_job(pbs, root_dir):
    sub_proc = subprocess.Popen('qsub {}/{}'.format(root_dir, pbs).split())
    sub_proc.communicate()
    rm_proc = subprocess.Popen('rm {}/{}'.format(root_dir, pbs).split())
    rm_proc.communicate()

if not opts:
    raise ValueError('Must provide an operation to perform')

for value in opts:
    if '-o' in value:
        operation = value[1]

if not operation:
    raise ValueError('Must provide an operation to perform')

if any('-a' in values for values in opts):
    for job in project.find_jobs():
        pbs = _write_pbs(job.get_id(), operation, project.root_directory())
        _submit_job(pbs, project.root_directory())
else:
    for value in opts:
        if '-j' in value:
            pbs = _write_pbs(value[1], operation, project.root_directory())
            _submit_job(pbs, project.root_directory())
