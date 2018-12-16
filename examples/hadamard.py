#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from qchannels.channels.abstract import AbstractChannelCircuit
from qchannels.core.manage_parameters import set_parameters
from qchannels.core.launcher import Launcher
from qchannels.core.theory import fidelity, get_state, get_density_matrix_from_state

import numpy as np


class Hadamard(AbstractChannelCircuit):
    REL_SYSTEM_QUBITS = [0]  # It is require only one qubit

    def create_circuit(self, q_regs, c_regs):
        self.h(q_regs[0])

    @staticmethod
    def get_theory_channel():
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        return lambda rho: H@rho@H


parameters = set_parameters('Test Hadamard transformation')

mask = {0: 3}  # It's optional. It change a qubit in channel, more detail in AbstractChannelCircuit
channel = Hadamard(backend_name=parameters['backend_name'], mask=mask)
launcher = Launcher(token=parameters['token'], backend_name=parameters['backend_name'],
                    shots=parameters['shots'])
rho = launcher.run(channel, meas_qubits=channel.system_qubits)[0]
print(fidelity(rho, channel.get_theory_channel()(
    get_density_matrix_from_state(get_state(0, dim=2))
)))
