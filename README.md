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
git clone git@github.com:jfuruness/lib_bgp_simulator.git
cd lib_bgp_simulator
pypy3 setup.py develop
```


Note for these docs - for testing, the examples creates tests where there is a maximum of one prefix, one subprefix, and one suprefixes at the most (or a subset of those)
