# GPac-2C

## Setup

Ensure both run.sh and driver.py are executable

`chmod +x run.sh`

`chmod +x ./source/driver.py`

Setup and activate a virtual environment

`/linux_apps/python-3.6.1/bin/python3 -m venv env`

`source ./env/bin/activate`

## Dependencies

Ensure all pip dependencies are installed
`pip install -r requirements.txt`

If you want to do my graphing and excel modules you'll need to install those dependencies as well
`pip install -r requirements_util.txt`

## Running

`./run.sh config_filepath [-p]`
