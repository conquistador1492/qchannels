from channels.abstract import AbstractChannelCircuit

from math import pi
import numpy as np

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_theory_channel():
        return theory_landau_streater_channel

    def create_circuit(self):
        qr, cr = self.qr, self.cr
        self.u2(pi, pi, qr[0])
        self.h(qr[3])

        self.cnot(qr[3], qr[2])
        self.cnot(qr[2], qr[0])
        self.cnot(qr[3], qr[2])

        self.u2(pi, pi, qr[0])
        self.h(qr[3])

        self.u2(0, 0, qr[1])
        self.u3(pi/4, 0, 0, qr[2])  # maybe u1
        self.y(qr[3])

        self.cnot(qr[1], qr[0])
        self.cnot(qr[3], qr[2])
        self.h(qr[0])
        self.u3(pi/4, 0, pi, qr[2])
        self.cnot(qr[2], qr[0])
        self.h(qr[0])
        self.u3(pi/4, 0, pi, qr[2])
        self.cnot(qr[1], qr[0])
        self.cnot(qr[3], qr[2])

        self.u3(pi / 4, 0, 0, qr[1])
        self.u3(-pi / 4, 0, 0, qr[2])
        self.cnot(qr[2], qr[1])

        self.h(qr[0])
        self.u3(pi/4, 0, pi, qr[1])
        self.cnot(qr[1], qr[0])
        self.u3(3*pi/4, 0, pi, qr[0])
        self.u3(pi/4, 0, pi, qr[1])
        self.cnot(qr[2], qr[1])

        self.u3(-pi/4, 0, 0, qr[1])
        self.h(qr[2])
        self.h(qr[3])
        self.cnot(qr[3], qr[2])
        self.h(qr[3])
        self.u2(0, 0, qr[2])

        self.cnot(qr[2], qr[0])
        self.u3(pi/4, 0, 0, qr[0])
        self.cnot(qr[1], qr[0])
        self.u3(-pi/4, 0, 0, qr[0])
        self.cnot(qr[2], qr[0])
        self.u3(-pi/4, 0, 0, qr[0])
