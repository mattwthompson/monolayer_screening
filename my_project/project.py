"""Define the project's workflow logic."""
from math import ceil

from flow import FlowProject
from flow import JobOperation


class MyProject(FlowProject):

    def classify(self, job):
        if job.isfile('init.top'):
            yield 'initialized'
        if job.isfile('nvt.tpr'):
            yield 'minimized'

    def next_operation(self, job):
        labels = set(self.classify(job))

        def op(name):
            return JobOperation(name, job, 'python scripts/run.py {} {}'.format(name, job))

        if 'initialized' not in labels:
            return op('initialize')
        if 'minimized' not in labels:
            return op('minimize')

    def submit_user(self, env, _id, operations, walltime, np, ppn,
                    serial=False, force=False, **kwargs):
        # Calculate the total number of required processors
        np_total = np if serial else np * len(operations)
        # Calculate the total number of required nodes
        nn = ceil(np_total / ppn)
        
        if not force:  # Perform basic check concerning the node utilization.
            usage = np * len(operations) / nn / ppn
            if usage < 0.9:
                raise RuntimeError("Bad node utilization!")

        # Create a submission script.
        sscript = env.script(_id=_id, walltime=walltime, nn=nn, ppn=ppn,
                             serial=serial, **kwargs)

        # Add some whitespace
        sscript.writeline()
        # Don't use uninitialized environment variables.
        sscript.writeline('set -u')
        # Exit on errors.
        sscript.writeline('set -e')
        # Switch into the project root directory
        sscript.writeline('cd {}'.format(self.root_directory()))
        sscript.writeline()

        # Iterate over all job-operations and write the command to the script
        for op in operations:
            self.write_human_readable_statepoint(sscript, op.job)
            sscript.write_cmd(op.cmd, np=np, bg=not serial)

        # Wait until all processes have finished
        sscript.writeline('wait')

        # Submit the script to the environment specific scheduler
        return env.submit(sscript, **kwargs)


def get_project(*args, **kwargs):
    """Find a project configuration and return the associated project.

    This is a wrapper for: :py:meth:`.MyProject.get_project`
    """
    return MyProject.get_project(*args, **kwargs)
