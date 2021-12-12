from setuptools import setup, find_packages
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# https://stackoverflow.com/a/58534041/8903959
setup(
    name='lib_bgp_simulator',
    author="Justin Furuness, Cameron Morris",
    author_email="jfuruness@gmail.com",
    version="0.0.1",
    url='https://github.com/jfuruness/lib_bgp_simulator.git',
    license="BSD",
    description="Simulates BGP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Furuness", "BGP", "Simulations", "ROV",
              "Peers", "Customers", "Providers"],
    include_package_data=True,
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=[
        'graphviz',
        'lib_caida_collector @ git+ssh://git@github.com/jfuruness/lib_caida_collector.git',
        'matplotlib',
        'pytest',
        'pytest-xdist',
        'tqdm',
        'yamlable',
        'pytest-cov',
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'],
    entry_points={
        'console_scripts': 'lib_bgp_simulator = lib_bgp_simulator.__main__:main'
    },
    extras_require = { 
        'cluster': ['ray'],
    }, 
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
