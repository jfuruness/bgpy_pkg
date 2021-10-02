NEEDS DOCS

Installation for dev:
```
git clone git@github.com:jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
python3 setup.py develop
```

Installation for speed
```
sudo apt install -y pypy3-dev python3-venv
# Higher version than in apt that supports python 3.7
# Must install from tarball
# https://www.pypy.org/download.html
<tarball_dir>/bin/pypy3 -m venv env
source env/bin/activate
sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev
git clone git@github.com:jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
# Many benifits to not using setup.py develop. One of which being that this installs from git repos
# https://stackoverflow.com/a/15731459/8903959
pip3 install -e .
```


Note for these docs - for testing, the examples creates tests where there is a maximum of one prefix, one subprefix, and one suprefixes at the most (or a subset of those)
