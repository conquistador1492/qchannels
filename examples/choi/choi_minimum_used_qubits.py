#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import numpy as np

from qchannels.core.launcher import Launcher
from qchannels.core.manage_parameters import set_parameters
from qchannels.core.theory import get_matrix_from_tomography_to_eij, get_qutrit_density_matrix_basis
from qchannels.core.theory import fidelity, create_theory_choi_matrix

from qiskit import QuantumCircuit

from basis import QUTRIT_BASIS_FUNC

parameters = set_parameters('Calculate Choi Matrix and fidelity between experiment '
                            'and theory prediction')

channel_class = parameters['channel_class']
channel = channel_class(backend_name=parameters['backend_name'])

launcher = Launcher(parameters['token'], parameters['backend_name'], parameters['shots'])

circuits = []
for rho_f in QUTRIT_BASIS_FUNC:
    qc = QuantumCircuit(channel.qr, channel.cr)
    rho_f(channel.qr, channel.cr, qc)
    qc += channel
    qc.name = channel_class.__name__.lower() + '_' + qc.name
    circuits.append(qc)

matrices = launcher.run(circuits, channel.get_system_qubits())

matrices = list(map(lambda rho: rho[:3,:3], matrices))

print('Fidelity of tomography')
theory_channel = channel.get_theory_channel()
for i, rho in enumerate(get_qutrit_density_matrix_basis()):
    print(fidelity(theory_channel(rho), matrices[i]))
print('=======')

matrices = np.array(matrices)
tomo_to_eij = get_matrix_from_tomography_to_eij()
eij_matrices = [[None for i in range(3)] for j in range(3)]
for i in range(3):
    for j in range(3):
        eij_matrices[i][j] = np.tensordot(tomo_to_eij[3*i+j,:], matrices, axes=(0, 0))
choi_exp = np.block(eij_matrices)/3
print(fidelity(choi_exp, create_theory_choi_matrix(theory_channel)))
