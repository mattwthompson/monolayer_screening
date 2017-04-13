"""This module contains the operation functions for this project.

Functions defined in this module can be executed using the
:py:mod:`.run` module.
"""
import logging

import numpy as np


logger = logging.getLogger(__name__)

def grompp(job):
    "Create a TPR file for ethane."
    grompp_str = _grompp_str(job, 'minimize', 'ethane', 'ethane')
    return grompp_str

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
    grompp_str = ('gmx_mpi grompp -f {0}/scripts/util/{1}.mdp -c '
                  '{0}/scripts/util/{3}.gro -p {0}/scripts/util/{4}.top -o '
                  '{2}/{1}.tpr'.format(job._project.root_directory(), op_name, 
                  job.workspace(), gro_name, sys_name))
    return grompp_str
