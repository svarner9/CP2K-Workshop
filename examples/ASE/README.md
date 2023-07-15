# ASE Example
In this example we run the same exact simulation but using ASE to wrap CP2K, rather than running directly in CP2K.

## Prerequisites
We will need a python file, called ```sim.py``` that will run the simulation. In this
python file we will need to include everything for ASE as well as a stripped version of our cp2k input file. And of course we will also need our slurm file for sbatch.

### Python file (sim.py)
The file is pretty self-explanatory, but I will call your attention to how we set up the CP2K calculator. There are two ways to pass information to the CP2K calculator in ASE:
1. via a string containing part of the input file
2. via arguments in the CP2K calculator method in ASE

Not all parts of the input script are translated to arguments in the CP2K calculator method, so you will likely always need to use both to completely specify the system, as in the example below.
```
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
```
If your atoms are starting without any velocities, you will need to add them in the python file as well. This is done with the following command:
```
MaxwellBoltzmannDistribution(atoms, temperature_K=T)
```
The rest of the python file is just normal ASE commands for setting up an integrator and running a simulation.

### Slurm script (submit.sh)
The slurm script has an extra nuance, which is that we need to tell ASE how to use the CP2K shell, which we do through an environment variable:
```
export ASE_CP2K_COMMAND="mpirun -np 64 $CONDA_PREFIX/bin/cp2k_shell.psmp"
```
To run the simulation script, we use python:
```
python sim.py
```

## Running the calculation
We will need to make sure we have our cp2k conda environment activated, and then we can run the slurm script using sbatch:
```
conda activate cp2k
sbatch submit.sh
```

## Results
The results of the simulation are available in the following files:
* ```md.traj```: trajectory file
* ```md.log```: log file
* ```cp2k.out```: output file