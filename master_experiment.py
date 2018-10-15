#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from Qconfig import config
from qiskit import QuantumRegister, ClassicalRegister, execute, IBMQ

from qiskit.tools.qcvv.tomography import *
from tools import chunks, MAX_JOBS_PER_ONE

import numpy as np
import argparse

from landau import LandauCircuit

parser = argparse.ArgumentParser(description='Run experiments on IBM computers')
parser.add_argument('-n', '--num-token', type=int, default=0, help='Number of token from Qconfig.py')
parser.add_argument('-t', '--token', default=None, help='Specific token')
parser.add_argument('-b', '--backend', type=str, default='ibmq_16_melbourne', help='Name of backend (default: %(default)s)')
parser.add_argument('-s', '--shots', type=int, default=8192, help='Number of shots in experiment')

args = parser.parse_args()
if args.token is not None:
    APItoken = args.token
else:
    from Qconfig import tokens
    APItoken = tokens[args.num_token]
IBMQ.enable_account(APItoken, **config)

backend = next(filter(lambda backend: backend.configuration().get('name') == args.backend, IBMQ.backends()))
shots = args.shots

np.set_printoptions(threshold=np.nan)

num_qubits = 5
q = QuantumRegister(num_qubits)
c = ClassicalRegister(num_qubits)

circuit_name = 'landau'
qc = LandauCircuit(q, c, name=circuit_name,
                   coupling_map=backend.configuration()['coupling_map'])
qc.circuit_name = circuit_name

tomo_set = tomography_set([0, 3])
circuits = create_tomography_circuits(qc, q, c, tomo_set)

res = None
for i, part_circuits in enumerate(chunks(circuits, MAX_JOBS_PER_ONE)):
    print(f'chunk number: {i + 1}')
    execute_kwargs = {
        'circuits': part_circuits,
        'backend': backend,
        'shots': shots,
        'max_credits': 15
    }
    new_res = execute(**execute_kwargs).result()
    if res is None:
        res = new_res
    else:
        res += new_res


density_matrix = fit_tomography_data(tomography_data(res, qc.name, tomo_set))
print(f"[{density_matrix}]")