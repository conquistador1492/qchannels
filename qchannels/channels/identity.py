from qchannels.channels.abstract import AbstractChannelCircuit


class IdentityCircuit(AbstractChannelCircuit):
    @staticmethod
    def get_theory_channel():
        return lambda rho: rho

    def create_circuit(self, q_regs):
        pass
