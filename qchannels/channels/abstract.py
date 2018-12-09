from abc import ABC, abstractmethod

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer
from qiskit._register import Register

from qchannels.core.tools import LOCAL_SIMULATOR, BACKENDS, IBMQ_SIMULATOR


class MaskRegister(Register):
    def __init__(self, *args, mask=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mask = mask if mask is not None else {}

    def __getitem__(self, item):
        return super().__getitem__(self.mask.get(item, item))

    def __setitem__(self, key, value):
        super().__setitem__(self.mask.get(key, key), value)


class MaskQuantumRegister(MaskRegister, QuantumRegister):
    pass


class MaskClassicalRegister(MaskRegister, ClassicalRegister):
    pass


class AbstractChannelCircuit(ABC, QuantumCircuit):
    NUM_QUBITS = 5
    @staticmethod
    @abstractmethod
    def get_theory_channel():
        """
        :return: function
        """
        pass

    @abstractmethod
    def create_circuit(self, q_regs, c_regs):
        """
        Built circuit from gates.
        :param q_regs: quantum bits
        :param c_regs: classical bits
        """
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

    def __init__(self, name=None, q_reg=None, c_reg=None, mask=None,
                 backend_name=LOCAL_SIMULATOR, num_qubits=None):
        """
        :param mask: dict. Circuit for channel can be defined for first qubits and
         changing mask you can move channel on specific qubits.
         In mask key is qubit using in create_circuit and this value is real qubit in a circuit.
         If mask doesn't have a key, then its same as key is equal to value.
         For example, let us suppose, channel is CNOT with zero qubit as control
         and first as target. If mask is equal to  {0: 1, 1: 2} then first qubit is control and
         second qubit is target.
        :param backend_name: str. There is necessary for circuit that depend on topology of backend.
        :param coupling_map: backend.configuration()['coupling_map'] (default: 'all-to-all')
        """
        backend = next(filter(lambda backend: backend.name() == backend_name, BACKENDS))

        self.coupling_map = backend.configuration()['coupling_map']
        self.backend = backend
        self.mask = mask

        if num_qubits is not None:
            self.num_qubits = num_qubits
        elif self.backend not in Aer.backends() and self.backend.name() != IBMQ_SIMULATOR:
            self.num_qubits = self.backend.configuration()['n_qubits']
        else:
            self.num_qubits = self.NUM_QUBITS
        self.set_regs(q_reg, c_reg)

        super().__init__(self.qr, self.cr, name=name)

        self.create_circuit(self.qr, self.cr)

    def set_regs(self, q_reg, c_reg):
        self.qr = MaskQuantumRegister(self.num_qubits, mask=self.mask) if q_reg is None else q_reg
        self.cr = MaskClassicalRegister(self.num_qubits, mask=self.mask) if c_reg is None else c_reg

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

    def __call__(self, channel):
        """
        F1(F2(rho))
        :param channel: AbstractChannelCircuit
        """
        raise NotImplementedError

    def __mul__(self, other):
        """
        Tensor product
        """
        raise NotImplementedError
