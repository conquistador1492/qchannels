
import qiskit as qk

import numpy as np
import argparse
qr = qk.QuantumRegister(4)
cr = qk.ClassicalRegister(4)
qc = qk.QuantumCircuit(qr, cr)

basis = []
def rho0(qr, cr, qc):
    qc.circuit_name = "rho_A0" #where A and 0 stand for type of basics element

def rho1(qr, cr, qc):
    qc.circuit_name = "rho_A1"
    qc.x(qr[0])
def rho2(qr, cr, qc):
    qc.circuit_name = "rho_A2"
    qc.x(qr[3])
def rho3(qr, cr, qc):
    qc.circuit_name = "rho_B0"
    qc.h(qr[0])
def rho4(qr, cr, qc):
    qc.circuit_name = "rho_B1"
    qc.h(qr[3])
def rho5(qr, cr, qc):
    qc.circuit_name = "rho_B2"
    qc.h(qr[3])
    qc.x(qr[0])
    qc.cx(qr[3], qr[2])
    qc.cx(qr[2], qr[0])
    qc.cx(qr[3], qr[2]) #CNOT from 3rd to 1st :)
def rho6(qr, cr, qc):
    rho3(qr, cr, qc)
    qc.circuit_name = "rho_C0"
    qs.s(qr[0])
def rho7(qr, cr, qc):
    rho4(qr, cr, qc)
    qc.circuit_name = "rho_C1"
    qs.s(qr[3])
def rho8(qr, cr, qc):
    rho5(qr, cr, qc)
    qc.circuit_name = "rho_C2"
    qs.s(qr[0])

basis.append(rho0)
basis.append(rho1)
basis.append(rho2)
basis.append(rho3)
basis.append(rho4)
basis.append(rho5)
basis.append(rho6)
basis.append(rho7)
basis.append(rho8)
