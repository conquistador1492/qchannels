#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import numpy as np
from scipy.linalg import sqrtm

DIM = 3
Jx = np.array([
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
])/np.sqrt(2)
Jy = np.array([
    [0, -1j, 0],
    [1j, 0, -1j],
    [0, 1j, 0]
])/np.sqrt(2)
Jz = np.diag([1, 0, -1])
S = np.array([
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0]
])  # 00 -> -1, 01 -> 0, 10 -> 1


def get_state(a, *, dim=None):
    if dim is None:
        dim = DIM
    vals = [[0] for i in range(dim)]
    vals[a][0] = 1
    return np.array(vals)


def get_qutrit_density_matrix_basis():
    basis_states = np.array(
        [get_state(a) for a in [0b00, 0b01, 0b10]] +
        [(get_state(a) + get_state(b)) / np.sqrt(2) for a, b in [(0b00, 0b01), (0b00, 0b10), (0b01, 0b10)]] +
        [(get_state(a) + 1j * get_state(b)) / np.sqrt(2) for a, b in [(0b00, 0b01), (0b00, 0b10), (0b01, 0b10)]]
    )
    return np.array(
        [state@np.transpose(np.conj(state)) for state in basis_states]
    )


def fidelity(rho1, rho2):
    return np.trace(sqrtm(
        sqrtm(rho1)@rho2@sqrtm(rho1)
    ))


def theory_landau_channel(rho):
    global Jx, Jy, Jz
    rho = S@rho@S
    return S@(Jx@rho@Jx + Jy@rho@Jy + Jz@rho@Jz)@S/2


def create_theory_choi_matrix(channel=None, dim=DIM):
    if channel is None:
        channel = theory_landau_channel

    blocks = [[None for i in range(dim)] for j in range(dim)]
    for i in range(dim):
        for j in range(dim):
            rho = np.zeros((dim, dim))
            rho[i,j] = 1
            blocks[i][j] = np.copy(channel(rho))
    return np.block(blocks)/dim


def get_matrix_from_tomography_to_eij(matrices=None):
    if matrices is None:
        matrices = get_qutrit_density_matrix_basis()

    dim = matrices[0].shape[0]
    ER = np.zeros((dim**2, dim**2), dtype=complex)
    for k, matrix in enumerate(matrices):
        for i in range(dim):
            for j in range(dim):
                ER[3 * i + j, k] = matrix[i, j]
    return np.linalg.inv(ER)

if __name__ == '__main__':
    choi = create_theory_choi_matrix()
    assert(0.999 < fidelity(choi, choi) < 1.001)