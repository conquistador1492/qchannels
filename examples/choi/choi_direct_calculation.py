#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
from qchannels.core.theory import fidelity, create_theory_choi_matrix
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from qchannels.core.manage_parameters import set_parameters
from qchannels.core.launcher import Launcher
from qchannels.channels import IdentityCircuit

from math import acos, sqrt, pi
import numpy as np

# TODO change description
parameters = set_parameters(
    'Calculate Choi Matrix and fidelity between experiment and theory prediction',
)

identity_mask = {}
channel_mask = {i: i+2 for i in range(4)}
num_qubits = 2*2+2
channel_class = parameters['channel_class']

qr = QuantumRegister(num_qubits)
cr = ClassicalRegister(num_qubits)
test_channel = channel_class(backend_name=parameters['backend_name'], mask=channel_mask,
                             num_qubits=num_qubits, q_reg=qr, c_reg=cr)
identity_channel = IdentityCircuit(backend_name=parameters['backend_name'], mask=identity_mask,
                                   q_reg=qr, c_reg=cr,
                                   system_qubits=[0, 1], num_qubits=num_qubits)

system_qubits = test_channel.SYSTEM_QUBITS

preparation_circuit = QuantumCircuit(qr, cr)
preparation_circuit.u3(2*acos(1/sqrt(3)), 0, 0, test_channel.qr[system_qubits[0]])
preparation_circuit.u3(0, 0, -pi/2, test_channel.qr[system_qubits[1]])
preparation_circuit.cx(test_channel.qr[system_qubits[0]], test_channel.qr[system_qubits[1]])
preparation_circuit.u3(pi/4, 0, -pi/2, test_channel.qr[system_qubits[1]])
preparation_circuit.cx(test_channel.qr[system_qubits[0]], test_channel.qr[system_qubits[1]])
preparation_circuit.u3(pi, 0, -pi/2, test_channel.qr[system_qubits[0]])
preparation_circuit.u3(pi/4, 0, pi, test_channel.qr[system_qubits[1]])

preparation_circuit.cx(test_channel.qr[system_qubits[0]], identity_channel.qr[0])
preparation_circuit.cx(test_channel.qr[system_qubits[1]], identity_channel.qr[1])
circuit = preparation_circuit + test_channel + identity_channel

launcher = Launcher(parameters['token'], parameters['backend_name'], parameters['shots'])
choi = launcher.run(circuit, meas_qubits=identity_channel.get_system_qubits() +
                                         test_channel.get_system_qubits())[0]

choi = np.delete(choi, [3, 7, 11, 15, 12, 13, 14], 0)
choi = np.delete(choi, [3, 7, 11, 15, 12, 13, 14], 1)

print(fidelity(choi, create_theory_choi_matrix(channel_class.get_theory_channel())))
