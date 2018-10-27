from mlboardclient import utils
import argparse
import sys


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('mode', choices=['worker','ps', 'eval'], help='Set executable role')
    parser.add_argument('--worker', type=str, default='worker',help='Worker resource name')
    parser.add_argument('--ps', type=str, default='ps',help='PS server resource name')
    parser.add_argument('--no_chief', dest='no_chief', action='store_true',
                       help='Use old style tensorflow cluster_spec without chief worker')
    args = parser.parse_args(sys.argv[1:])
    print(utils.setup_tf_distributed(args.mode, worker_names=args.worker, ps_names=args.ps,no_chief=args.no_chief))