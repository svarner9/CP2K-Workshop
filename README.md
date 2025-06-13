# CP2K and ASE Workshop
Some examples of how to run biased AIMD simulations using the CP2K software, combined with the ASE and PySAGES python packages.

## Program installation
We will be using conda to install the necessary python packages, and the CP2K software.

### CP2K
The CP2K software can be downloaded and compiled for the machine you want to run on, however,
this is a very difficult process, so for this tutorial, we will simply use the conda package manager to install it.

This is NOT recommended, since it will not be optimized for the machine, but it will work for the purposes of this tutorial.

Make a new conda environment, and install the cp2k package:
```
conda create -n cp2k
conda activate cp2k
conda install -c conda-forge cp2k
```
The cp2k executable files we are looking for should be at,
```
$CONDA_PREFIX/bin/cp2k.psmp
$CONDA_PREFIX/bin/cp2k_shell.psmp
```
where ```$CONDA_PREFIX``` is the path to the conda environment you just created. The ```cp2k.psmp``` file is the main executable, and ```cp2k_shell.psmp``` is the shell that is used by ASE to run cp2k.

We will also need the ```cp2k/data``` folder which contains the basis sets and pseudopotentials. We can get
this from the cp2k github repository:
```
git clone https://github.com/cp2k/cp2k.git
mv cp2k/data $CONDA_PREFIX/cp2k-data
rm -rf cp2k
```
For this tutorial only, I have included some custom data files in ```./custom-data```. These are the files that are used in the examples. Lets copy them to the cp2k-data folder:
```
cp -r custom-data/* $CONDA_PREFIX/cp2k-data
```


### ASE
ASE is a python package that allows us to run the cp2k software from python. It can be installed using conda:
```
conda install -c conda-forge ase
```

### PySAGES
PySAGES is a python implementation of SSAGES which allows us to run enhanced sampling methods
within various MD packages (we are using ASE). There are a few steps to installing PySAGES, but it is not too difficult.

First we need to install the dependencies.
```
conda install --yes numpy numba
conda install --yes -c conda-forge cupy
conda install --yes gsd matplotlib
pip install --upgrade "jax[cuda11_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

If we don't need cuda aware Jax, then we can install the cpu only version. However, even if you aren't using GPU right away, the version above will still work just fine, so it is recomended to use that one.
```
conda install --yes jax jaxlib
```

Now to install PySAGES, we can clone the repository and install it using pip.
```
cd $HOME
git clone https://github.com/SSAGESLabs/PySAGES.git
cd PySAGES
pip install .
```

If you are using Pylance, then you probably want to add PySAGES to the include paths. To do this, you can go to the Pylance extension settings and add ```~/PySAGES``` to you include paths.

## Running the examples
The examples run NVT simulations of sodium chloride (NaCl) in water (H2O).

There are examples of three different ways of running simulations:
1. Directly in CP2K using the ```cp2k.psmp``` executable.
2. Using ASE to run CP2K with the ```cp2k_shell.psmp``` executable.
3. Using PySAGES wrap ASE and run CP2K with the ```cp2k_shell.psmp``` executable.

The three examples are in separate folders called, respectively:
1. ```examples/CP2K```
2. ```examples/ASE```
3. ```examples/PySAGES```

For details about the examples, see the README.md files in each folder.
