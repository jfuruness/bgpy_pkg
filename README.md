[![Windows](https://svgshare.com/i/ZhY.svg)](https://svgshare.com/i/ZhY.svg)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
![Tests](https://github.com/jfuruness/lib_bgp_simulator/actions/workflows/tests.yml/badge.svg)

# lib\_bgp\_simulator
This package simulates BGP, ROV, BGP propagation, various attack/defend scenarios, draws diagrams of the internet, etc

* [Description](#package-description)
* [Usage](#usage)
* [Installation](#installation)
* [Testing](#testing)
* [Development/Contributing](#developmentcontributing)
* [History](#history)
* [Credits](#credits)
* [Licence](#license)
* [TODO](#todo)

## Package Description

TODO

## Usage
* [lib\_bgp\_simulator](#lib_bgp_simulator)

TODO

## Installation
* [lib\_bgp\_simulator](#lib_bgp_simulator)

Install python and pip if you have not already. Then run:

```bash
sudo apt-get install -y graphviz libjpeg-dev zlib1g-dev texlive-xetex
pip3 install wheel
```

For production:

```bash
pip3 install git@github.com:jfuruness/lib_bgp_simulator.git
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:
```bash
git clone https://github.com/jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
pip3 install -e .[test]
```

To test the development package: [Testing](#testing)


## Testing
* [lib\_bgp\_simulator](#lib_bgp_simulator)

To test the package after installation:

```
cd lib_bgp_simulator
pytest lib_bgp_simulator
flake8 lib_bgp_simulator
mypy lib_bgp_simulator
```

If you want to run it across multiple environments, and have python 3.9 installed:

```
cd lib_bgp_simulator
tox
```


## Development/Contributing
* [lib\_bgp\_simulator](#lib_bgp_simulator)

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Run tox
6. Email me at jfuruness@gmail.com

## History
* [lib\_bgp\_simulator](#lib_bgp_simulator)
* 0.0.1 Refactored package. Semi working version

## Credits
* [lib\_bgp\_simulator](#lib_bgp_simulator)

Thanks to Cameron Morris for helping with extending the BGP policy to include withdrawals, RIBsIn, RIBsOut

Thanks to Reynaldo for filling in some system test graphs

Thanks to Dr. Herzberg and Dr. Wang for employing me and allowing this project to be open source

## License
* [lib\_bgp\_simulator](#lib_bgp_simulator)

BSD License (see license file)

## TODO
* [lib\_bgp\_simulator](#lib_bgp_simulator)

See Jira
