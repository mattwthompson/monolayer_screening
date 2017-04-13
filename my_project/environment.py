"""Configuration of the project enviroment.

The environments defined in this module can be auto-detected.
This helps to define environment specific behaviour in heterogenous
environments.
"""
import flow
from flow.environment import get_environment
from flow.environment import format_timedelta


__all__ = ['get_environment']


class TitanEnvironment(flow.environment.MoabEnvironment):
    hostname_pattern = 'titan'
    cores_per_node = 16

    @classmethod
    def script(cls, _id, nn, walltime, **kwargs):
        js = super(TitanEnvironment, cls).script()
        js.writeline('#!/bin/sh -l')
        js.writeline('#PBS -N {}'.format(_id))
        js.writeline('#PBS -A MAT149')
        js.writeline('#PBS -q debug') # Comment this out for production runs
        js.writeline('#PBS -l nodes={}'.format(nn))
        js.writeline('#PBS -l walltime={}'.format(format_timedelta(walltime)))
        js.writeline('#PBS -j oe')
        js.writeline('#PBS -V')
        return js
