#!/usr/bin/env python
"Submit job-operations to a scheduler."
import argparse
import logging

from project import get_project
import environment


def main(args):
    env = environment.get_environment(test=args.test)
    if args.ppn is None:
        try:
            args.ppn = env.cores_per_node
        except AttributeError:
            raise ValueError(
                "Did not find a default value for the processors-per-node (ppn)."
                "Please provide `--ppn` argument")

    project = get_project()
    env.scheduler = env.get_scheduler()
    project.submit(env, **vars(args))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    get_project().add_submit_args(parser)
    group = parser.add_argument_group(
        "Execution configuration:",
        "Specify the execution environment.")
    group.add_argument(
        '--np',
        type=int,
        default=1,
        help="Specify the total # of processors to be used per operation.")
    group.add_argument(
        '--ppn',
        type=int,
        help="Specify the number of processors allocated to each node.")
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help="Use TestEnvironment for testing.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    main(args)
