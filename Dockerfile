# syntax=docker/dockerfile:1

FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y \
    curl \
    python3 \
    python3-pip \
    graphviz \
    git \
    texlive-xetex \
  && rm -rf /var/lib/apt/lists/*
RUN curl -L "https://downloads.python.org/pypy/pypy3.7-v7.3.5-linux64.tar.bz2" \
    | tar -xjC / \
    && ln -s /pypy3.7-v7.3.5-linux64/bin/pypy3 /usr/local/bin/pypy3 \
    && /usr/local/bin/pypy3 -m ensurepip
COPY . /bgp_simulator_pkg/
RUN pypy3 -m pip install -e /bgp_simulator_pkg/
