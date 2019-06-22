from qchannels.channels import AbstractChannelCircuit

import numpy as np


class HadamardCircuit(AbstractChannelCircuit):
    REL_SYSTEM_QUBITS = [0]  # It is require only one qubit

    def create_circuit(self, q_regs):
        self.h(q_regs[0])

    @staticmethod
    def get_theory_channel():
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        return lambda rho: H@rho@H
