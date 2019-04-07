from abc import ABC, abstractmethod

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, BasicAer
from qiskit.circuit.register import Register

from qchannels.core.tools import LOCAL_SIMULATOR, BACKENDS, IBMQ_SIMULATOR


class MaskRegister:
    def __init__(self, reg: Register, mask=None):
        self.reg = reg
        self.mask = mask if mask is not None else {}

    def __getitem__(self, item):
        return self.reg, self.mask.get(item, item)


class AbstractChannelCircuit(ABC, QuantumCircuit):
    """
    Abstract class for channels. Unitary gates should be written in create_circuit() function.
    Those registers have a relative address and its orders saved in self.rel_system_qubits and
    self.rel_env_qubits. The real address is written in self.system_qubits and
    self.env_qubits using mask in __init__ function.
    E.g. consider Hadamard transformation with mask {0: 5}. In create_circuit()
    write self.h(q_regs[0]) and self.REL_SYSTEM_QUBITS = [0].
    Then instance has self.rel_system_qubits = [0] and self.system_qubits = [5].
    Also, self.qr, self.rel_qr, self.cr, self.cr are relative and absolute registers.
    """
    NUM_QUBITS = 5

    REL_SYSTEM_QUBITS = []
    REL_ENV_QUBITS = []

    @staticmethod
    def get_theory_channel():
        """
        :return: function
        """
        raise NotImplementedError

    @abstractmethod
    def create_circuit(self, q_regs: MaskRegister, c_regs: MaskRegister):
        """
        Built circuit from gates.
        :param q_regs: quantum bits
        :param c_regs: classical bits
        """
        pass

    def cnot(self, a, b):
        if self.coupling_map is None or [a[1], b[1]] in self.coupling_map:
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
                 rel_system_qubits=None, env_qubits=None, coupling_map=None):
        """
        :param mask: dict. Circuit for the channel can be defined for first qubits and
        changing a mask you can move channel on specific qubits. In the mask,
        a key is qubit using in create_circuit and this value is real qubit in a circuit.
        If the mask doesn't have a key, then its same as the key is equal to value.
        For example, let us suppose, the channel is CNOT with a zero qubit as control and
        first as a target. If the mask is equal to  {0: 1, 1: 2}
        then first qubit is control and second qubit is a target.
        :param backend_name: str. There is necessary for circuit that depend on topology of backend.
        :param coupling_map: backend.configuration()['coupling_map'] (default: 'all-to-all')
        """
        backend = next(filter(lambda backend: backend.name() == backend_name, BACKENDS))

        self.coupling_map = getattr(backend.configuration(), 'coupling_map', None) \
            if coupling_map is None else coupling_map
        self.backend = backend
        self.mask = mask if mask is not None else {}
        self.rel_system_qubits = rel_system_qubits if rel_system_qubits is not None else self.REL_SYSTEM_QUBITS
        self.rel_env_qubits = env_qubits if env_qubits is not None else self.REL_ENV_QUBITS
        self.system_qubits = list(map(lambda x: self.mask.get(x, x), self.rel_system_qubits))
        self.env_qubits = list(map(lambda x: self.mask.get(x, x), self.rel_env_qubits))

        if num_qubits is not None:
            self.num_qubits = num_qubits
        elif q_reg is not None:
            if isinstance(q_reg, QuantumRegister):
                self.num_qubits = q_reg.size
            elif isinstance(q_reg, MaskRegister):
                self.num_qubits = q_reg.reg.size
        elif self.backend not in BasicAer.backends() and self.backend.name() != IBMQ_SIMULATOR:
            self.num_qubits = self.backend.configuration().n_qubits
        else:
            self.num_qubits = max([*self.system_qubits, *self.env_qubits]) + 1

        if self.mask != {} and max([*self.system_qubits, *self.env_qubits]) >= self.num_qubits:
            raise Exception(f"We can't use qubits over initialized(0 < x < {self.num_qubits})")

        self.set_regs(q_reg, c_reg)

        super().__init__(self.qr, self.cr, name=name)

        self.create_circuit(self.rel_qr, self.rel_cr)

    def set_regs(self, q_reg, c_reg):
        if q_reg is None:
            self.qr = QuantumRegister(self.num_qubits)
        else:
            self.qr = q_reg

        if c_reg is None:
            self.cr = ClassicalRegister(self.num_qubits)
        else:
            self.cr = c_reg

        self.rel_qr = MaskRegister(self.qr, mask=self.mask)
        self.rel_cr = MaskRegister(self.cr, mask=self.mask)

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

    # TODO implement add, create new class for addition

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
