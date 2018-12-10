
def rho0(qr, cr, qc):
    qc.name = "rho_A0" #where A and 0 stand for type of basics element


def rho1(qr, cr, qc):
    qc.name = "rho_A1"
    qc.x(qr[0])


def rho2(qr, cr, qc):
    qc.name = "rho_A2"
    qc.x(qr[3])


def rho3(qr, cr, qc):
    qc.name = "rho_B0"
    qc.h(qr[0])


def rho4(qr, cr, qc):
    qc.name = "rho_B1"
    qc.h(qr[3])


def rho5(qr, cr, qc):
    qc.name = "rho_B2"
    qc.h(qr[3])
    qc.x(qr[0])
    qc.cx(qr[3], qr[2])
    qc.cx(qr[2], qr[0])
    qc.cx(qr[3], qr[2]) #CNOT from 3rd to 1st :)


def rho6(qr, cr, qc):
    rho3(qr, cr, qc)
    qc.name = "rho_C0"
    qc.s(qr[0])


def rho7(qr, cr, qc):
    rho4(qr, cr, qc)
    qc.name = "rho_C1"
    qc.s(qr[3])


def rho8(qr, cr, qc):
    rho5(qr, cr, qc)
    qc.name = "rho_C2"
    qc.s(qr[3])

variables = locals()
QUTRIT_BASIS_FUNC = [variables['rho' + str(i)] for i in range(9)]
