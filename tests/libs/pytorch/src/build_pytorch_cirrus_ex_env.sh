#!/bin/bash 

PYTHON_TAG=python`echo ${CRAY_PYTHON_LEVEL} | cut -d. -f1-2`

# PRFX=${HOME/home/work}/pyenvs
# PYVENV_ROOT=${PRFX}/${PYVENV_NAME}
# PYVENV_SITEPKGS=${PYVENV_ROOT}/lib/${PYTHON_TAG}/site-packages

echo ${PYVENV_NAME}

mkdir -p ${PYVENV_NAME}
cd ${PYVENV_NAME}

python -m venv --system-site-packages ${PYVENV_NAME}
extend-venv-activate ${PYVENV_NAME}
source ${PYVENV_NAME}/bin/activate

mkdir -p ${PYVENV_NAME}/repos
cd ${PYVENV_NAME}/repos

## Install mlperf loging package
wget https://github.com/mlcommons/logging/archive/refs/tags/5.1.0-rc4.tar.gz
tar -zxvf 5.1.0-rc4.tar.gz
python -m pip install -e logging-5.1.0-rc4

python -m pip install git+https://github.com/ildoonet/pytorch-gradual-warmup-lr.git

python -m pip install h5py

deactivate