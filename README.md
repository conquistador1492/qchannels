This package is a library of algorithms for quantum computing
that uses [Qiskit Terra](https://qiskit.org/terra) to build out, compile and run quantum circuits.
It allows create quantum channels, easy move it through qubits and make
tomography. Also, it has ui interface for quick change different backends.


For example, consider Hadamard transformation.
Built the channel and make tomography
(using `mask` you can place it on different qubit without channel code changing)
```python
from qchannels.channels.abstract import AbstractChannelCircuit
from qchannels.core.manage_parameters import set_parameters
from qchannels.core.launcher import Launcher

import numpy as np


class Hadamard(AbstractChannelCircuit):
    REL_SYSTEM_QUBITS = [0]  # It is require only one qubit

    def create_circuit(self, q_regs, c_regs):
        self.h(q_regs[0])

    @staticmethod
    def get_theory_channel():
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        return lambda rho: H@rho@H


parameters = set_parameters('Test Hadamard transformation')

mask = {0: 3}  # It's optional. It change a qubit in channel, more detail in AbstractChannelCircuit
channel = Hadamard(backend_name=parameters['backend_name'], mask=mask)
launcher = Launcher(token=parameters['token'], backend_name=parameters['backend_name'],
                    shots=parameters['shots'])
print(launcher.run(channel, meas_qubits=channel.system_qubits)[0])
```

You can execute this file and get density matrix:
```bash
$ python examples/hadamard.py
[[0.50073241+0.j         0.49999289-0.00256344j]
 [0.49999289+0.00256344j 0.49926759+0.j        ]]
```
In order to run it on real computer, you just have to put it in arguments
```bash
$ python examples/hadamard.py -b ibmqx4
```
More information about arguments:
```bash
$ python examples/hadamard.py --help
```
Also you can measure fidelity of the channel. Just add:
```python
rho = launcher.run(channel, meas_qubits=channel.system_qubits)[0]
print(fidelity(rho, channel.get_theory_channel()(
    get_density_matrix_from_state(get_state(0, dim=2))
)))
```



### Dependencies

At least [Python 3.6 or later](https://www.python.org/downloads/) is needed

### Setup your environment

We recommend using python virtual environments to improve your experience. Refer to our
[Environment Setup documentation](doc/install.rst#3.1-Setup-the-environment) for more information.

### Installation
We encourage installing this package via the PIP tool (a python package manager):

```bash
pip install .
```
or
```bash
pip install package_directory/
```

### Instructions
Add your IBM token to Qconfig.py.example, rename to Qconfig.py
and move it to directory with the executable file.
