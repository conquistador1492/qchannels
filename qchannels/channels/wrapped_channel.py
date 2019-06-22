from qchannels.channels import OneQubitGates, AbstractChannelCircuit


class WrappedChannel(AbstractChannelCircuit):
    def __new__(cls, channel: AbstractChannelCircuit,
                theta_dict_before=None, phi_dict_before=None, lambda_dict_before=None,
                theta_dict_after=None, phi_dict_after=None, lambda_dict_after=None):
        """
        :param theta_dict_before: dict, list or np.array
        :param phi_dict_before: dict, list or np.array
        :param lambda_dict_before: dict, list or np.array
        :param theta_dict_after: dict, list or np.array
        :param phi_dict_after: dict, list or np.array
        :param lambda_dict_after: dict, list or np.array
        """
        qr = channel.qr
        mask = channel.mask

        return OneQubitGates(
            theta_dict_before, phi_dict_before, lambda_dict_before,
            qr=qr, mask=mask, rel_system_qubits=channel.rel_system_qubits
        ) + channel + OneQubitGates(
            theta_dict_after, phi_dict_after, lambda_dict_after,
            qr=qr, mask=mask, rel_system_qubits=channel.rel_system_qubits
        )
