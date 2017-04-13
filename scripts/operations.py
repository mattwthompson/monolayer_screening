"""This module contains the operation functions for this project.

Functions defined in this module can be executed using the
:py:mod:`.run` module.
"""
import logging
from math import ceil
import os
import subprocess

import numpy as np

from util.decorators import job_chdir
from util.hoomd import redirect_log, store_meta_data


logger = logging.getLogger(__name__)

@job_chdir
def grompp(job):
    "Create a TPR file for ethane."
    grompp = _grompp_str(job, 'minimize', 'ethane', 'ethane')
    grompp_proc = subprocess.Popen(grompp.split())
    grompp_proc.communicate()

def auto(job):
    "This is a meta-operation to execute multiple operations."
    from my_project.project import get_project
    project = get_project()
    logger.info("Running meta operation 'auto' for job '{}'.".format(job))
    for i in range(10):
        next_op = project.next_operation(job)
        if next_op is None:
            logger.info("No next operation, exiting.")
            break
        else:
            logger.info("Running next operation '{}'...".format(next_op))
            func = globals()[next_op.name]
            func(job)
    else:
        logger.warning("auto: Reached max # operations limit!")

def _grompp_str(job, op_name, gro_name, sys_name):
    """Helper function, returns grompp command string for operation """
    grompp_str = ('aprun gmx grompp -f {0}/scripts/util/{1}.mdp -c {2}/{3}.gro '
                  '-p {2}/{4}.top -o {2}/{1}.tpr'
                  ''.format(job._project.root_directory(), op_name, job.workspace(), 
                  gro_name, sys_name))
    return grompp_str
