from abc import ABC, abstractmethod

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, BasicAer
from qiskit.circuit.register import Register

from qchannels.core.tools import LOCAL_SIMULATOR, BACKENDS, IBMQ_SIMULATOR

from copy import deepcopy


class MaskRegister:
    def __init__(self, reg: Register, mask=None):
        self.reg = reg
        self.mask = mask if mask is not None else {}

    def __getitem__(self, item):
        return self.reg, self.mask.get(item, item)


class AbstractChannelCircuit(ABC, QuantumCircuit):
    """
    Abstract class for quantum channels. Unitary gates should be written in create_circuit() function.
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
    def create_circuit(self, q_regs: MaskRegister):
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

    def __init__(self, name=None, qr=None, mask=None,
                 backend_name=LOCAL_SIMULATOR, num_qubits=None,
                 rel_system_qubits=None, rel_env_qubits=None, coupling_map=None):
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
        self.rel_env_qubits = rel_env_qubits if rel_env_qubits is not None else self.REL_ENV_QUBITS
        self.system_qubits = list(map(lambda x: self.mask.get(x, x), self.rel_system_qubits))
        self.env_qubits = list(map(lambda x: self.mask.get(x, x), self.rel_env_qubits))

        if num_qubits is not None:
            self.num_qubits = num_qubits
        elif qr is not None:
            if isinstance(qr, QuantumRegister):
                self.num_qubits = qr.size
            elif isinstance(qr, MaskRegister):
                self.num_qubits = qr.reg.size
        elif self.backend not in BasicAer.backends() and self.backend.name() != IBMQ_SIMULATOR:
            self.num_qubits = self.backend.configuration().n_qubits
        else:
            self.num_qubits = max([*self.system_qubits, *self.env_qubits]) + 1

        if self.mask != {} and max([*self.system_qubits, *self.env_qubits]) >= self.num_qubits:
            raise Exception(f"We can't use qubits over initialized(0 < x < {self.num_qubits})")

        self.set_regs(qr)

        super().__init__(self.qr, name=name)

        self.create_circuit(self.rel_qr)

    def set_regs(self, qr):
        if qr is None:
            self.qr = QuantumRegister(self.num_qubits)
        elif isinstance(qr, MaskRegister):
            self.qr = qr.reg
        else:
            self.qr = qr

        self.rel_qr = MaskRegister(self.qr, mask=self.mask)

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

    def __iadd__(self, other):
        if not isinstance(other, QuantumCircuit):
            raise TypeError('Terms must be `QuantumCircuit`')

        if self.qr != other.qregs[0]:
            raise TypeError('The circuits have different quantum registers')

        if other.cregs:
            raise NotImplementedError("The circuits mustn't have classical registers")

        self.data += other.data

        if not isinstance(other, AbstractChannelCircuit):
            used_qubits = list(set(map(lambda x: x[1], sum(map(lambda x: x[1], other.data), []))))

            for qubit in used_qubits:
                if qubit not in self.system_qubits:
                    self.system_qubits.append(qubit)
        else:
            for key, value in other.mask.items():
                if key not in self.mask:
                    self.mask[key] = value

            for qubit in other.rel_system_qubits:
                if qubit not in self.rel_system_qubits and\
                        self.mask.get(qubit, qubit) not in self.system_qubits:
                    self.rel_system_qubits.append(qubit)
                    self.system_qubits.append(self.mask.get(qubit, qubit))

            for qubit in other.rel_env_qubits:
                if qubit not in self.rel_env_qubits and \
                                self.mask.get(qubit, qubit) not in self.env_qubits:
                    self.rel_env_qubits.append(qubit)
                    self.env_qubits.append(self.mask.get(qubit, qubit))

            for qubit in other.system_qubits:
                if qubit not in self.system_qubits:
                    self.system_qubits.append(qubit)

            for qubit in other.env_qubits:
                if qubit not in self.env_qubits:
                    self.env_qubits.append(qubit)

            self.rel_qr = MaskRegister(self.qr, mask=self.mask)

        # TODO
        self.get_theory_channel = AbstractChannelCircuit.get_theory_channel
        return self

    def __add__(self, other):
        first_term = deepcopy(self)
        first_term += other
        return first_term

    def __radd__(self, other):
        return circuit_to_channel(other) + self


def circuit_to_channel(circuit: QuantumCircuit):
    channel = type('QuantumChannelCircuit', (AbstractChannelCircuit, ), {
        'create_circuit': (lambda self, rel_qr: None)
    })(qr=circuit.qregs[0], rel_system_qubits=list(set(
        map(lambda x: x[1], sum(map(lambda x: x[1], circuit.data), [])))
    ))
    channel.data = circuit.data
    return channel
