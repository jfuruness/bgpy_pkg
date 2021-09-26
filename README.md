NEEDS DOCS

Installation for dev:
```
git clone git@github.com:jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
python3 setup.py develop
```

Installation for speed
```
sudo apt install -y pypy3 pypy3-dev python3-venv
pypy3 -m venv env
source env/bin/activate
sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev     libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk     libharfbuzz-dev libfribidi-dev libxcb1-dev
pypy3 -m pip install matplotlib
git clone git@github.com:jfuruness/lib_utils.git
cd lib_bgp_simulator
pypy3 setup.py develop
git clone git@github.com:jfuruness/lib_caida_collector.git
cd lib_bgp_simulator
pypy3 setup.py develop
git clone git@github.com:jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
pypy3 setup.py develop
```


Note for these docs - for testing, the examples creates tests where there is a maximum of one prefix, one subprefix, and one suprefixes at the most (or a subset of those)
