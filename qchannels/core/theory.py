#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from scipy.linalg import sqrtm
import numpy as np

DIM = 3


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
    """
    R. Jozsa, Fidelity for mixed quantum states. J. Modern Opt. 41, 2315–2323 (1994)
    https://arxiv.org/pdf/quant-ph/0408063.pdf
    """
    return np.trace(sqrtm(
        sqrtm(rho1)@rho2@sqrtm(rho1)
    ))**2


def create_theory_choi_matrix(channel, dim=DIM):
    """
    :param channel: function
    """
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
    return np.transpose(np.linalg.inv(ER))

if __name__ == '__main__':
    from importlib import import_module

    module = import_module('qchannels.channels')
    channel_class_names = filter(lambda x: 'Circuit' in x and 'AbstractChannel' not in x, dir(module))
    for class_name in channel_class_names:
        channelClass = getattr(import_module('qchannels.channels'), class_name)
        choi = create_theory_choi_matrix(channelClass.get_theory_channel())
        assert(0.999 < fidelity(choi, choi) < 1.001)
