from abc import ABC, abstractmethod

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer
from qiskit._register import Register

from qchannels.core.tools import LOCAL_SIMULATOR, BACKENDS, IBMQ_SIMULATOR


class MaskRegister:
    def __init__(self, reg: Register, mask=None):
        self.reg = reg
        self.mask = mask if mask is not None else {}

    def __getitem__(self, item):
        return self.reg, self.mask.get(item, item)


class AbstractChannelCircuit(ABC, QuantumCircuit):
    NUM_QUBITS = 5

    # Don't use it directly because it have to be gone though mask.
    # Call get_system_qubits() and get_env_qubits()
    SYSTEM_QUBITS = []
    ENV_QUBITS = []

    @staticmethod
    @abstractmethod
    def get_theory_channel():
        """
        :return: function
        """
        pass

    @abstractmethod
    def create_circuit(self, q_regs: MaskRegister, c_regs: MaskRegister):
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
                 backend_name=LOCAL_SIMULATOR, num_qubits=None,
                 system_qubits=None, env_qubits=None, coupling_map=None):
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

        self.coupling_map = backend.configuration()['coupling_map'] \
            if coupling_map is None else coupling_map
        self.backend = backend
        self.mask = mask if mask is not None else {}
        self.system_qubits = system_qubits if system_qubits is not None else self.SYSTEM_QUBITS
        self.env_qubits = env_qubits if env_qubits is not None else self.ENV_QUBITS

        if num_qubits is not None:
            self.num_qubits = num_qubits
        elif self.backend not in Aer.backends() and self.backend.name() != IBMQ_SIMULATOR:
            self.num_qubits = self.backend.configuration()['n_qubits']
        else:
            self.num_qubits = self.NUM_QUBITS

        if self.mask != {} and max(self.mask.values()) >= self.num_qubits:
            raise Exception("We can't use qubits over initialized(0 < x < self.num_qubits)")

        self.set_regs(q_reg, c_reg)

        super().__init__(self.qr, self.cr, name=name)

        self.create_circuit(self.mqr, self.mcr)

    def set_regs(self, q_reg, c_reg):
        if q_reg is None:
            self.qr = QuantumRegister(self.num_qubits)
        else:
            self.qr = q_reg

        if c_reg is None:
            self.cr = ClassicalRegister(self.num_qubits)
        else:
            self.cr = c_reg

        self.mqr = MaskRegister(self.qr, mask=self.mask)
        self.mcr = MaskRegister(self.cr, mask=self.mask)

    def get_system_qubits(self):
        """
        Channel consist of system and environmental qubits
        """
        return list(map(lambda x: self.mask.get(x, x), self.system_qubits))

    def get_env_qubits(self):
        """
        Channel consist of system and environmental qubits
        """
        return list(map(lambda x: self.mask.get(x, x), self.env_qubits))

    # TODO rename
    def mask_to_real(self, x):
        return self.mask.get(x, x)

    # TODO rename
    def real_to_mask(self, x):
        for key, value in self.mask:
            if value == x:
                return key
        else:
            return x

    def __call__(self, channel):
        """
        TODO

        F1(F2(rho))
        :param channel: AbstractChannelCircuit
        """
        raise NotImplementedError

    def __mul__(self, other):
        """
        TODO

        Tensor product
        """
        raise NotImplementedError
