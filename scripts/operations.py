"""This module contains the operation functions for this project.

Functions defined in this module can be executed using the
:py:mod:`.run` module.
"""
import logging
from math import ceil

from util.hoomd import redirect_log, store_meta_data


logger = logging.getLogger(__name__)


def initialize(job):
    from pkg_resources import resource_filename

    from mbuild.lib.atoms import H

    from atools.fileio import write_monolayer_ndx
    from atools.lib.chains import Alkylsilane
    from atools.recipes import SurfaceMonolayer
    from atools.structure import identify_rigid_groups
    "Initialize the simulation configuration."
    with job:
        chainlength = job.sp.chainlength
        n_chains = job.sp.n
        seed = job.sp.seed
        surface = job.sp.surface
        terminal_group = job.sp.terminal_group

        chain_proto = Alkylsilane(chain_length=chainlength, 
                                  terminal_group=terminal_group)
        monolayer = SurfaceMonolayer(surface=surface, chains=chain_proto,
                                     n_chains=n_chains, seed=seed,
                                     backfill=H())

        forcefield_dir = resource_filename('atools', 'forcefields')
        monolayer.save('init.gro', 
            forcefield_files=os.path.join(forcefield_dir, 'oplsaa-silica.xml'))
        monolayer.save('init.top', 
            forcefield_files=os.path.join(forcefield_dir, 'oplsaa-silica.xml'))
        rigid_groups = identify_rigid_groups(monolayer=monolayer, 
            terminal_group=terminal_group, freeze_thickness=0.5)
        write_monolayer_ndx(rigid_groups=rigid_groups, filename='init.ndx')


def minimize(job):
    "Energy minimization."
    sp = job.statepoint()


'''
def sample(job):
    "Sample operation."
    import hoomd
    from hoomd import md
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize('')
    with job:
        with redirect_log(job):
            with hoomd.context.SimulationContext():
                hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
                group = hoomd.group.all()
                gsd_restart = hoomd.dump.gsd(
                    'restart.gsd', truncate=True, period=100, phase=0, group=group)
                lj = md.pair.lj(r_cut=job.sp.r_cut, nlist=md.nlist.cell())
                lj.pair_coeff.set('A', 'A', epsilon=job.sp.epsilon, sigma=job.sp.sigma)
                md.integrate.mode_standard(dt=0.005)
                md.integrate.npt(
                    group=group, kT=job.sp.kT, tau=job.sp.tau,
                    P=job.sp.p, tauP=job.sp.tauP)
                hoomd.analyze.log('dump.log', ['volume'], 100, phase=0)
                try:
                    hoomd.run_upto(STEPS)
                except hoomd.WalltimeLimitReached:
                    logger.warning("Reached walltime limit.")
                finally:
                    gsd_restart.write_restart()
                    job.document['sample_step'] = hoomd.get_step()
                    store_meta_data(job)
'''


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
