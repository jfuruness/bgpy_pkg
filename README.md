NEEDS DOCS

Installation for dev
```
sudo apt install -y pypy3-dev python3-venv graphviz
# Higher version than in apt that supports python 3.7
# Must install from tarball
# https://www.pypy.org/download.html
<tarball_dir>/bin/pypy3 -m venv env
source env/bin/activate
git clone git@github.com:jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
# Many benifits to not using setup.py develop. One of which being that this installs from git repos
# https://stackoverflow.com/a/15731459/8903959
pypy3 -m pip install -e .
```


Note for these docs - for testing, the examples creates tests where there is a maximum of one prefix, one subprefix, and one suprefixes at the most (or a subset of those)
