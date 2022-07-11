#!/bin/bash

# https://stackoverflow.com/a/23164271/8903959
~/work/pypy_env/bin/pypy3 -m cProfile -o /tmp/myLog.profile no_prof_speed_tests.py
~/work/pypy_env/bin/gprof2dot -f pstats /tmp/myLog.profile -o /tmp/callingGraph.dot
dot -Tpng /tmp/callingGraph.dot > ~/Desktop/profile_results.png
