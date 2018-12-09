import numpy as np
from qiskit import IBMQ, Aer

np.set_printoptions(threshold=np.nan)

IBMQ_SIMULATOR = 'ibmq_qasm_simulator'
LOCAL_SIMULATOR = 'qasm_simulator'
SIMULATORS = [IBMQ_SIMULATOR, LOCAL_SIMULATOR]
MAX_JOBS_PER_ONE = 70
BACKENDS = Aer.backends()  # In set_parameters() BACKENDS will be supplemented IBMQ.backends()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def destroy_circuits(qp):
    for circuit_name in qp.get_circuit_names():
        qp.destroy_circuit(circuit_name)
