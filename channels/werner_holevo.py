from channels.abstract import AbstractChannelCircuit
from math import pi
import numpy as np

DIM = 3


def theory_werner_holevo(rho, dim=DIM):
    return (np.eye(dim)*np.trace(rho) - np.transpose(rho))/(dim - 1)


class WernerHolevoCircuit(AbstractChannelCircuit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_circuit(self):
        qr, cr = self.qr, self.cr

        self.x(qr[0])
        self.u2(0, 0, qr[1])
        self.u3(pi / 4, 0, 0, qr[2])  # maybe u1
        self.y(qr[3])

        self.cnot(qr[1], qr[0])
        self.cnot(qr[3], qr[2])
        self.h(qr[0])
        self.u3(pi / 4, 0, pi, qr[2])
        self.cnot(qr[2], qr[0])
        self.h(qr[0])
        self.u3(pi / 4, 0, pi, qr[2])
        self.cnot(qr[1], qr[0])
        self.cnot(qr[3], qr[2])

        self.u3(pi / 4, 0, 0, qr[1])
        self.u3(-pi / 4, 0, 0, qr[2])
        self.cnot(qr[2], qr[1])

        self.h(qr[0])
        self.u3(pi / 4, 0, pi, qr[1])
        self.cnot(qr[1], qr[0])
        self.u3(3 * pi / 4, 0, pi, qr[0])
        self.u3(pi / 4, 0, pi, qr[1])
        self.cnot(qr[2], qr[1])

        self.u3(-pi / 4, 0, 0, qr[1])
        self.h(qr[2])
        self.h(qr[3])
        self.cnot(qr[3], qr[2])
        self.h(qr[3])
        self.u2(0, 0, qr[2])

        self.cnot(qr[2], qr[0])
        self.u3(pi / 4, 0, 0, qr[0])
        self.cnot(qr[1], qr[0])
        self.u3(-pi / 4, 0, 0, qr[0])
        self.cnot(qr[2], qr[0])
        self.u3(-pi / 4, 0, 0, qr[0])

    @staticmethod
    def get_theory_channel():
        return theory_werner_holevo
