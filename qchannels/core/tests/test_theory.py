from unittest import TestCase
import numpy as np
from qchannels.core.theory import create_channel_from_choi_matrix, partial_trace_with_halves
from qchannels.core.theory import get_qutrit_density_matrix_basis
from qchannels.core.theory import create_choi_matrix_from_channel, get_kraus_operators_from_choi
from qchannels.channels.identity import IdentityCircuit


class TestTheory(TestCase):
    def assertNumpyArrayAlmostEqual(self, first, second, *args, **kwargs):
        self.assertAlmostEqual(np.sum(np.abs(first - second)), 0, *args, **kwargs)

    def test_partial_trace(self):
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        a = a / np.trace(a)
        b = b / np.trace(b)
        AB = np.kron(a, b)
        self.assertAlmostEqual(np.sum(np.abs(partial_trace_with_halves(AB, 1) - a)), 0)
        self.assertAlmostEqual(np.sum(np.abs(partial_trace_with_halves(AB, 2) - b)), 0)

        self.assertAlmostEqual(np.sum(np.abs(partial_trace_with_halves(np.kron(b, a), 2) - a)), 0)
        self.assertAlmostEqual(np.sum(np.abs(partial_trace_with_halves(np.kron(b, a), 1) - b)), 0)

        c = np.array([[10, 0], [0, 20]])
        c = c / np.trace(c)
        self.assertAlmostEqual(np.sum(np.abs(partial_trace_with_halves(np.kron(a, c), 1) - a)), 0)
        self.assertAlmostEqual(np.sum(np.abs(partial_trace_with_halves(np.kron(a, c), 2) - c)), 0)

        self.assertAlmostEqual(np.trace(np.abs(partial_trace_with_halves(AB, 1))), 1)
        self.assertAlmostEqual(np.trace(np.abs(partial_trace_with_halves(AB, 2))), 1)

    def test_create_choi_matrix_from_channel(self):
        X, Y, Z = np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])
        self.assertNumpyArrayAlmostEqual(
            create_choi_matrix_from_channel(lambda rho: rho, dim=2),
            np.array([
                [1, 0, 0, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 0, 0, 1]
            ]) / 2
        )
        self.assertNumpyArrayAlmostEqual(
            create_choi_matrix_from_channel(lambda rho: X@rho@X, dim=2),
            np.array([
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0]
            ]) / 2
        )
        self.assertNumpyArrayAlmostEqual(
            create_choi_matrix_from_channel(lambda rho: Y@rho@Y, dim=2),
            np.array([
                [0, 0, 0, 0],
                [0, 1, -1, 0],
                [0, -1, 1, 0],
                [0, 0, 0, 0]
            ]) / 2
        )
        self.assertNumpyArrayAlmostEqual(
            create_choi_matrix_from_channel(lambda rho: Z@rho@Z, dim=2),
            np.array([
                [1, 0, 0, -1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [-1, 0, 0, 1]
            ]) / 2
        )

    def test_channel_to_matrix(self):
        # Choi matrix for Id channel
        choi = np.array([
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0, 1],
        ])/3
        self.assertNumpyArrayAlmostEqual(
            create_choi_matrix_from_channel(lambda rho: rho, dim=3), choi
        )
        self.assertAlmostEqual(np.trace(choi), 1)

        channel = create_channel_from_choi_matrix(choi)
        for rho in get_qutrit_density_matrix_basis():
            self.assertNumpyArrayAlmostEqual(channel(rho), rho, msg=f"\n{rho}\n\n {channel(rho)}")

        gates = [np.eye(2), np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]),
                 np.diag([1, -1])]
        bases = [np.diag([1, 0]), np.array([[0, 1], [0, 0]]), np.array([[0, 0], [1, 0]]),
                 np.diag([0, 1]), np.array([[0, 1j], [0, 0]]), np.array([[0, 0], [1j, 0]]),
                 np.diag([1j, 0]), np.diag([0, 1])]
        for gate in gates:
            channel = lambda rho: gate@rho@(gate.transpose().conj())
            choi = create_choi_matrix_from_channel(channel, dim=2)
            new_channel = create_channel_from_choi_matrix(choi)
            for rho in bases:
                self.assertNumpyArrayAlmostEqual(
                    new_channel(rho), channel(rho),
                    msg=f"\n{new_channel(rho)}\n {channel(rho)}\n gate: {gate}\n"
                        f"initial state: {rho}\n choi: {choi}"
                )

    def assertKrausOperators(self, a, b):
        self.assertEqual(len(a), len(b))
        for i, array in enumerate(b):
            self.assertNumpyArrayAlmostEqual(a[i], b[i])

    def test_get_kraus_operators_from_choi(self):
        CNOT = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        cnot_channel = lambda rho: CNOT@rho@CNOT

        choi = create_choi_matrix_from_channel(cnot_channel, dim=4)
        krauses = get_kraus_operators_from_choi(choi)
        theory_krauses = [CNOT]

        self.assertKrausOperators(krauses, theory_krauses)

        krauses = get_kraus_operators_from_choi(create_choi_matrix_from_channel(
            IdentityCircuit.get_theory_channel(), dim=4
        ))
        theory_krauses = [np.eye(4)]

        self.assertKrausOperators(krauses, theory_krauses)

        n_X, n_Y, n_Z = np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])
        for pauli in [n_X, n_Y, n_Z]:
            krauses = get_kraus_operators_from_choi(create_choi_matrix_from_channel(
                lambda rho: pauli@rho@np.conj(pauli.T), dim=2
            ))
            theory_krauses = [pauli]
            try:
                self.assertKrausOperators(krauses, theory_krauses)
            except AssertionError:
                self.assertKrausOperators(krauses, list(map(lambda x: -x, theory_krauses)))

        krauses = get_kraus_operators_from_choi(create_choi_matrix_from_channel(
            lambda rho: (n_X@rho@np.conj(n_X.T) + n_Z@rho@np.conj(n_Z.T))/2, dim=2
        ))
        theory_krauses = [n_Z/np.sqrt(2), n_X/np.sqrt(2)]
        try:
            self.assertKrausOperators(krauses, theory_krauses)
        except AssertionError:
            print(krauses)
            raise

