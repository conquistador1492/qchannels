from qchannels.channels.abstract import MaskRegister
from qiskit import QuantumCircuit


def preparation_full_set_of_qutrit_density_matrices(qr, cr=None, backend_name=None):
    """
    It use 0 and 3rd qubit
    :param qr: QuantumRegister or MaskRegister
    :param cr: ClassicalRegister or MaskRegister
    """
    names = ["rho_A0", "rho_A1", "rho_A2", "rho_B0", "rho_B1", "rho_B2",
             "rho_C0", "rho_C1", "rho_C2"]

    def _rho0(_qr, _cr, qc=None):
        qc.name = names[0] # where A and 0 stand for type of basics element
        return qc

    def _rho1(_qr, _cr, qc=None):
        qc.name = names[1]
        qc.x(_qr[0])
        return qc

    def _rho2(_qr, _cr, qc=None):
        qc.name = names[2]
        qc.x(_qr[3])
        return qc

    def _rho3(_qr, _cr, qc=None):
        qc.name = names[3]
        qc.h(_qr[0])
        return qc

    def _rho4(_qr, _cr, qc=None):
        qc.name = names[4]
        qc.h(_qr[3])
        return qc

    if backend_name in ['ibmqx4', 'ibmqx5']:
        def _rho5(_qr, _cr, qc=None):
            qc.name = names[5]
            qc.h(_qr[3])
            qc.x(_qr[0])
            qc.cx(_qr[3], _qr[2])
            qc.cx(_qr[2], _qr[0])
            qc.cx(_qr[3], _qr[2])  # CNOT from 3rd to 0 :)
            return qc
    else:
        def _rho5(_qr, _cr, qc=None):
            qc.name = names[5]
            qc.h(_qr[3])
            qc.x(_qr[0])
            qc.cx(_qr[3], _qr[0])
            return qc

    def _rho6(_qr, _cr, qc=None):
        qc = _rho3(_qr, _cr, qc)
        qc.name = names[6]
        qc.s(_qr[0])
        return qc

    def _rho7(_qr, _cr, qc=None):
        qc = _rho4(_qr, _cr, qc)
        qc.name = names[7]
        qc.s(_qr[3])
        return qc

    def _rho8(_qr, _cr, qc=None):
        qc = _rho5(_qr, _cr, qc)
        qc.name = names[8]
        qc.s(_qr[3])
        return qc

    variables = locals()
    if isinstance(qr, MaskRegister):
        qqr = qr.reg
    else:
        qqr = qr
    if isinstance(cr, MaskRegister):
        ccr = cr.reg
    else:
        ccr = cr
    if ccr is not None:
        return [variables[f"_rho{i}"](qr, cr, QuantumCircuit(qqr, ccr)) for i in range(9)]
    else:
        return [variables[f"_rho{i}"](qr, cr, QuantumCircuit(qqr)) for i in range(9)]
