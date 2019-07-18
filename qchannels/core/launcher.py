from copy import copy
import numpy as np
from itertools import product

from qiskit import execute, QuantumCircuit
from qiskit.tools.monitor import job_monitor
from qiskit.ignis.verification.tomography import StateTomographyFitter
from qiskit.ignis.verification.tomography import state_tomography_circuits

from qchannels.core.tools import MAX_JOBS_PER_ONE, SIMULATORS, BACKENDS, chunks


def sort_list_and_transformation_matrix(a):
    """
    There is to sorts qubit. Also, it returns S matrix for changed density matrix
    :param a: list
    :return: (list, np.array(2**len(a), 2**len(a)))
    """
    length = len(a)
    S = np.eye(2**length, 2**length)
    b = copy(a)
    # bubble sort
    for i in range(length):
        for j in range(length-i-1):
            if b[j] > b[j+1]:
                b[j], b[j+1] = b[j+1], b[j]

                # TODO It's slow. Change it, please
                step_matrix = np.eye(2**length, 2**length)
                for digits in product([0, 1], repeat=length):
                    if digits[j] == digits[j+1]:
                        continue

                    first_number = sum([bit*2**n for n, bit in enumerate(digits)])
                    second_number = 0
                    for n, bit in enumerate(digits):
                        if n == j:
                            second_number += bit*2**(j+1)
                        elif n == j + 1:
                            second_number += bit*2**j
                        else:
                            second_number += bit*2**n

                    step_matrix[first_number, second_number] = 1
                    step_matrix[second_number, first_number] = 1
                    step_matrix[first_number, first_number] = 0
                    step_matrix[second_number, second_number] = 0

                S = step_matrix@S
    return b, S


class Launcher:
    def __init__(self, token=None, backend_name='ibmq_16_melbourne',
                 shots=8192):
        self.shots = shots
        self.token = token

        self.backend = next(filter(lambda x: x.name() == backend_name, BACKENDS))

        if backend_name in SIMULATORS:
            self.max_jobs_per_one = 10**6  # approximately infinity :)
        else:
            self.max_jobs_per_one = MAX_JOBS_PER_ONE

    def run(self, circuits, meas_qubits=None, measure=None, count_chunks=False):
        """
        :param circuits: list of QuantumCircuit or QuantumCircuit
        :param meas_qubits: list of qubits that will be measured.
        :param measure: optional. By default after channel transformation we do tomography.
        Not implemented now
        :return: depend on measure parameter. By default, it's list of density matrix
        """
        if measure is not None:
            raise NotImplementedError

        if isinstance(circuits, QuantumCircuit):
            circuits = [circuits]

        meas_qubits, s_matrix = sort_list_and_transformation_matrix(meas_qubits)
        number_measure_experiments = 3**len(meas_qubits)

        jobs = []
        for qc in circuits:
            qr = qc.qregs[0]
            tomo_circuits = state_tomography_circuits(
                qc, [qr[qubit_number] for qubit_number in meas_qubits]
            )
            jobs.extend(tomo_circuits)

        res = None
        for i, chunk_jobs in enumerate(chunks(jobs, self.max_jobs_per_one)):
            if count_chunks:
                print(f'chunk number: {i + 1}')
            execute_kwargs = {
                'experiments': chunk_jobs,
                'backend': self.backend,
                'shots': self.shots,
                'max_credits': 15
            }

            new_res = execute(**execute_kwargs).result()
            
            if res is None:
                res = new_res
            else:
                res.results.extend(new_res.results)

        matrices = []
        for i in range(int(len(res.results) / number_measure_experiments)):
            res_matrix = copy(res)
            res_matrix.results = res.results[
                i*number_measure_experiments:(i + 1)*number_measure_experiments
            ]

            rho = StateTomographyFitter(
                res_matrix,
                jobs[i*number_measure_experiments:(i + 1)*number_measure_experiments]
            ).fit()
            rho = np.linalg.inv(s_matrix) @ rho @ s_matrix
            matrices.append(rho)
        return matrices


