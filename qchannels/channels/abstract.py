from abc import ABC, abstractmethod

from qiskit import QuantumCircuit, IBMQ, QuantumRegister, ClassicalRegister

from qchannels.core.tools import IBMQ_SIMULATOR


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

    def __init__(self, name=None, q_reg=None, c_reg=None,
                 backend_name=IBMQ_SIMULATOR):
        """
        :param backend_name: str. there is necessary for circuit that depend on topology of backend
        """
        backend = next(filter(
            lambda backend: backend.name() == backend_name, IBMQ.backends()
        ))

        self.coupling_map = backend.configuration()['coupling_map']
        self.backend = backend
        self.set_regs(q_reg, c_reg)

        super().__init__(self.qr, self.cr, name=name)

        self.create_circuit()

    def set_regs(self, q_reg, c_reg):
        num_qubits = self.backend.configuration()['n_qubits']
        if q_reg is None:
            self.qr = QuantumRegister(num_qubits)
        else:
            self.qr = q_reg
        if c_reg is None:
            self.cr = ClassicalRegister(num_qubits)
        else:
            self.cr = c_reg

    def get_system_qubits(self):
        """
        Channel consist of system and environmental qubits
        """
        return [i for i in range(self.qr.size)]

    def get_env_qubits(self):
        """
        Channel consist of system and environmental qubits
        """
        system_qubits = self.get_system_qubits()
        return [i for i in range(self.qr.size) if i not in system_qubits]

    # def __call__(self, channel):
    #     """
    #     F1(F2(rho))
    #     :param channel: AbstractChannelCircuit
    #     """
    #     raise NotImplementedError
    #
    def __mul__(self, other):
        """
        Tensor product
        """
        raise NotImplementedError
