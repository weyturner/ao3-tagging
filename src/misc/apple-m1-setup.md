
Using and installing data science programs on a Apple Macbook Air M1
====================================================================


Use
---

This needs to be done each time a new Terminal window is opened.

Change to the Conda environment used for this project:

```
conda activate ao3-tagging
```

Change to the directory containing this projects:

```
cd src/ao3-tagging
```

Start Jupyter notebook

```
jupyter notebook
```

After a few seconds a browser tab should open with Jupyter.

Start a new Jupyter session by pressing [New🞃] and the selecting
[Python3].

See the folder src/explore/notebooks for saved Jupyter notebooks.


Background
----------

The Apple Macbook M1 uses the same type of CPU as Apple's
smartphones. It's called a "ARM-64 instruction set" which Apple market
as "Apple Silicon". Being in a larger computer than a phone, the CPU
is faster than the smartphone CPU as the laptop CPU can be larger and
use more power.

This is a different type of CPU to used in other manufactuers' laptop
computers. They use Intel or AMD CPUs. These use the "Intel x86-64
instruction set".

These x86-64 CPUs are not much more powerful than the Apple M1 CPU,
but use far more power. This is why the Macbook Air M1 needs no fan,
and the Macbook Air M2 could be made so thin.

Programs created for the "Intel x86-64" CPU can't be used on a
"ARM-64" CPU. The program needs to be re-created (jargon:
're-compiled') for the "ARM-64" CPU.

As a result, some care has to be taken when reading instructions on
web forums about installing software.


Installation
------------

Installation only needs to be done once.

The Anaconda project supports data sceince applications across MacOS,
Windows and Linux. Although most Linux distributions already come with
a wide selection of data science tools, Windows and MacOS do not.

The full Anaconda installation includes all the data science packages
you would every need. This is about 4GB of disk. This is handy for
researchers on national security projects, as those computers don't
have Internet access to install further packages.

But we do have Internet access. So we will install the minimum
Anaconda installation, Minconda, and install any packages we need from
a server on the internet. The usual Anaconda commands all work, they
simply use the internet as their source for package installation.

There's a small wrinkle, MacOS doesn't have libjpeg, that's easily
fixed as we've already installed `brew` so that we can have Linux
utilties under MacOS:

```
brew install libjpeg
```

Now install Miniconda by downloading

https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh

and running

```
bash Downloads/Miniconda3-latest-MacOSX-arm64.sh
```

When asked

> Do you wish the installer to initialize Miniconda3 by running conda
> init?”

respond "yes".

Close and reopen Terminal

Create the ao3-tagging project:

```
conda create --name ao3-tagging
```

Switch to that project and install the software packages the
ao3-tagging project needs:

```
conda activate ao3-tagging
conda install numpy pandas matplotlib jupyter seaborn pyyaml
```
