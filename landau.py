from qiskit import QuantumCircuit
from math import pi


class LandauCircuit(QuantumCircuit):
    def cnot(self, a, b):
        if self.coupling_map == 'all-to-all' or [a[1], b[1]] in self.coupling_map:
            self.cx(a, b)
        elif [b[1], a[1]] in self.coupling_map:
            self.h(a)
            self.h(b)
            self.cx(b, a)
            self.h(a)
            self.h(a)
        else:
            raise Exception(f"We can't put CNOT here. {a[1], b[1]}")

    def __init__(self, *regs, name=None, coupling_map=None):
        super().__init__(*regs, name=name)
        self.coupling_map = coupling_map
        self.qr = list(self.get_qregs().values())[0]
        self.cr = list(self.get_cregs().values())[0]

        self.landau_scheme()

    def landau_scheme(self):
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
        self.u3(pi / 4, 0, 0, qr[2])
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