# Flixtube: P2P streaming
Project made as the Master Thesis ["Utilizing IPFS as a content provider for DASH video streaming"](https://github.com/andreasmalling/Master-Thesis).

## Getting started
1. Install *Docker*, *Docker Compose*, *Pumba* and *Python 3.5*
2. Download and unzip the project from this code repository
3. Navigate into root folder of project
4. Run ``python3 run.py envs/exp.env`` for a simple experiment or check out ``python3 run.py --help`` for more options

## Project description
This project simulates various user behaviour and emulates certain network conditions in a testing framework used for evaluating IPFS as a backend for hosting videos watch through the MPEG-DASH protocol. This is done in a docker environment.

A steady state local IPFS network is started, hosting any specified video resource among any chosen number of peers.
An experimental state of users are introduced, and network conditions may be applied.

All behaviour any network trafic are logged in a MongoDB, and plotted when the experiment are done.
