# PySAGES Example
This example will show how to run the same simulation, but with some enhanced sampling implemented through pysages. We will use ```SpectralABF``` to sample a small window of the potential energy surface for the separation of Na and Cl.
* Note that the simulation in this example is no where near converged, and is only meant to show how to use pysages.

## Prerequisites
Be sure to have installed PySAGES according to the instructions in the main README.md file. Don't forget to compile PySAGES while in your cp2k conda environment.

Similarly to the ASE only version of the code, we just need a python script (```sim.py```) and a slurm script (```submit.sh```). In the python script, we set up the similar manner, but this time within a function that we pass to PySAGES. This way PySAGES can start the simulation and have all of the information it needs to implement the enhanced sampling.

Here is an example of how to define the simulation in a function:
```
def simulation(T=T, dt=dt, friction=friction):
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

    return dyn
```
Notice at the end, we return the integrator, which will be taken in by PySAGES later in the script in order to run the simulation with enhanced sampling.

The PySAGES code can all be found within the ```main()``` method. There are a few steps to setting up and running the enhanced sampling:

1. Define the grid that you want to sample on
```
grid = pysages.Grid(lower=(2.8), upper=(3.3), shape=(20,), periodic=False)
```
2. Define a restraint to keep the system within the grid
```
restraint = CVRestraints(lower=(2.75), upper=(3.35), ku=(75), kl=(75))
```
3. Define the collective variable (CV)
```
cvs = [Distance([[339],[340]]),]
```
4. Set up the enhanced sampling method
```
method = SpectralABF(cvs, grid, restraints=restraint, N=250)
```
5. Run the simulation
```
state = pysages.run(method,simulation,10,callback)
```
6. Pickle the results
```
with open('raw_result.pickle', 'wb') as f:
        pickle.dump(state, f)
```
7. Analyze and plot the results (helper functions provided within python script)
```
result = pysages.analyze(state)
    plot_energy(result)
    plot_forces(result)
    plot_histogram(result)
    save_energy_forces(result)
```

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
The general results of the simulation are available in the following files:
* ```md.traj```: trajectory file
* ```md.log```: log file
* ```cp2k.out```: output file

The enhanced sampling results are available in the following files:
* ```raw_result.pickle```: raw results from PySAGES
* ```cv.dat```: The trajectory of the collective variable
* ```energy.png``` and ```FES.cv```: The free energy surface
* ```forces.png``` and ```Force.cv```: The force on the collective variable
* ```histogram.png``` and ```Histogram.csv```: The histogram of the collective variable