import argparse
import math

from mlboardclient.api import client


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--argument',
        help='Define x for func',
        dest='x',
        type=float,
        default=0.0,
    )

    return parser


def f(x):
    return math.exp(-(x - 2)**2) + math.exp(-(x - 6)**2/10) + 1 / (x**2 + 1)


def main():
    parser = get_parser()
    args = parser.parse_args()

    checked_value = f(args.x)
    print('f(%s) = %s' % (args.x, checked_value))
    client.update_task_info({'checked_value': float(checked_value)})


if __name__ == '__main__':
    main()
