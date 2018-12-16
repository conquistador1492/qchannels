from math import pi

import numpy as np

from qchannels.channels.abstract import AbstractChannelCircuit
from qchannels.core.tools import SIMULATORS

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


def theory_landau_streater_channel(rho):
    global Jx, Jy, Jz
    rho = S@rho@S
    return S@(Jx@rho@Jx + Jy@rho@Jy + Jz@rho@Jz)@S/2


class LandauStreaterCircuit(AbstractChannelCircuit):
    REL_SYSTEM_QUBITS = [0, 3]
    REL_ENV_QUBITS = [1, 2]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_theory_channel():
        return theory_landau_streater_channel

    def set_regs(self, q_reg, c_reg):
        if self.backend.name() in [*SIMULATORS, 'ibmqx4']:
            super().set_regs(q_reg, c_reg)
        else:
            raise NotImplementedError

    def create_circuit(self, q_regs, c_regs):
        self.u2(pi, pi, q_regs[0])
        self.h(q_regs[3])

        self.cnot(q_regs[3], q_regs[2])
        self.cnot(q_regs[2], q_regs[0])
        self.cnot(q_regs[3], q_regs[2])

        self.u2(pi, pi, q_regs[0])
        self.h(q_regs[3])

        self.u2(0, 0, q_regs[1])
        self.u3(pi/4, 0, 0, q_regs[2])  # maybe u1
        self.y(q_regs[3])

        self.cnot(q_regs[1], q_regs[0])
        self.cnot(q_regs[3], q_regs[2])
        self.h(q_regs[0])
        self.u3(pi/4, 0, pi, q_regs[2])
        self.cnot(q_regs[2], q_regs[0])
        self.h(q_regs[0])
        self.u3(pi/4, 0, pi, q_regs[2])
        self.cnot(q_regs[1], q_regs[0])
        self.cnot(q_regs[3], q_regs[2])

        self.u3(pi / 4, 0, 0, q_regs[1])
        self.u3(-pi / 4, 0, 0, q_regs[2])
        self.cnot(q_regs[2], q_regs[1])

        self.h(q_regs[0])
        self.u3(pi/4, 0, pi, q_regs[1])
        self.cnot(q_regs[1], q_regs[0])
        self.u3(3*pi/4, 0, pi, q_regs[0])
        self.u3(pi/4, 0, pi, q_regs[1])
        self.cnot(q_regs[2], q_regs[1])

        self.u3(-pi/4, 0, 0, q_regs[1])
        self.h(q_regs[2])
        self.h(q_regs[3])
        self.cnot(q_regs[3], q_regs[2])
        self.h(q_regs[3])
        self.u2(0, 0, q_regs[2])

        self.cnot(q_regs[2], q_regs[0])
        self.u3(pi/4, 0, 0, q_regs[0])
        self.cnot(q_regs[1], q_regs[0])
        self.u3(-pi/4, 0, 0, q_regs[0])
        self.cnot(q_regs[2], q_regs[0])
        self.u3(-pi/4, 0, 0, q_regs[0])
