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


def initialize(job):
    "Initialize the simulation configuration."
    from pkg_resources import resource_filename

    from mbuild.lib.atoms import H

    from atools.fileio import write_monolayer_ndx
    from atools.lib.chains import Alkylsilane
    from atools.recipes import DualSurface, SilicaInterface, SurfaceMonolayer
    from atools.structure import identify_rigid_groups

    with job:
        chainlength = job.statepoint()['chainlength']
        n_chains = job.statepoint()['n']
        seed = job.statepoint()['seed']
        terminal_group = job.statepoint()['terminal_group']

        surface = SilicaInterface(thickness=1.2, seed=seed)
        chain_proto = Alkylsilane(chain_length=chainlength, 
                                  terminal_group=terminal_group)
        monolayer = SurfaceMonolayer(surface=surface, chains=chain_proto,
                                     n_chains=n_chains, seed=seed,
                                     backfill=H())
        dual_monolayer = DualSurface(monolayer)
        box = dual_monolayer.boundingbox
        dual_monolayer.periodicity += np.array([0, 0, 5. * box.lengths[2]])

        forcefield_dir = resource_filename('atools', 'forcefields')
        dual_monolayer.save('init.gro', 
            forcefield_files=os.path.join(forcefield_dir, 'oplsaa-silica.xml'),
            overwrite=True)
        dual_monolayer.save('init.top', 
            forcefield_files=os.path.join(forcefield_dir, 'oplsaa-silica.xml'),
            overwrite=True)
        rigid_groups = identify_rigid_groups(monolayer=dual_monolayer, 
            terminal_group=terminal_group, freeze_thickness=0.5)
        write_monolayer_ndx(rigid_groups=rigid_groups, filename='init.ndx')

@job_chdir
def fix_overlaps(job):
    "Initial minimization to fix overlaps between terminal groups."
    grompp = _grompp_str(job, 'em_terminal', 'init', 'init')
    grompp_proc = subprocess.Popen(grompp.split())
    grompp_proc.communicate()
    mdrun = _mdrun_str(job, 'em_terminal')
    mdrun_proc = subprocess.Popen(mdrun.split())
    mdrun_proc.communicate()

@job_chdir
def minimize(job):
    "Energy minimize."
    grompp = _grompp_str(job, 'em', 'em_terminal', 'init')
    grompp_proc = subprocess.Popen(grompp.split())
    grompp_proc.communicate()
    mdrun = _mdrun_str(job, 'em')
    mdrun_proc = subprocess.Popen(mdrun.split())
    mdrun_proc.communicate()

@job_chdir
def equilibrate(job):
    "NVT equilibration."
    grompp = _grompp_str(job, 'nvt', 'em', 'init')
    grompp_proc = subprocess.Popen(grompp.split())
    grompp_proc.communicate()
    mdrun = _mdrun_str(job, 'nvt')
    mdrun_proc = subprocess.Popen(mdrun.split())
    mdrun_proc.communicate()

# I feel like there should be a way to only have one
# function definition here taking load as an arg...
def shear_5nN(job):
    "Shear at a constant normal load of 5nN."
    _shear(job, 5)

def shear_10nN(job):
    "Shear at a constant normal load of 10nN."
    _shear(job, 10)

def shear_15nN(job):
    "Shear at a constant normal load of 15nN."
    _shear(job, 15)

def shear_20nN(job):
    "Shear at a constant normal load of 20nN."
    _shear(job, 20)

def shear_25nN(job):
    "Shear at a constant normal load of 25nN."
    _shear(job, 25)

@job_chdir
def _shear(job, load):
    grompp = _grompp_str(job, 'shear_{}nN'.format(load), 'nvt', 'init')
    grompp_proc = subprocess.Popen(grompp.split())
    grompp_proc.communicate()
    mdrun = _mdrun_str(job, 'shear_{}nN'.format(load))
    mdrun_proc = subprocess.Popen(mdrun.split())
    mdrun_proc.communicate()

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
    grompp_str = ('gmx grompp -f {0}/scripts/util/mdp_files/{1}.mdp -c {2}/{3}.gro '
                  '-p {2}/{4}.top -n {2}/{4}.ndx -o {2}/{1}.tpr'
                  ''.format(job._project.root_directory(), op_name, job.workspace(), 
                  gro_name, sys_name))
    return grompp_str

def _mdrun_str(job, op_name):
    """Helper function, returns mdrun command string for operation """
    mdrun_str = 'gmx mdrun -v -deffnm {} -ntmpi 1'.format(op_name)
    return mdrun_str
