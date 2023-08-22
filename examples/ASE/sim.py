from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.langevin import Langevin
from ase.io.trajectory import Trajectory
from ase import units
from ase.io import read, write
from ase.calculators.cp2k import CP2K
import os

# System parameters
T = 300
dt = 0.5 * units.fs
friction = 0.05
append = True

cp2k_inp = '''
&FORCE_EVAL
&DFT
    BASIS_SET_FILE_NAME BASIS_PBE
    POTENTIAL_FILE_NAME PBE_POTENTIALS
    &QS
        METHOD GPW
        EXTRAPOLATION PS
        EXTRAPOLATION_ORDER 3
        EPS_DEFAULT 1.0E-10
    &END QS
    &POISSON
        PERIODIC XYZ
    &END POISSON
    &SCF
        EPS_SCF 1.0E-6
        SCF_GUESS ATOMIC
        MAX_SCF 50
        &OT T
            MINIMIZER DIIS
            PRECONDITIONER FULL_SINGLE_INVERSE
        &END OT
    &END SCF
    &XC
        &XC_FUNCTIONAL PBE
        &END XC_FUNCTIONAL
        &VDW_POTENTIAL
            DISPERSION_FUNCTIONAL PAIR_POTENTIAL
            &PAIR_POTENTIAL
            TYPE DFTD3
            PARAMETER_FILE_NAME dftd3.dat
            REFERENCE_FUNCTIONAL PBE
            R_CUTOFF [angstrom] 16.0
            &END PAIR_POTENTIAL
        &END VDW_POTENTIAL
    &END XC
    &LS_SCF
        MAX_SCF 50
    &END LS_SCF
&END DFT
&SUBSYS
    &KIND H
        MASS 2.0
        BASIS_SET DZVP-MOLOPT-PBE-GTH-q1
        POTENTIAL GTH-PBE-q1
    &END KIND
    &KIND O
        BASIS_SET DZVP-MOLOPT-PBE-GTH-q6
        POTENTIAL GTH-PBE-q6
    &END KIND
    &KIND Na
        BASIS_SET DZVP-MOLOPT-PBE-GTH-q9
        POTENTIAL GTH-PBE-q9
    &END KIND
    &KIND Cl
        BASIS_SET DZVP-MOLOPT-PBE-GTH-q7
        POTENTIAL GTH-PBE-q7
    &END KIND
&END SUBSYS
&END FORCE_EVAL
'''

if os.path.exists('md.traj'):
    traj = Trajectory('md.traj')
    atoms = traj[-1]
else:
    atoms = read('initial.xyz')

for atom in atoms:
    new_masses = atoms.get_masses()
    if atom.symbol == 'H':
        new_masses[atom.index] = 2.014
        atoms.set_masses(masses=new_masses)

calc = CP2K(basis_set_file=None,
            potential_file=None,
            basis_set=None,
            pseudo_potential=None,
            xc=None,
            max_scf=None,
            uks=None,
            cutoff=300*units.Ry,
            stress_tensor=False,
            inp=cp2k_inp)

atoms.set_calculator(calc)
# MaxwellBoltzmannDistribution(atoms, temperature_K=300)

dyn = Langevin(atoms,
               timestep=dt,
               temperature_K=T,
               friction=friction,
               logfile='md.log')

if os.path.exists('md.traj') and append:
    traj = Trajectory('md.traj', 'a', atoms)
else:
    traj = Trajectory('md.traj', 'w', atoms)


dyn.attach(traj.write, interval=1)
dyn.run(10)

traj.close()