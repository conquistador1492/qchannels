from copy import copy


def preparation_full_set_of_qutrit_density_matrices(qr, cr, qc, backend_name=None):
    """
    :param qr: QuantumRegister or MaskRegister
    :param cr: ClassicalRegister or MaskRegister
    """
    names = ["rho_A0", "rho_A1", "rho_A2", "rho_B0", "rho_B1", "rho_B2",
             "rho_C0", "rho_C1", "rho_C2"]

    def _copy_qc(f):
        def new_f(qr, cr, qc=None):
            qc = copy(qc)
            f(qr, cr, qc)
            return qc
        return new_f

    @_copy_qc
    def _rho0(qr, cr, qc=None):
        qc.name = names[0]  # where A and 0 stand for type of basics element

    @_copy_qc
    def _rho1(qr, cr, qc=None):
        qc.name = names[1]
        qc.x(qr[0])

    @_copy_qc
    def _rho2(qr, cr, qc=None):
        qc.name = names[2]
        qc.x(qr[3])

    @_copy_qc
    def _rho3(qr, cr, qc=None):
        qc.name = names[3]
        qc.h(qr[0])

    @_copy_qc
    def _rho4(qr, cr, qc=None):
        qc.name = names[4]
        qc.h(qr[3])

    if backend_name in ['ibmqx4', 'ibmqx5']:
        @_copy_qc
        def _rho5(qr, cr, qc=None):
            qc.name = names[5]
            qc.h(qr[3])
            qc.x(qr[0])
            qc.cx(qr[3], qr[2])
            qc.cx(qr[2], qr[0])
            qc.cx(qr[3], qr[2])  # CNOT from 3rd to 0 :)
    else:
        @_copy_qc
        def _rho5(qr, cr, qc=None):
            qc.name = names[5]
            qc.h(qr[3])
            qc.x(qr[0])
            qc.cx(qr[3], qr[0])

    @_copy_qc
    def _rho6(qr, cr, qc=None):
        _rho3(qr, cr, qc)
        qc.name = names[6]
        qc.s(qr[0])

    @_copy_qc
    def _rho7(qr, cr, qc=None):
        _rho4(qr, cr, qc)
        qc.name = names[7]
        qc.s(qr[3])

    @_copy_qc
    def _rho8(qr, cr, qc=None):
        _rho5(qr, cr, qc)
        qc.name = names[8]
        qc.s(qr[3])

    variables = locals()
    return [variables[f"_rho{i}"](qr, cr, qc) for i in range(9)]
