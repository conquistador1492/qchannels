#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from qiskit import QuantumRegister, ClassicalRegister

from qchannels.core.theory import fidelity, create_theory_choi_matrix
from qchannels.core.manage_parameters import set_parameters
from qchannels.core.launcher import Launcher
from qchannels.channels import IdentityCircuit, QutritSuperpositionCircuit
from qchannels.core.tools import SIMULATORS, BACKENDS

import numpy as np

# TODO change description
parameters = set_parameters(
    'Calculate Choi Matrix by direct method',
)

identity_mask = {0: 6, 1: 7}
channel_mask = {3: 11, 0: 12, 2: 16, 1: 17}
if parameters['backend_name'] in SIMULATORS:
    num_qubits = 20
else:
    backend = next(filter(lambda backend: backend.name() == parameters['backend_name'], BACKENDS))
    num_qubits = backend.configuration()['n_qubits']

channel_class = parameters['channel_class']

qr = QuantumRegister(num_qubits)
cr = ClassicalRegister(num_qubits)
test_channel = channel_class(backend_name=parameters['backend_name'], mask=channel_mask,
                             q_reg=qr, c_reg=cr)
identity_channel = IdentityCircuit(backend_name=parameters['backend_name'], mask=identity_mask,
                                   q_reg=qr, c_reg=cr, rel_system_qubits=[0, 1])

preparation_circuit = QutritSuperpositionCircuit(
    backend_name=parameters['backend_name'],
    mask={key: test_channel.system_qubits[key] for key in [0, 1]},
    q_reg=qr, c_reg=cr
)
preparation_circuit.cnot(preparation_circuit.rel_qr[0], identity_channel.rel_qr[0])
preparation_circuit.cnot(preparation_circuit.rel_qr[1], identity_channel.rel_qr[1])
circuit = preparation_circuit + test_channel + identity_channel

launcher = Launcher(parameters['token'], parameters['backend_name'], parameters['shots'])
choi = launcher.run(circuit, meas_qubits=identity_channel.system_qubits +
                                         test_channel.system_qubits)[0]

choi = np.delete(choi, [3, 7, 11, 15, 12, 13, 14], 0)
choi = np.delete(choi, [3, 7, 11, 15, 12, 13, 14], 1)

print(fidelity(choi, create_theory_choi_matrix(channel_class.get_theory_channel())))
