import numpy as np

np.set_printoptions(threshold=np.nan)

LOCAL_BACKEND = 'local_qasm_simulator'
MAX_JOBS_PER_ONE = 70


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def destroy_circuits(qp):
    for circuit_name in qp.get_circuit_names():
        qp.destroy_circuit(circuit_name)
