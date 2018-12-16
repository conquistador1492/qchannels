from math import pi

import numpy as np

from qchannels.channels.abstract import AbstractChannelCircuit
from qchannels.core.tools import SIMULATORS

DIM = 3


def theory_werner_holevo(rho, dim=DIM):
    return (np.eye(dim)*np.trace(rho) - np.transpose(rho))/(dim - 1)


class WernerHolevoCircuit(AbstractChannelCircuit):
    REL_SYSTEM_QUBITS = [0, 3]
    REL_ENV_QUBITS = [1, 2]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_circuit(self, q_regs, c_regs):
        self.x(q_regs[0])
        self.u2(0, 0, q_regs[1])
        self.u3(pi / 4, 0, 0, q_regs[2])  # maybe u1
        self.y(q_regs[3])

        self.cnot(q_regs[1], q_regs[0])
        self.cnot(q_regs[3], q_regs[2])
        self.h(q_regs[0])
        self.u3(pi / 4, 0, pi, q_regs[2])
        self.cnot(q_regs[2], q_regs[0])
        self.h(q_regs[0])
        self.u3(pi / 4, 0, pi, q_regs[2])
        self.cnot(q_regs[1], q_regs[0])
        self.cnot(q_regs[3], q_regs[2])

        self.u3(pi / 4, 0, 0, q_regs[1])
        self.u3(-pi / 4, 0, 0, q_regs[2])
        self.cnot(q_regs[2], q_regs[1])

        self.h(q_regs[0])
        self.u3(pi / 4, 0, pi, q_regs[1])
        self.cnot(q_regs[1], q_regs[0])
        self.u3(3 * pi / 4, 0, pi, q_regs[0])
        self.u3(pi / 4, 0, pi, q_regs[1])
        self.cnot(q_regs[2], q_regs[1])

        self.u3(-pi / 4, 0, 0, q_regs[1])
        self.h(q_regs[2])
        self.h(q_regs[3])
        self.cnot(q_regs[3], q_regs[2])
        self.h(q_regs[3])
        self.u2(0, 0, q_regs[2])

        self.cnot(q_regs[2], q_regs[0])
        self.u3(pi / 4, 0, 0, q_regs[0])
        self.cnot(q_regs[1], q_regs[0])
        self.u3(-pi / 4, 0, 0, q_regs[0])
        self.cnot(q_regs[2], q_regs[0])
        self.u3(-pi / 4, 0, 0, q_regs[0])

    @staticmethod
    def get_theory_channel():
        return theory_werner_holevo
