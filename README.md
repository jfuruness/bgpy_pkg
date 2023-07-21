Docs [here](https://github.com/jfuruness/lib_ddos_simulator/wiki)

Example system test on a small topology:
![system test](https://example.com/images/sunset.jpg)














# NOTE: This documentation is slightly outdated. We have external documentation we are moving in the week of July 17th.


[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
![Tests](https://github.com/jfuruness/bgpy/actions/workflows/tests.yml/badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# bgpy
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

This package simulates BGP, ROV, BGP propagation, various attack/defend scenarios, draws diagrams of the internet, etc

## Usage
* [bgpy](#bgpy)

Note: the simulator takes about 1-2GB per core. Make sure you don't run out of RAM!

NOTE: This section is located within our external documentation, which we plan on moving into the repo the week of July 17, however, there are some examples below

Some good examples for how to use this can be found in bgpy/bgpy/\_\_main\_\_.py, and can be run by running:

```bash
bgpy
```

## Installation
* [bgpy](#bgpy)

Install python and pip if you have not already. Then run:

```bash
# Needed for graphviz and Pillow
sudo apt-get install -y graphviz libjpeg-dev zlib1g-dev
pip3 install pip --upgrade
pip3 install wheel
```

For production:

```bash
pip3 install git@github.com:jfuruness/bgpy.git
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:
```bash
git clone https://github.com/jfuruness/bgpy.git
cd bgpy
pip3 install -e .[test]
```

To test the development package: [Testing](#testing)


## Testing
* [bgpy](#bgpy)

To test the package after installation:

```
cd bgpy
ruff bgpy
black bgpy
pytest bgpy
```

If you want to run it across multiple environments, and have python 3.10 installed:

```
cd bgpy
tox
```


## Development/Contributing
* [bgpy](#bgpy)

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Add an engine test if you've made a change in the simulation_engine, or a system/unit test if the simulation_framework was modified
5. Run tox (for faster iterations: flake8, mypy, and pytest can be helpful)
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin my-new-feature`
8. Ensure github actions are passing tests
9. Email me at jfuruness@gmail.com in case I don't see the PR

## History
* [bgpy](#bgpy)

* 1.0.0 First Major Release. Many changes for the conference version. Since prior to this point all changes were internal, won't list them all here, but will keep better records from now on.
* 0.2.1 Various bug fixes. PRs from Cameron (Thank you!). input clique rounding up now. Victims/attackers no longer being counted. No more windows support.
* 0.2.0 Fixed subgraph issues. Changed the -1 and 101% cases to be SpecialPercentAdoptions
* 0.1.03 Fixed subgraph bug that resulted in incorrect graphs
* 0.1.02 Removed slots from ASes since it does not increase speed, and now ASes with different slots can be interchanged
* 0.1.01 Added optional gao rexford kwargs to allow easier subclassing (I undid this)
* 0.1.0 Major refactor and name change. I believe this version will be stable. Deps saved.
* 0.0.4 Major refactor
* 0.0.2 Fixed dependencies so that they weren't relying off ssh, since github doesn't support pip installs with ssh and github actions failed
* 0.0.1 Refactored package. Semi working version

## Credits
* [bgpy](#bgpy)

Thanks to Cameron Morris for helping with extending the BGP policy to include withdrawals, RIBsIn, RIBsOut.

Thanks to Cameron and Reynaldo for helping out a ton with this simulator and it's corresponding testing. They have been major contributors and I appreciate it.

Also thanks to Reynaldo for the awesome name, love it.

Thanks to Dr. Herzberg and Dr. Wang for employing me and allowing this project to be open source

Thanks to Matt Jaccino and Tony Zheng for assistance with the initial implementation of the Caida Collector

## License
* [bgpy](#bgpy)

BSD License (see license file)

## TODO
* [bgpy](#bgpy)

* Update the typing so that the AS class is either consistently coming from the CaidaCollector or the BGPSimpleAS, not this weird mix of both.
* Imports should be reordered sensibly
See Jira

## Design Decisions

We can't output CSVs for each trial of the graph and then later aggregate, analyze the data, etc.
This is because we would be outputting a ton of data into CSVs (30+ gigabytes for the RPV++ configuration for example) and this would be way too slow for Python.
Instead, we average the trials as we go, keeping it in RAM, and only writing the aggregate data onto disk at the end.

We ended up moving the caida collector into this repo for a few reasons.
There is less dependency madness. If you are installing for development, pypy will overwrite your local install of the caida collector witht he caida collector within git.
This will allow for much better typing
Previously this was separate because it was used in many other places, however, now it is only used within this simulator
This is really coupled with the simulator now, since the base of the caida collector serves as the base for the simulator itself
We will be able to dynamically make the subgraphs part of the caida collector, with an enum that someone can inherit and use, veasy easily if it's part of the simulator

__slots__ was initially used for a speedup, however this caused problems with extendability because we are swapping out the __class__ attribute for ASes that may have routing policies that require the use of new instance attributes. This is specifically noted as a use case against __slots__ in the documentation. Also, when we ran the testing with pypy to determine the time difference, it was less than 1 second with everything having slots or nothing have slots for 100 trials. In other words, the difference was negligable, so for easier development, __slots__ were removed from everything other than the announcements. Additionally, a lot of the benefit of these is likely negated by using the YamlAble base class, which, afaik, doesn't use slots.

pytest-cov has also been removed. It brings the testing time up to 10 minutes (when normally it is less than 30 seconds). This does not play well with pypy, and also does not work with multiprocessing after their 4.0.0 release, so thus it is no longer a default. Developers can add it as they wish, just be aware it is quite slow.
