from unittest import TestCase

from qchannels.channels import HadamardCircuit, WrappedChannel
from qchannels.core.tools import LOCAL_SIMULATOR
from qchannels.core.launcher import Launcher
from qchannels.core.theory import fidelity

from math import pi
import numpy as np


class TestWrappedChannel(TestCase):
    def assertNumpyArrayAlmostEqual(self, first, second, *args, **kwargs):
        self.assertAlmostEqual(np.sum(np.abs(first - second)), 0, *args, **kwargs)

    def test_wrapped_channel(self):
        launcher = Launcher(backend_name=LOCAL_SIMULATOR)
        hadamard = HadamardCircuit()
        wrapped_channel = WrappedChannel(hadamard, theta_dict_before=[pi/2],
                                         lambda_dict_before=[pi])
        self.assertNumpyArrayAlmostEqual(
            launcher.run(wrapped_channel, hadamard.system_qubits)[0],
            np.diag([1, 0]), delta=0.03
        )

        wrapped_channel = WrappedChannel(hadamard, theta_dict_after=[pi/2],
                                         lambda_dict_after=[pi])
        self.assertAlmostEqual(fidelity(
            launcher.run(wrapped_channel, hadamard.system_qubits)[0],
            np.diag([1, 0])
        ), 1, delta=0.03)

        wrapped_channel = WrappedChannel(
            hadamard, theta_dict_before=[pi/2], lambda_dict_before=[pi],
            theta_dict_after=[pi/2], lambda_dict_after=[pi]
        )
        self.assertAlmostEqual(fidelity(
            launcher.run(wrapped_channel, hadamard.system_qubits)[0],
            np.array([[1, 1], [1, 1]])/2
        ), 1, delta=0.03)

        wrapped_channel = WrappedChannel(
            hadamard, theta_dict_before=[pi], lambda_dict_before=[pi]
        )
        self.assertAlmostEqual(fidelity(
            launcher.run(wrapped_channel, hadamard.system_qubits)[0],
            np.array([[1, -1], [-1, 1]]) / 2
        ), 1, delta=0.03)
