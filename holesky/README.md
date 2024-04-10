# EigenDA Exploration -- Holesky
This repository contains exploratory work around the use of EigenDA as a data availability solution for IPFS systems. This setup is intended for the Holesky testnet.

### Prerequisite:
* [Install Conda](https://docs.anaconda.com/free/distro-or-miniconda/)
* [Install Go](https://go.dev/doc/install)

* Run the following:
```
    mkdir eigenda-setup && cd eigenda-setup
    git clone https://github.com/dmp267/eigenda-exploration.git
    git clone https://github.com/Layr-Labs/eigenda.git

    conda env create -f eigenda-exploration/holesky/eigenda.env.yml && conda activate eigenda-exploration

    cd eigenda
    make build
    cd ../eigenda-exploration/holesky

    python hello_world.py
```
* Clone the [Layr-Labs/EigenDA repo](https://github.com/Layr-Labs/eigenda/tree/master)
