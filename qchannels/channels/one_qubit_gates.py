from qchannels.channels.abstract import AbstractChannelCircuit, MaskRegister

import numpy as np
from collections import defaultdict


class OneQubitGates(AbstractChannelCircuit):
    REL_SYSTEM_QUBITS = [0]
    REL_ENV_QUBITS = []

    def __init__(self, theta_dict=None, phi_dict=None, lambda_dict=None, **kwargs):
        """
        # TODO rename
        :param theta_dict: dict, list or np.array
        :param phi_dict: dict, list or np.array
        :param lambda_dict: dict, list or np.array

        [[cos(theta/2), -exp(i*lambda)*sin(theta/2)],
         [exp(i*phi)*sin(theta/2), exp(i*(lambda + phi))*cos(theta/2)]]
        """

        theta_dict = {} if theta_dict is None else theta_dict
        phi_dict = {} if phi_dict is None else phi_dict
        lambda_dict = {} if lambda_dict is None else lambda_dict

        if isinstance(theta_dict, (list, np.ndarray, np.generic)):
            theta_dict = {i: theta_dict[i] for i in range(len(theta_dict))}

        if isinstance(phi_dict, (list, np.ndarray, np.generic)):
            phi_dict = {i: phi_dict[i] for i in range(len(phi_dict))}

        if isinstance(lambda_dict, (list, np.ndarray, np.generic)):
            lambda_dict = {i: lambda_dict[i] for i in range(len(lambda_dict))}

        self.theta_dict, self.phi_dict, self.lambda_dict = [defaultdict(int) for i in range(3)]

        self.theta_dict.update(theta_dict)
        self.phi_dict.update(phi_dict)
        self.lambda_dict.update(lambda_dict)

        if 'rel_system_qubits' not in kwargs:
            rel_system_qubits = list(set(
                list(self.theta_dict.keys()) + list(self.phi_dict.keys()) +
                list(self.lambda_dict.keys())
            ))
            if not rel_system_qubits:
                rel_system_qubits = self.REL_SYSTEM_QUBITS
            kwargs['rel_system_qubits'] = rel_system_qubits

        super().__init__(**kwargs)

    def create_circuit(self, q_regs: MaskRegister):
        for qubit in self.rel_system_qubits + self.rel_env_qubits:
            self.u3(self.theta_dict[qubit], self.phi_dict[qubit], self.lambda_dict[qubit],
                    q_regs[qubit])

    @staticmethod
    def get_theory_channel():
        # TODO
        raise NotImplementedError()
