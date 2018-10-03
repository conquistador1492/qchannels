#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from Qconfig import config
from qiskit import QuantumProgram
from qiskit import execute, register

from qiskit.tools.qcvv.tomography import *
from tools import chunks, LOCAL_BACKEND, MAX_JOBS_PER_ONE

import numpy as np
import argparse

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
register(APItoken, **config)

backend = args.backend
shots = args.shots

np.set_printoptions(threshold=np.nan)

num_qubits = 5
qp = QuantumProgram()
q = qp.create_quantum_register('q', num_qubits)
c = qp.create_classical_register('c', num_qubits)

circuit_name = 'test'
qc = qp.create_circuit(circuit_name, [q], [c])
qc.circuit_name = circuit_name

qc.h(q[0])

tomo_set = tomography_set([0])
circuits_names = create_tomography_circuits(qp, circuit_name, q, c, tomo_set)
qp.destroy_circuit(circuit_name)

# One more bug in IBM
for name in qp.get_circuit_names():
    qp.get_circuit(name).name = name

res = None
for i, part_circuits in enumerate(chunks(list(map(lambda name: qp.get_circuit(name),
                        qp.get_circuit_names())), MAX_JOBS_PER_ONE)):
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


density_matrix = fit_tomography_data(tomography_data(res, circuit_name, tomo_set))
print(f"[{density_matrix}]")
