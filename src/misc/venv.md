# Python virtual environment

Fedora doesn't package wordcloud, we'll need to do it the hard way.


## MacOS

Use the conda system with MacOS rather than using Python environments.


### Usage

The usual instructions, namely:

```
cd src/ao3-tagging
conda activate ao3-tagging
jupyter notebook
```

### Before use: install worldcloud,  and any other Python packages

```
conda activate ao3-tagging
conda install wordcloud
```


## Linux

You'll want a virtuall environment, and you'll want that available to
Jupyter too.


### Usage

```
cd src/ao3-tagging
source venv/bin/activate
jupyter notebook
```

Inside Jupyter select Kernel | Change Kernel | venv. Restart the kernel
and run all cells.


### Before first use: create venv, create kernel, install workcloud

Create a Python virtual environment with

```
cd src/ao3-tagging
virtualenv venv --system-site-packages
source venv/bin/activate
```

Install wordcloud, or any other Python package, with

```
cd src/ao3-tagging
source venv/bin/activate
pip install wordcloud
```

Create a Jupyter kernel to use this virtual environment

```
cd src/ao3-tagging
source venv/bin/activate
python -m ipykernel install --user --name venv
jupyter notebook
```

and follow the instructions above to change the kernel.


### Removing the Jupyter kernel

```
cd src/ao3-tagging
source venv/bin/activate
jupyter-kernelspec uninstall venv
# or ipython kernelspec remove venv
```


## References

https://paulnelson.ca/posts/install-virtual-env-ipykernel-jupyter

https://ipython.readthedocs.io/en/stable/install/kernel_install.html
