#!/bin/bash

if [[ "$(uname -s)" == 'Darwin' ]]; then
    PYTHON_VERSION=3.7.3
    rm -fr ~/.pyenv
    git clone -b v1.2.11 https://github.com/pyenv/pyenv.git ~/.pyenv
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"

    eval "$(pyenv init -)"

    PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install "$PYTHON_VERSION"
    pyenv shell "$PYTHON_VERSION" system
fi

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
conan user
