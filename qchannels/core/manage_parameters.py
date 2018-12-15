import argparse
import sys
import os
import re
from importlib import import_module
import datetime

from qiskit import IBMQ, Aer

from Qconfig import tokens, config
from qchannels.core.tools import IBMQ_SIMULATOR, BACKENDS


class DefaultArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('-n', '--num-token', type=int, default=0,
                          help='Number of token from Qconfig.py')
        self.add_argument('-t', '--token', default=None, help='Specific token')
        self.add_argument('-b', '--backend', type=str, default=IBMQ_SIMULATOR,
                          help='Name of backend (default: %(default)s)')
        self.add_argument('-s', '--shots', type=int, default=8192,
                          help='Number of shots in experiment (default: %(default)s)')
        self.add_argument('-c', '--channel', type=str, default='Landau-Streater',
                          help=f"Name of channel from {get_channel_names()} (default: %(default)s)")
        self.add_argument('--show-backends', action='store_true',
                          help='Show available backends(the backend might be on maintenance)')
        self.add_argument('-f', '--file', action='store_true',
                          help='Redirect output to file')


def get_channel_names():
    channel_class_names = map(lambda x: x.replace('Circuit', ''),
                              filter(lambda x: 'Circuit' in x and 'AbstractChannel' not in x,
                                     dir(import_module('qchannels.channels'))))
    return list(map(lambda class_name: '-'.join([s for s in re.split("([A-Z][^A-Z]*)", class_name) if s]),
                    channel_class_names))


def set_parameters(description='Test Channels', parser_class=None, additional_argument_list=None):
    """
    :param additional_argument_list: list of (args, kwargs)
    """
    if parser_class is None:
        parser = DefaultArgumentParser(description=description)
    else:
        parser = parser_class(description=description)

    if additional_argument_list is not None:
        for additional_argument in additional_argument_list:
            parser.add_argument(*additional_argument[0], **additional_argument[1])

    args = parser.parse_args()
    if args.token is not None:
        token = args.token
    else:
        token = tokens[args.num_token]

    IBMQ.enable_account(token, **config)
    if args.show_backends:
        for backend in [*IBMQ.available_backends(), *Aer.available_backends()]:
            print(backend.name())
        sys.exit()

    global BACKENDS
    BACKENDS += IBMQ.backends()

    if args.file:
        OUTPUT_DIR = 'outputs'
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        sys.stdout = open(
            f"{OUTPUT_DIR}/output_change_fidelity_post_selection_"
            f"{args.backend}_{args.channel.lower().replace('-', '_')}_"
            f"{datetime.datetime.today().strftime('%Y_%m_%d')}", 'a'
        )

    channel_class = getattr(import_module('qchannels.channels'),
                            args.channel.replace('-', '') + 'Circuit')

    return {
        'token': token,
        'backend_name': args.backend,
        'shots': args.shots,
        'channel_class': channel_class,
        'args': args  # args can have additional field that isn't covered recently
    }
