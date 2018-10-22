from qiskit import QuantumCircuit
from abc import ABC, abstractmethod


class AbstractChannelCircuit(ABC, QuantumCircuit):
    @staticmethod
    @abstractmethod
    def get_theory_channel():
        """
        :return: function
        """
        pass

    @abstractmethod
    def create_circuit(self):
        pass

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

        self.create_circuit()
