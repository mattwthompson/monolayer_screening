"""Configuration of the project enviroment.

The environments defined in this module can be auto-detected.
This helps to define environment specific behaviour in heterogenous
environments.
"""
import flow
from flow.environment import get_environment
from flow.environment import format_timedelta


__all__ = ['get_environment']


class CenaEnvironment(flow.environment.TorqueEnvironment):
    hostname_pattern = 'johncena'
    cores_per_node = 1

    @classmethod
    def script(cls, _id, nn, walltime, ppn=None, **kwargs):
        if ppn is None:
            ppn = cls.cores_per_node
        js = super(CenaEnvironment, cls).script()
        js.writeline('#!/bin/sh -l')
        js.writeline('#PBS -j oe')
        js.writeline('#PBS -l nodes={}:ppn={}'.format(nn, ppn))
        js.writeline('#PBS -l walltime={}'.format(format_timedelta(walltime)))
        js.writeline('#PBS -N {}'.format(_id))
        js.writeline('#PBS -V')
        return js
