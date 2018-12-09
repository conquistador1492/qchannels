#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from qchannels.core.launcher import Launcher

from qchannels.core.manage_parameters import set_parameters

parameters = set_parameters('Calculate Choi Matrix and fidelity between experiment '
                            'and theory prediction')

channel_class = parameters['channel_class']

launcher = Launcher(parameters['token'], parameters['backend_name'], parameters['shots'])
channel = channel_class(backend_name=parameters['backend_name'])

rho = launcher.run(channel, channel.get_system_qubits())
print(rho)
