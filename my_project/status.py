#!/usr/bin/env python
"""Print the project's status to screen."""
import argparse
from multiprocessing import Pool

from project import get_project
from environment import get_environment


def main(args):
    try:
        scheduler = get_environment().get_scheduler()
    except AttributeError:
        scheduler = None

    project = get_project()
    with Pool() as pool:
        project.print_status(None, pool=pool, **vars(args))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    get_project().add_print_status_args(parser)
    main(parser.parse_args())
