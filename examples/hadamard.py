#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from qchannels.channels import HadamardCircuit
from qchannels.core.manage_parameters import set_parameters
from qchannels.core.launcher import Launcher
from qchannels.core.theory import fidelity, get_state, get_density_matrix_from_state

parameters = set_parameters('Test Hadamard transformation')

mask = {0: 3}  # It's optional. It changes a qubit in channel, more details in AbstractChannelCircuit
channel = HadamardCircuit(backend_name=parameters['backend_name'], mask=mask)
launcher = Launcher(token=parameters['token'], backend_name=parameters['backend_name'],
                    shots=parameters['shots'])
rho = launcher.run(channel, meas_qubits=channel.system_qubits)[0]
print(fidelity(rho, channel.get_theory_channel()(
    get_density_matrix_from_state(get_state(0, dim=2))
)))
