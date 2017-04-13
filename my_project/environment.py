import flow
from flow.environment import format_timedelta


class TitanEnvironment(flow.environment.MoabEnvironment):
    hostname_pattern = 'titan'
    MAX_NUM_APRUN = 50

    class TitanJobScript(flow.environment.JobScript):
        pass

    def __init__(self, *args, **kwargs):
        self._mpi_cmds = dict()
        super(TitanEnvironment, self).__init__(*args, **kwargs)

    def mpi_cmd(self, cmd, np=1):
        ph = 'MPI_CMD_' + str(len(self._mpi_cmds))
        self._mpi_cmds[ph] = (np, cmd)
        return '{' + ph + '}'

    def submit(self, script, *args, **kwargs):
        if len(self._mpi_cmds) > self.MAX_NUM_APRUN:
            cmds = {ph: "# bundled in wrarprun command below" for ph in self._mpi_cmds}
            s = script.getvalue().format(**cmds)
            script.truncate(0)
            for line in s.split('\n'):
                script.writeline(line)
            cmds = ('-n {} {}'.format(np, cmd) for np, cmd in self._mpi_cmds.values())
            wraprun_cmd = 'wraprun {}'.format(' : '.join(cmds))
            script.writeline(wraprun_cmd)

        else:
            cmds = {ph: 'aprun -n {np} -N 1 -b {cmd}'.format(np=np, cmd=cmd)
                    for ph, (np, cmd) in self._mpi_cmds.items()}
            s = script.getvalue().format(** cmds)
            script.truncate(0)
            for line in s.split('\n'):
                script.writeline(line)
        super(TitanEnvironment, self).submit(script, *args, **kwargs)

    def script(self, _id, nn, walltime, **kwargs):
        js = self.TitanJobScript(self)
        js.writeline('#PBS -N {}'.format(_id))
        js.writeline('#PBS -A MAT110')
        js.writeline('#PBS -l nodes={}'.format(nn))
        js.writeline('#PBS -l walltime={}'.format(format_timedelta(walltime)))
        js.writeline('#PBS -j oe')
        js.writeline('#PBS -V')
        return js
