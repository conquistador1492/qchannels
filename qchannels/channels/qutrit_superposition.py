from qchannels.channels.abstract import AbstractChannelCircuit
from math import acos, pi, sqrt


class QutritSuperpositionCircuit(AbstractChannelCircuit):
    """
    Transform |00> state to (|00>+|01>+|10>)/sqrt(3) state
    """
    def create_circuit(self, q_regs):
        self.u3(2 * acos(1 / sqrt(3)), 0, 0, q_regs[0])
        self.u3(0, 0, -pi / 2, q_regs[1])
        self.cx(q_regs[0], q_regs[1])
        self.u3(pi / 4, 0, -pi / 2, q_regs[1])
        self.cx(q_regs[0], q_regs[1])
        self.u3(pi, 0, -pi / 2, q_regs[0])
        self.u3(pi / 4, 0, pi, q_regs[1])

    @staticmethod
    def get_theory_channel():
        raise NotImplementedError

    NUM_QUBITS = 2
    REL_SYSTEM_QUBITS = [0, 1]
