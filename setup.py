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
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        'lib_caida_collector@git+https://github.com/jfuruness/lib_caida_collector',
        'lib_utils@git+https://github.com/jfuruness/lib_utils',
        'matplotlib==3.3.4',
        'pytest',
        'tqdm',
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
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
